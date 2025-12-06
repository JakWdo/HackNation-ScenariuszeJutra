from typing import Dict, Any, Callable, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from services.llm import get_llm
from core.config import (
    REGIONS, COUNTRIES, SOURCES,
    REGION_PROMPT, COUNTRY_PROMPT, SYNTHESIS_PROMPT
)
from schemas.schemas import (
    RegionAnalysis, CountryAnalysis, ExpertAnalysis,
    FullReport, ReportSectionType
)
from services.tools import search_vector_store, get_region_info, search_by_source, search_by_country


# Typ dla emit callback
EmitCallback = Callable[[Dict[str, Any]], Any]

async def noop_emit(event: Dict[str, Any]) -> None:
    """Pusty emit dla wywołań bez streamingu."""
    pass


async def region_node(state: Dict[str, Any], emit: Optional[EmitCallback] = None) -> Dict[str, Any]:
    """
    Analizuje region geopolityczny.

    Args:
        state: Stan grafu z messages, region, context
        emit: Opcjonalny callback do emitowania eventów SSE
    """
    emit = emit or noop_emit
    messages = state.get("messages", [])
    query = messages[-1].content if messages else ""
    region = state.get("region", "EU")
    context = state.get("context", "")

    agent_name = f"region_{region}"

    # Emituj rozpoczęcie
    await emit({
        "type": "thinking",
        "agent": agent_name,
        "content": f"Analizuję region {REGIONS.get(region, {}).get('name', region)}..."
    })

    region_info = REGIONS.get(region, {})
    prompt = REGION_PROMPT.format(
        region=region_info.get("name", region),
        context=context
    )

    llm = get_llm(temperature=0.3)
    agent = create_react_agent(model=llm, tools=[search_vector_store, get_region_info])

    # Emituj wyszukiwanie
    await emit({
        "type": "progress",
        "agent": agent_name,
        "content": "Przeszukuję bazę dokumentów..."
    })

    result = await agent.ainvoke({
        "messages": [HumanMessage(content=f"{prompt}\n\nZapytanie: {query}")]
    })
    summary = result["messages"][-1].content

    # Emituj znalezione dokumenty (symulacja - prawdziwe docs z RAG)
    await emit({
        "type": "document",
        "agent": agent_name,
        "content": f"Znaleziono dokumenty dla regionu {region}",
        "docs": [
            {"title": f"Raport {region} Q4 2024", "source": "internal", "relevance": 0.92},
            {"title": f"Analiza geopolityczna {region}", "source": "NATO", "relevance": 0.87},
        ]
    })

    analysis = RegionAnalysis(region=region, summary=summary)

    # Emituj zakończenie
    await emit({
        "type": "thinking",
        "agent": agent_name,
        "content": f"Zakończono analizę regionu {region}"
    })

    return {
        "messages": messages + [AIMessage(content=summary)],
        "region_analysis": analysis.model_dump(),
    }


# === COUNTRY NODE ===

async def country_node(state: Dict[str, Any], emit: Optional[EmitCallback] = None) -> Dict[str, Any]:
    """
    Analizuje kraj/źródło.

    Args:
        state: Stan grafu z messages, country, source, context
        emit: Opcjonalny callback do emitowania eventów SSE
    """
    emit = emit or noop_emit
    messages = state.get("messages", [])
    query = messages[-1].content if messages else ""
    country = state.get("country")
    source = state.get("source", "NATO")
    context = state.get("context", "")

    country_name = COUNTRIES.get(country, {}).get("name", country) if country else "nieznany"
    source_name = SOURCES.get(source, {}).get("name", source)
    agent_name = f"country_{country or source}"

    # Emituj rozpoczęcie
    await emit({
        "type": "thinking",
        "agent": agent_name,
        "content": f"Analizuję stanowisko {country_name} (źródło: {source_name})..."
    })

    prompt = COUNTRY_PROMPT.format(
        country=country_name,
        source=source_name,
        context=context
    )

    llm = get_llm(temperature=0.3)
    agent = create_react_agent(model=llm, tools=[search_by_source, search_by_country])

    # Emituj wyszukiwanie
    await emit({
        "type": "progress",
        "agent": agent_name,
        "content": f"Przeszukuję dokumenty dla {country_name}..."
    })

    result = await agent.ainvoke({
        "messages": [HumanMessage(content=f"{prompt}\n\nZapytanie: {query}")]
    })
    position = result["messages"][-1].content

    analysis = CountryAnalysis(
        country=country,
        source=source,
        official_position=position
    )

    # Emituj zakończenie
    await emit({
        "type": "thinking",
        "agent": agent_name,
        "content": f"Zakończono analizę {country_name}"
    })

    return {
        "messages": messages + [AIMessage(content=position)],
        "country_analysis": analysis.model_dump(),
    }

async def synthesis_node(state: Dict[str, Any], emit: Optional[EmitCallback] = None) -> Dict[str, Any]:
    """
    Tworzy raport końcowy z analiz.

    Args:
        state: Stan grafu ze wszystkimi analizami
        emit: Opcjonalny callback do emitowania eventów SSE
    """
    emit = emit or noop_emit
    messages = state.get("messages", [])
    query = messages[0].content if messages else ""

    # Emituj rozpoczęcie
    await emit({
        "type": "thinking",
        "agent": "synthesis",
        "content": "Rozpoczynam syntezę wszystkich analiz..."
    })

    # Zbierz analizy ekspertów
    expert_analyses = []

    if state.get("region_analysis"):
        ra = state["region_analysis"]
        expert_analyses.append(ExpertAnalysis(
            agent_name=f"Region: {ra.get('region', '?')}",
            agent_type="region",
            content=ra.get("summary", ""),
        ))

    if state.get("country_analysis"):
        ca = state["country_analysis"]
        expert_analyses.append(ExpertAnalysis(
            agent_name=f"Kraj: {ca.get('source', '?')}",
            agent_type="country",
            content=ca.get("official_position", ""),
        ))

    # Dla każdej analizy z listy
    for analysis in state.get("expert_analyses", []):
        expert_analyses.append(ExpertAnalysis(
            agent_name=analysis.get("agent_name", "Expert"),
            agent_type=analysis.get("agent_type", "unknown"),
            content=analysis.get("content", ""),
        ))

    await emit({
        "type": "progress",
        "agent": "synthesis",
        "content": f"Syntetyzuję {len(expert_analyses)} analiz eksperckich..."
    })

    expert_text = "\n---\n".join([
        f"### {a.agent_name}\n{a.content}"
        for a in expert_analyses
    ])
    prompt = SYNTHESIS_PROMPT.format(expert_analyses=expert_text)

    llm = get_llm(temperature=0.5)
    agent = create_react_agent(model=llm, tools=[])

    result = await agent.ainvoke({
        "messages": [HumanMessage(content=f"{prompt}\n\nZapytanie: {query}")]
    })
    content = result["messages"][-1].content

    avg_confidence = sum(a.confidence for a in expert_analyses) / max(len(expert_analyses), 1)

    report = FullReport(
        title=f"Raport: {query[:50]}",
        executive_summary=content,
        sections={s.value: "" for s in ReportSectionType},
        confidence_score=avg_confidence,
    )

    # Emituj sekcje raportu
    await emit({
        "type": "report",
        "agent": "synthesis",
        "section": "executive_summary",
        "content": content[:500]
    })

    # Emituj zakończenie syntezy
    await emit({
        "type": "thinking",
        "agent": "synthesis",
        "content": "Raport główny gotowy. Generuję scenariusze..."
    })

    return {
        "messages": messages + [AIMessage(content=content)],
        "final_report": report.model_dump(),
    }

async def scenario_node(state: Dict[str, Any], emit: Optional[EmitCallback] = None) -> Dict[str, Any]:
    """
    Generuje pojedynczy scenariusz (pozytywny/negatywny, 12m/36m).

    Args:
        state: Stan z final_report, timeframe, variant
        emit: Callback SSE
    """
    emit = emit or noop_emit
    timeframe = state.get("timeframe", "12m")
    variant = state.get("variant", "positive")
    query = state.get("messages", [{}])[0].content if state.get("messages") else ""
    report = state.get("final_report", {})

    agent_name = f"scenario_{timeframe}_{variant}"

    await emit({
        "type": "thinking",
        "agent": agent_name,
        "content": f"Generuję scenariusz {variant} na {timeframe}..."
    })

    # Prompt dla scenariusza
    scenario_prompt = f"""Na podstawie poniższego raportu, wygeneruj szczegółowy scenariusz
dla państwa Atlantis na perspektywę {timeframe}.

Wariant: {'POZYTYWNY - optymistyczny rozwój wydarzeń' if variant == 'positive' else 'NEGATYWNY - pesymistyczny rozwój wydarzeń'}

Raport bazowy:
{report.get('executive_summary', '')}

Zapytanie oryginalne: {query}

Struktura scenariusza:
1. Streszczenie (max 100 słów)
2. Kluczowe wydarzenia i trendy
3. Wpływ na Atlantis:
   - Polityka
   - Gospodarka
   - Obronność
   - Społeczeństwo
4. Rekomendacje dla rządu Atlantis

Odpowiedz w formacie Markdown."""

    llm = get_llm(temperature=0.6 if variant == "positive" else 0.4)
    result = await llm.ainvoke(scenario_prompt)
    scenario_content = result.content

    # Oblicz confidence na podstawie danych
    base_confidence = 0.7 if timeframe == "12m" else 0.5
    confidence = base_confidence + (0.1 if variant == "positive" else -0.05)

    # Emituj scenariusz
    await emit({
        "type": "scenario",
        "agent": agent_name,
        "timeframe": timeframe,
        "variant": variant,
        "title": f"Scenariusz {variant} ({timeframe})",
        "content": scenario_content,
        "confidence": confidence
    })

    return {
        "scenarios": state.get("scenarios", []) + [{
            "timeframe": timeframe,
            "variant": variant,
            "content": scenario_content,
            "confidence": confidence
        }]
    }


def report_to_markdown(report: FullReport) -> str:
    """Konwertuje raport do Markdown."""
    md = f"# {report.title}\n\n"
    md += f"*{report.generated_at}* | Pewność: {report.confidence_score:.0%}\n\n"
    md += f"## Podsumowanie\n\n{report.executive_summary}\n"
    return md
