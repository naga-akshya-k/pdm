"""
Unit Tests for Anomaly Detection, Evidence-Backed Diagnosis, Health, and RUL.
"""

from backend.models.anomaly import IndustrialAnomalyDetector
from backend.models.diagnosis import IndustrialFaultDiagnostician
from backend.models.health import IndustrialHealthEvaluator
from backend.models.rul import IndustrialRULEngine

def test_anomaly_detection_nominal():
    detector = IndustrialAnomalyDetector()
    nominal_features = {
        "Temperature": 62.0, "Vibration": 0.20, "Motor_Current": 8.0,
        "Acoustic_Noise": 42.0, "Pressure": 4.5, "RPM": 3000.0,
        "Frequency": 50.0, "Load": 15.0
    }
    res = detector.evaluate_anomaly(nominal_features)
    assert res["anomaly_status"] == "NORMAL"
    assert res["anomaly_score"] < 0.50

def test_anomaly_detection_critical():
    detector = IndustrialAnomalyDetector()
    critical_features = {
        "Temperature": 98.0, "Vibration": 3.8, "Motor_Current": 24.0,
        "Acoustic_Noise": 89.0, "Pressure": 1.8, "RPM": 2800.0,
        "Frequency": 72.0, "Load": 110.0
    }
    res = detector.evaluate_anomaly(critical_features)
    assert res["anomaly_status"] == "CRITICAL"
    assert res["anomaly_score"] > 0.65

def test_evidence_backed_bearing_diagnosis():
    diag = IndustrialFaultDiagnostician()
    bearing_features = {
        "Temperature": 70.0,
        "Vibration": 1.45,         # > 0.8
        "Acoustic_Noise": 74.0,    # > 65.0
        "Vibration_kurtosis": 5.2, # > 4.5
        "Motor_Current": 9.0,
        "Pressure": 4.5,
        "RPM": 3000.0,
        "Frequency": 50.0
    }
    res = diag.diagnose_condition(bearing_features, anomaly_status="WARNING")
    assert "Bearing" in res["detected_fault"]
    assert len(res["evidence"]) >= 2
    assert res["confidence"] >= 0.80

def test_unconfirmed_anomaly_disclaimer():
    diag = IndustrialFaultDiagnostician()
    vague_anomaly_features = {
        "Temperature": 63.0,
        "Vibration": 0.22,
        "Acoustic_Noise": 43.0,
        "Motor_Current": 12.0,     # slight elevation alone
        "Pressure": 4.4,
        "RPM": 2980.0,
        "Frequency": 50.0
    }
    res = diag.diagnose_condition(vague_anomaly_features, anomaly_status="WARNING")
    assert "Root cause requires inspection" in res["detected_fault"]
    assert res["confidence"] <= 0.60

def test_iso_10816_severity_zones():
    evaluator = IndustrialHealthEvaluator()
    assert evaluator.evaluate_iso_10816(0.18)["zone"] == "Zone A"
    assert evaluator.evaluate_iso_10816(0.45)["zone"] == "Zone B"
    assert evaluator.evaluate_iso_10816(1.10)["zone"] == "Zone C"
    assert evaluator.evaluate_iso_10816(2.50)["zone"] == "Zone D"

def test_scientifically_honest_rul():
    rul_eng = IndustrialRULEngine()
    res = rul_eng.estimate_rul({"Vibration": 0.20, "Temperature": 62.0}, health_index=88.0)
    assert res["rul_interval_lower"] < res["estimated_rul_days"] < res["rul_interval_upper"]
    assert "confidence" in res
    assert "advisory_note" in res
