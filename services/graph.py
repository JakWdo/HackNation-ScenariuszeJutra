"""
Graf LangGraph - supervisor i workflow z SSE streaming.

Obsługuje dwa tryby:
1. run_analysis() - synchroniczny, bez streamingu
2. run_analysis_streaming() - asynchroniczny z emit callback
"""
from typing import Dict, Any, List, Callable, Optional
from functools import partial

from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END

from services.llm import get_llm
from core.config import SUPERVISOR_PROMPT, REGIONS
from schemas.schemas import RouteResponse
from agents.nodes import region_node, country_node, synthesis_node, scenario_node, EmitCallback


# Dostępni agenci
AGENTS = {
    "region_agent": {"node": region_node, "desc": "Analiza regionów (EU, USA, NATO)"},
    "country_agent": {"node": country_node, "desc": "Analiza krajów i źródeł"},
    "synthesis_agent": {"node": synthesis_node, "desc": "Tworzenie raportów końcowych"},
}


def create_supervisor_node(emit: Optional[EmitCallback] = None):
    """
    Tworzy node supervisora decydującego o routingu.

    Args:
        emit: Opcjonalny callback SSE
    """
    llm = get_llm(temperature=0.3)
    options = ["FINISH"] + list(AGENTS.keys())
    members_desc = "\n".join([f"- {name}: {data['desc']}" for name, data in AGENTS.items()])

    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
        ("system", f"Wybierz: {options}"),
    ])

    chain = prompt | llm.with_structured_output(RouteResponse)

    async def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state.get("messages", [])
        query = messages[0].content if messages else ""

        # Emituj że supervisor myśli
        if emit:
            await emit({
                "type": "thinking",
                "agent": "supervisor",
                "content": f"Analizuję zapytanie i wybieram następnego agenta..."
            })

        result = chain.invoke({
            "messages": messages,
            "members_desc": members_desc,
            "query": query
        })
        next_step = result.next if result.next in options else "FINISH"

        # Emituj decyzję
        if emit:
            await emit({
                "type": "progress",
                "agent": "supervisor",
                "content": f"Przekazuję do: {next_step}"
            })

        print(f"[SUPERVISOR] -> {next_step}")
        return {"next": next_step}

    return supervisor_node


def build_graph(emit: Optional[EmitCallback] = None) -> StateGraph:
    """
    Buduje graf agentów.

    Args:
        emit: Opcjonalny callback SSE dla streaming
    """
    from typing import TypedDict, Annotated, Sequence
    import operator

    class GraphState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        next: str
        region: str | None
        country: str | None
        source: str | None
        context: str
        region_analysis: Dict[str, Any] | None
        country_analysis: Dict[str, Any] | None
        expert_analyses: List[Dict[str, Any]] | None
        final_report: Dict[str, Any] | None
        scenarios: List[Dict[str, Any]] | None
        timeframe: str | None
        variant: str | None

    workflow = StateGraph(GraphState)

    # Dodaj supervisor z emit
    workflow.add_node("supervisor", create_supervisor_node(emit))

    # Dodaj agentów z emit callback
    for name, data in AGENTS.items():
        # Wrap node z emit
        if emit:
            async def node_with_emit(state, node_fn=data["node"], emit_fn=emit):
                return await node_fn(state, emit_fn)
            workflow.add_node(name, node_with_emit)
        else:
            workflow.add_node(name, data["node"])

        workflow.add_edge(name, "supervisor")

    # Routing
    conditional_map = {name: name for name in AGENTS.keys()}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
    workflow.add_edge(START, "supervisor")

    return workflow.compile()


def run_analysis(
    query: str,
    region: str = None,
    country: str = None,
    source: str = None,
    context: str = ""
) -> Dict[str, Any]:
    """
    Uruchamia pełną analizę (synchronicznie, bez streamingu).

    Args:
        query: Zapytanie analityczne
        region: Kod regionu (EU, USA, NATO, RUSSIA, ASIA)
        country: Kod kraju (DE, US, PL, ...)
        source: Kod źródła (NATO, EU_COMMISSION, ...)
        context: Dodatkowy kontekst

    Returns:
        Dict ze stanem końcowym grafu
    """
    graph = build_graph()
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "next": "",
        "region": region,
        "country": country,
        "source": source,
        "context": context,
        "region_analysis": None,
        "country_analysis": None,
        "expert_analyses": [],
        "final_report": None,
        "scenarios": [],
        "timeframe": None,
        "variant": None,
    }
    return graph.invoke(initial_state)


async def run_analysis_streaming(
    query: str,
    config: Dict[str, Any],
    emit: EmitCallback
) -> Dict[str, Any]:
    """
    Uruchamia analizę z SSE streaming.

    Flow:
    1. Supervisor analizuje zapytanie
    2. Dla każdego regionu - uruchom region_node
    3. Dla każdego kraju - uruchom country_node
    4. Synteza wszystkich analiz
    5. Generowanie 4 scenariuszy (12m/36m × pos/neg)

    Args:
        query: Zapytanie analityczne
        config: Konfiguracja z regions, countries, sectors, weights
        emit: Callback do emitowania eventów SSE

    Returns:
        Dict z final_report i scenarios
    """
    regions = config.get("regions", ["EU"])
    countries = config.get("countries", [])
    sectors = config.get("sectors", ["POLITICS", "ECONOMY", "DEFENSE", "SOCIETY"])
    timeframes = config.get("timeframes", ["12m", "36m"])
    variants = config.get("scenarios", ["positive", "negative"])

    # === FAZA 1: Meta Supervisor ===
    await emit({
        "type": "thinking",
        "agent": "meta_supervisor",
        "content": f"Analizuję zapytanie: {query[:100]}..."
    })

    await emit({
        "type": "progress",
        "agent": "meta_supervisor",
        "content": f"Planuję analizę dla {len(regions)} regionów, {len(countries)} krajów"
    })

    # === FAZA 2: Analiza regionów ===
    all_analyses = []

    for region in regions:
        await emit({
            "type": "thinking",
            "agent": f"region_{region}",
            "content": f"Rozpoczynam analizę regionu {REGIONS.get(region, {}).get('name', region)}..."
        })

        # Uruchom region_node
        region_state = {
            "messages": [HumanMessage(content=query)],
            "region": region,
            "context": f"Sektory: {', '.join(sectors)}"
        }

        try:
            result = await region_node(region_state, emit)
            if result.get("region_analysis"):
                all_analyses.append({
                    "agent_name": f"Region: {region}",
                    "agent_type": "region",
                    "content": result["region_analysis"].get("summary", "")
                })
        except Exception as e:
            await emit({
                "type": "error",
                "agent": f"region_{region}",
                "content": f"Błąd analizy regionu {region}: {str(e)}"
            })

    # === FAZA 3: Analiza krajów ===
    for country in countries[:5]:  # Limit do 5 krajów dla demo
        await emit({
            "type": "thinking",
            "agent": f"country_{country}",
            "content": f"Analizuję stanowisko kraju {country}..."
        })

        country_state = {
            "messages": [HumanMessage(content=query)],
            "country": country,
            "source": "NATO",  # Domyślne źródło
            "context": f"Regiony: {', '.join(regions)}"
        }

        try:
            result = await country_node(country_state, emit)
            if result.get("country_analysis"):
                all_analyses.append({
                    "agent_name": f"Kraj: {country}",
                    "agent_type": "country",
                    "content": result["country_analysis"].get("official_position", "")
                })
        except Exception as e:
            await emit({
                "type": "error",
                "agent": f"country_{country}",
                "content": f"Błąd analizy kraju {country}: {str(e)}"
            })

    # === FAZA 4: Synteza ===
    await emit({
        "type": "thinking",
        "agent": "synthesis",
        "content": f"Syntetyzuję {len(all_analyses)} analiz eksperckich..."
    })

    synthesis_state = {
        "messages": [HumanMessage(content=query)],
        "expert_analyses": all_analyses,
        "region_analysis": None,
        "country_analysis": None,
    }

    synthesis_result = await synthesis_node(synthesis_state, emit)
    final_report = synthesis_result.get("final_report", {})

    # === FAZA 5: Generowanie scenariuszy ===
    scenarios = []

    for timeframe in timeframes:
        for variant in variants:
            await emit({
                "type": "thinking",
                "agent": f"scenario_{timeframe}_{variant}",
                "content": f"Generuję scenariusz {variant} na {timeframe}..."
            })

            scenario_state = {
                "messages": [HumanMessage(content=query)],
                "final_report": final_report,
                "timeframe": timeframe,
                "variant": variant,
                "scenarios": []
            }

            try:
                result = await scenario_node(scenario_state, emit)
                if result.get("scenarios"):
                    scenarios.extend(result["scenarios"])
            except Exception as e:
                await emit({
                    "type": "error",
                    "agent": f"scenario_{timeframe}_{variant}",
                    "content": f"Błąd generowania scenariusza: {str(e)}"
                })
    return {
        "final_report": final_report,
        "scenarios": scenarios,
        "expert_analyses": all_analyses
    }


# ============================================================================
# MVP FLOW - Uproszczony przepływ (2 kroki zamiast 4)
# ============================================================================

async def run_mvp_analysis(
    query: str,
    config: Dict[str, Any],
    emit: EmitCallback
) -> Dict[str, Any]:
    """
    Uproszczony flow MVP: analysis_node → scenarios_node

    Zastępuje skomplikowany run_analysis_streaming() dwoma prostymi krokami:
    1. analysis_node - RAG search + generowanie raportu
    2. scenarios_node - 4 scenariusze równolegle

    Args:
        query: Zapytanie analityczne
        config: Konfiguracja (regions, countries, sectors, timeframes)
        emit: Callback do emitowania eventów SSE

    Returns:
        Dict z analysis_report, scenarios, retrieved_docs
    """
    from agents.nodes import analysis_node, scenarios_node

    # Początkowy stan
    state = {
        "messages": [HumanMessage(content=query)],
        "config": config,
        "analysis_report": "",
        "retrieved_docs": [],
        "scenarios": []
    }

    # === KROK 1: Analiza ===
    await emit({
        "type": "thinking",
        "agent": "system",
        "content": f"Rozpoczynam analizę: {query[:100]}..."
    })

    try:
        state = await analysis_node(state, emit)
    except Exception as e:
        await emit({
            "type": "error",
            "agent": "analysis",
            "content": f"Błąd podczas analizy: {str(e)}"
        })
        raise

    # === KROK 2: Scenariusze ===
    try:
        state = await scenarios_node(state, emit)
    except Exception as e:
        await emit({
            "type": "error",
            "agent": "scenarios",
            "content": f"Błąd podczas generowania scenariuszy: {str(e)}"
        })
        raise

    return {
        "analysis_report": state.get("analysis_report", ""),
        "scenarios": state.get("scenarios", []),
        "retrieved_docs": state.get("retrieved_docs", [])
    }
