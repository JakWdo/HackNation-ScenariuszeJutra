import chromadb
import json
import os

PERSIST_PATH = "./data/chromadb"
# Nazwa domyślnej kolekcji z services/rag/vector_store.py
DEFAULT_COLLECTION_NAME = "geopolitical_documents" 

def inspect():
    if not os.path.exists(PERSIST_PATH):
        print(f"BŁĄD: Katalog {PERSIST_PATH} nie istnieje. Czy uruchomiłeś pipeline (scripts/run_pipeline.py)?")
        return

    print(f"--- Podłączanie do ChromaDB w {PERSIST_PATH} ---")
    try:
        client = chromadb.PersistentClient(path=PERSIST_PATH)
    except Exception as e:
        print(f"Błąd połączenia: {e}")
        return

    collections = client.list_collections()
    print(f"Znaleziono {len(collections)} kolekcji: {[c.name for c in collections]}")

    target_col = None
    # Próba znalezienia głównej kolekcji lub użycie pierwszej dostępnej
    for c in collections:
        if c.name == DEFAULT_COLLECTION_NAME:
            target_col = c
            break
    
    if not target_col and collections:
        target_col = collections[0]
        print(f"Główna kolekcja '{DEFAULT_COLLECTION_NAME}' nieznaleziona. Używam '{target_col.name}'.")
    elif not target_col:
        print("Brak kolekcji w bazie.")
        return

    count = target_col.count()
    print(f"\nKolekcja: {target_col.name}")
    print(f"Liczba dokumentów: {count}")

    if count == 0:
        print("Kolekcja jest pusta.")
        return

    # Pobranie próbki 5 dokumentów
    print("\n--- Podgląd 5 pierwszych dokumentów ---")
    try:
        result = target_col.get(limit=5)
        
        ids = result['ids']
        metadatas = result['metadatas']
        documents = result['documents']

        for i in range(len(ids)):
            print(f"\n[Dokument {i+1}] ID: {ids[i]}")
            meta_str = json.dumps(metadatas[i], indent=2, ensure_ascii=False) if metadatas[i] else "{}"
            print(f"Metadata: {meta_str}")
            content_preview = documents[i][:200].replace('\n', ' ') + "..." if documents[i] else "Brak treści"
            print(f"Treść (skrót): {content_preview}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Błąd podczas pobierania dokumentów: {e}")

if __name__ == "__main__":
    inspect()
