"""Dagster assets : dérive Evidently et rapport de santé pipeline."""

from __future__ import annotations

from dagster import asset

from dagster_orchestrator.assets.ml_assets import train_otif_model
from ml_engine.drift_monitor import run_drift_check
from monitoring.pipeline_health import pipeline_health


@asset(deps=[train_otif_model])
def check_data_drift(context) -> dict:
    """Mesure la dérive entre commandes livrées et commandes en cours."""
    report = run_drift_check()
    context.log.info("Drift : detected=%s share=%s", report["drift_detected"], report["drift_share"])
    return report


@asset(deps=[check_data_drift])
def pipeline_health_report(context) -> dict:
    """Agrège Elementary (dbt), drift, MLflow et logs RAG pour le cockpit."""
    report = pipeline_health()
    context.log.info("Santé pipeline : %s", report)
    return report
