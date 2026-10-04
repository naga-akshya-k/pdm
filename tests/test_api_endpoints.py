"""
Integration Tests for FastAPI Endpoints.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_system_status_endpoint():
    res = client.get("/api/system/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "operating_mode" in data
    assert "real_telemetry_offline_alarm" in data

def test_fleet_machines_endpoint():
    res = client.get("/api/machines")
    assert res.status_code == 200
    data = res.json()
    assert "fleet" in data
    assert len(data["fleet"]) >= 1

def test_current_telemetry_endpoint():
    res = client.get("/api/current")
    assert res.status_code == 200
    data = res.json()
    assert "machine_health" in data
    assert "anomaly_status" in data
    assert "fault_diagnosis" in data
    assert "maintenance_recommendation" in data
    assert "data_source" in data

def test_maintenance_recommendation_endpoint():
    res = client.get("/api/maintenance")
    assert res.status_code == 200
    data = res.json()
    assert "recommended_action" in data
    assert "evidence" in data
    assert "inspection_priority" in data

def test_mqtt_status_endpoint():
    res = client.get("/api/mqtt/status")
    assert res.status_code == 200
    data = res.json()
    assert "is_connected" in data
    assert "watchdog" in data

def test_live_tags_endpoint():
    res = client.get("/api/tags/live")
    assert res.status_code == 200
    data = res.json()
    assert "tags" in data
    assert len(data["tags"]) >= 1

def test_mlops_retrain_endpoint():
    res = client.post("/api/mlops/retrain", json={"algorithm": "Gradient Boosting"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["candidate"]["status"] == "WAITING_FOR_ENGINEER_APPROVAL"
