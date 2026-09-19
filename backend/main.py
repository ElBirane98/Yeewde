from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from backend.database import get_connection
from ml_engine.config import DUCKDB_PATH
from ml_engine.drift_monitor import load_drift_report
from ml_engine.explainability import explain_po, global_feature_importance
from ml_engine.predict import predict_po
from monitoring.pipeline_health import pipeline_health
from rag_engine.query import ask_rag_engine

app = FastAPI(title="Yeewde AI API", version="1.0.0")
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    question: str


class SimulateRequest(BaseModel):
    po_id: str
    new_lead_time: int | None = Field(default=None, ge=1, le=365)
    new_supplier_id: str | None = None
    new_quantity: int | None = Field(default=None, ge=1)


@app.get("/health")
def health() -> dict[str, Any]:
    if not DUCKDB_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base DuckDB introuvable.",
        )
    return {"status": "ok", "database": str(DUCKDB_PATH), "duckdb_exists": True}


@app.get("/health/pipeline")
def health_pipeline() -> dict[str, Any]:
    return pipeline_health()


@app.get("/kpi/otif")
def kpi_otif() -> dict[str, Any]:
    try:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    AVG(otif_score) AS global_otif,
                    AVG(CASE WHEN is_on_time THEN 1.0 ELSE 0.0 END) AS on_time_rate,
                    AVG(CASE WHEN is_in_full THEN 1.0 ELSE 0.0 END) AS in_full_rate,
                    COUNT(*) AS total_orders
                FROM gold.marts_otif_kpi
                WHERE otif_score IS NOT NULL
                """
            ).fetchone()
            supplier_rows = conn.execute(
                """
                  SELECT supplier_id, supplier_risk_class, otif_rate,
                      avg_delay_days, total_incidents, critical_incidents,
                      total_orders
                FROM gold.marts_supplier_kpi
                ORDER BY otif_rate ASC NULLS LAST, supplier_id
                """
            ).fetchall()
    except Exception as exc:
        logger.exception("Lecture KPI impossible")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Les KPI ne sont pas disponibles. Exécutez le pipeline dbt.",
        ) from exc

    return {
        "global_otif": round(float(row[0] or 0), 4),
        "on_time_rate": round(float(row[1] or 0), 4),
        "in_full_rate": round(float(row[2] or 0), 4),
        "total_orders": int(row[3] or 0),
        "by_supplier": [
            {
                "supplier_id": supplier_id,
                "supplier_risk_class": risk_class,
                "otif_rate": round(float(otif_rate or 0), 4),
                "avg_delay_days": round(float(avg_delay_days or 0), 2),
                "total_incidents": int(total_incidents or 0),
                "critical_incidents": int(critical_incidents or 0),
                "total_orders": int(total_orders or 0),
            }
            for (
                supplier_id,
                risk_class,
                otif_rate,
                avg_delay_days,
                total_incidents,
                critical_incidents,
                total_orders,
            ) in supplier_rows
        ],
    }


@app.get("/predict/{po_id}")
def predict(po_id: str) -> dict[str, Any]:
    try:
        result = predict_po(po_id)
    except Exception as exc:
        logger.exception("Prédiction impossible pour %s", po_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le modèle de prédiction est indisponible.",
        ) from exc
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@app.get("/explain/{po_id}")
def explain(po_id: str) -> dict[str, Any]:
    try:
        payload = explain_po(po_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle ML indisponible.",
        ) from exc
    if payload.get("error"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=payload["error"])
    return payload


@app.get("/model/importance")
def model_importance() -> dict[str, Any]:
    try:
        return {"features": global_feature_importance()}
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle ML indisponible.",
        ) from exc


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    question = (request.question or "").strip()
    if not question:
        return {"answer": "Merci de poser une question valide."}

    try:
        return {"answer": ask_rag_engine(question)}
    except Exception as exc:
        logger.exception("Question RAG impossible")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le service RAG est indisponible.",
        ) from exc


@app.post("/simulate")
def simulate(request: SimulateRequest) -> dict[str, Any]:
    try:
        from erp_simulator.po_simulator import simulate_po_impact

        return simulate_po_impact(
            request.po_id.strip(),
            new_lead_time=request.new_lead_time,
            new_supplier_id=request.new_supplier_id,
            new_quantity=request.new_quantity,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle ou base indisponible pour la simulation.",
        ) from exc
    except Exception as exc:
        logger.exception("Simulation impossible")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La simulation What-If a échoué.",
        ) from exc


@app.get("/drift/status")
def drift_status() -> dict[str, Any]:
    return load_drift_report()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
