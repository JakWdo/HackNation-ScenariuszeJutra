"""
SSE Streaming - real-time eventy z agentów do frontendu.

Sesje analizy przechowywane in-memory (dla demo).
Produkcyjnie: Redis lub podobne.
"""
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Callable, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class EventType(str, Enum):
    """Typy eventów SSE."""
    THINKING = "thinking"      # Agent "myśli"
    DOCUMENT = "document"      # Znaleziono dokumenty
    PROGRESS = "progress"      # Postęp pracy
    REPORT = "report"          # Fragment raportu
    SCENARIO = "scenario"      # Scenariusz końcowy
    ERROR = "error"            # Błąd
    DONE = "done"              # Zakończono
    HEARTBEAT = "heartbeat"    # Keep-alive


@dataclass
class AnalysisSession:
    """Sesja analizy z kolejką eventów."""
    session_id: str
    query: str
    config: Dict[str, Any]
    events: asyncio.Queue = field(default_factory=asyncio.Queue)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    result: Optional[Dict[str, Any]] = None


# In-memory store sesji
_sessions: Dict[str, AnalysisSession] = {}


def create_session(session_id: str, query: str, config: Dict[str, Any]) -> AnalysisSession:
    """Tworzy nową sesję analizy."""
    session = AnalysisSession(
        session_id=session_id,
        query=query,
        config=config
    )
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> Optional[AnalysisSession]:
    """Pobiera sesję po ID."""
    return _sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    """Usuwa sesję."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


async def emit_event(session_id: str, event: Dict[str, Any]) -> bool:
    """
    Emituje event do sesji.

    Event format:
    {
        "type": "thinking" | "document" | "progress" | "report" | "scenario" | "error" | "done",
        "agent": "supervisor" | "region_EU" | "country_DE" | ...,
        "content": "...",
        "timestamp": "ISO datetime",
        ...dodatkowe pola zależne od typu
    }

    Returns:
        True jeśli event został dodany, False jeśli sesja nie istnieje
    """
    session = get_session(session_id)
    if not session:
        return False

    # Dodaj timestamp jeśli brak
    if "timestamp" not in event:
        event["timestamp"] = datetime.now().isoformat()

    await session.events.put(event)
    return True


async def event_generator(session_id: str, timeout: float = 30.0) -> AsyncGenerator[str, None]:
    """
    Generator SSE dla danej sesji.
    Używany przez endpoint GET /api/stream/{session_id}

    Args:
        session_id: ID sesji
        timeout: Timeout w sekundach między eventami (heartbeat)

    Yields:
        Stringi w formacie SSE: "data: {...}\n\n"
    """
    session = get_session(session_id)
    if not session:
        yield f"data: {json.dumps({'type': 'error', 'content': 'Sesja nie znaleziona'})}\n\n"
        return

    try:
        while True:
            try:
                # Czekaj na event z timeout
                event = await asyncio.wait_for(
                    session.events.get(),
                    timeout=timeout
                )

                # Serializuj i wyślij
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

                # Zakończ jeśli done lub error
                if event.get("type") in (EventType.DONE, EventType.ERROR, "done", "error"):
                    break

            except asyncio.TimeoutError:
                # Heartbeat co timeout sekund
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

    except asyncio.CancelledError:
        # Klient rozłączył się
        pass
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


def create_emit_callback(session_id: str) -> Callable:
    """
    Tworzy async callback do przekazania agentom.

    Użycie w agencie:
        emit = create_emit_callback(session_id)
        await emit({"type": "thinking", "agent": "region_EU", "content": "Analizuję..."})

    Returns:
        Async funkcja emit(event: dict) -> bool
    """
    async def emit(event: Dict[str, Any]) -> bool:
        return await emit_event(session_id, event)

    return emit


# === HELPER FUNCTIONS dla agentów ===

async def emit_thinking(emit: Callable, agent: str, content: str):
    """Helper: emituj event typu 'thinking'."""
    await emit({
        "type": EventType.THINKING,
        "agent": agent,
        "content": content
    })


async def emit_documents(emit: Callable, agent: str, docs: list, query: str = ""):
    """Helper: emituj event z dokumentami."""
    await emit({
        "type": EventType.DOCUMENT,
        "agent": agent,
        "content": f"Znaleziono {len(docs)} dokumentów",
        "query": query,
        "docs": [
            {
                "title": doc.get("title", doc.get("content", "")[:50]),
                "source": doc.get("source", "unknown"),
                "relevance": doc.get("relevance", 0.0),
                "url": doc.get("url"),
                "credibility": doc.get("credibility")
            }
            for doc in docs[:10]  # Max 10 w UI
        ]
    })


async def emit_progress(emit: Callable, agent: str, status: str, progress: float = None):
    """Helper: emituj postęp."""
    event = {
        "type": EventType.PROGRESS,
        "agent": agent,
        "content": status
    }
    if progress is not None:
        event["progress"] = progress
    await emit(event)


async def emit_report_section(emit: Callable, section: str, content: str):
    """Helper: emituj sekcję raportu."""
    await emit({
        "type": EventType.REPORT,
        "agent": "synthesis",
        "section": section,
        "content": content
    })


async def emit_scenario(emit: Callable, timeframe: str, variant: str, title: str, content: str, confidence: float):
    """Helper: emituj scenariusz."""
    await emit({
        "type": EventType.SCENARIO,
        "agent": "synthesis",
        "timeframe": timeframe,
        "variant": variant,
        "title": title,
        "content": content,
        "confidence": confidence
    })


async def emit_done(emit: Callable, session_id: str, result: Dict[str, Any] = None):
    """Helper: emituj zakończenie."""
    await emit({
        "type": EventType.DONE,
        "session_id": session_id,
        "result": result
    })


async def emit_error(emit: Callable, error: str, agent: str = "system"):
    """Helper: emituj błąd."""
    await emit({
        "type": EventType.ERROR,
        "agent": agent,
        "content": error
    })
