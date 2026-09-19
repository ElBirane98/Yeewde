"""
rag_engine/retriever.py
Recherche les documents pertinents dans ChromaDB pour une question donnee.
"""
from __future__ import annotations

import logging
import re

import duckdb

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:  # ChromaDB is optional when the SQL fallback is used.
    chromadb = None
    embedding_functions = None

from rag_engine.config import CHROMA_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL, N_RESULTS
from ml_engine.config import DUCKDB_PATH

logger = logging.getLogger(__name__)

_SUPPLIER_RE = re.compile(r"\bSUP\d+\b|\b(supplier|fournisseur)\s*[:=]?\s*([A-Z0-9]+)\b", re.IGNORECASE)


def extract_supplier_id(query: str) -> str | None:
    """Extrait un identifiant fournisseur depuis une question de type business."""
    if not query:
        return None

    match = re.search(r"\bSUP\d+\b", query, flags=re.IGNORECASE)
    if match:
        return match.group(0).upper()

    match = re.search(r"\b(?:supplier|fournisseur)\s*[:=]?\s*([A-Z0-9]+)\b", query, flags=re.IGNORECASE)
    if match:
        return match.group(1).upper()

    return None


def get_collection():
    """Charge la collection ChromaDB existante."""
    if chromadb is None or embedding_functions is None:
        raise RuntimeError("ChromaDB n'est pas installé.")
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


def _fallback_documents(
    query: str, n_results: int = N_RESULTS, supplier_id: str | None = None
) -> list[str]:
    """Fallback local sur DuckDB quand Chroma n'existe pas."""
    try:
        with duckdb.connect(str(DUCKDB_PATH), read_only=True) as conn:
            if supplier_id:
                rows = conn.execute(
                    """
                    SELECT supplier_id, supplier_risk_class, otif_rate, avg_delay_days,
                           total_incidents, critical_incidents
                    FROM gold.marts_supplier_kpi
                    WHERE lower(supplier_id) = lower(?)
                    """,
                    [supplier_id],
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT supplier_id, supplier_risk_class, otif_rate, avg_delay_days,
                           total_incidents, critical_incidents
                    FROM gold.marts_supplier_kpi
                    ORDER BY otif_rate ASC NULLS LAST
                    LIMIT ?
                    """,
                    [max(1, n_results)],
                ).fetchall()
    except duckdb.Error as exc:
        logger.warning("Fallback DuckDB indisponible: %s", exc)
        return [
            "Le moteur vectoriel RAG est indisponible. Les données de base restent accessibles via la base DuckDB du projet.",
            "Le projet Yeewde contient une table gold.marts_supplier_kpi qui conserve les indicateurs OTIF, délai moyen et incidents qualité par fournisseur.",
        ]

    docs: list[str] = []
    for supplier_id, risk_class, otif_rate, avg_delay_days, total_incidents, critical_incidents in rows:
        docs.append(
            f"Fournisseur {supplier_id} | Classe {risk_class} | OTIF {float(otif_rate or 0):.1%} | "
            f"Délai moyen {float(avg_delay_days or 0):.1f} jours | Incidents {int(total_incidents or 0)} | "
            f"Incidents critiques {int(critical_incidents or 0)}."
        )

    if not docs:
        if supplier_id:
            return [f"Aucune donnée fournisseur disponible pour '{supplier_id}'."]
        docs = [
            f"Pas de données RAG liées à la requête '{query}'. Le fallback local a été activé pour assurer la continuité du service.",
            "Les tables gold.marts_supplier_kpi et gold.marts_otif_kpi restent disponibles dans DuckDB pour l'analyse opérationnelle.",
        ]
    return docs


def retrieve(query: str, n_results: int = N_RESULTS) -> list[str]:
    """
    Recherche les documents les plus pertinents pour une question.
    """
    supplier_id = extract_supplier_id(query)
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count()),
        )
        docs = results["documents"][0] if results["documents"] else []
        if docs:
            print(f"[retriever] {len(docs)} documents recuperes pour : '{query[:60]}...'")
            return docs
    except Exception as exc:
        logger.info("Recherche Chroma indisponible, fallback DuckDB: %s", exc)

    fallback_docs = _fallback_documents(query, n_results, supplier_id=supplier_id)
    print(f"[retriever] fallback local active pour la requête : '{query[:60]}...'")
    return fallback_docs


def retrieve_for_supplier(supplier_id: str) -> list[str]:
    """Recupere directement le document d'un fournisseur specifique."""
    try:
        collection = get_collection()
        results = collection.get(ids=[str(supplier_id)])
        docs = results["documents"] if results["documents"] else []
        if docs:
            return docs
    except Exception as exc:
        logger.info("Recherche Chroma fournisseur indisponible, fallback DuckDB: %s", exc)

    return _fallback_documents(f"fournisseur {supplier_id}", 1, supplier_id=supplier_id)

if __name__ == "__main__":
    docs = retrieve("Quel est l'OTIF global et les problèmes de livraison ?")
    print("\n--- Documents retrouvés ---")
    for i, doc in enumerate(docs, 1):
        print(f"\n[Doc {i}]:\n{doc}")
