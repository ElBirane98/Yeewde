from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_kpi_endpoint():
    response = client.get("/kpi/otif")
    assert response.status_code == 200
    payload = response.json()
    assert "global_otif" in payload
    assert "by_supplier" in payload
    if payload["by_supplier"]:
        supplier = payload["by_supplier"][0]
        assert {
            "supplier_risk_class",
            "avg_delay_days",
            "total_incidents",
            "critical_incidents",
        }.issubset(supplier)


def test_predict_endpoint_returns_not_found_for_unknown_po():
    response = client.get("/predict/PO-UNKNOWN-1")
    assert response.status_code == 404
    payload = response.json()
    assert "introuvable" in payload["detail"]
