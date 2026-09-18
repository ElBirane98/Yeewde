"""
Définition centralisée des objets Dagster pour Yeewde AI
Orchestration Ingestion, dbt, ML, RAG et Monitoring.
"""

from dagster import Definitions, load_assets_from_package_module
from dagster_orchestrator import assets

# Chargement automatique de tous les modules contenus dans le sous-dossier assets/
all_assets = load_assets_from_package_module(assets)

# Export obligatoire de la variable 'defs'
defs = Definitions(
    assets=all_assets,
    schedules=[],
    sensors=[],
    resources={}
)