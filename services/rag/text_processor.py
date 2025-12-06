"""
Przetwarzanie i chunking dokumentów.

Dzieli dokumenty na mniejsze fragmenty (chunki) z metadanymi
dla efektywnego wyszukiwania wektorowego.
"""
from typing import List, Optional
from dataclasses import dataclass, field
import hashlib
from datetime import datetime
import logging
import json

from langchain_text_splitters import RecursiveCharacterTextSplitter

from schemas.schemas import DocumentMetadata

logger = logging.getLogger(__name__)


@dataclass
class ProcessedChunk:
    """Reprezentacja przetworzonego chunka dokumentu."""

    chunk_id: str
    document_id: str
    text: str
    metadata: dict
    chunk_index: int

    def to_dict(self) -> dict:
        """Konwertuje chunk do słownika."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "metadata": self.metadata,
            "chunk_index": self.chunk_index,
        }


@dataclass
class DocumentProcessorConfig:
    """Konfiguracja procesora dokumentów."""

    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: List[str] = field(default_factory=lambda: ["\n\n", "\n", ". ", ", ", " "])
    min_chunk_size: int = 100


class DocumentProcessor:
    """
    Przetwarza dokumenty na chunki z metadanymi.

    Używa RecursiveCharacterTextSplitter do inteligentnego
    dzielenia tekstu z zachowaniem kontekstu.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
        min_chunk_size: int = 100
    ):
        """
        Inicjalizuje procesor dokumentów.

        Args:
            chunk_size: Docelowy rozmiar chunka w znakach
            chunk_overlap: Nakładanie się chunków dla zachowania kontekstu
            separators: Lista separatorów do dzielenia tekstu
            min_chunk_size: Minimalny rozmiar chunka (mniejsze są pomijane)
        """
        default_separators = ["\n\n", "\n", ". ", ", ", " "]

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators or default_separators,
            length_function=len,
        )

        logger.info(
            f"DocumentProcessor zainicjalizowany: "
            f"chunk_size={chunk_size}, overlap={chunk_overlap}"
        )

    def process_document(
        self,
        content: str,
        metadata: DocumentMetadata,
        document_id: Optional[str] = None
    ) -> List[ProcessedChunk]:
        """
        Przetwarza dokument na listę chunków z metadanymi.

        Args:
            content: Treść dokumentu
            metadata: Metadane dokumentu (źródło, region, kraj, etc.)
            document_id: Opcjonalny ID dokumentu (generowany jeśli brak)

        Returns:
            Lista ProcessedChunk z tekstem i metadanymi
        """
        if not content or not content.strip():
            logger.warning("Próba przetworzenia pustego dokumentu")
            return []

        # Generuj ID dokumentu jeśli nie podano
        if not document_id:
            document_id = self._generate_document_id(content)

        # Podziel tekst na chunki
        chunks = self.text_splitter.split_text(content)

        # Filtruj zbyt krótkie chunki
        chunks = [c for c in chunks if len(c) >= self.min_chunk_size]

        if not chunks:
            logger.warning(f"Dokument {document_id} nie zawiera chunków po filtracji")
            return []

        processed_chunks = []

        for i, chunk_text in enumerate(chunks):
            chunk_id = f"{document_id}-chunk-{i:04d}"

            # Buduj metadane chunka
            chunk_metadata = self._build_chunk_metadata(
                document_id=document_id,
                chunk_id=chunk_id,
                chunk_index=i,
                chunk_text=chunk_text,
                doc_metadata=metadata,
                has_previous=i > 0,
                has_next=i < len(chunks) - 1,
                total_chunks=len(chunks),
            )

            processed_chunks.append(ProcessedChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                text=chunk_text,
                metadata=chunk_metadata,
                chunk_index=i,
            ))

        logger.debug(
            f"Dokument {document_id} przetworzony: "
            f"{len(processed_chunks)} chunków"
        )

        return processed_chunks

    def process_text(
        self,
        content: str,
        source: str,
        region: Optional[str] = None,
        country: Optional[str] = None,
        url: Optional[str] = None,
        date: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> List[ProcessedChunk]:
        """
        Przetwarza tekst z prostymi parametrami metadanych.

        Uproszczona wersja process_document() dla szybkiego użycia.

        Args:
            content: Treść dokumentu
            source: Źródło (NATO, EU_COMMISSION, etc.)
            region: Region (EU, USA, NATO, RUSSIA, ASIA)
            country: Kod kraju (DE, US, PL, etc.)
            url: URL źródłowy
            date: Data dokumentu (ISO format)
            document_id: Opcjonalny ID dokumentu

        Returns:
            Lista ProcessedChunk
        """
        metadata = DocumentMetadata(
            source=source,
            region=region,
            country=country,
            url=url,
            date=date,
        )

        return self.process_document(content, metadata, document_id)

    def _build_chunk_metadata(
        self,
        document_id: str,
        chunk_id: str,
        chunk_index: int,
        chunk_text: str,
        doc_metadata: DocumentMetadata,
        has_previous: bool,
        has_next: bool,
        total_chunks: int,
    ) -> dict:
        """Buduje pełne metadane dla chunka."""
        metadata = {
            # Identyfikacja
            "document_id": document_id,
            "chunk_id": chunk_id,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,

            # Źródło
            "source": doc_metadata.source or "",
            "url": doc_metadata.url or "",

            # Lokalizacja geograficzna
            "region": doc_metadata.region or "",
            "country": doc_metadata.country or "",

            # Czas
            "date": doc_metadata.date or "",

            # Techniczne
            "text_length": len(chunk_text),
            "has_previous_context": has_previous,
            "has_next_context": has_next,
            "ingestion_date": datetime.now().isoformat(),
        }

        # Parsuj rok i miesiąc z daty
        if doc_metadata.date:
            try:
                metadata["year"] = int(doc_metadata.date[:4])
                if len(doc_metadata.date) >= 7:
                    metadata["month"] = int(doc_metadata.date[5:7])
            except (ValueError, IndexError):
                pass

        return metadata

    def _generate_document_id(self, content: str, length: int = 12) -> str:
        """Generuje stabilny ID dokumentu na podstawie treści."""
        return hashlib.sha1(content.encode("utf-8")).hexdigest()[:length]

    def estimate_chunks(self, content: str) -> int:
        """
        Szacuje liczbę chunków dla danego tekstu.

        Args:
            content: Treść dokumentu

        Returns:
            Szacowana liczba chunków
        """
        if not content:
            return 0

        content_length = len(content)
        effective_chunk_size = self.chunk_size - self.chunk_overlap

        if effective_chunk_size <= 0:
            return 1

        return max(1, (content_length + effective_chunk_size - 1) // effective_chunk_size)


# Domyślna instancja procesora
_default_processor: Optional[DocumentProcessor] = None


def get_document_processor() -> DocumentProcessor:
    """Zwraca singleton instancję DocumentProcessor."""
    global _default_processor
    if _default_processor is None:
        _default_processor = DocumentProcessor()
    return _default_processor
