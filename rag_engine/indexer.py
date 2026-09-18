"""
rag_engine/indexer.py
Construit l'index vectoriel ChromaDB a partir des donnees Gold (DuckDB).
Chaque document = un fournisseur avec ses KPIs historiques.
Usage : python -m rag_engine.indexer
"""
import duckdb
import chromadb
from chromadb.utils import embedding_functions

from rag_engine.config import CHROMA_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL
from ml_engine.config import DUCKDB_PATH


def build_supplier_documents() -> list[dict]:
    """
    Charge marts_supplier_kpi depuis DuckDB Gold et construit
    des documents texte lisibles pour l'indexation.
    """
    conn = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    rows = conn.execute("SELECT * FROM gold.marts_supplier_kpi").fetchall()
    cols = [d[0] for d in conn.description]
    conn.close()

    documents = []
    for row in rows:
        r = dict(zip(cols, row))
        supplier_id = r.get("supplier_id", "UNKNOWN")

        doc_text = (
            f"Fournisseur {supplier_id} | "
            f"Classe de risque : {r.get('supplier_risk_class', 'N/A')} | "
            f"Total commandes : {r.get('total_orders', 0)} | "
            f"Commandes livrees : {r.get('delivered_orders', 0)} | "
            f"Commandes en attente : {r.get('pending_orders', 0)} | "
            f"Taux OTIF : {r.get('otif_rate', 0):.1%} | "
            f"Taux livraison a temps : {r.get('on_time_rate', 0):.1%} | "
            f"Taux quantite complete : {r.get('in_full_rate', 0):.1%} | "
            f"Retard moyen : {r.get('avg_delay_days', 0):.1f} jours | "
            f"Retard max : {r.get('max_delay_days', 0)} jours | "
            f"Incidents qualite : {r.get('total_incidents', 0)} | "
            f"Incidents critiques : {r.get('critical_incidents', 0)} | "
            f"Depense totale : {r.get('total_ordered_spend', 0):,.0f} USD"
        )

        documents.append({
            "id": str(supplier_id),
            "text": doc_text,
            "metadata": {
                "supplier_id": str(supplier_id),
                "risk_class": str(r.get("supplier_risk_class", "")),
                "otif_rate": float(r.get("otif_rate") or 0),
                "total_orders": int(r.get("total_orders") or 0),
            }
        })

    print(f"[indexer] {len(documents)} documents fournisseurs prepares")
    return documents


def build_index(force_rebuild: bool = False):
    """
    Cree ou recharge la collection ChromaDB.
    Si force_rebuild=True, supprime et reindexe.
    """
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Verifie si la collection existe deja
    existing = [c.name for c in client.list_collections()]
    if CHROMA_COLLECTION in existing and not force_rebuild:
        collection = client.get_collection(CHROMA_COLLECTION)
        print(f"[indexer] Collection '{CHROMA_COLLECTION}' existante "
              f"({collection.count()} docs) - pas de reindexation")
        return collection

    # Supprime si rebuild force
    if CHROMA_COLLECTION in existing:
        client.delete_collection(CHROMA_COLLECTION)
        print(f"[indexer] Collection '{CHROMA_COLLECTION}' supprimee pour rebuild")

    # Fonction d'embedding (locale, pas d'API)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    collection = client.create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    # Indexation
    docs = build_supplier_documents()
    collection.add(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        metadatas=[d["metadata"] for d in docs],
    )

    print(f"[indexer] Index construit : {collection.count()} documents dans '{CHROMA_COLLECTION}'")
    return collection


if __name__ == "__main__":
    build_index(force_rebuild=True)
    print("[indexer] Done.")
