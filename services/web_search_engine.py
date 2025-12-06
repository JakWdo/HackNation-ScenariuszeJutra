import os
from typing import List
import hashlib
import chromadb

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class WebSearchEngine:
    def __init__(self):
        self.search = DuckDuckGoSearchRun()

    def search_web(self, query: str) -> str:
        return self.search.run(query)

    def search_web_for_rag(self, query: str) -> List[str]:
        """
        Searches the web for the given query and returns a list of relevant snippets
        suitable for a RAG system.
        """
        # DuckDuckGoSearchRun returns a single string,
        # we might want to split it into more manageable chunks
        # or integrate with a tool that returns structured results.
        # For simplicity, we'll return the full result as a single item in a list.
        result = self.search.run(query)
        # In a real RAG system, you might want to parse this result
        # into multiple, smaller, semantically coherent chunks.
        # For now, we treat the entire result as one "document" or snippet.
        return [result]

class TextProcessor: 
    def __init__(self, content):
        self.content = content

        self.chunks = None
        self.embeddings = None

    def chunk_document(self, document_content: str, document_id: str = None):
        """
        Chunks a document using the provided text splitter and adds metadata.
        Applies a simple contextual chunking strategy by ensuring each chunk
        retains some context from the original document.
        """
        chunks = self.text_splitter.split_text(document_content)

        def _stable_id(text: str, length: int = 12) -> str:
            """Generates a stable, short ID for a given text."""
            return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]
        
        processed_chunks = []
        for i, chunk_text in enumerate(chunks):
            chunk_metadata = {
                "chunk_id": f"{document_id or _stable_id(document_content)}-chunk-{i}",
                "document_id": document_id or _stable_id(document_content),
                "chunk_index": i,
                "text_length": len(chunk_text),
            }
            # Add context from previous chunk if available (simple strategy)
            if i > 0:
                previous_chunk_text = chunks[i-1]
                chunk_metadata["has_previous_context"] = True

            processed_chunks.append(
                {"document_id": document_id, "text": chunk_text, "metadata": chunk_metadata}
            )
        
        self.processed_chunks = processed_chunks

    def embedder(self):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        for chunk in self.processed_chunks['text']:
            embeddings.embed_query(chunk)

    def vector_store(self):
        client = chromadb.Client()
        collection = client.create_collection("") # ustawic specyficzna nazwe

        collection.add(
            documents=[doc_id for doc_id in self.processed_chunks['document_id']], 
            metadatas=[{"source": metadata for _, metadata in self.processed_chunks['metadata'].items()}], 
            ids=[], 
        )

        self.collection = collection

class DataProcessor: 
    def __init__(self, llm):
        self.llm = llm 
        self.web_search_engine = WebSearchEngine()

    def run_search_engine(self, search_query: str):
        docs = self.web_search_engine.search_web(search_query)
        
        pass


if __name__ == '__main__':
    # Example usage
    web_search = WebSearchEngine()

    print("--- Testing search_web ---")
    query_general = "current weather in London"
    general_result = web_search.search_web(query_general)
    print(f"Query: {query_general}\nResult: {general_result[:500]}...")

    print("\n--- Testing search_web_for_rag ---")
    query_rag = "latest advancements in AI for medical diagnosis"
    rag_results = web_search.search_web_for_rag(query_rag)
    print(f"Query: {query_rag}")
    for i, snippet in enumerate(rag_results):
        print(f"Snippet {i+1}:\n{snippet[:500]}...")
    
    def get_search_urls(query: str) -> List[str]:
        """
        Searches the web for the given query and returns a list of relevant URLs.
        This tool is useful when the user explicitly asks for links or sources related to a topic.
        """
        # DuckDuckGoSearchRun doesn't directly expose a method to get just URLs
        # without content. We'll simulate this by performing a search and
        # attempting to extract URLs from the result string.
        # This is a basic implementation and might not be exhaustive or perfect.
        result = web_search.search_web(query)
        
        # A simple regex to find URLs in the search result string
        import re
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', result)
        print(urls)
        
        # Filter out duplicates and ensure they are valid-looking URLs
        unique_urls = []
        for url in urls:
            # Basic validation: check if it looks like a proper URL start
            if url.startswith("http") or url.startswith("www."):
                if url not in unique_urls:
                    unique_urls.append(url)
        
        return unique_urls

    print("\n--- Testing get_search_urls ---")
    query_urls = "best AI research papers 2023"
    url_results = get_search_urls(query_urls)
    print(f"Query: {query_urls}")
    if url_results:
        for i, url in enumerate(url_results[:5]): # Print up to 5 URLs
            print(f"URL {i+1}: {url}")
    else:
        print("No URLs found.")


