"""
Scraper dokumentów z publicznych źródeł geopolitycznych.

Obsługuje: NATO.int, EC.europa.eu, US State Department, UK FCDO
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import httpx
from bs4 import BeautifulSoup
import trafilatura
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScrapedDocument:
    """Pojedynczy zescrapowany dokument."""
    url: str
    title: str
    content: str
    source: str  # "NATO", "EU_COMMISSION", etc.
    date: Optional[str] = None  # ISO format
    region: Optional[str] = None
    country: Optional[str] = None
    document_type: str = "article"  # "report", "statement", "article"
    metadata: Dict[str, Any] = field(default_factory=dict)


class SourceConfig:
    """Konfiguracja źródeł do scrapowania."""

    NATO = {
        "base_url": "https://www.nato.int",
        "search_paths": [
            "/cps/en/natohq/news.htm",
            "/cps/en/natohq/official_texts.htm"
        ],
        "source_code": "NATO",
        "region": "NATO",
        "max_documents": 30,
        "keywords": ["news", "press", "statement", "publication"]
    }

    EU_COMMISSION = {
        "base_url": "https://ec.europa.eu",
        "search_paths": [
            "/commission/presscorner/home/en"
        ],
        "source_code": "EU_COMMISSION",
        "region": "EU",
        "max_documents": 30,
        "keywords": ["press-release", "statement"]
    }

    US_STATE = {
        "base_url": "https://www.state.gov",
        "search_paths": [
            "/briefings-foreign-press-centers/",
            "/press-releases/"
        ],
        "source_code": "US_STATE",
        "region": "USA",
        "max_documents": 30,
        "keywords": ["press-releases", "briefings"]
    }


class DocumentScraper:
    """Główna klasa scrapera z retry logic i rate limiting."""

    def __init__(self, timeout: int = 30, rate_limit_delay: float = 1.5):
        """
        Args:
            timeout: Timeout dla requestów HTTP (sekundy)
            rate_limit_delay: Opóźnienie między requestami (sekundy)
        """
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "GeopoliticalAnalysisBot/1.0 (Educational Research; +https://github.com/yourusername/project)"
            }
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def fetch_url(self, url: str) -> Optional[str]:
        """
        Pobiera HTML z retry logic.

        Args:
            url: URL do pobrania

        Returns:
            HTML jako string lub None jeśli błąd
        """
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            logger.warning(f"Błąd HTTP dla {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd dla {url}: {e}")
            return None

    async def scrape_source(self, source_config: Dict[str, Any]) -> List[ScrapedDocument]:
        """
        Scrapuje dokumenty z jednego źródła.

        Args:
            source_config: Konfiguracja źródła (z SourceConfig)

        Returns:
            Lista zescrapowanych dokumentów
        """
        documents = []
        base_url = source_config["base_url"]
        max_documents = source_config.get("max_documents", 30)

        logger.info(f"Scrapuję źródło: {source_config['source_code']}")

        for search_path in source_config["search_paths"]:
            listing_url = f"{base_url}{search_path}"
            logger.info(f"Pobieram listing: {listing_url}")

            html = await self.fetch_url(listing_url)
            if not html:
                logger.warning(f"Nie udało się pobrać {listing_url}")
                continue

            # Wyciągnij URL-e artykułów
            article_urls = self._extract_article_urls(
                html,
                base_url,
                source_config.get("keywords", [])
            )

            logger.info(f"Znaleziono {len(article_urls)} potencjalnych artykułów")

            # Scrapuj każdy artykuł
            for article_url in article_urls[:max_documents]:
                doc = await self._scrape_single_document(article_url, source_config)
                if doc:
                    documents.append(doc)
                    logger.debug(f"Zescrapowano: {doc.title[:60]}...")

                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)

                if len(documents) >= max_documents:
                    break

            if len(documents) >= max_documents:
                break

        logger.info(f"Zakończono scraping {source_config['source_code']}: {len(documents)} dokumentów")
        return documents

    async def _scrape_single_document(
        self,
        url: str,
        config: Dict[str, Any]
    ) -> Optional[ScrapedDocument]:
        """
        Scrapuje pojedynczy dokument używając trafilatura.

        Args:
            url: URL dokumentu
            config: Konfiguracja źródła

        Returns:
            ScrapedDocument lub None jeśli błąd
        """
        html = await self.fetch_url(url)
        if not html:
            return None

        # Ekstrakcja treści przez trafilatura
        content = trafilatura.extract(
            html,
            include_tables=True,
            include_links=False,
            favor_precision=True,
            favor_recall=False
        )

        if not content or len(content) < 200:
            logger.debug(f"Za krótki content dla {url}: {len(content) if content else 0} znaków")
            return None

        # Parsowanie metadanych
        soup = BeautifulSoup(html, 'html.parser')
        title = self._extract_title(soup)
        date = self._extract_date(soup)

        return ScrapedDocument(
            url=url,
            title=title,
            content=content,
            source=config["source_code"],
            date=date,
            region=config.get("region"),
            country=config.get("country"),
            document_type=self._infer_document_type(url, title),
            metadata={
                "scraped_at": datetime.now().isoformat(),
                "base_url": config["base_url"]
            }
        )

    def _extract_article_urls(
        self,
        html: str,
        base_url: str,
        keywords: List[str]
    ) -> List[str]:
        """
        Wyciąga URL-e artykułów z listingu.

        Args:
            html: HTML strony z listingiem
            base_url: Bazowy URL źródła
            keywords: Słowa kluczowe do filtrowania linków

        Returns:
            Lista URL-i artykułów
        """
        soup = BeautifulSoup(html, 'html.parser')
        urls = set()

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Filtrowanie po keywords
            if keywords and not any(kw in href.lower() for kw in keywords):
                continue

            # Konwersja relative → absolute URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                full_url = f"{base_url}{href}"
            else:
                full_url = f"{base_url}/{href}"

            # Podstawowa walidacja
            if full_url.startswith(base_url) and not any(
                ext in full_url.lower() for ext in ['.pdf', '.jpg', '.png', '.xml']
            ):
                urls.add(full_url)

        return list(urls)

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Wyciąga tytuł ze strony."""
        # Próbuj h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        # Fallback: title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)

        return "Unknown Title"

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Wyciąga datę publikacji ze strony."""
        # Próbuj meta tag
        date_meta = soup.find('meta', {'property': 'article:published_time'})
        if date_meta and date_meta.get('content'):
            return date_meta['content']

        # Próbuj time tag
        time_tag = soup.find('time', {'datetime': True})
        if time_tag:
            return time_tag['datetime']

        return None

    def _infer_document_type(self, url: str, title: str) -> str:
        """Inferencja typu dokumentu na podstawie URL i tytułu."""
        url_lower = url.lower()
        title_lower = title.lower()

        if 'press' in url_lower or 'statement' in title_lower:
            return "statement"
        elif 'report' in url_lower or 'publication' in url_lower:
            return "report"
        elif 'speech' in url_lower or 'remarks' in title_lower:
            return "speech"

        return "article"

    async def close(self):
        """Zamyka HTTP client."""
        await self.client.aclose()


async def scrape_all_sources() -> List[ScrapedDocument]:
    """
    Scrapuje wszystkie skonfigurowane źródła.

    Returns:
        Lista wszystkich zescrapowanych dokumentów
    """
    scraper = DocumentScraper()
    sources = [
        SourceConfig.NATO,
        SourceConfig.EU_COMMISSION,
        SourceConfig.US_STATE
    ]

    all_documents = []

    for source in sources:
        try:
            docs = await scraper.scrape_source(source)
            all_documents.extend(docs)
        except Exception as e:
            logger.error(f"Błąd scrapowania {source['source_code']}: {e}")
            continue

    await scraper.close()

    logger.info(f"Łącznie zescrapowano {len(all_documents)} dokumentów z {len(sources)} źródeł")
    return all_documents
