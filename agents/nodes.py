from typing import Dict, Any, Callable, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from services.llm import get_llm
from core.config import (
    REGIONS, COUNTRIES, SOURCES,
    REGION_PROMPT, COUNTRY_PROMPT, SYNTHESIS_PROMPT,
    SCENARIO_ANALYSIS_PROMPT, RECOMMENDATIONS_PROMPT,
    QUALITY_RULES, REPORT_LENGTH_REQUIREMENTS
)
from schemas.schemas import (
    RegionAnalysis, CountryAnalysis, ExpertAnalysis,
    FullReport, ReportSectionType
)
from services.tools import search_vector_store, get_region_info, search_by_source, search_by_country, get_search_service
from services.rag.search import SearchStrategy


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

    # Emituj wyszukiwanie
    await emit({
        "type": "progress",
        "agent": agent_name,
        "content": "Przeszukuję bazę dokumentów..."
    })

    # 1. Waliduj region - fallback do None jeśli nie istnieje w bazie
    search_region = region if region in REGIONS else None

    # 2. Wyszukaj dokumenty PRZED agentem
    service = get_search_service()
    search_results = service.search(
        query=query,
        n_results=5,
        region=search_region,
        strategy=SearchStrategy.HYBRID
    )

    # 3. Emituj PRAWDZIWE dokumenty
    await emit({
        "type": "document",
        "agent": agent_name,
        "content": f"Znaleziono {len(search_results)} dokumentów dla regionu {region}",
        "docs": [
            {
                "title": r.metadata.title or r.content[:80] + "..." if len(r.content) > 80 else r.content,
                "source": r.metadata.source,
                "relevance": round(r.relevance_score, 2),
                "url": r.metadata.url
            }
            for r in search_results
        ]
    })

    # 4. Przygotuj kontekst dokumentów dla agenta
    docs_context = "\n---\n".join([
        f"[Źródło: {r.metadata.source}, Relevance: {r.relevance_score:.2f}]\n{r.content}"
        for r in search_results
    ]) if search_results else "Brak dokumentów w bazie dla tego regionu."

    # 5. Uruchom agenta z kontekstem dokumentów
    llm = get_llm(temperature=0.3)
    agent = create_react_agent(model=llm, tools=[search_vector_store, get_region_info])

    result = await agent.ainvoke({
        "messages": [HumanMessage(content=f"{prompt}\n\nDokumenty źródłowe:\n{docs_context}\n\nZapytanie: {query}")]
    })
    summary = result["messages"][-1].content

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

    # Emituj wyszukiwanie
    await emit({
        "type": "progress",
        "agent": agent_name,
        "content": f"Przeszukuję dokumenty dla {country_name}..."
    })

    # 1. Wyszukaj dokumenty PRZED agentem (po źródle lub kraju)
    service = get_search_service()
    search_results = []

    # Priorytet: najpierw po źródle, potem po kraju
    if source:
        search_results = service.search(
            query=query,
            n_results=5,
            source=source,
            strategy=SearchStrategy.HYBRID
        )

    if not search_results and country:
        search_results = service.search(
            query=query,
            n_results=5,
            country=country,
            strategy=SearchStrategy.HYBRID
        )

    # Fallback: wyszukaj bez filtrów
    if not search_results:
        search_results = service.search(
            query=query,
            n_results=5,
            strategy=SearchStrategy.HYBRID
        )

    # 2. Emituj PRAWDZIWE dokumenty
    await emit({
        "type": "document",
        "agent": agent_name,
        "content": f"Znaleziono {len(search_results)} dokumentów dla {country_name} ({source_name})",
        "docs": [
            {
                "title": r.metadata.title or r.content[:80] + "..." if len(r.content) > 80 else r.content,
                "source": r.metadata.source,
                "relevance": round(r.relevance_score, 2),
                "url": r.metadata.url
            }
            for r in search_results
        ]
    })

    # 3. Przygotuj kontekst dokumentów dla agenta
    docs_context = "\n---\n".join([
        f"[Źródło: {r.metadata.source}, Relevance: {r.relevance_score:.2f}]\n{r.content}"
        for r in search_results
    ]) if search_results else "Brak dokumentów w bazie dla tego kraju/źródła."

    # 4. Uruchom agenta z kontekstem dokumentów
    llm = get_llm(temperature=0.3)
    
    agent = create_react_agent(model=llm, tools=[search_by_source, search_by_country])

    result = await agent.ainvoke({
        "messages": [HumanMessage(content=f"{prompt}\n\nDokumenty źródłowe:\n{docs_context}\n\nZapytanie: {query}")]
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

    # Prompt dla scenariusza - używa SCENARIO_ANALYSIS_PROMPT
    scenario_type = "POZYTYWNY" if variant == "positive" else "NEGATYWNY"
    word_limit = "300-400" if timeframe == "12m" else "350-450"

    # Dane wejściowe i wagi (symulowane - w pełnej wersji z RAG)
    input_data = f"Raport bazowy:\n{report.get('executive_summary', '')}\n\nZapytanie: {query}"
    weights = "Domyślne wagi: geopolityka=0.8, ekonomia=0.7, obronność=0.9"

    scenario_prompt = SCENARIO_ANALYSIS_PROMPT.format(
        input_data=input_data,
        weights=weights
    )

    scenario_prompt += f"""

ZADANIE: Wygeneruj scenariusz {scenario_type} dla państwa Atlantis na perspektywę {timeframe}.

Limit słów: {word_limit}

Struktura:
1. Sytuacja wyjściowa (~50 słów)
2. Rozwój wydarzeń (~150-200 słów)
3. WYJAŚNIENIE KORELACJI I ZWIĄZKÓW PRZYCZYNOWO-SKUTKOWYCH (min. 120 słów) - OBOWIĄZKOWE
4. Kluczowe niepewności (~30-50 słów)

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


# ============================================================================
# MVP NODES - Uproszczone węzły (2 zamiast 4)
# ============================================================================

import asyncio
from core.config import MVP_ANALYSIS_PROMPT, MVP_SCENARIO_PROMPT


async def analysis_node(state: Dict[str, Any], emit: Optional[EmitCallback] = None) -> Dict[str, Any]:
    """
    Główny węzeł analizy MVP: RAG search → LLM → raport.
    Łączy funkcje region_node + country_node + synthesis_node.

    Args:
        state: Stan z messages, config
        emit: Callback SSE

    Returns:
        Stan z analysis_report i retrieved_docs
    """
    emit = emit or noop_emit
    messages = state.get("messages", [])
    query = messages[-1].content if messages else ""
    config = state.get("config", {})

    regions = config.get("regions", ["EU"])
    countries = config.get("countries", [])
    sectors = config.get("sectors", ["security", "trade", "diplomacy"])

    # === FAZA 1: Wyszukiwanie dokumentów ===
    await emit({
        "type": "thinking",
        "agent": "analysis",
        "content": f"Przeszukuję bazę dokumentów dla: {query[:100]}..."
    })

    service = get_search_service()
    all_docs = []

    # Wyszukaj dla każdego regionu
    for region in regions:
        try:
            results = service.search(
                query=query,
                n_results=5,
                region=region if region in REGIONS else None,
                strategy=SearchStrategy.HYBRID
            )
            all_docs.extend(results)
        except Exception as e:
            await emit({
                "type": "error",
                "agent": "analysis",
                "content": f"Błąd wyszukiwania dla regionu {region}: {str(e)}"
            })

    # Wyszukaj dla krajów (limit do 3)
    for country in countries[:3]:
        try:
            results = service.search(
                query=query,
                n_results=3,
                country=country if country in COUNTRIES else None,
                strategy=SearchStrategy.HYBRID
            )
            all_docs.extend(results)
        except Exception as e:
            await emit({
                "type": "error",
                "agent": "analysis",
                "content": f"Błąd wyszukiwania dla kraju {country}: {str(e)}"
            })

    # Fallback - wyszukaj bez filtrów jeśli brak wyników
    if not all_docs:
        await emit({
            "type": "thinking",
            "agent": "analysis",
            "content": "Brak wyników z filtrami, szukam w całej bazie..."
        })
        results = service.search(
            query=query,
            n_results=10,
            strategy=SearchStrategy.HYBRID
        )
        all_docs.extend(results)

    # Deduplikacja
    seen = set()
    unique_docs = []
    for doc in all_docs:
        content_hash = hash(doc.content[:200] if len(doc.content) > 200 else doc.content)
        if content_hash not in seen:
            seen.add(content_hash)
            unique_docs.append(doc)

    # Emituj dokumenty
    await emit({
        "type": "document",
        "agent": "analysis",
        "content": f"Znaleziono {len(unique_docs)} dokumentów",
        "docs": [
            {
                "title": d.metadata.title or (d.content[:80] + "..." if len(d.content) > 80 else d.content),
                "source": d.metadata.source,
                "relevance": round(d.relevance_score, 2),
                "url": d.metadata.url
            }
            for d in unique_docs[:10]
        ]
    })

    # === FAZA 2: Generowanie raportu ===
    await emit({
        "type": "thinking",
        "agent": "analysis",
        "content": "Generuję raport analityczny..."
    })

    # Przygotuj kontekst dokumentów
    docs_context = "\n---\n".join([
        f"[Źródło: {d.metadata.source}] {d.content}"
        for d in unique_docs[:15]
    ]) if unique_docs else "Brak dokumentów w bazie. Analiza oparta na wiedzy ogólnej."

    # Prompt MVP
    analysis_prompt = MVP_ANALYSIS_PROMPT.format(
        query=query,
        regions=", ".join(regions),
        countries=", ".join(countries) if countries else "brak specyficznych",
        sectors=", ".join(sectors),
        documents=docs_context
    )

    llm = get_llm(temperature=0.4)
    result = await llm.ainvoke(analysis_prompt)
    report_content = result.content

    # Emituj raport
    await emit({
        "type": "report",
        "agent": "analysis",
        "section": "main_analysis",
        "content": report_content[:1500] if len(report_content) > 1500 else report_content
    })

    await emit({
        "type": "thinking",
        "agent": "analysis",
        "content": "Raport główny gotowy. Przechodzę do scenariuszy..."
    })

    return {
        **state,
        "analysis_report": report_content,
        "retrieved_docs": [
            {
                "content": d.content,
                "source": d.metadata.source,
                "relevance": d.relevance_score,
                "url": d.metadata.url
            }
            for d in unique_docs
        ]
    }


async def scenarios_node(state: Dict[str, Any], emit: Optional[EmitCallback] = None) -> Dict[str, Any]:
    """
    Generuje 4 scenariusze równolegle (asyncio.gather).

    Scenariusze:
    - 12m pozytywny, 12m negatywny
    - 36m pozytywny, 36m negatywny

    Args:
        state: Stan z analysis_report
        emit: Callback SSE

    Returns:
        Stan z scenarios
    """
    emit = emit or noop_emit
    report = state.get("analysis_report", "")
    messages = state.get("messages", [])
    query = messages[0].content if messages else ""

    await emit({
        "type": "thinking",
        "agent": "scenarios",
        "content": "Generuję 4 scenariusze rozwoju sytuacji..."
    })

    # Konfiguracja scenariuszy
    scenario_configs = [
        {"timeframe": "12 miesięcy", "variant": "positive", "variant_pl": "POZYTYWNY", "word_limit": "300-400"},
        {"timeframe": "12 miesięcy", "variant": "negative", "variant_pl": "NEGATYWNY", "word_limit": "300-400"},
        {"timeframe": "36 miesięcy", "variant": "positive", "variant_pl": "POZYTYWNY", "word_limit": "350-450"},
        {"timeframe": "36 miesięcy", "variant": "negative", "variant_pl": "NEGATYWNY", "word_limit": "350-450"},
    ]

    async def generate_single_scenario(config: dict) -> dict:
        """Generuje pojedynczy scenariusz."""
        timeframe = config["timeframe"]
        variant = config["variant"]
        variant_pl = config["variant_pl"]
        word_limit = config["word_limit"]

        scenario_prompt = MVP_SCENARIO_PROMPT.format(
            timeframe=timeframe,
            variant_pl=variant_pl,
            word_limit=word_limit,
            report=report,
            query=query
        )

        # Różna temperatura dla pozytywnych/negatywnych
        llm = get_llm(temperature=0.5 if variant == "positive" else 0.3)
        result = await llm.ainvoke(scenario_prompt)

        # Confidence zależny od horyzontu czasowego
        confidence = 0.75 if "12" in timeframe else 0.55

        return {
            "timeframe": timeframe,
            "variant": variant,
            "content": result.content,
            "confidence": confidence
        }

    # Generuj wszystkie równolegle
    scenarios = await asyncio.gather(*[
        generate_single_scenario(cfg) for cfg in scenario_configs
    ])

    # Emituj każdy scenariusz
    for scenario in scenarios:
        await emit({
            "type": "scenario",
            "agent": "scenarios",
            "timeframe": scenario["timeframe"],
            "variant": scenario["variant"],
            "title": f"Scenariusz {scenario['variant']} ({scenario['timeframe']})",
            "content": scenario["content"],
            "confidence": scenario["confidence"]
        })

    await emit({
        "type": "thinking",
        "agent": "scenarios",
        "content": "Wszystkie scenariusze wygenerowane."
    })

    return {
        **state,
        "scenarios": list(scenarios)
    }
