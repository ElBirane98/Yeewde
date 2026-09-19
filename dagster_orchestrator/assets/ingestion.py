from __future__ import annotations

from dagster import asset

from data_sources.bronze import materialize_bronze


@asset
def bronze_ingestion(context) -> dict:
    result = materialize_bronze()
    context.log.info("Bronze matérialisé : %s lignes", result["row_count"])
    return result
