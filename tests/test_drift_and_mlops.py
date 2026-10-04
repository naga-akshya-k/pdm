"""
Unit Tests for Drift Monitoring and MLOps Continuous Improvement Governance.
"""

import numpy as np
from backend.monitoring.drift import IndustrialDriftMonitor
from backend.mlops.governance import MLOpsGovernanceEngine

def test_drift_monitor_stable():
    np.random.seed(42)
    monitor = IndustrialDriftMonitor()
    # Baseline nominal samples drawn from the baseline distribution
    stable_samples = [
        {"Temperature": float(62.0 + np.random.normal(0, 0.8)), "Vibration": float(0.20 + np.random.normal(0, 0.03))}
        for _ in range(50)
    ]
    res = monitor.evaluate_data_drift(stable_samples)
    assert res["data_drift_detected"] is False

def test_drift_monitor_significant():
    monitor = IndustrialDriftMonitor()
    # Drastic distribution shift
    drift_samples = [
        {"Temperature": float(95.0 + np.random.normal(0, 1.0)), "Vibration": float(2.2 + np.random.normal(0, 0.1))}
        for _ in range(40)
    ]
    res = monitor.evaluate_data_drift(drift_samples)
    assert res["data_drift_detected"] is True
    assert len(res["drifted_features"]) >= 1

def test_mlops_candidate_training_and_approval():
    mlops = MLOpsGovernanceEngine(models_dir="models", registry_file="models/test_registry.json")
    # 1. Train candidate
    candidate = mlops.train_candidate_model(algorithm="Gradient Boosting")
    assert candidate["status"] == "WAITING_FOR_ENGINEER_APPROVAL"
    cand_version = candidate["version"]

    # 2. Candidate cannot be active before approval
    assert mlops.active_version != cand_version

    # 3. Engineer approval gate
    approval = mlops.approve_candidate(cand_version, approver_name="Senior Reliability Engineer", notes="Verified on bench")
    assert approval["status"] == "success"
    assert mlops.active_version == cand_version

    # 4. Rollback
    rollback = mlops.rollback_version("v1.0", engineer_name="Plant Operations Lead")
    assert rollback["status"] == "success"
    assert mlops.active_version == "v1.0"
