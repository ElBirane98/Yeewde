"""
rag_engine/retriever.py
Recherche les documents pertinents dans ChromaDB pour une question donnee.
"""
import chromadb
from chromadb.utils import embedding_functions

from rag_engine.config import CHROMA_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL, N_RESULTS


def get_collection():
    """Charge la collection ChromaDB existante."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    try:
        collection = client.get_collection(
            name=CHROMA_COLLECTION,
            embedding_function=ef,
        )
        return collection
    except Exception:
        raise RuntimeError(
            f"Collection '{CHROMA_COLLECTION}' introuvable. "
            "Lancez d'abord : python -m rag_engine.indexer"
        )


def retrieve(query: str, n_results: int = N_RESULTS) -> list[str]:
    """
    Recherche les documents les plus pertinents pour une question.

    Args:
        query   : question en langage naturel
        n_results: nombre de documents a retourner

    Returns:
        Liste de textes de documents pertinents
    """
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
    )
    docs = results["documents"][0] if results["documents"] else []
    print(f"[retriever] {len(docs)} documents recuperes pour : '{query[:60]}...'")
    return docs


def retrieve_for_supplier(supplier_id: str) -> list[str]:
    """Recupere directement le document d'un fournisseur specifique."""
    collection = get_collection()
    results = collection.get(ids=[str(supplier_id)])
    docs = results["documents"] if results["documents"] else []
    if not docs:
        print(f"[retriever] Fournisseur '{supplier_id}' non trouve dans l'index")
    return docs

if __name__ == "__main__":
    # Test de recherche par texte
    docs = retrieve("Quel est l'OTIF global et les problèmes de livraison ?")
    print("\n--- Documents retrouvés ---")
    for i, doc in enumerate(docs, 1):
        print(f"\n[Doc {i}]:\n{doc}")

    # Test de récupération directe par identifiant fournisseur (ex: 'SUP001')
    docs_supplier = retrieve_for_supplier("SUP001")
    print("\n--- Document du fournisseur SUP001 ---")
    print(docs_supplier)