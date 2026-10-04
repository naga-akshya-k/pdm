"""
Unified Industrial Predictive Maintenance Pipeline.
Coordinates data validation, time-series storage, sliding windowing,
feature engineering, anomaly detection, fault diagnosis, health index,
RUL estimation, drift monitoring, and explainable maintenance recommendations.
"""

import time
import datetime
import logging
from typing import Dict, Any, List, Optional

from backend.data.storage import TimeSeriesStorage
from backend.features.window_buffer import MachineWindowBuffer
from backend.models.anomaly import IndustrialAnomalyDetector
from backend.models.diagnosis import IndustrialFaultDiagnostician
from backend.models.health import IndustrialHealthEvaluator
from backend.models.rul import IndustrialRULEngine
from backend.monitoring.drift import IndustrialDriftMonitor
from backend.maintenance.recommendation import MaintenanceRecommendationEngine
from backend.mlops.governance import MLOpsGovernanceEngine

logger = logging.getLogger("pdm.pipeline")

class PredictiveMaintenancePipeline:
    def __init__(
        self,
        storage: Optional[TimeSeriesStorage] = None,
        window_size: int = 10,
        models_dir: str = "models"
    ):
        self.storage = storage or TimeSeriesStorage()
        self.window_buffer = MachineWindowBuffer(window_size=window_size)
        self.anomaly_detector = IndustrialAnomalyDetector()
        self.fault_diagnostician = IndustrialFaultDiagnostician()
        self.health_evaluator = IndustrialHealthEvaluator()
        self.rul_engine = IndustrialRULEngine()
        self.drift_monitor = IndustrialDriftMonitor()
        self.recommendation_engine = MaintenanceRecommendationEngine()
        self.mlops_engine = MLOpsGovernanceEngine(models_dir=models_dir)

        # In-memory latest inference caches per machine: { machine_id: inference_dict }
        self.latest_inferences: Dict[str, Dict[str, Any]] = {}
        # In-memory recent records history per machine
        self.history_records: Dict[str, List[Dict[str, Any]]] = {}

    def process_telemetry_packet(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unified processing pipeline:
        Works identically for real MQTT, simulation, and historical replay.
        """
        machine_id = str(envelope.get("machine_id", "MCH-802X"))
        timestamp = envelope.get("timestamp", datetime.datetime.utcnow().isoformat() + "Z")
        features = envelope.get("features", {})
        is_simulation = envelope.get("is_simulation", False)
        is_replay = envelope.get("is_replay", False)
        data_source = "HISTORICAL REPLAY" if is_replay else ("SIMULATION" if is_simulation else "REAL INDUSTRIAL DATA")

        # 1. Store Raw Readings into Persistent Database
        raw_rows = [
            {
                "timestamp": timestamp,
                "machine_id": machine_id,
                "tag_id": tag,
                "sensor_type": feat,
                "value": val,
                "is_simulation": is_simulation,
                "quality": envelope.get("data_quality", "GOOD")
            }
            for feat, val in features.items()
            for tag in [feat]
        ]
        self.storage.insert_raw_telemetry(raw_rows)

        # 2. Append to Sliding Window Buffer
        self.window_buffer.append_sample(machine_id, timestamp, features)

        # 3. Extract Multivariate Engineered Features
        window_features = self.window_buffer.extract_window_features(machine_id)
        if not window_features:
            window_features = dict(features)

        # 4. Anomaly Detection (Isolation Forest + Multidimensional Z-Scores)
        anomaly_res = self.anomaly_detector.evaluate_anomaly(window_features)

        # 5. Evidence-Backed Fault Diagnosis
        fault_res = self.fault_diagnostician.diagnose_condition(
            window_features,
            anomaly_res["anomaly_status"]
        )

        # 6. Machine Health Index & ISO 10816 Severity Standard
        health_res = self.health_evaluator.compute_health_index(
            window_features,
            anomaly_res["anomaly_score"],
            subcomponents=envelope.get("subcomponents")
        )

        # 7. Scientifically Honest RUL Estimation
        rul_res = self.rul_engine.estimate_rul(
            window_features,
            health_res["health_index"]
        )

        # 8. Explainable Maintenance Recommendation
        maint_rec = self.recommendation_engine.generate_recommendation(
            machine_id=machine_id,
            machine_name=envelope.get("machine_name", f"Asset {machine_id}"),
            health_info=health_res,
            anomaly_info=anomaly_res,
            fault_info=fault_res,
            rul_info=rul_res
        )

        # 9. Track and Evaluate Data Drift
        if machine_id not in self.history_records:
            self.history_records[machine_id] = []
        
        flat_record = dict(features)
        flat_record["timestamp"] = timestamp
        self.history_records[machine_id].append(flat_record)
        if len(self.history_records[machine_id]) > 500:
            self.history_records[machine_id].pop(0)

        drift_res = self.drift_monitor.evaluate_data_drift(self.history_records[machine_id])

        # 10. Assemble Consolidated Decision Snapshot
        inference_snapshot = {
            "machine_id": machine_id,
            "machine_name": envelope.get("machine_name", f"Asset {machine_id}"),
            "timestamp": timestamp,
            "data_source": data_source,
            "features": features,
            "window_features": window_features,
            "health_score": health_res["health_index"],
            "machine_status": health_res["status"],
            "iso_10816": health_res["iso_10816"],
            "subcomponents": health_res["subcomponents"],
            "anomaly_score": anomaly_res["anomaly_score"],
            "anomaly_status": anomaly_res["anomaly_status"],
            "contributing_sensors": anomaly_res["contributing_sensors"],
            "fault_diagnosis": fault_res["detected_fault"],
            "fault_category": fault_res["fault_category"],
            "confidence": fault_res["confidence"],
            "fault_evidence": fault_res["evidence"],
            "estimated_rul": rul_res["estimated_rul_days"],
            "rul_lower": rul_res["rul_interval_lower"],
            "rul_upper": rul_res["rul_interval_upper"],
            "rul_confidence": rul_res["confidence"],
            "rul_calibrated": rul_res["rul_calibrated"],
            "rul_advisory": rul_res["advisory_note"],
            "maintenance_recommendation": maint_rec,
            "data_drift": drift_res,
            "mlops": {
                "active_version": self.mlops_engine.active_version,
                "model_algorithm": self.mlops_engine.registry.get(self.mlops_engine.active_version, {}).get("algorithm", "Random Forest")
            }
        }

        # 11. Persist to Storage & Memory Cache
        self.storage.insert_inference(inference_snapshot)
        self.latest_inferences[machine_id] = inference_snapshot

        return inference_snapshot

    def get_latest_inference(self, machine_id: str) -> Optional[Dict[str, Any]]:
        return self.latest_inferences.get(machine_id)
