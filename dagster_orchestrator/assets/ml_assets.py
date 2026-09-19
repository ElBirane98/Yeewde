"""Dagster asset for model training."""

from __future__ import annotations

from dagster import asset

from dagster_orchestrator.assets.dbt_assets import dbt_transformations
from ml_engine.config import MODEL_PATH
from ml_engine.train import train


@asset(deps=[dbt_transformations])
def train_otif_model(context) -> dict:
    """Train and persist the OTIF model only after validated dbt data."""
    _, metrics = train()
    context.log.info("Modèle OTIF entraîné : %s", metrics)
    return {"model_path": str(MODEL_PATH), "metrics": metrics}
