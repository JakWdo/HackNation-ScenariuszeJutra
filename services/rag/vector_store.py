"""
Zarządzanie persystentną bazą wektorową ChromaDB.

Obsługuje przechowywanie, wyszukiwanie i zarządzanie
embeddingami dokumentów geopolitycznych.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

import chromadb
from chromadb.config import Settings as ChromaSettings

from .embeddings import EmbeddingService
from .text_processor import ProcessedChunk

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manager dla ChromaDB z persystentnym storage.

    Obsługuje:
    - Persystencję danych między restartami
    - Batch upsert z automatycznym embedowaniem
    - Wyszukiwanie semantyczne z filtrowaniem metadanych
    - Zarządzanie kolekcjami
    """

    DEFAULT_PERSIST_PATH = "./data/chromadb"
    MAIN_COLLECTION = "geopolitical_documents"

    def __init__(
        self,
        persist_path: Optional[str] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        """
        Inicjalizuje VectorStoreManager.

        Args:
            persist_path: Ścieżka do persystentnego storage
            embedding_service: Serwis do generowania embeddingów
        """
        self.persist_path = Path(persist_path or self.DEFAULT_PERSIST_PATH)
        self.persist_path.mkdir(parents=True, exist_ok=True)

        # Inicjalizuj klienta ChromaDB z persystencją
        self._client = chromadb.PersistentClient(
            path=str(self.persist_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self._embedding_service = embedding_service or EmbeddingService()
        self._collections: Dict[str, chromadb.Collection] = {}

        logger.info(f"VectorStoreManager zainicjalizowany: {self.persist_path}")

    def get_or_create_collection(
        self,
        name: Optional[str] = None,
        distance_metric: str = "cosine"
    ) -> chromadb.Collection:
        """
        Pobiera lub tworzy kolekcję.

        Args:
            name: Nazwa kolekcji (domyślnie MAIN_COLLECTION)
            distance_metric: Metryka odległości (cosine, l2, ip)

        Returns:
            Kolekcja ChromaDB
        """
        collection_name = name or self.MAIN_COLLECTION

        if collection_name not in self._collections:
            self._collections[collection_name] = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": distance_metric}
            )
            logger.debug(f"Kolekcja '{collection_name}' załadowana/utworzona")

        return self._collections[collection_name]

    def add_chunks(
        self,
        chunks: List[ProcessedChunk],
        collection_name: Optional[str] = None,
        batch_size: int = 100
    ) -> int:
        """
        Dodaje chunki do kolekcji z automatycznym embedowaniem.

        Args:
            chunks: Lista ProcessedChunk do dodania
            collection_name: Nazwa kolekcji (opcjonalna)
            batch_size: Rozmiar batcha dla operacji (domyślnie 100)

        Returns:
            Liczba dodanych chunków
        """
        if not chunks:
            return 0

        collection = self.get_or_create_collection(collection_name)
        added_count = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            ids = [chunk.chunk_id for chunk in batch]
            documents = [chunk.text for chunk in batch]
            metadatas = [self._sanitize_metadata(chunk.metadata) for chunk in batch]

            # Generuj embeddingi
            embeddings = self._embedding_service.embed_documents(documents)

            # Upsert (dodaj lub zaktualizuj)
            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )

            added_count += len(batch)
            logger.debug(f"Dodano batch {i // batch_size + 1}: {len(batch)} chunków")

        logger.info(f"Dodano {added_count} chunków do kolekcji")
        return added_count

    def add_document(
        self,
        document_id: str,
        text: str,
        metadata: Dict[str, Any],
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Dodaje pojedynczy dokument do kolekcji.

        Args:
            document_id: ID dokumentu
            text: Treść dokumentu
            metadata: Metadane dokumentu
            collection_name: Nazwa kolekcji (opcjonalna)

        Returns:
            True jeśli sukces
        """
        collection = self.get_or_create_collection(collection_name)

        # Generuj embedding
        embedding = self._embedding_service.embed_query(text)

        if not embedding:
            logger.error(f"Nie udało się wygenerować embeddingu dla {document_id}")
            return False

        collection.upsert(
            ids=[document_id],
            documents=[text],
            metadatas=[self._sanitize_metadata(metadata)],
            embeddings=[embedding]
        )

        return True

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None,
        include: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Wykonuje zapytanie semantyczne z opcjonalnym filtrowaniem.

        Args:
            query_text: Tekst zapytania
            n_results: Liczba wyników (domyślnie 5)
            where: Filtr na metadanych (np. {"region": "EU"})
            where_document: Filtr na treści dokumentu
            collection_name: Nazwa kolekcji (opcjonalna)
            include: Pola do zwrócenia (documents, metadatas, distances)

        Returns:
            Słownik z wynikami: documents, metadatas, distances, ids
        """
        collection = self.get_or_create_collection(collection_name)

        # Generuj embedding zapytania
        query_embedding = self._embedding_service.embed_query(query_text)

        if not query_embedding:
            logger.warning("Nie udało się wygenerować embeddingu zapytania")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

        # Wykonaj zapytanie
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=include or ["documents", "metadatas", "distances"]
        )

        return results

    def query_by_region(
        self,
        query_text: str,
        region: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Wyszukuje dokumenty dla konkretnego regionu."""
        return self.query(
            query_text=query_text,
            n_results=n_results,
            where={"region": region}
        )

    def query_by_country(
        self,
        query_text: str,
        country: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Wyszukuje dokumenty dla konkretnego kraju."""
        return self.query(
            query_text=query_text,
            n_results=n_results,
            where={"country": country}
        )

    def query_by_source(
        self,
        query_text: str,
        source: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Wyszukuje dokumenty z konkretnego źródła."""
        return self.query(
            query_text=query_text,
            n_results=n_results,
            where={"source": source}
        )

    def delete_document(
        self,
        document_id: str,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Usuwa dokument z kolekcji.

        Args:
            document_id: ID dokumentu do usunięcia
            collection_name: Nazwa kolekcji (opcjonalna)

        Returns:
            True jeśli sukces
        """
        collection = self.get_or_create_collection(collection_name)

        try:
            # Usuń wszystkie chunki dokumentu
            collection.delete(
                where={"document_id": document_id}
            )
            logger.info(f"Usunięto dokument {document_id}")
            return True
        except Exception as e:
            logger.error(f"Błąd usuwania dokumentu {document_id}: {e}")
            return False

    def get_collection_stats(
        self,
        collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Zwraca statystyki kolekcji.

        Args:
            collection_name: Nazwa kolekcji (opcjonalna)

        Returns:
            Słownik ze statystykami
        """
        collection = self.get_or_create_collection(collection_name)

        return {
            "name": collection.name,
            "count": collection.count(),
            "persist_path": str(self.persist_path),
        }

    def list_collections(self) -> List[str]:
        """Zwraca listę nazw wszystkich kolekcji."""
        collections = self._client.list_collections()
        return [c.name for c in collections]

    def reset_collection(
        self,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Resetuje (czyści) kolekcję.

        Args:
            collection_name: Nazwa kolekcji (opcjonalna)

        Returns:
            True jeśli sukces
        """
        name = collection_name or self.MAIN_COLLECTION

        try:
            self._client.delete_collection(name)
            if name in self._collections:
                del self._collections[name]
            logger.info(f"Kolekcja '{name}' zresetowana")
            return True
        except Exception as e:
            logger.error(f"Błąd resetowania kolekcji '{name}': {e}")
            return False

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanityzuje metadane dla ChromaDB.

        ChromaDB wymaga prostych typów: str, int, float, bool.
        Złożone typy są konwertowane do stringów.
        """
        sanitized = {}

        for key, value in metadata.items():
            if value is None:
                sanitized[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, (list, dict)):
                import json
                sanitized[key] = json.dumps(value)
            else:
                sanitized[key] = str(value)

        return sanitized


# Singleton instancja
_vector_store_manager: Optional[VectorStoreManager] = None


def get_vector_store_manager() -> VectorStoreManager:
    """Zwraca singleton instancję VectorStoreManager."""
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
    return _vector_store_manager
