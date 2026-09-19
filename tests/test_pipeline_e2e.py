from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_end_to_end_smoke():
    health = client.get("/health")
    assert health.status_code == 200

    kpi = client.get("/kpi/otif")
    assert kpi.status_code == 200

    predict = client.get("/predict/PO-TEST-1")
    assert predict.status_code == 404

    drift = client.get("/drift/status")
    assert drift.status_code == 200
    assert "drift_detected" in drift.json()

    pipeline = client.get("/health/pipeline")
    assert pipeline.status_code == 200
    pipeline_payload = pipeline.json()
    assert "healthy" in pipeline_payload
    assert "checks" in pipeline_payload
    assert "data_health" in pipeline_payload
    assert "model_health" in pipeline_payload
    assert "rag_health" in pipeline_payload
