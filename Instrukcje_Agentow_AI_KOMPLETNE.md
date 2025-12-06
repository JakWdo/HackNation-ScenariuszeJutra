# 🤖 Instrukcje dla Agentów AI - Generowanie Kodu
## WERSJA KOMPLETNA (z listą źródeł)

Ten dokument zawiera **wszystko** co potrzebne do zbudowania systemu zbierania danych dla projektu "Scenariusze Jutra" - narzędzia foresightowego dla MSZ.

---

## 📋 SPIS TREŚCI

1. [Kontekst projektu](#kontekst-projektu)
2. [Etap 1: Struktura projektu](#etap-1-generowanie-struktury-projektu)
3. [Etap 2: Lista źródeł (GOTOWA)](#etap-2-gotowa-lista-źródeł)
4. [Etap 3: Kod scraperów](#etap-3-kod-scraperów)
5. [Etap 4: Przetwarzanie NLP](#etap-4-przetwarzanie-nlp)
6. [Etap 5: Baza danych](#etap-5-storage-i-baza-danych)
7. [Etap 6: CLI i orchestracja](#etap-6-orchestracja-i-cli)
8. [Etap 7: Testy](#etap-7-testy)
9. [ZAŁĄCZNIK A: Pełna lista źródeł JSON](#załącznik-a-pełna-lista-źródeł-json)

---

## KONTEKST PROJEKTU

### Cel
Narzędzie do analizy foresightowej generujące scenariusze geopolityczne dla fikcyjnego państwa **Atlantis** (członek UE i NATO) w perspektywie 12 i 36 miesięcy.

### Państwo Atlantis - profil
- Populacja: 28 mln
- Położenie: dostęp do Bałtyku
- Gospodarka: przemysł ciężki, motoryzacyjny, ICT, ambicje w OZE i AI
- Armia: 150 tys. żołnierzy
- Waluta: inna niż euro
- Kluczowi partnerzy: Niemcy, Francja, Finlandia, Ukraina, USA, Japonia

### Wagi tematyczne (KRYTYCZNE dla scoringu)
| Temat | Waga | Opis |
|-------|------|------|
| technology_semiconductors | 30 | Produkcja GPU, łańcuchy dostaw |
| energy_renewables | 25 | Ceny ropy, OZE, transformacja |
| automotive_ev | 15 | Przemysł europejski vs Azja |
| eu_economy | 15 | PKB strefy euro |
| ukraine_situation | 10 | Rozejm, inwestycje |
| foreign_investments | 5 | USA/UE w Ukrainie |

### Wymagania techniczne
- Zakres czasowy: dane od **2021-01-01**
- Wolumen: do 50 mln słów (rozszerzalny do 5 mld)
- Języki: angielski (priorytet), polski
- Wyjaśnialność: chain of thought dla każdej predykcji

---

## ETAP 1: Generowanie struktury projektu

### Prompt 1.1: Inicjalizacja projektu

```
Stwórz strukturę katalogów i pliki konfiguracyjne dla projektu "Scenariusze Jutra" - systemu zbierania danych geopolitycznych.

WYMAGANIA:
1. Utwórz następującą strukturę katalogów:

scenariusze_jutra/
├── config/
│   ├── settings.py
│   ├── sources.yaml
│   └── logging_config.yaml
├── scrapers/
│   ├── __init__.py
│   ├── base.py
│   ├── ministry.py
│   ├── institution.py
│   └── financial.py
├── processors/
│   ├── __init__.py
│   ├── text_cleaner.py
│   ├── nlp_pipeline.py
│   └── embeddings.py
├── storage/
│   ├── __init__.py
│   ├── database.py
│   └── file_storage.py
├── utils/
│   ├── __init__.py
│   ├── rate_limiter.py
│   ├── validators.py
│   └── helpers.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── embeddings/
├── logs/
├── tests/
├── requirements.txt
├── setup.py
├── .env.example
└── README.md

2. W pliku requirements.txt umieść:
- requests>=2.31.0
- beautifulsoup4>=4.12.0
- aiohttp>=3.9.0
- scrapy>=2.11.0
- pdfplumber>=0.10.0
- spacy>=3.7.0
- langdetect>=1.0.9
- openai>=1.0.0
- chromadb>=0.4.0
- psycopg2-binary>=2.9.0
- sqlalchemy>=2.0.0
- pydantic>=2.5.0
- python-dotenv>=1.0.0
- structlog>=23.2.0
- pandas>=2.0.0
- numpy>=1.24.0
- pytest>=7.4.0
- feedparser>=6.0.0
- playwright>=1.40.0
- redis>=5.0.0
- tqdm>=4.66.0
- click>=8.1.0

3. W settings.py stwórz klasę konfiguracyjną z:
- Ustawieniami bazy danych (PostgreSQL)
- Kluczami API (z .env)
- Rate limiting config
- Ścieżkami do katalogów

4. W .env.example umieść przykładowe zmienne środowiskowe:
DATABASE_URL=postgresql://user:pass@localhost:5432/scenariusze
OPENAI_API_KEY=sk-xxx
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO

OUTPUT: Wszystkie pliki z podstawowym kodem/konfiguracją
```

---

## ETAP 2: GOTOWA LISTA ŹRÓDEŁ

**UWAGA: Lista źródeł jest już przygotowana w ZAŁĄCZNIKU A na końcu dokumentu.**

Agent powinien:
1. Skopiować JSON z Załącznika A do pliku `config/sources_master.json`
2. Stworzyć loader w `config/sources.py`:

```python
# config/sources.py
import json
from pathlib import Path
from typing import Dict, List
from pydantic import BaseModel

class SourceConfig(BaseModel):
    source_id: str
    name_en: str = None
    name: str = None
    base_url: str
    english_url: str = None
    endpoints: Dict[str, str] = {}
    priority: str = "medium"
    scraping_method: str = "static"
    active: bool = True
    rss_url: str = None
    notes: str = None

def load_sources() -> Dict[str, List[SourceConfig]]:
    """Wczytuje wszystkie źródła z pliku JSON"""
    path = Path(__file__).parent / "sources_master.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    sources = {
        "ministries": [],
        "institutions": [],
        "financial": []
    }
    
    # Ministerstwa
    for country, info in data["ministries"].items():
        for src in info["sources"]:
            sources["ministries"].append(SourceConfig(**src))
    
    # Instytucje
    for org in data["institutions"]["international_organizations"]:
        sources["institutions"].append(SourceConfig(**org))
    for tt in data["institutions"]["think_tanks"]:
        sources["institutions"].append(SourceConfig(**tt))
    
    # Finansowe
    for fin in data["institutions"]["financial"]:
        sources["financial"].append(SourceConfig(**fin))
    
    return sources

def get_source_by_id(source_id: str) -> SourceConfig:
    """Pobiera pojedyncze źródło po ID"""
    all_sources = load_sources()
    for category in all_sources.values():
        for src in category:
            if src.source_id == source_id:
                return src
    raise ValueError(f"Source {source_id} not found")
```

---

## ETAP 3: Kod scraperów

### Prompt 3.1: Base Scraper

```
Stwórz bazową klasę scrapera w Pythonie z następującymi funkcjonalnościami:

PLIK: scrapers/base.py

WYMAGANIA:
1. Klasa BaseScraper z metodami:
   - __init__(self, source_config: SourceConfig, session: aiohttp.ClientSession = None)
   - async fetch(self, url: str) -> str | bytes
   - parse(self, content: str) -> List[Document]
   - async store(self, documents: List[Document])
   - async run(self) -> int  # zwraca liczbę pobranych dokumentów

2. Obsługa:
   - Rate limiting (asyncio.Semaphore + sleep)
   - Retry z exponential backoff (max 3 próby)
   - Rotacja User-Agent
   - Obsługa proxy (opcjonalna)
   - Timeout (connection=10s, read=30s)

3. Logowanie (structlog):
   - Info: start/stop scrapowania, liczba dokumentów
   - Warning: retry attempts
   - Error: failed requests

4. Dataclass Document:
   @dataclass
   class Document:
       url: str
       title: str
       content: str
       publication_date: datetime | None
       source_id: str
       document_type: str
       language: str
       metadata: dict
       raw_html: str | None = None
       scrape_timestamp: datetime = field(default_factory=datetime.utcnow)

5. Obsługa błędów:
   - ScraperException (bazowy)
   - RateLimitException
   - ContentParseException
   - NetworkException

6. Context manager dla sesji aiohttp

7. Dekorator @retry z konfiguracją

8. Lista User-Agents do rotacji:
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "ScenariuszeJutra-Bot/1.0 (Research; contact@example.com)"
]

STYL KODU:
- Type hints wszędzie
- Docstrings (Google style)
- Async/await
- Pydantic dla walidacji config

OUTPUT: Kompletny plik base.py z testami jednostkowymi
```

### Prompt 3.2: Ministry Scraper

```
Stwórz scraper dla stron ministerstw dziedziczący po BaseScraper.

PLIK: scrapers/ministry.py

ŹRÓDŁA DO OBSŁUŻENIA (z ZAŁĄCZNIKA A):
- Strony gov.uk (UK) - struktura: /news-and-communications, .atom feeds
- Strony .gov (US) - struktura: /news, /press-releases
- Strony .gouv.fr (FR) - struktura: /en/latest-news
- Strony .de (DE) - struktura: /en/news
- Strony .gov.ru (RU) - może wymagać proxy
- Strony .gov.cn (CN) - może wymagać specjalnej obsługi
- Strony .gov.in (IN) - struktura: /press-releases.htm
- Strony .gov.sa (SA) - dynamiczny JS, wymaga Playwright

SPECYFIKA:
1. Parsowanie typowych struktur stron rządowych:
   - Listy newsów z paginacją
   - Komunikaty prasowe
   - Sekcje przemówień
   - Dokumenty PDF (linki)

2. Metody:
   - parse_news_list(html) -> List[NewsItem]
   - parse_article(html) -> Article
   - extract_date(html) -> datetime (obsługa różnych formatów)
   - extract_author(html) -> str
   - handle_pagination(html) -> Optional[str]  # next page URL

3. Selektory CSS/XPath dla różnych typów stron:
   
   # UK gov.uk
   UK_SELECTORS = {
       "news_list": ".gem-c-document-list__item",
       "title": ".gem-c-document-list__item-title",
       "date": "time[datetime]",
       "link": "a.gem-c-document-list__item-title"
   }
   
   # US .gov
   US_SELECTORS = {
       "news_list": ".news-item, .press-release-item",
       "title": "h2, h3",
       "date": ".date, time",
       "link": "a"
   }
   
   # EU ec.europa.eu
   EU_SELECTORS = {
       "news_list": ".ecl-content-item",
       "title": ".ecl-content-item__title",
       "date": ".ecl-content-item__date",
       "link": "a.ecl-link"
   }

4. Konfiguracja per-source:
   - Selektory (overridable w source config)
   - Date format per country
   - Pagination type (offset/cursor/page)

5. Obsługa JavaScript (fallback do Playwright):
   - Detekcja dynamicznego contentu
   - Lazy loading
   - Infinite scroll

6. Filtrowanie po dacie:
   - Pobieraj tylko dokumenty >= 2021-01-01
   - Early exit jeśli napotkano starsze

OUTPUT: Kompletny plik ministry.py
```

### Prompt 3.3: PDF Extractor

```
Stwórz moduł do ekstrakcji tekstu z plików PDF.

PLIK: scrapers/pdf_extractor.py

FUNKCJONALNOŚCI:
1. Klasa PDFExtractor:
   - extract_text(pdf_bytes: bytes) -> str
   - extract_tables(pdf_bytes: bytes) -> List[pd.DataFrame]
   - extract_metadata(pdf_bytes: bytes) -> dict

2. Obsługa różnych typów PDF:
   - Text-based (pdfplumber)
   - Scanned/OCR (pytesseract jako fallback)

3. Czyszczenie tekstu:
   - Usuwanie headers/footers
   - Łączenie podzielonych słów (hy-phenation)
   - Normalizacja whitespace

4. Metadane do ekstrakcji:
   - Tytuł, Autor, Data
   - Liczba stron
   - Język (detekcja)

OUTPUT: Kompletny moduł
```

### Prompt 3.4: Institution Scraper

```
Stwórz scraper dla think-tanków i instytucji międzynarodowych.

PLIK: scrapers/institution.py

ŹRÓDŁA (z ZAŁĄCZNIKA A):
- IISS (iiss.org) - /blogs, /publications
- CSIS (csis.org) - /analysis, RSS feed
- Chatham House - /publications, RSS
- ECFR (ecfr.eu) - /publications, RSS
- Atlantic Council - /blogs, RSS
- Kiel Institute - /publications, Ukraine Support Tracker
- NATO (nato.int) - /news.xml RSS
- EU Commission - API dostępne
- UN (un.org) - RSS feed
- OECD - API SDMX-JSON

SPECYFIKA:
1. Obsługa RSS/Atom feeds (feedparser)
2. Obsługa API gdzie dostępne (EU, OECD)
3. Parsowanie research papers i reports
4. Ekstrakcja autorów i afiliacji

OUTPUT: Kompletny plik institution.py
```

---

## ETAP 4: Przetwarzanie NLP

### Prompt 4.1: Text Cleaner

```
Stwórz moduł do czyszczenia i normalizacji tekstu.

PLIK: processors/text_cleaner.py

KLASA TextCleaner:

1. Metody główne:
   - clean(text: str) -> str  # pełny pipeline
   - normalize_whitespace(text: str) -> str
   - remove_boilerplate(text: str, source_type: str) -> str
   - remove_html_artifacts(text: str) -> str
   - fix_encoding(text: str) -> str

2. Boilerplate patterns per source type:
   BOILERPLATE_PATTERNS = {
       "gov_uk": ["Share this page", "Is this page useful", "Help us improve"],
       "gov_us": ["An official website of the United States", "Share:", "Print:"],
       "eu": ["European Commission", "Press corner", "Follow the European Commission"],
       "think_tank": ["Subscribe to our newsletter", "Follow us on", "Share this"]
   }

3. Normalizacja:
   - Unicode normalization (NFKC)
   - Smart quotes -> straight quotes
   - Em/en dashes normalization

4. Quality metrics:
   - text_quality_score(text) -> float (0-1)
   - is_mostly_boilerplate(text) -> bool
   - language_confidence(text) -> float

OUTPUT: Moduł z testami
```

### Prompt 4.2: NLP Pipeline

```
Stwórz pipeline NLP do analizy dokumentów.

PLIK: processors/nlp_pipeline.py

KOMPONENTY:

1. EntityExtractor (spaCy):
   - extract_entities(text) -> Dict[str, List[str]]
   - Kategorie: COUNTRY, ORG, PERSON, DATE, EVENT, MONEY
   - Mapowanie nazw krajów do kodów ISO
   - Lista krajów kluczowych dla Atlantis:
     ATLANTIS_KEY_COUNTRIES = [
         "Germany", "France", "Finland", "Ukraine", "United States", "Japan",
         "Russia", "China", "Saudi Arabia", "United Kingdom", "India"
     ]

2. TopicClassifier:
   - classify(text) -> Dict[str, float]
   - Kategorie z wagami projektu:
     TOPIC_WEIGHTS = {
         "technology_semiconductors": 30,
         "automotive_ev": 15,
         "eu_economy": 15,
         "ukraine_situation": 10,
         "foreign_investments": 5,
         "energy_renewables": 25
     }
   
   - Keywords per topic:
     TOPIC_KEYWORDS = {
         "technology_semiconductors": ["GPU", "processor", "chip", "semiconductor", "NVIDIA", "TSMC", "fab", "lithography"],
         "automotive_ev": ["electric vehicle", "EV", "battery", "automotive", "car manufacturer", "BYD", "Tesla"],
         "eu_economy": ["GDP", "eurozone", "ECB", "inflation", "recession", "growth"],
         "ukraine_situation": ["Ukraine", "Kyiv", "reconstruction", "ceasefire", "Zelenskyy"],
         "foreign_investments": ["FDI", "investment", "critical minerals", "rare earth"],
         "energy_renewables": ["renewable", "solar", "wind", "oil price", "OPEC", "natural gas", "LNG"]
     }

3. SentimentAnalyzer:
   - analyze(text) -> SentimentResult
   - Overall sentiment (-1 do 1)
   - Tone: formal/informal/urgent/neutral

4. RelevanceScorer:
   - score_for_atlantis(document: Document) -> float
   - Formuła:
     relevance = sum(topic_score * TOPIC_WEIGHTS[topic] for topic in topics) / 100
     relevance *= geography_boost  # 1.5x jeśli wspomina kluczowe kraje
     relevance *= recency_factor   # 1.0-0.5 w zależności od wieku

5. Pipeline orchestrator:
   class NLPPipeline:
       def process(self, document: Document) -> ProcessedDocument

OUTPUT: Kompletny moduł
```

### Prompt 4.3: Embeddings Generator

```
Stwórz moduł do generowania i zarządzania embeddingami.

PLIK: processors/embeddings.py

KOMPONENTY:

1. TextChunker:
   - chunk_text(text, chunk_size=500, overlap=50) -> List[Chunk]
   - Chunk at sentence boundaries

2. EmbeddingGenerator:
   - Wsparcie dla OpenAI text-embedding-3-small
   - Batch processing (max 100 per request)
   - Rate limiting
   - Caching w Redis

3. VectorStore (ChromaDB wrapper):
   - add_documents(documents: List[ProcessedDocument])
   - search(query: str, n=10, filters: dict = None) -> List[SearchResult]
   - Filtrowanie po: source_id, date_range, topic, relevance_score

4. Similarity:
   - find_duplicates(threshold=0.95) -> List[Tuple[str, str]]

OUTPUT: Moduł z integracją
```

---

## ETAP 5: Storage i baza danych

### Prompt 5.1: Database Schema i ORM

```
Stwórz moduł bazy danych z SQLAlchemy ORM.

PLIK: storage/database.py

MODELE:

1. Source:
   - id: int (PK)
   - source_id: str (unique) -- np. "DE_MOD", "CSIS"
   - country: str (nullable)
   - source_type: str -- "ministry", "think_tank", "financial", "international_org"
   - name: str
   - base_url: str
   - config: JSON
   - priority: str -- "high", "medium", "low"
   - active: bool
   - created_at, updated_at: datetime

2. Document:
   - id: int (PK)
   - source_id: str (FK)
   - url: str (unique)
   - title: str
   - content: text
   - content_hash: str (SHA256)
   - word_count: int
   - publication_date: date
   - scrape_date: datetime
   - document_type: str -- "news", "press_release", "report", "speech"
   - language: str
   - metadata: JSON

3. ProcessedDocument:
   - id: int (PK)
   - document_id: int (FK)
   - summary: text
   - keywords: ARRAY[str]
   - entities: JSON
   - topics: JSON  -- {"technology_semiconductors": 0.8, ...}
   - sentiment_score: float
   - relevance_score: float  -- dla Atlantis
   - processed_at: datetime

4. Embedding:
   - id: int (PK)
   - document_id: int (FK)
   - chunk_index: int
   - chunk_text: text
   - embedding: JSON  -- lub VECTOR jeśli pgvector
   - created_at: datetime

5. ScrapeLog:
   - id, source_id, start_time, end_time
   - documents_found, documents_new, errors
   - status: str -- "success", "partial", "failed"

SQL DO INICJALIZACJI:
-- Utwórz tabelę sources z danymi z ZAŁĄCZNIKA A
INSERT INTO sources (source_id, country, source_type, name, base_url, priority, active)
VALUES 
    ('DE_MAE', 'Germany', 'ministry', 'Federal Foreign Office', 'https://www.auswaertiges-amt.de', 'high', true),
    ('DE_MOD', 'Germany', 'ministry', 'Federal Ministry of Defence', 'https://www.bmvg.de', 'high', true),
    -- ... reszta z ZAŁĄCZNIKA A

OUTPUT: Kompletny moduł z migracjami Alembic
```

---

## ETAP 6: Orchestracja i CLI

### Prompt 6.1: Main Runner

```
Stwórz główny skrypt uruchamiający scraping.

PLIK: run_scraper.py

CLI (click):
@click.command()
@click.option('--sources', '-s', help='Lista source_id oddzielona przecinkami lub "all"')
@click.option('--type', '-t', type=click.Choice(['ministry', 'institution', 'financial', 'all']))
@click.option('--country', '-c', help='Filtr po kraju (np. Germany, France)')
@click.option('--since', default='2021-01-01', help='Data początkowa (YYYY-MM-DD)')
@click.option('--limit', default=100, help='Max dokumentów per source')
@click.option('--dry-run', is_flag=True, help='Tylko sprawdź, nie zapisuj')
@click.option('--verbose', '-v', is_flag=True, help='Debug logging')

PRZYKŁADY UŻYCIA:
python run_scraper.py --sources DE_MOD,DE_MAE --limit 100
python run_scraper.py --type ministry --country Germany
python run_scraper.py --type institution --since 2024-01-01
python run_scraper.py --all

FUNKCJONALNOŚCI:
1. Równoległe scrapowanie (asyncio, max 5 concurrent)
2. Progress bar (tqdm)
3. Graceful shutdown (SIGINT)
4. Resume capability (zapisuje stan do Redis)
5. Summary report na końcu

OUTPUT: Kompletny skrypt
```

### Prompt 6.2: Processing Pipeline Runner

```
Stwórz skrypt do uruchamiania przetwarzania NLP.

PLIK: run_processing.py

CLI:
@click.command()
@click.option('--batch-size', default=50)
@click.option('--source-filter', help='Tylko określone źródła')
@click.option('--reprocess', is_flag=True, help='Przetwórz ponownie wszystkie')
@click.option('--components', default='all', help='clean,nlp,embed lub all')

PIPELINE:
1. Pobierz nieprzetworzonych dokumentów z DB
2. Dla każdego dokumentu:
   a. TextCleaner.clean()
   b. NLPPipeline.process()
   c. EmbeddingGenerator.generate()
3. Zapisz ProcessedDocument do DB
4. Zapisz embeddings do ChromaDB

OUTPUT: Kompletny skrypt
```

### Prompt 6.3: Scenario Generator

```
Stwórz moduł do generowania scenariuszy z użyciem LLM.

PLIK: generators/scenario_generator.py

KLASA ScenarioGenerator:

1. __init__(self, vector_store, llm_client):
   - Inicjalizacja z ChromaDB i OpenAI/Claude

2. generate_scenario(self, params: ScenarioParams) -> Scenario:
   
   @dataclass
   class ScenarioParams:
       time_horizon: int  # 12 lub 36 miesięcy
       variant: str  # "positive" lub "negative"
       input_factors: List[InputFactor]  # 6 czynników z wyzwania
       weights: Dict[str, int]  # wagi istotności
   
   @dataclass
   class InputFactor:
       description: str
       weight: int
       keywords: List[str]

3. Przepływ:
   a. Dla każdego input_factor:
      - Wyszukaj relevantne dokumenty w vector store
      - Pobierz top 20 chunków
   b. Zbuduj kontekst z pobranych dokumentów
   c. Wywołaj LLM z promptem scenariuszowym
   d. Parsuj odpowiedź do struktury Scenario

4. PROMPT TEMPLATE:
   ```
   Jesteś analitykiem geopolitycznym przygotowującym scenariusze dla państwa Atlantis.
   
   PROFIL ATLANTIS:
   - Państwo członkowskie UE i NATO
   - 28 mln mieszkańców, dostęp do Bałtyku
   - Silne sektory: przemysł ciężki, motoryzacyjny, ICT
   - Kluczowi partnerzy: Niemcy, Francja, USA, Ukraina, Japonia
   
   DANE WEJŚCIOWE (z wagami istotności):
   {input_factors_formatted}
   
   KONTEKST Z DOKUMENTÓW:
   {retrieved_context}
   
   ZADANIE:
   Wygeneruj scenariusz {variant} dla Atlantis w perspektywie {time_horizon} miesięcy.
   
   FORMAT ODPOWIEDZI:
   1. STRESZCZENIE (max 200 słów)
   2. SZCZEGÓŁOWY SCENARIUSZ
      - Dla każdego czynnika: wpływ na Atlantis
      - Interakcje między czynnikami
      - Timeline wydarzeń
   3. CHAIN OF THOUGHT
      - Jakie dane doprowadziły do wniosków
      - Korelacje między faktami
      - Ścieżka przyczynowo-skutkowa
   4. REKOMENDACJE
      - Co zrobić aby {uniknąć negatywnego / osiągnąć pozytywny} scenariusz
   ```

5. Wyjaśnialność (KRYTYCZNE):
   - Każdy wniosek musi mieć źródło
   - Tagowanie faktów: [FAKT:źródło:data]
   - Eksplicytne pokazanie wag

OUTPUT: Kompletny moduł
```

---

## ETAP 7: Testy

### Prompt 7.1: Test Suite

```
Stwórz kompletny zestaw testów dla projektu.

STRUKTURA:
tests/
├── conftest.py           # Fixtures
├── test_scrapers/
│   ├── test_base.py
│   ├── test_ministry.py
│   └── test_pdf.py
├── test_processors/
│   ├── test_cleaner.py
│   ├── test_nlp.py
│   └── test_embeddings.py
├── test_storage/
│   └── test_database.py
├── test_integration/
│   └── test_full_pipeline.py
└── fixtures/
    ├── sample_html/
    │   ├── gov_uk_news.html
    │   ├── csis_article.html
    │   └── nato_press.html
    ├── sample_pdf/
    │   └── sample_report.pdf
    └── expected_outputs/

WYMAGANIA:
1. Fixtures:
   - Mock aiohttp session
   - Sample HTML files (pobrane z prawdziwych źródeł)
   - Test database (SQLite in-memory)

2. Unit tests dla każdego modułu

3. Integration test: full pipeline
   - Scrape -> Process -> Store -> Search

4. Coverage minimum 80%

OUTPUT: Wszystkie pliki testów
```

---

## Podsumowanie kolejności wykonania

| # | Prompt | Output | Zależności |
|---|--------|--------|------------|
| 1 | 1.1 | Struktura projektu | - |
| 2 | - | Skopiuj ZAŁĄCZNIK A do sources_master.json | 1 |
| 3 | 3.1 | base.py | 1 |
| 4 | 3.2 | ministry.py | 3 |
| 5 | 3.3 | pdf_extractor.py | 3 |
| 6 | 3.4 | institution.py | 3 |
| 7 | 4.1 | text_cleaner.py | 1 |
| 8 | 4.2 | nlp_pipeline.py | 7 |
| 9 | 4.3 | embeddings.py | 8 |
| 10 | 5.1 | database.py | 1 |
| 11 | 6.1 | run_scraper.py | 3,4,5,6,10 |
| 12 | 6.2 | run_processing.py | 7,8,9,10 |
| 13 | 6.3 | scenario_generator.py | 9 |
| 14 | 7.1 | testy | wszystkie |

---

## ZAŁĄCZNIK A: Pełna lista źródeł JSON

**Skopiuj poniższy JSON do pliku `config/sources_master.json`:**

```json
{
  "metadata": {
    "project": "Scenariusze Jutra",
    "version": "1.0",
    "created": "2025-12",
    "description": "Lista źródeł danych do analizy foresightowej",
    "date_filter": "2021-01-01",
    "total_sources": 95
  },
  
  "ministries": {
    "Germany": {
      "country_code": "DE",
      "language": "de",
      "english_available": true,
      "sources": [
        {
          "source_id": "DE_MAE",
          "ministry_type": "foreign_affairs",
          "name_en": "Federal Foreign Office",
          "name_native": "Auswärtiges Amt",
          "base_url": "https://www.auswaertiges-amt.de",
          "english_url": "https://www.auswaertiges-amt.de/en",
          "endpoints": {
            "news": "/en/newsroom",
            "press_releases": "/en/newsroom/news",
            "speeches": "/en/newsroom/speeches",
            "publications": "/en/publications"
          },
          "rss_url": null,
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "DE_MOD",
          "ministry_type": "defense",
          "name_en": "Federal Ministry of Defence",
          "name_native": "Bundesministerium der Verteidigung",
          "base_url": "https://www.bmvg.de",
          "english_url": "https://www.bmvg.de/en",
          "endpoints": {
            "news": "/en/news",
            "press_releases": "/en/press",
            "publications": "/en/publications"
          },
          "rss_url": null,
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "DE_BMI",
          "ministry_type": "interior",
          "name_en": "Federal Ministry of the Interior",
          "name_native": "Bundesministerium des Innern",
          "base_url": "https://www.bmi.bund.de",
          "english_url": "https://www.bmi.bund.de/EN",
          "endpoints": {
            "news": "/EN/news/news_node.html",
            "press_releases": "/EN/press/press_node.html"
          },
          "priority": "medium",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "DE_BMWK",
          "ministry_type": "economy",
          "name_en": "Federal Ministry for Economic Affairs and Climate Action",
          "name_native": "Bundesministerium für Wirtschaft und Klimaschutz",
          "base_url": "https://www.bmwk.de",
          "english_url": "https://www.bmwk.de/Navigation/EN/Home/home.html",
          "endpoints": {
            "news": "/Navigation/EN/Press/press.html",
            "press_releases": "/Navigation/EN/Press/press-releases/press-releases.html",
            "publications": "/Navigation/EN/Publications/publications.html"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "DE_BMBF",
          "ministry_type": "higher_education",
          "name_en": "Federal Ministry of Education and Research",
          "name_native": "Bundesministerium für Bildung und Forschung",
          "base_url": "https://www.bmbf.de",
          "english_url": "https://www.bmbf.de/bmbf/en/home/home_node.html",
          "endpoints": {
            "news": "/bmbf/en/news/news_node.html"
          },
          "priority": "medium",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "DE_BMDV",
          "ministry_type": "digital_technology",
          "name_en": "Federal Ministry for Digital and Transport",
          "name_native": "Bundesministerium für Digitales und Verkehr",
          "base_url": "https://www.bmdv.bund.de",
          "english_url": "https://www.bmdv.bund.de/EN",
          "endpoints": {
            "news": "/EN/Home/home.html"
          },
          "priority": "medium",
          "scraping_method": "static",
          "active": true
        }
      ]
    },
    
    "France": {
      "country_code": "FR",
      "language": "fr",
      "english_available": true,
      "sources": [
        {
          "source_id": "FR_MAE",
          "ministry_type": "foreign_affairs",
          "name_en": "Ministry for Europe and Foreign Affairs",
          "name_native": "Ministère de l'Europe et des Affaires étrangères",
          "base_url": "https://www.diplomatie.gouv.fr",
          "english_url": "https://www.diplomatie.gouv.fr/en",
          "endpoints": {
            "news": "/en/latest-news",
            "press_releases": "/en/press-releases",
            "speeches": "/en/the-minister-and-the-minister-of-state/speeches"
          },
          "rss_url": "https://www.diplomatie.gouv.fr/spip.php?page=backend",
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "FR_MOD",
          "ministry_type": "defense",
          "name_en": "Ministry of the Armed Forces",
          "name_native": "Ministère des Armées",
          "base_url": "https://www.defense.gouv.fr",
          "english_url": "https://www.defense.gouv.fr/english",
          "endpoints": {
            "news": "/english/news"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "FR_ECO",
          "ministry_type": "economy",
          "name_en": "Ministry for the Economy and Finance",
          "name_native": "Ministère de l'Économie et des Finances",
          "base_url": "https://www.economie.gouv.fr",
          "english_url": "https://www.economie.gouv.fr/welcome-to-the-french-ministry-for-the-economy-and-finance",
          "endpoints": {
            "news": "/actualites",
            "press_releases": "/presse"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "FR_ENERGY",
          "ministry_type": "energy",
          "name_en": "Ministry for Ecological Transition",
          "name_native": "Ministère de la Transition écologique",
          "base_url": "https://www.ecologie.gouv.fr",
          "english_url": "https://www.ecologie.gouv.fr/en",
          "endpoints": {
            "news": "/en/newsroom"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        }
      ]
    },
    
    "United_Kingdom": {
      "country_code": "GB",
      "language": "en",
      "english_available": true,
      "sources": [
        {
          "source_id": "GB_FCDO",
          "ministry_type": "foreign_affairs",
          "name_en": "Foreign, Commonwealth & Development Office",
          "base_url": "https://www.gov.uk/government/organisations/foreign-commonwealth-development-office",
          "endpoints": {
            "news": "/news-and-communications",
            "press_releases": "/announcements?announcement_filter_option=press-releases",
            "speeches": "/announcements?announcement_filter_option=speeches",
            "publications": "/publications"
          },
          "rss_url": "https://www.gov.uk/government/organisations/foreign-commonwealth-development-office.atom",
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "GB_MOD",
          "ministry_type": "defense",
          "name_en": "Ministry of Defence",
          "base_url": "https://www.gov.uk/government/organisations/ministry-of-defence",
          "endpoints": {
            "news": "/news-and-communications",
            "press_releases": "/announcements?announcement_filter_option=press-releases",
            "publications": "/publications"
          },
          "rss_url": "https://www.gov.uk/government/organisations/ministry-of-defence.atom",
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "GB_DBT",
          "ministry_type": "trade",
          "name_en": "Department for Business and Trade",
          "base_url": "https://www.gov.uk/government/organisations/department-for-business-and-trade",
          "endpoints": {
            "news": "/news-and-communications",
            "publications": "/publications"
          },
          "rss_url": "https://www.gov.uk/government/organisations/department-for-business-and-trade.atom",
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "GB_DESNZ",
          "ministry_type": "energy",
          "name_en": "Department for Energy Security and Net Zero",
          "base_url": "https://www.gov.uk/government/organisations/department-for-energy-security-and-net-zero",
          "endpoints": {
            "news": "/news-and-communications",
            "publications": "/publications"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "GB_DSIT",
          "ministry_type": "digital_technology",
          "name_en": "Department for Science, Innovation and Technology",
          "base_url": "https://www.gov.uk/government/organisations/department-for-science-innovation-and-technology",
          "endpoints": {
            "news": "/news-and-communications",
            "publications": "/publications"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        }
      ]
    },
    
    "United_States": {
      "country_code": "US",
      "language": "en",
      "english_available": true,
      "sources": [
        {
          "source_id": "US_STATE",
          "ministry_type": "foreign_affairs",
          "name_en": "U.S. Department of State",
          "base_url": "https://www.state.gov",
          "endpoints": {
            "news": "/press-releases",
            "press_releases": "/press-releases",
            "speeches": "/remarks-and-releases-secretary",
            "publications": "/reports"
          },
          "rss_url": "https://www.state.gov/rss-feeds/",
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "US_DOD",
          "ministry_type": "defense",
          "name_en": "U.S. Department of Defense",
          "base_url": "https://www.defense.gov",
          "endpoints": {
            "news": "/News",
            "press_releases": "/News/Releases",
            "speeches": "/News/Speeches"
          },
          "rss_url": "https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx",
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "US_DOC",
          "ministry_type": "economy",
          "name_en": "U.S. Department of Commerce",
          "base_url": "https://www.commerce.gov",
          "endpoints": {
            "news": "/news",
            "press_releases": "/news/press-releases"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "US_USTR",
          "ministry_type": "trade",
          "name_en": "Office of the U.S. Trade Representative",
          "base_url": "https://ustr.gov",
          "endpoints": {
            "news": "/about-us/press-office",
            "press_releases": "/about-us/press-office/press-releases",
            "publications": "/about-us/press-office/reports-and-publications"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "US_DOE",
          "ministry_type": "energy",
          "name_en": "U.S. Department of Energy",
          "base_url": "https://www.energy.gov",
          "endpoints": {
            "news": "/news",
            "press_releases": "/news/press-releases"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        }
      ]
    },
    
    "Russia": {
      "country_code": "RU",
      "language": "ru",
      "english_available": true,
      "notes": "Access may be restricted. Consider using proxy.",
      "sources": [
        {
          "source_id": "RU_MID",
          "ministry_type": "foreign_affairs",
          "name_en": "Ministry of Foreign Affairs of Russia",
          "name_native": "МИД России",
          "base_url": "https://www.mid.ru",
          "english_url": "https://www.mid.ru/en",
          "endpoints": {
            "news": "/en/foreign_policy/news",
            "press_releases": "/en/press_service/spokesman/official_statement"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true,
          "notes": "May require special handling due to geo-restrictions"
        },
        {
          "source_id": "RU_MOD",
          "ministry_type": "defense",
          "name_en": "Ministry of Defence of Russia",
          "name_native": "Минобороны России",
          "base_url": "https://eng.mil.ru",
          "endpoints": {
            "news": "/en/news_page/country"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "RU_MINENERGO",
          "ministry_type": "energy",
          "name_en": "Ministry of Energy of Russia",
          "name_native": "Минэнерго России",
          "base_url": "https://minenergo.gov.ru",
          "english_url": "https://minenergo.gov.ru/en",
          "endpoints": {
            "news": "/en/activity/news"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        }
      ]
    },
    
    "China": {
      "country_code": "CN",
      "language": "zh",
      "english_available": true,
      "notes": "Content may be state-controlled. Apply critical analysis.",
      "sources": [
        {
          "source_id": "CN_FMPRC",
          "ministry_type": "foreign_affairs",
          "name_en": "Ministry of Foreign Affairs of China",
          "name_native": "中华人民共和国外交部",
          "base_url": "https://www.fmprc.gov.cn",
          "english_url": "https://www.fmprc.gov.cn/mfa_eng",
          "endpoints": {
            "news": "/mfa_eng/xwfw_665399/",
            "press_releases": "/mfa_eng/xwfw_665399/s2510_665401/",
            "speeches": "/mfa_eng/wjdt_665385/zyjh_665391/"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "CN_MOD",
          "ministry_type": "defense",
          "name_en": "Ministry of National Defense of China",
          "name_native": "国防部",
          "base_url": "http://eng.mod.gov.cn",
          "endpoints": {
            "news": "/news/",
            "press_releases": "/press/"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true,
          "notes": "HTTP only"
        },
        {
          "source_id": "CN_MOFCOM",
          "ministry_type": "trade",
          "name_en": "Ministry of Commerce of China",
          "name_native": "商务部",
          "base_url": "http://english.mofcom.gov.cn",
          "endpoints": {
            "news": "/article/newsrelease/",
            "press_releases": "/article/policyrelease/"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        }
      ]
    },
    
    "India": {
      "country_code": "IN",
      "language": "en",
      "english_available": true,
      "sources": [
        {
          "source_id": "IN_MEA",
          "ministry_type": "foreign_affairs",
          "name_en": "Ministry of External Affairs",
          "base_url": "https://www.mea.gov.in",
          "endpoints": {
            "news": "/press-releases.htm",
            "speeches": "/speeches-statements.htm",
            "publications": "/reports.htm"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "IN_MOD",
          "ministry_type": "defense",
          "name_en": "Ministry of Defence",
          "base_url": "https://mod.gov.in",
          "endpoints": {
            "press_releases": "/press-release",
            "publications": "/documents/reports"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        },
        {
          "source_id": "IN_MNRE",
          "ministry_type": "energy",
          "name_en": "Ministry of New and Renewable Energy",
          "base_url": "https://mnre.gov.in",
          "endpoints": {
            "news": "/",
            "publications": "/reports"
          },
          "priority": "high",
          "scraping_method": "static",
          "active": true
        }
      ]
    },
    
    "Saudi_Arabia": {
      "country_code": "SA",
      "language": "ar",
      "english_available": true,
      "sources": [
        {
          "source_id": "SA_MOFA",
          "ministry_type": "foreign_affairs",
          "name_en": "Ministry of Foreign Affairs",
          "name_native": "وزارة الخارجية",
          "base_url": "https://www.mofa.gov.sa",
          "english_url": "https://www.mofa.gov.sa/en",
          "endpoints": {
            "news": "/en/MediaCenter/NewsReleases",
            "speeches": "/en/MediaCenter/Speeches"
          },
          "priority": "high",
          "scraping_method": "dynamic",
          "active": true,
          "notes": "Requires JavaScript rendering (Playwright)"
        },
        {
          "source_id": "SA_MOE",
          "ministry_type": "energy",
          "name_en": "Ministry of Energy",
          "name_native": "وزارة الطاقة",
          "base_url": "https://www.moenergy.gov.sa",
          "english_url": "https://www.moenergy.gov.sa/en",
          "endpoints": {
            "news": "/en/MediaCenter/Pages/News.aspx"
          },
          "priority": "high",
          "scraping_method": "dynamic",
          "active": true
        }
      ]
    }
  },
  
  "institutions": {
    "international_organizations": [
      {
        "source_id": "EU_COM",
        "name": "European Commission",
        "type": "international_org",
        "base_url": "https://ec.europa.eu",
        "endpoints": {
          "news": "/commission/presscorner/home/en",
          "press_releases": "/commission/presscorner/api/files/document/print/en/press-release",
          "publications": "/info/publications_en",
          "data": "/eurostat"
        },
        "api_available": true,
        "api_url": "https://ec.europa.eu/commission/presscorner/api",
        "rss_url": "https://ec.europa.eu/commission/presscorner/rss/en/press-release",
        "focus_areas": ["eu_policy", "economy", "trade", "energy", "technology"],
        "priority": "high",
        "active": true
      },
      {
        "source_id": "NATO",
        "name": "North Atlantic Treaty Organization",
        "type": "international_org",
        "base_url": "https://www.nato.int",
        "endpoints": {
          "news": "/cps/en/natohq/news.htm",
          "press_releases": "/cps/en/natohq/press_releases.htm",
          "publications": "/cps/en/natohq/publications.htm",
          "speeches": "/cps/en/natohq/opinions.htm"
        },
        "rss_url": "https://www.nato.int/cps/en/natohq/news.xml",
        "focus_areas": ["defense", "security", "military"],
        "priority": "high",
        "active": true
      },
      {
        "source_id": "UN",
        "name": "United Nations",
        "type": "international_org",
        "base_url": "https://www.un.org",
        "endpoints": {
          "news": "/en/news",
          "press_releases": "/press/en",
          "publications": "/en/library"
        },
        "rss_url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "focus_areas": ["international_relations", "humanitarian", "development"],
        "priority": "high",
        "active": true
      },
      {
        "source_id": "OECD",
        "name": "Organisation for Economic Co-operation and Development",
        "type": "international_org",
        "base_url": "https://www.oecd.org",
        "endpoints": {
          "news": "/newsroom/",
          "publications": "/publications/",
          "data": "/statistics/"
        },
        "api_available": true,
        "api_url": "https://stats.oecd.org/SDMX-JSON/",
        "focus_areas": ["economy", "trade", "development", "statistics"],
        "priority": "high",
        "active": true
      },
      {
        "source_id": "GCC",
        "name": "Gulf Cooperation Council",
        "type": "international_org",
        "base_url": "https://www.gcc-sg.org",
        "endpoints": {
          "news": "/en-us/News"
        },
        "focus_areas": ["gulf_region", "energy", "economy"],
        "priority": "medium",
        "active": true
      }
    ],
    
    "think_tanks": [
      {
        "source_id": "IISS",
        "name": "International Institute for Strategic Studies",
        "type": "think_tank",
        "base_url": "https://www.iiss.org",
        "endpoints": {
          "news": "/blogs",
          "publications": "/publications",
          "research": "/research-papers"
        },
        "focus_areas": ["defense", "security", "geopolitics", "military"],
        "content_types": ["analysis", "reports", "commentary"],
        "priority": "high",
        "active": true
      },
      {
        "source_id": "CSIS",
        "name": "Center for Strategic and International Studies",
        "type": "think_tank",
        "base_url": "https://www.csis.org",
        "endpoints": {
          "news": "/analysis",
          "publications": "/publications",
          "research": "/programs"
        },
        "rss_url": "https://www.csis.org/analysis/feed",
        "focus_areas": ["defense", "economy", "technology", "geopolitics"],
        "content_types": ["analysis", "reports", "briefs"],
        "priority": "high",
        "active": true
      },
      {
        "source_id": "CHATHAM",
        "name": "Chatham House",
        "type": "think_tank",
        "base_url": "https://www.chathamhouse.org",
        "endpoints": {
          "publications": "/publications",
          "research": "/research"
        },
        "rss_url": "https://www.chathamhouse.org/rss.xml",
        "focus_areas": ["international_affairs", "economy", "energy", "security"],
        "priority": "high",
        "active": true
      },
      {
        "source_id": "ECFR",
        "name": "European Council on Foreign Relations",
        "type": "think_tank",
        "base_url": "https://ecfr.eu",
        "endpoints": {
          "publications": "/publications"
        },
        "rss_url": "https://ecfr.eu/feed/",
        "focus_areas": ["eu_policy", "foreign_policy", "security", "geopolitics"],
        "priority": "high",
        "active": true
      },
      {
        "source_id": "ATLANTIC",
        "name": "Atlantic Council",
        "type": "think_tank",
        "base_url": "https://www.atlanticcouncil.org",
        "endpoints": {
          "news": "/blogs",
          "publications": "/in-depth-research-reports"
        },
        "rss_url": "https://www.atlanticcouncil.org/feed/",
        "focus_areas": ["transatlantic", "security", "economy", "technology"],
        "priority": "high",
        "active": true
      },
      {
        "source_id": "KIEL",
        "name": "Kiel Institute for the World Economy",
        "type": "think_tank",
        "base_url": "https://www.ifw-kiel.de",
        "endpoints": {
          "news": "/en/publications/media-information",
          "publications": "/en/publications",
          "ukraine_tracker": "/en/topics/war-against-ukraine/ukraine-support-tracker"
        },
        "focus_areas": ["economy", "trade", "development", "ukraine_support"],
        "special_datasets": ["Ukraine Support Tracker"],
        "priority": "high",
        "active": true
      }
    ],
    
    "financial": [
      {
        "source_id": "NASDAQ",
        "name": "NASDAQ",
        "type": "financial",
        "base_url": "https://www.nasdaq.com",
        "endpoints": {
          "news": "/news-and-insights",
          "market_data": "/market-activity"
        },
        "api_available": true,
        "focus_areas": ["markets", "technology", "economy"],
        "priority": "medium",
        "active": true
      },
      {
        "source_id": "LSEG",
        "name": "London Stock Exchange Group",
        "type": "financial",
        "base_url": "https://www.lseg.com",
        "endpoints": {
          "news": "/newsroom",
          "insights": "/insights"
        },
        "focus_areas": ["markets", "economy", "europe"],
        "priority": "medium",
        "active": true
      },
      {
        "source_id": "JPX",
        "name": "Japan Exchange Group",
        "type": "financial",
        "base_url": "https://www.jpx.co.jp",
        "endpoints": {
          "news": "/english/news/",
          "market_data": "/english/markets/"
        },
        "focus_areas": ["markets", "asia", "economy"],
        "priority": "medium",
        "active": true
      }
    ]
  },
  
  "scraping_config": {
    "default_settings": {
      "rate_limit_seconds": 2.0,
      "max_retries": 3,
      "timeout_seconds": 30,
      "user_agent": "ScenariuszeJutra-Bot/1.0 (Research Project)",
      "respect_robots_txt": true,
      "min_date": "2021-01-01"
    },
    "by_priority": {
      "high": {
        "rate_limit_seconds": 1.5,
        "max_pages_per_run": 100
      },
      "medium": {
        "rate_limit_seconds": 2.0,
        "max_pages_per_run": 50
      },
      "low": {
        "rate_limit_seconds": 3.0,
        "max_pages_per_run": 25
      }
    }
  }
}
```

---

## Uwagi końcowe

### Dla wykonawcy (agenta AI):

1. **Zacznij od Prompt 1.1** - stwórz strukturę projektu
2. **Skopiuj JSON z ZAŁĄCZNIKA A** do `config/sources_master.json`
3. **Wykonuj prompty po kolei** - każdy buduje na poprzednich
4. **Testuj na małej próbce** - np. tylko DE_MOD i CSIS
5. **Dokumentuj odstępstwa** od specyfikacji

### Kluczowe wymagania MSZ:

- ✅ Wyjaśnialność (chain of thought)
- ✅ Wagi istotności tematów
- ✅ Filtrowanie od 2021-01-01
- ✅ Obsługa 8 krajów + 14 instytucji
- ✅ Generowanie 4 scenariuszy (12m/36m × pozytywny/negatywny)

---

*Wersja 2.0 KOMPLETNA | Scenariusze Jutra | Grudzień 2025*
