"""
Enterprise Industrial Predictive Maintenance Platform (PdM v3).
FastAPI Backend Orchestrator & Central Time-Series Processing Gateway.
"""

import sys
import os
import asyncio
import logging
import datetime
import time
from typing import Optional, Dict, Any, List
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Ensure project modules are discoverable
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.append(base_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdm.main")

from backend.data.storage import TimeSeriesStorage
from backend.pipeline import PredictiveMaintenancePipeline
from backend.ingestion.mqtt_consumer import IndustrialMQTTConsumer
from backend.ingestion.replay import HistoricalTelemetryReplayer
from simulator.industrial_simulator import FleetSimulatorManager, FLEET_CONFIGS

app = FastAPI(
    title="Industrial Predictive Maintenance Platform (PdM v3)",
    description="Real-Time Time-Series Ingestion, Anomaly Detection, Evidence-Backed Diagnosis, and MLOps Governance.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Platform Singletons
storage = TimeSeriesStorage()
pipeline = PredictiveMaintenancePipeline(storage=storage)
fleet_manager = FleetSimulatorManager()

mqtt_consumer = IndustrialMQTTConsumer(
    broker_host=os.getenv("MQTT_BROKER_HOST", "127.0.0.1"),
    broker_port=int(os.getenv("MQTT_BROKER_PORT", "1883")),
    topic="plant/bay4/+/telemetry",
    pipeline_callback=pipeline.process_telemetry_packet
)

replayer = HistoricalTelemetryReplayer(
    csv_path=os.path.join(base_dir, "datasets", "sensor_data.csv"),
    ingest_callback=mqtt_consumer.process_incoming_packet
)

class AppState:
    def __init__(self):
        self.auto_play = False  # Keep simulation paused until operator explicitly clicks Resume
        self.simulation_speed = 1.0
        self.selected_machine_id = "MCH-802X"

app_state = AppState()

def tick_simulation_machine(m_id: str):
    """Generates next physics step and injects as standard telemetry packet into the pipeline."""
    sim = fleet_manager.simulators.get(m_id)
    if not sim:
        return
    raw_step = sim.step()
    packet = {
        "machine_id": m_id,
        "machine_name": sim.config["name"],
        "timestamp": raw_step["Timestamp"],
        "is_simulation": True,
        "is_replay": False,
        "tags": {
            "TURB_MTR_DE_VIB_RMS": raw_step["Vibration"],
            "TURB_MTR_VIB_FREQ_01": raw_step["Frequency"],
            "TURB_MTR_STATOR_TEMP": raw_step["Temperature"],
            "TURB_MTR_PHASE_CURRENT": raw_step["Motor_Current"],
            "TURB_MTR_ACOUSTIC_DB": raw_step["Acoustic_Noise"],
            "TURB_MTR_LUBE_OIL_PRES": raw_step["Pressure"],
            "TURB_MTR_SHAFT_SPEED": raw_step["RPM"],
            "TURB_MTR_KW_LOAD": raw_step["Load"],
        },
        "subcomponents": raw_step.get("Subcomponents")
    }
    mqtt_consumer.process_incoming_packet(packet)

# Seed initial baseline steps
for m_id in FLEET_CONFIGS:
    tick_simulation_machine(m_id)

async def background_simulation_loop():
    """Background clock loop for simulated machine telemetry."""
    while True:
        try:
            watchdog_status = mqtt_consumer.watchdog.get_status()
            # Simulation NEVER runs while receiving real industrial packets
            if watchdog_status["current_mode"] == "REAL INDUSTRIAL DATA" and watchdog_status["is_stream_live"]:
                app_state.auto_play = False  # Freeze simulation during live ingress
            else:
                if app_state.auto_play and not replayer.is_replaying:
                    for m_id in FLEET_CONFIGS:
                        tick_simulation_machine(m_id)
            sleep_sec = max(0.05, float(app_state.simulation_speed))
            await asyncio.sleep(sleep_sec)
        except Exception as e:
            logger.error(f"Error in background_simulation_loop: {e}", exc_info=True)
            await asyncio.sleep(1.0)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(background_simulation_loop())
    mqtt_consumer.start()

@app.on_event("shutdown")
def on_shutdown():
    mqtt_consumer.stop()
    replayer.stop_replay()

# ==========================================
# SYSTEM & MQTT APIS
# ==========================================

@app.get("/api/system/status")
@app.get("/api/status")
def get_system_status():
    watchdog_st = mqtt_consumer.watchdog.get_status()
    latest = pipeline.get_latest_inference(app_state.selected_machine_id)
    return {
        "status": "online",
        "app_version": "3.0.0",
        "active_machine_id": app_state.selected_machine_id,
        "operating_mode": watchdog_st["current_mode"],
        "data_source": watchdog_st["current_mode"],
        "mqtt_connected": mqtt_consumer.is_connected,
        "mqtt_stream_live": watchdog_st["is_stream_live"],
        "real_telemetry_offline_alarm": watchdog_st["real_telemetry_offline_alarm"],
        "alarm_message": watchdog_st["alarm_message"],
        "active_ai_model": pipeline.mlops_engine.registry.get(pipeline.mlops_engine.active_version, {}).get("algorithm", "Random Forest"),
        "model_version": pipeline.mlops_engine.active_version,
        "current_time": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "health_score": latest["health_score"] if latest else 100.0,
        "anomaly_status": latest["anomaly_status"] if latest else "NORMAL"
    }

@app.get("/api/mqtt/status")
def get_mqtt_status():
    return mqtt_consumer.get_status()

@app.post("/api/mqtt/inject")
def inject_mqtt_payload(payload: Dict[str, Any]):
    res = mqtt_consumer.process_incoming_packet(payload)
    return {"status": "success", "packet": res}

class MQTTConfigRequest(BaseModel):
    broker_host: Optional[str] = None
    broker_port: Optional[int] = 1883
    topic: Optional[str] = None

@app.post("/api/mqtt/config")
def update_mqtt_config(req: MQTTConfigRequest):
    mqtt_consumer.stop()
    if req.broker_host:
        mqtt_consumer.broker_host = req.broker_host.strip()
    if req.broker_port:
        mqtt_consumer.broker_port = int(req.broker_port)
    if req.topic:
        mqtt_consumer.topic = req.topic.strip()
    mqtt_consumer.start()
    return {"status": "success", "config": mqtt_consumer.get_status()}

# ==========================================
# FLEET & MACHINE ASSET APIS
# ==========================================

@app.get("/api/machines")
@app.get("/api/fleet/overview")
def get_fleet_machines():
    fleet_summary = []
    for m_id, cfg in FLEET_CONFIGS.items():
        latest = pipeline.get_latest_inference(m_id)
        fleet_summary.append({
            "machine_id": m_id,
            "name": cfg["name"],
            "type": cfg["type"],
            "location": cfg["location"],
            "health": latest["health_score"] if latest else 100.0,
            "status": latest["machine_status"] if latest else "Healthy",
            "anomaly_status": latest["anomaly_status"] if latest else "NORMAL",
            "anomaly_score": latest["anomaly_score"] if latest else 0.0,
            "rul_days": latest["estimated_rul"] if latest else 300,
            "is_active": (m_id == app_state.selected_machine_id)
        })
    return {"fleet": fleet_summary, "active_machine_id": app_state.selected_machine_id}

class SelectMachineReq(BaseModel):
    machine_id: str

@app.post("/api/fleet/select")
def select_machine(req: SelectMachineReq):
    if req.machine_id in FLEET_CONFIGS:
        app_state.selected_machine_id = req.machine_id
        return {"status": "success", "active_machine_id": req.machine_id}
    raise HTTPException(status_code=404, detail="Machine not found in fleet.")

@app.get("/api/machines/{machine_id}")
def get_machine_detail(machine_id: str):
    if machine_id not in FLEET_CONFIGS:
        raise HTTPException(status_code=404, detail="Machine not found")
    cfg = FLEET_CONFIGS[machine_id]
    latest = pipeline.get_latest_inference(machine_id)
    return {"config": cfg, "latest": latest}

@app.get("/api/machines/{machine_id}/telemetry")
@app.get("/api/current")
def get_current_telemetry(machine_id: Optional[str] = None, unit_system: str = "metric"):
    target_id = machine_id or app_state.selected_machine_id
    latest = pipeline.get_latest_inference(target_id)
    if not latest:
        tick_simulation_machine(target_id)
        latest = pipeline.get_latest_inference(target_id)

    cfg = FLEET_CONFIGS.get(target_id, FLEET_CONFIGS["MCH-802X"])
    feats = latest.get("features", {})
    watchdog_st = mqtt_consumer.watchdog.get_status()

    # Unit conversion if imperial requested
    temp = feats.get("Temperature", 62.0)
    vib = feats.get("Vibration", 0.20)
    pres = feats.get("Pressure", 4.5)
    temp_unit = "°C"
    vib_unit = "mm/s"
    pres_unit = "bar"

    if unit_system.lower() == "imperial":
        temp = round(temp * 1.8 + 32.0, 1)
        vib = round(vib / 25.4, 4)
        pres = round(pres * 14.5038, 1)
        temp_unit = "°F"
        vib_unit = "ips"
        pres_unit = "psi"

    return {
        "machine_id": target_id,
        "machine_name": cfg["name"],
        "machine_type": cfg["type"],
        "location": cfg["location"],
        "timestamp": latest["timestamp"],
        "data_source": latest["data_source"],
        "real_telemetry_offline_alarm": watchdog_st["real_telemetry_offline_alarm"],
        "temperature": temp,
        "vibration": vib,
        "motor_current": feats.get("Motor_Current", 8.0),
        "acoustic_noise": feats.get("Acoustic_Noise", 42.0),
        "pressure": pres,
        "rpm": feats.get("RPM", 3000.0),
        "frequency": feats.get("Frequency", 50.0),
        "load": feats.get("Load", 15.0),
        "units": {
            "temperature": temp_unit,
            "vibration": vib_unit,
            "motor_current": "A",
            "acoustic_noise": "dB",
            "pressure": pres_unit,
            "rpm": "RPM",
            "frequency": "Hz",
            "load": "%"
        },
        "machine_health": latest["health_score"],
        "machine_status": latest["machine_status"],
        "actual_rul_days": latest["estimated_rul"],
        "predicted_rul_days": latest["estimated_rul"],
        "rul_interval_lower": latest["rul_lower"],
        "rul_interval_upper": latest["rul_upper"],
        "rul_confidence": latest["rul_confidence"],
        "rul_calibrated": latest["rul_calibrated"],
        "rul_advisory": latest["rul_advisory"],
        "active_ai_model": latest["mlops"]["model_algorithm"],
        "model_version": latest["mlops"]["active_version"],
        "anomaly_score": latest["anomaly_score"],
        "anomaly_status": latest["anomaly_status"],
        "fault_diagnosis": latest["fault_diagnosis"],
        "fault_confidence": latest["confidence"],
        "fault_evidence": latest["fault_evidence"],
        "subcomponents": latest["subcomponents"],
        "maintenance_recommendation": latest["maintenance_recommendation"],
        "early_warning": {
            "early_warning_status": latest["machine_status"],
            "early_warning_level": "RED" if latest["anomaly_status"] == "CRITICAL" else ("AMBER" if latest["anomaly_status"] == "WARNING" else "GREEN"),
            "lead_time_to_failure_days": latest["estimated_rul"],
            "lead_time_to_failure_hours": latest["estimated_rul"] * 24,
            "iso_10816": latest["iso_10816"],
            "root_cause_attribution": latest["contributing_sensors"],
            "operator_action_checklist": [
                {"task": latest["maintenance_recommendation"]["recommended_action"], "urgency": latest["maintenance_recommendation"]["severity"]}
            ]
        },
        "auto_play": app_state.auto_play,
        "simulation_speed": app_state.simulation_speed,
        "mqtt_live": watchdog_st["is_stream_live"],
        "mqtt_delta_t_ms": mqtt_consumer.last_delta_t_ms
    }

@app.get("/api/machines/{machine_id}/history")
@app.get("/api/history")
def get_history(machine_id: Optional[str] = None):
    target_id = machine_id or app_state.selected_machine_id
    records = storage.get_recent_inferences(target_id, limit=60)
    flat_history = []
    for r in records:
        f = r["features"]
        flat_history.append({
            "Timestamp": r["timestamp"],
            "Temperature": f.get("Temperature", 62.0),
            "Vibration": f.get("Vibration", 0.20),
            "Motor_Current": f.get("Motor_Current", 8.0),
            "Acoustic_Noise": f.get("Acoustic_Noise", 42.0),
            "Pressure": f.get("Pressure", 4.5),
            "RPM": f.get("RPM", 3000.0),
            "Frequency": f.get("Frequency", 50.0),
            "Load": f.get("Load", 15.0),
            "Machine_Health": r["health_score"],
            "Predicted_RUL": r["estimated_rul"],
            "Anomaly_Score": r["anomaly_score"],
            "Machine_Status": r["anomaly_status"]
        })
    return flat_history

@app.get("/api/logs")
def get_logs(unit_system: str = "metric"):
    latest = pipeline.get_latest_inference(app_state.selected_machine_id)
    return {"logs": [latest] if latest else []}

@app.get("/api/tags/live")
def get_live_tags():
    latest = pipeline.get_latest_inference(app_state.selected_machine_id)
    feats = latest.get("features", {}) if latest else {}
    watchdog_st = mqtt_consumer.watchdog.get_status()
    from backend.ingestion.tag_mapper import IndustrialTagMapper
    mapper = IndustrialTagMapper()
    tag_list = []
    
    # Baselines for normal ranges
    cfg = FLEET_CONFIGS.get(app_state.selected_machine_id, FLEET_CONFIGS["MCH-802X"])
    baselines = cfg.get("baselines", {})
    
    # Sensible operational standard margins for each feature
    norm_ranges = {
        "Vibration": (0.0, 1.8),
        "Frequency": (48.0, 52.0),
        "Temperature": (40.0, 80.0),
        "Motor_Current": (5.0, 15.0),
        "Acoustic_Noise": (35.0, 65.0),
        "Pressure": (3.5, 5.5),
        "RPM": (2850.0, 3150.0),
        "Load": (10.0, 85.0),
    }

    now_ts = time.time()
    for tag_id, meta in mapper.tags.items():
        feat = meta["feature_name"]
        val = feats.get(feat, 0.0)
        norm_min, norm_max = norm_ranges.get(feat, (meta.get("valid_min", 0.0), meta.get("valid_max", 100.0)))
        
        # Check if this specific tag was received recently (within 3.0s window)
        tag_ts = mqtt_consumer.tag_last_arrival.get(tag_id) or mqtt_consumer.tag_last_arrival.get(feat)
        is_tag_active = False
        if tag_ts is not None and (now_ts - tag_ts) <= 3.0 and watchdog_st["is_stream_live"]:
            is_tag_active = True

        tag_list.append({
            "tag_id": tag_id,
            "feature_name": feat,
            "description": meta.get("description", feat),
            "unit": meta.get("unit", ""),
            "current_value": val,
            "valid_min": meta.get("valid_min", 0.0),
            "valid_max": meta.get("valid_max", 100.0),
            "normal_min": norm_min,
            "normal_max": norm_max,
            "crit_threshold": meta.get("iso_alert_threshold"),
            "is_active_streaming": is_tag_active,
            "source": latest.get("data_source", "SIMULATION") if latest else "SIMULATION"
        })
    return {
        "machine_id": app_state.selected_machine_id,
        "total_tags": len(tag_list),
        "mqtt_live": watchdog_st["is_stream_live"],
        "mqtt_delta_t_ms": mqtt_consumer.last_delta_t_ms,
        "tags": tag_list
    }

# ==========================================
# DIAGNOSTICS, DRIFT & MAINTENANCE APIS
# ==========================================

@app.get("/api/early_warning")
def get_early_warning():
    latest = pipeline.get_latest_inference(app_state.selected_machine_id)
    if not latest:
        return {}
    return {
        "early_warning": {
            "early_warning_status": latest["machine_status"],
            "early_warning_level": "RED" if latest["anomaly_status"] == "CRITICAL" else ("AMBER" if latest["anomaly_status"] == "WARNING" else "GREEN"),
            "lead_time_to_failure_days": latest["estimated_rul"],
            "lead_time_to_failure_hours": latest["estimated_rul"] * 24,
            "iso_10816": latest["iso_10816"],
            "root_cause_attribution": latest["contributing_sensors"],
            "operator_action_checklist": [
                {"task": latest["maintenance_recommendation"]["recommended_action"], "urgency": latest["maintenance_recommendation"]["severity"]}
            ]
        }
    }

@app.get("/api/machines/{machine_id}/maintenance")
@app.get("/api/maintenance")
def get_maintenance_view(machine_id: Optional[str] = None):
    target_id = machine_id or app_state.selected_machine_id
    latest = pipeline.get_latest_inference(target_id)
    if not latest:
        return {}
    rec = latest["maintenance_recommendation"]
    return {
        "machine_id": target_id,
        "predicted_rul_days": latest["estimated_rul"],
        "machine_health": latest["health_score"],
        "maintenance_status": rec["severity"],
        "recommended_action": rec["recommended_action"],
        "inspection_priority": rec["priority"],
        "next_inspection_window": rec["suggested_timeframe"],
        "detected_issue": rec["detected_issue"],
        "evidence": rec["evidence"],
        "confidence": rec["confidence"],
        "action_type": rec["severity"],
        "critical_subcomponents": [k for k, v in latest.get("subcomponents", {}).items() if v < 50.0],
        "financial_analysis": {
            "estimated_unplanned_downtime_loss_usd": 35000 if rec["severity"] in ["CRITICAL", "HIGH"] else 5000,
            "estimated_preventive_servicing_cost_usd": 3200,
            "net_roi_savings_usd": 31800 if rec["severity"] in ["CRITICAL", "HIGH"] else 1800
        }
    }

@app.get("/api/machines/{machine_id}/drift")
@app.get("/api/drift/status")
def get_drift_status(machine_id: Optional[str] = None):
    target_id = machine_id or app_state.selected_machine_id
    latest = pipeline.get_latest_inference(target_id)
    drift = latest.get("data_drift", {}) if latest else {}
    perf = pipeline.drift_monitor.get_performance_drift_summary()
    return {
        "drift_detected": drift.get("data_drift_detected", False),
        "overall_psi": drift.get("overall_psi", 0.04),
        "drifted_features": drift.get("drifted_features", []),
        "features": drift.get("feature_metrics", {}),
        "performance_drift": perf,
        "status": drift.get("status", "STABLE")
    }

@app.post("/api/drift/recalibrate")
def recalibrate_drift():
    # Recalibrates baseline to recent data
    recs = pipeline.history_records.get(app_state.selected_machine_id, [])
    if recs:
        base_dict = {}
        for feat in ["Temperature", "Vibration", "Motor_Current", "Acoustic_Noise", "Pressure", "RPM", "Frequency", "Load"]:
            vals = [float(r[feat]) for r in recs if feat in r]
            if len(vals) >= 10:
                import numpy as np
                base_dict[feat] = np.array(vals)
        if base_dict:
            pipeline.drift_monitor._init_baseline(base_dict)
    return {"status": "success", "message": "Baseline distributions recalibrated to recent operating telemetry."}

# ==========================================
# MLOPS & MODEL GOVERNANCE APIS
# ==========================================

@app.get("/api/models")
@app.get("/api/models/benchmark")
@app.get("/api/regenerative/status")
def get_models_overview():
    mlops_st = pipeline.mlops_engine.get_status()
    prod_m = mlops_st.get("production_model", {})
    cand_m = mlops_st.get("candidate_model", {})
    
    # Format for UI Leaderboard & Governance
    benchmarks = {
        "Random Forest": {
            "name": "Random Forest Regressor",
            "type": "Ensemble Decision Forest",
            "mae": prod_m.get("metrics", {}).get("mae", 28.5),
            "rmse": prod_m.get("metrics", {}).get("rmse", 39.2),
            "r2_score": prod_m.get("metrics", {}).get("r2_score", 0.865),
            "inference_latency_ms": 1.2,
            "status": prod_m.get("status", "PRODUCTION")
        },
        "Gradient Boosting": {
            "name": "Gradient Boosting Regressor",
            "type": "Sequential Boosting Ensemble",
            "mae": cand_m.get("metrics", {}).get("mae", 24.1) if cand_m else 26.2,
            "rmse": cand_m.get("metrics", {}).get("rmse", 34.8) if cand_m else 36.5,
            "r2_score": cand_m.get("metrics", {}).get("r2_score", 0.892) if cand_m else 0.880,
            "inference_latency_ms": 1.8,
            "status": cand_m.get("status", "CANDIDATE") if cand_m else "BENCHMARK"
        }
    }
    return {
        "active_model_name": prod_m.get("algorithm", "Random Forest"),
        "model_version": pipeline.mlops_engine.active_version,
        "models": benchmarks,
        "mlops": mlops_st,
        "pipeline_state": "WAITING_FOR_ENGINEER_APPROVAL" if pipeline.mlops_engine.candidate_version else "IDLE",
        "current_version": pipeline.mlops_engine.active_version,
        "candidate_version": pipeline.mlops_engine.candidate_version,
        "candidate_benchmarks": benchmarks,
        "version_history": pipeline.mlops_engine.registry
    }

class RetrainRequest(BaseModel):
    algorithm: Optional[str] = "Gradient Boosting"

@app.post("/api/mlops/retrain")
@app.post("/api/retraining/start")
@app.post("/api/regenerative/retrain")
def trigger_retraining(req: Optional[RetrainRequest] = None):
    algo = req.algorithm if req and req.algorithm else "Gradient Boosting"
    cand = pipeline.mlops_engine.train_candidate_model(
        algorithm=algo,
        operational_records=pipeline.history_records.get(app_state.selected_machine_id)
    )
    return {"status": "success", "candidate": cand}

class ApproveRequest(BaseModel):
    candidate_name: Optional[str] = None
    approver_name: Optional[str] = "Lead Reliability Engineer"
    notes: Optional[str] = "Approved after drift review and validation"

@app.post("/api/models/{version}/approve")
@app.post("/api/regenerative/deploy")
def approve_model(version: Optional[str] = None, req: Optional[ApproveRequest] = None):
    target_version = version or (req.candidate_name if req else None) or pipeline.mlops_engine.candidate_version
    if not target_version:
        raise HTTPException(status_code=400, detail="No candidate version specified for approval.")
    approver = req.approver_name if req and req.approver_name else "Reliability Engineer"
    notes = req.notes if req and req.notes else ""
    res = pipeline.mlops_engine.approve_candidate(target_version, approver, notes)
    return res

@app.post("/api/models/{version}/rollback")
def rollback_model(version: str):
    return pipeline.mlops_engine.rollback_version(version, engineer_name="Plant Operations Lead")

# ==========================================
# SIMULATION & REPLAY APIS
# ==========================================

class ControlRequest(BaseModel):
    action: str  # play | pause | reset | step
    speed: Optional[float] = 1.0

@app.post("/api/control")
def control_simulation(req: ControlRequest):
    if req.action == "play":
        app_state.auto_play = True
    elif req.action == "pause":
        app_state.auto_play = False
    elif req.action == "step":
        tick_simulation_machine(app_state.selected_machine_id)
    elif req.action == "reset":
        sim = fleet_manager.get_active_simulator()
        sim.reset()
        tick_simulation_machine(app_state.selected_machine_id)
    if req.speed is not None:
        app_state.simulation_speed = max(0.05, float(req.speed))
    return {"status": "success", "auto_play": app_state.auto_play, "simulation_speed": app_state.simulation_speed}

@app.post("/api/simulation/start")
def start_simulation():
    app_state.auto_play = True
    return {"status": "success", "auto_play": True}

@app.post("/api/simulation/stop")
def stop_simulation():
    app_state.auto_play = False
    return {"status": "success", "auto_play": False}

class ReplayRequest(BaseModel):
    speed: Optional[float] = 1.0

@app.post("/api/simulation/replay")
def trigger_replay(req: Optional[ReplayRequest] = None):
    speed = req.speed if req and req.speed else 1.0
    replayer.start_replay(speed=speed)
    return {"status": "success", "replayer": replayer.get_status()}

class FaultInjectRequest(BaseModel):
    fault_type: str
    duration_steps: Optional[int] = 30
    machine_id: Optional[str] = None

@app.post("/api/simulator/fault")
def inject_fault(req: FaultInjectRequest):
    target_id = req.machine_id or app_state.selected_machine_id
    sim = fleet_manager.simulators.get(target_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Machine not found")
    sim.inject_fault(req.fault_type, duration_steps=req.duration_steps)
    return {"status": "success", "active_fault": sim.active_fault}

@app.post("/api/simulator/clear_fault")
def clear_fault(req: Optional[Dict[str, Any]] = None):
    sim = fleet_manager.get_active_simulator()
    sim.active_fault = "None"
    sim.active_event = "None"
    return {"status": "success"}

# Legacy CMMS endpoint compatibility
@app.get("/api/cmms/work_orders")
def get_work_orders_compat():
    latest = pipeline.get_latest_inference(app_state.selected_machine_id)
    rec = latest.get("maintenance_recommendation", {}) if latest else {}
    return [{
        "order_id": f"REC-2026-{app_state.selected_machine_id}",
        "machine_id": app_state.selected_machine_id,
        "machine_name": FLEET_CONFIGS.get(app_state.selected_machine_id, {}).get("name", "Machine"),
        "status": "OPEN",
        "priority": rec.get("priority", "Moderate"),
        "maintenance_type": "Condition Monitoring Inspection",
        "recommended_action": rec.get("recommended_action", "Routine monitoring"),
        "next_inspection_window": rec.get("suggested_timeframe", "Next turnaround"),
        "assigned_role": "Reliability Specialist",
        "estimated_duration_hours": 3,
        "required_parts": ["Diagnostic Inspection Kit"],
        "latest_health": latest.get("health_score", 100.0) if latest else 100.0,
        "predicted_rul_days": latest.get("estimated_rul", 300) if latest else 300,
        "financial_savings_usd": 15000
    }]

# Mount frontend production build if available
frontend_dist_dir = os.path.join(base_dir, "frontend", "dist")
if os.path.exists(frontend_dist_dir):
    assets_dir = os.path.join(frontend_dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        target = os.path.join(frontend_dist_dir, full_path)
        if full_path and os.path.exists(target) and os.path.isfile(target):
            return FileResponse(target)
        return FileResponse(os.path.join(frontend_dist_dir, "index.html"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
