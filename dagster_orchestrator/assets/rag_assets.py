"""Dagster asset for the supplier RAG index."""

from __future__ import annotations

from dagster import asset

from dagster_orchestrator.assets.dbt_assets import dbt_transformations
from rag_engine.indexer import build_index


@asset(deps=[dbt_transformations])
def build_rag_index(context) -> dict[str, int]:
    """Refresh the vector index from the validated supplier mart."""
    collection = build_index(force_rebuild=True)
    count = collection.count()
    context.log.info("Index RAG construit avec %s documents.", count)
    return {"document_count": count}
