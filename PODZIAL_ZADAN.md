# Scenariusze Jutra - Podział Zadań

## Timeline

| Faza | Czas | Cel |
|------|------|-----|
| **TERAZ → 19:00** | 3.5h | Szkic działający E2E |
| **19:00 → 23:00** | 4h | Polish + debugging |
| **Jutro 8:00 → 11:00** | 3h | Final fixes + prezentacja |

### Synchronizacje
- **17:30** - Osoba 1 & 2: test query do ChromaDB
- **18:30** - Osoba 2 & 3: test streaming agentów do UI
- **19:00** - Full E2E test

---

## 👤 OSOBA 1: Data Pipeline

**Cel:** ChromaDB z ~500+ dokumentów do 19:00

| # | Task | Plik | Czas |
|---|------|------|------|
| 1.1 | Setup ChromaDB + Gemini embeddings | `services/vector_store.py` | 30min |
| 1.2 | RSS/Atom scraper (NATO, CSIS, EU, UK) | `scrapers/rss_scraper.py` | 1h |
| 1.3 | HTML scraper (State, Kiel, DE) | `scrapers/html_scraper.py` | 1h |
| 1.4 | Chunker z metadanymi | `services/chunker.py` | 30min |
| 1.5 | Script do uruchomienia | `scripts/ingest.py` | 30min |

**Źródła do scrapowania:**
- NATO: `https://www.nato.int/cps/en/natohq/news.xml` (RSS)
- EU Commission: `https://ec.europa.eu/commission/presscorner/rss` (RSS)
- CSIS: `https://www.csis.org/analysis/feed` (RSS)
- UK FCDO: `https://www.gov.uk/government/organisations/foreign-commonwealth-development-office.atom` (Atom)
- US State: `https://www.state.gov/press-releases` (HTML)
- Kiel Institute: `https://www.ifw-kiel.de/publications` (HTML)
- DE Economy: `https://www.bmwk.de/Navigation/EN/Press` (HTML)

---

## 👤 OSOBA 2: Agent System

**Cel:** Pipeline agentów generujący raport z CLI do 19:00

| # | Task | Plik | Czas |
|---|------|------|------|
| 2.1 | Gemini LLM wrapper | `services/llm.py` | 30min |
| 2.2 | Region Agent (EU, USA) | `agents/region_agent.py` | 1h |
| 2.3 | Country/Source Agent | `agents/country_agent.py` | 1h |
| 2.4 | Synthesis Agent (raporty) | `agents/synthesis_agent.py` | 45min |
| 2.5 | Supervisor update (na Gemini) | `services/supervisor_agent.py` | 45min |

**Flow:** Supervisor → Region Agents → Country Agents → Synthesis → 4 raporty

---

## 👤 OSOBA 3: Frontend + Streaming

**Cel:** UI z live reasoning + raportami do 19:00

| # | Task | Plik | Czas |
|---|------|------|------|
| 3.1 | FastAPI endpoints | `api/routes.py` | 30min |
| 3.2 | SSE streaming | `api/streaming.py` | 1h |
| 3.3 | React - input form | `frontend/src/components/InputForm.tsx` | 45min |
| 3.4 | React - live reasoning | `frontend/src/components/ReasoningPanel.tsx` | 1h |
| 3.5 | React - raport display | `frontend/src/components/ReportView.tsx` | 30min |

**Endpoints:**
- `POST /api/analyze` → uruchamia analizę, zwraca session_id
- `GET /api/stream/{session_id}` → SSE z reasoning agentów
- `GET /api/report/{session_id}` → finalny raport

---

## Quick Start

```bash
# Instalacja
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env

# Osoba 1
python scripts/ingest.py

# Osoba 2
python -m agents.test_pipeline

# Osoba 3
uvicorn main:app --reload --port 8000
cd frontend && npm install && npm run dev
```
