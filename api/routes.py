"""
FastAPI Routes - endpointy API z SSE streaming.
"""
import uuid
import asyncio
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.streaming import (
    create_session,
    get_session,
    event_generator,
    create_emit_callback,
    emit_thinking,
    emit_done,
    emit_error,
)
from services.graph import run_analysis_streaming
from core.config import REGIONS, COUNTRIES, SOURCES
from schemas.schemas import AnalyzeRequest, AnalyzeResponse, SessionStatusResponse


router = APIRouter(prefix="/api", tags=["analysis"])


# === ENDPOINTS ===

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Rozpoczyna analizę geopolityczną asynchronicznie.

    Zwraca session_id do użycia z GET /api/stream/{session_id}
    """
    session_id = str(uuid.uuid4())

    # Regiony i sektory są teraz stringami (elastyczne)
    regions = request.regions or ["europe"]
    sectors = request.sectors or ["security", "diplomacy", "trade", "conflicts"]

    # Konfiguracja
    config = {
        "regions": regions,
        "countries": request.countries or [],
        "sectors": sectors,
        "weights": request.weights or {},
        "timeframes": request.timeframes or ["12m", "36m"],
        "scenarios": ["positive", "negative"],
    }

    # Stwórz sesję
    create_session(session_id, request.query, config)

    # Uruchom analizę w tle
    background_tasks.add_task(
        run_analysis_background,
        session_id,
        request.query,
        config
    )

    return AnalyzeResponse(session_id=session_id)


async def run_analysis_background(session_id: str, query: str, config: dict):
    """
    Background task wykonujący analizę.
    Emituje eventy przez SSE.
    """
    emit = create_emit_callback(session_id)
    session = get_session(session_id)

    if not session:
        return

    try:
        session.status = "running"
        await emit_thinking(emit, "system", f"Rozpoczynam analizę: {query[:100]}...")

        # Uruchom graf z callbackiem
        result = await run_analysis_streaming(query, config, emit)

        # Zapisz wynik
        session.result = result
        session.status = "completed"

        await emit_done(emit, session_id, result)

    except Exception as e:
        session.status = "error"
        await emit_error(emit, str(e))
        raise


@router.get("/stream/{session_id}")
async def stream(session_id: str):
    """
    SSE endpoint - streamuje eventy z analizy w czasie rzeczywistym.

    Użycie w JavaScript:
    ```js
    const eventSource = new EventSource(`/api/stream/${sessionId}`);
    eventSource.onmessage = (e) => {
        const event = JSON.parse(e.data);
        console.log(event.type, event.content);
    };
    ```

    Event types:
    - thinking: Agent analizuje
    - document: Znaleziono dokumenty
    - progress: Postęp
    - report: Sekcja raportu
    - scenario: Scenariusz końcowy
    - error: Błąd
    - done: Zakończono
    - heartbeat: Keep-alive (co 30s)
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesja nie znaleziona")

    return StreamingResponse(
        event_generator(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Wyłącz buforowanie nginx
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.get("/session/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """Pobiera status sesji."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesja nie znaleziona")

    return SessionStatusResponse(
        session_id=session.session_id,
        status=session.status,
        created_at=session.created_at.isoformat(),
        query=session.query
    )


@router.get("/session/{session_id}/result")
async def get_session_result(session_id: str):
    """Pobiera wynik analizy (po zakończeniu)."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesja nie znaleziona")

    if session.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analiza nie zakończona. Status: {session.status}"
        )

    return {
        "session_id": session_id,
        "query": session.query,
        "result": session.result
    }


# === ENDPOINTS POMOCNICZE ===

@router.get("/regions")
async def list_regions():
    """Lista dostępnych regionów."""
    return {
        "regions": [
            {"code": code, "name": data["name"], "countries": data.get("countries", [])}
            for code, data in REGIONS.items()
        ]
    }


@router.get("/countries")
async def list_countries():
    """Lista dostępnych krajów."""
    return {
        "countries": [
            {"code": code, "name": data["name"]}
            for code, data in COUNTRIES.items()
        ]
    }


@router.get("/sources")
async def list_sources():
    """Lista dostępnych źródeł."""
    return {
        "sources": [
            {"code": code, "name": data["name"], "type": data["type"]}
            for code, data in SOURCES.items()
        ]
    }
