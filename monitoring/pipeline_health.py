from __future__ import annotations

from pathlib import Path

from ml_engine.drift_monitor import load_drift_report
from rag_engine.logging import get_rag_stats


def pipeline_health() -> dict:
    root = Path(__file__).resolve().parent.parent
    checkpoints = {
        "data_dir": (root / "data").exists(),
        "duckdb": (root / "data" / "yeewde.duckdb").exists(),
        "model": (root / "mlruns" / "models" / "lgbm_otif.pkl").exists(),
        "dbt_project": (root / "dbt_yeewde" / "dbt_project.yml").exists(),
        "chroma_index": (root / "vector_db" / "chroma_data").exists(),
    }
    ok = all(checkpoints.values())
    return {
        "healthy": ok,
        "checks": checkpoints,
        "data_health": {
            "duckdb_ready": checkpoints["duckdb"],
            "dbt_project": checkpoints["dbt_project"],
        },
        "model_health": {
            "model_present": checkpoints["model"],
            "drift": load_drift_report(),
        },
        "rag_health": get_rag_stats(),
    }


if __name__ == "__main__":
    print(pipeline_health())
