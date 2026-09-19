"""Dagster asset for the dbt transformations."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from dagster import asset

from dagster_orchestrator.assets.ingestion import bronze_ingestion

ROOT = Path(__file__).resolve().parents[2]
DBT_DIR = ROOT / "dbt_yeewde"


@asset(deps=[bronze_ingestion])
def dbt_transformations(context) -> dict[str, str]:
    """Build models and execute dbt data tests after Bronze ingestion."""
    command = [
        sys.executable,
        "-m",
        "dbt.cli.main",
        "build",
        "--project-dir",
        str(DBT_DIR),
        "--profiles-dir",
        str(DBT_DIR),
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode:
        context.log.error(result.stdout)
        context.log.error(result.stderr)
        raise RuntimeError("La transformation dbt a échoué.")
    context.log.info(result.stdout)
    return {"status": "success", "command": "dbt build"}
