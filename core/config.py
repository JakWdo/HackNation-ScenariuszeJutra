"""
Konfiguracja aplikacji - settings, prompts, stałe.
"""
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Ustawienia aplikacji z .env"""
    gemini_api_key: Optional[str] = None
    llm_model: str = "gemini-2.5-flash"
    hf_token: Optional[str] = None
    debug: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

REGIONS = {
    "EU": {"name": "Unia Europejska", "countries": ["DE", "FR", "PL"]},
    "USA": {"name": "Stany Zjednoczone", "countries": ["US"]},
    "NATO": {"name": "NATO", "countries": ["członkowie NATO"]},
    "RUSSIA": {"name": "Rosja", "countries": ["RU"]},
    "ASIA": {"name": "Azja-Pacyfik", "countries": ["CN", "JP"]},
}

COUNTRIES = {
    "DE": {"name": "Niemcy", "sources": ["DE_BMWK"]},
    "US": {"name": "USA", "sources": ["US_STATE", "CSIS"]},
    "UK": {"name": "Wielka Brytania", "sources": ["UK_FCDO"]},
    "PL": {"name": "Polska", "sources": []},
    "FR": {"name": "Francja", "sources": []},
    "CN": {"name": "Chiny", "sources": []},
    "JP": {"name": "Japonia", "sources": []},
    "RU": {"name": "Rosja", "sources": []},
}

SOURCES = {
    "NATO": {"name": "NATO", "type": "organization"},
    "EU_COMMISSION": {"name": "Komisja Europejska", "type": "organization"},
    "US_STATE": {"name": "Departament Stanu USA", "type": "government"},
    "UK_FCDO": {"name": "UK Foreign Office", "type": "government"},
    "CSIS": {"name": "CSIS", "type": "think_tank"},
    "DE_BMWK": {"name": "Niemieckie Ministerstwo Gospodarki", "type": "government"},
}
REGION_PROMPT = """Jesteś ekspertem ds. analizy geopolitycznej regionu {region}.

Zadania:
1. Analizuj wpływ wydarzeń na region {region}
2. Identyfikuj trendy i zagrożenia
3. Oceniaj relacje między krajami

Kontekst: {context}

Odpowiadaj konkretnie, powołując się na źródła."""

COUNTRY_PROMPT = """Jesteś ekspertem ds. polityki {country}.

Zadania:
1. Analizuj oficjalne stanowisko {country}
2. Identyfikuj kluczowe interesy
3. Śledź wypowiedzi polityków

Źródło: {source}
Kontekst: {context}

Odpowiadaj konkretnie, cytując źródła."""

SYNTHESIS_PROMPT = """Jesteś analitykiem tworzącym raporty strategiczne.

Zadania:
1. Zsyntezuj analizy ekspertów
2. Stwórz raport w 4 sekcjach:
   - POLITYKA
   - GOSPODARKA
   - OBRONNOŚĆ
   - SPOŁECZEŃSTWO

Analizy ekspertów:
{expert_analyses}

Format: Markdown z nagłówkami ##."""

SUPERVISOR_PROMPT = """Jesteś Meta Supervisorem koordynującym analityków.

To jest historia państwa, którego analitykiem jesteś:
**Nazwa państwa:** Atlantis
**Istotne cechy położenia geograficznego:** dostęp do Morza Bałtyckiego, kilka dużych żeglownych rzek, ograniczone zasoby wody pitnej
**Liczba ludności:** 28 mln
**Klimat:** umiarkowany
**Silne strony gospodarki:** przemysł ciężki, motoryzacyjny, spożywczy, chemiczny, ICT, ambicje odgrywania istotnej roli w zakresie OZE, przetwarzania surowców krytycznych oraz budowy ponadnarodowej infrastruktury AI (m.in. big data centers, giga fabryki AI, komputery kwantowe)
**Liczebność armii:** 150 tys. zawodowych żołnierzy
**Stopnień cyfryzacji społeczeństwa:** powyżej średniej europejskiej
**Waluta:** inna niż euro
**Kluczowe relacje dwustronne:** Niemcy, Francja, Finlandia, Ukraina, USA, Japonia
**Potencjalne zagrożenia polityczne i gospodarcze:** niestabilność w UE, rozpad UE na grupy „różnych prędkości” pod względem tempa rozwoju oraz zainteresowania głębszą integracją; negatywna kampania wizerunkowa ze strony kilku aktorów państwowych wymierzona przeciw rządowi lub społeczeństwu Atlantis; zakłócenia w dostawach paliw węglowodorowych z USA, Skandynawii, Zatoki Perskiej (wynikające z potencjalnych zmian w polityce wewnętrznej krajów eksporterów lub problemów w transporcie, np. ataki Hutich na gazowce na Morzu Czerwonym); narażenie na spowolnienie rozwoju sektora ICT z powodu embarga na wysokozaawansowane procesory
**Potencjalne zagrożenie militarne:** zagrożenie atakiem zbrojnym jednego z sąsiadów; trwające od wielu lat ataki hybrydowe co najmniej jednego sąsiada, w tym w obszarze infrastruktury krytycznej i cyberprzestrzeni
**Kamienie milowe w rozwoju politycznym i gospodarczym:** demokracja parlamentarna od 130 lat; okres stagnacji gospodarczej w latach 1930-1950 oraz 1980-1990; członkostwo w UE i NATO od roku 1997; 25. gospodarka świata wg PKB od roku 2020; deficyt budżetowy oraz dług publiczny w okolicach średniej unijnej

Dostępni eksperci:
{members_desc}

Zapytanie: {query}

Wybierz następnego eksperta lub FINISH."""
