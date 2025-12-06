"""
Serwis embeddingu z cache i batch processing.

Używa Google Generative AI Embeddings (Gemini) do generowania
wektorowych reprezentacji tekstu.
"""
from typing import List, Optional
import hashlib
import logging

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Serwis do generowania embeddingów z:
    - Batch processing dla wydajności
    - Cache dla powtarzających się zapytań
    - Retry logic dla API errors
    """

    DEFAULT_MODEL = "models/gemini-embedding-001"

    def __init__(
        self,
        model: str = None,
        cache_enabled: bool = True,
        max_cache_size: int = 10000
    ):
        """
        Inicjalizuje serwis embeddingu.

        Args:
            model: Nazwa modelu embeddingu (domyślnie gemini-embedding-001)
            cache_enabled: Czy włączyć cache dla zapytań
            max_cache_size: Maksymalny rozmiar cache
        """
        self.model_name = model or self.DEFAULT_MODEL
        self.cache_enabled = cache_enabled
        self.max_cache_size = max_cache_size

        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model_name,
            google_api_key=settings.gemini_api_key
        )

        self._cache: dict[str, List[float]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=lambda retry_state: logger.warning(
            f"Embedding retry {retry_state.attempt_number}/3..."
        )
    )
    def embed_query(self, text: str) -> List[float]:
        """
        Generuje embedding dla pojedynczego zapytania.

        Args:
            text: Tekst do zakodowania

        Returns:
            Lista floatów reprezentująca wektor embeddingu
        """
        if not text or not text.strip():
            logger.warning("Próba embeddingu pustego tekstu")
            return []

        # Sprawdź cache
        if self.cache_enabled:
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                self._cache_hits += 1
                return self._cache[cache_key]
            self._cache_misses += 1

        # Generuj embedding
        embedding = self._embeddings.embed_query(text)

        # Zapisz do cache
        if self.cache_enabled:
            self._add_to_cache(cache_key, embedding)

        return embedding

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=lambda retry_state: logger.warning(
            f"Batch embedding retry {retry_state.attempt_number}/3..."
        )
    )
    def embed_documents(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generuje embeddingi dla listy dokumentów w batchach.

        Args:
            texts: Lista tekstów do zakodowania
            batch_size: Rozmiar batcha (domyślnie 100)

        Returns:
            Lista list floatów - embeddingi dla każdego tekstu
        """
        if not texts:
            return []

        # Filtruj puste teksty
        valid_texts = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
        if not valid_texts:
            return [[] for _ in texts]

        # Przetwarzaj w batchach
        all_embeddings: List[Optional[List[float]]] = [None] * len(texts)

        indices = [i for i, _ in valid_texts]
        filtered_texts = [t for _, t in valid_texts]

        for i in range(0, len(filtered_texts), batch_size):
            batch_texts = filtered_texts[i:i + batch_size]
            batch_indices = indices[i:i + batch_size]

            logger.debug(f"Embedding batch {i // batch_size + 1}, size: {len(batch_texts)}")

            batch_embeddings = self._embeddings.embed_documents(batch_texts)

            for idx, embedding in zip(batch_indices, batch_embeddings):
                all_embeddings[idx] = embedding

        # Zastąp None pustymi listami
        return [e if e is not None else [] for e in all_embeddings]

    def _get_cache_key(self, text: str) -> str:
        """Generuje klucz cache dla tekstu."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def _add_to_cache(self, key: str, embedding: List[float]) -> None:
        """Dodaje embedding do cache z kontrolą rozmiaru."""
        if len(self._cache) >= self.max_cache_size:
            # Usuń najstarszy element (FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[key] = embedding

    def get_cache_stats(self) -> dict:
        """Zwraca statystyki cache."""
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0

        return {
            "cache_size": len(self._cache),
            "max_cache_size": self.max_cache_size,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": round(hit_rate, 3),
        }

    def clear_cache(self) -> None:
        """Czyści cache."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Cache embeddingów wyczyszczony")
