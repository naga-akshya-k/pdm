import sys
import os
import asyncio
import logging
import datetime
from typing import Optional, Dict, Any, List
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

# Ensure project modules are discoverable
base_dir = os.path.dirname(os.path.abspath(__file__))
for folder in ['simulator', 'preprocessing', 'model', 'utils', 'ingestion']:
    folder_path = os.path.join(base_dir, folder)
    if os.path.exists(folder_path) and folder_path not in sys.path:
        sys.path.append(folder_path)
if base_dir not in sys.path:
    sys.path.append(base_dir)

from industrial_simulator import FleetSimulatorManager, FLEET_CONFIGS
from candidate_models import MultiModelAIEngine, FEATURE_COLS
from drift_detector import IndustrialDriftDetector
from regenerative_ai import RegenerativeAIPipeline
from early_warning_engine import IndustrialEarlyWarningEngine
from unit_converter import normalize_industrial_payload, to_canonical_units, from_canonical_units
from maintenance_engine import get_maintenance_recommendation, auto_generate_cmms_work_order, get_all_work_orders, WORK_ORDERS
from predict import get_future_trend
from utils import get_status_color
from mqtt_listener import mqtt_listener
from tag_mapping import TURBINE_TAG_REGISTRY, FEATURE_TO_TAG_MAP

app = FastAPI(
    title="Enterprise Industrial Predictive Maintenance Platform",
    description="Digital Twin SCADA Telemetry, Multi-Model AI Inference, Real-Time Drift Detection, Regenerative AI Layer, and CMMS Work Order Dispatcher.",
    version="2.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
fleet_manager = FleetSimulatorManager()
ai_engine = MultiModelAIEngine()
drift_detector = IndustrialDriftDetector()
early_warning_engine = IndustrialEarlyWarningEngine()
regenerative_pipeline = RegenerativeAIPipeline(ai_engine, drift_detector)

class SimulationState:
    def __init__(self):
        self.auto_play = False
        self.simulation_speed = 1.0
        # Multi-machine historical records storage: {machine_id: [records...]}
        self.history_records = {m_id: [] for m_id in FLEET_CONFIGS}
        self.prev_smoothed_rul = {m_id: None for m_id in FLEET_CONFIGS}

sim_state = SimulationState()

def generate_next_telemetry_step(machine_id: Optional[str] = None):
    """
    Ticks the specified or active machine simulator, runs active AI model prediction,
    applies EMA smoothing, evaluates maintenance policies, and checks CMMS work orders.
    """
    if machine_id is None:
        machine_id = fleet_manager.active_machine_id

    sim = fleet_manager.simulators.get(machine_id, fleet_manager.get_active_simulator())
    record = sim.step()

    # Predict RUL with active AI model
    raw_pred_rul, latency_ms = ai_engine.predict_rul(record)
    prev_rul = sim_state.prev_smoothed_rul.get(machine_id)
    if prev_rul is None:
        smoothed_rul = float(raw_pred_rul)
    else:
        # EMA temporal smoothing for stable industrial countdown
        smoothed_rul = 0.35 * float(raw_pred_rul) + 0.65 * prev_rul
    sim_state.prev_smoothed_rul[machine_id] = smoothed_rul
    pred_rul = max(0, int(round(smoothed_rul)))

    # Maintenance Decision Recommendation
    maint_info = get_maintenance_recommendation(
        predicted_rul=pred_rul,
        machine_health=record["Machine_Health"],
        active_event=record["Active_Event"],
        subcomponents=record.get("Subcomponents"),
        machine_info=sim.config
    )

    # Early Failure Detection & P-F Analysis
    early_warn = early_warning_engine.evaluate_early_failure(record, sim.config)
    record["Early_Warning"] = early_warn

    record["Predicted_RUL"] = pred_rul
    record["Inference_Latency_MS"] = latency_ms
    record["Active_AI_Model"] = ai_engine.active_model_name
    record["Model_Version"] = ai_engine.model_version
    record["Maintenance_Status"] = maint_info["maintenance_status"]
    record["Recommended_Action"] = maint_info["recommended_action"]
    record["Inspection_Priority"] = maint_info["inspection_priority"]
    record["Next_Inspection_Window"] = maint_info["next_inspection_window"]
    record["Action_Type"] = maint_info["action_type"]
    record["Critical_Subcomponents"] = maint_info["critical_subcomponents"]
    record["Financial_Analysis"] = maint_info["financial_analysis"]

    # Auto-generate work order on critical or urgent degradation
    if maint_info["inspection_priority"] in ["Critical", "Urgent"] and sim.current_step % 5 == 0:
        auto_generate_cmms_work_order(machine_id, sim.config["name"], maint_info, record)

    # Append to history
    hist = sim_state.history_records[machine_id]
    hist.append(record)
    if len(hist) > 1000:
        hist.pop(0)

    return record

# Seed initial step for all fleet machines
for m_id in FLEET_CONFIGS:
    if not sim_state.history_records[m_id]:
        generate_next_telemetry_step(m_id)

async def simulation_clock_loop():
    """Backend clock loop ticking all fleet simulators when auto_play is active."""
    while True:
        try:
            if sim_state.auto_play:
                for m_id in FLEET_CONFIGS:
                    generate_next_telemetry_step(m_id)
                sleep_time = max(0.05, float(sim_state.simulation_speed))
                await asyncio.sleep(sleep_time)
            else:
                await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"Error in simulation_clock_loop: {e}", exc_info=True)
            await asyncio.sleep(0.5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_clock_loop())
    try:
        mqtt_listener.start()
    except Exception as e:
        logger.warning(f"MQTT Listener init error: {e}")

@app.on_event("shutdown")
def shutdown_event():
    try:
        mqtt_listener.stop()
    except Exception:
        pass

# ==========================================
# FLEET, MQTT & TELEMETRY ENDPOINTS
# ==========================================

@app.get("/api/mqtt/status")
def get_mqtt_status():
    """Returns live MQTT ingestion gateway telemetry, jitter, cadence, and active Tag IDs."""
    return mqtt_listener.get_status()

@app.post("/api/mqtt/inject")
def inject_mqtt_packet(payload: Dict[str, Any]):
    """Allows testing or simulating GPU telemetry packets via HTTP injection."""
    mqtt_listener.inject_payload(payload)
    return {"status": "success", "ingested": True, "listener_status": mqtt_listener.get_status()}

class MQTTConfigRequest(BaseModel):
    broker_host: Optional[str] = None
    broker_port: Optional[int] = 1883
    topic: Optional[str] = None

@app.post("/api/mqtt/config")
def set_mqtt_config(req: MQTTConfigRequest):
    """Dynamically updates MQTT Broker IP, port, and topic to connect to workstation GPU."""
    status = mqtt_listener.configure(req.broker_host, req.broker_port, req.topic)
    return {"status": "success", "config": status}

@app.get("/api/status")
def get_status():
    active_sim = fleet_manager.get_active_simulator()
    is_live_mqtt = mqtt_listener.is_stream_active() and fleet_manager.active_machine_id == "MCH-802X"
    return {
        "status": "online",
        "active_machine_id": fleet_manager.active_machine_id,
        "machine_name": active_sim.config["name"],
        "machine_type": active_sim.config["type"],
        "location": active_sim.config["location"],
        "data_source": "Workstation GPU via MQTT (Tag IDs)" if is_live_mqtt else "Physics-Based Digital Twin SCADA Simulation",
        "mqtt_connected": mqtt_listener.is_connected,
        "mqtt_stream_active": is_live_mqtt,
        "active_ai_model": ai_engine.active_model_name,
        "model_version": ai_engine.model_version,
        "current_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/fleet/overview")
def get_fleet_overview():
    return {
        "fleet": fleet_manager.get_fleet_summary(),
        "active_machine_id": fleet_manager.active_machine_id
    }

class SelectMachineRequest(BaseModel):
    machine_id: str

@app.post("/api/fleet/select")
def select_fleet_machine(req: SelectMachineRequest):
    res = fleet_manager.set_active_machine(req.machine_id)
    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    return res

@app.get("/api/current")
def get_current_telemetry(unit_system: str = "metric"):
    active_m_id = fleet_manager.active_machine_id
    hist = sim_state.history_records.get(active_m_id, [])
    if not hist:
        generate_next_telemetry_step(active_m_id)
        hist = sim_state.history_records[active_m_id]

    row = hist[-1]
    health = float(row.get("Machine_Health", 100.0))
    stage_text, stage_color = get_status_color(health)

    raw_temp = float(row.get("Temperature", 62.0))
    raw_vib = float(row.get("Vibration", 0.20))
    raw_curr = float(row.get("Motor_Current", 8.0))
    raw_noise = float(row.get("Acoustic_Noise", 42.0))
    raw_press = float(row.get("Pressure", 4.5))
    raw_rpm = float(row.get("RPM", 3000.0))
    raw_freq = float(row.get("Frequency", 50.0))
    raw_load = float(row.get("Load", 15.0))
    pred_rul = int(row.get("Predicted_RUL", 0))

    # Check if live workstation GPU telemetry is actively streaming via MQTT for MCH-802X
    is_live_mqtt = False
    mqtt_delta_t = None
    data_source_str = "Physics-Based Digital Twin SCADA Simulation"

    if mqtt_listener.is_stream_active() and active_m_id in [mqtt_listener.active_machine_id, "MCH-802X"] and active_m_id == "MCH-802X":
        live_stream = mqtt_listener.get_live_telemetry()
        if live_stream and "features" in live_stream:
            feats = live_stream["features"]
            raw_temp = float(feats.get("Temperature", 62.0))
            raw_vib = float(feats.get("Vibration", 0.20))
            raw_curr = float(feats.get("Motor_Current", 8.0))
            raw_noise = float(feats.get("Acoustic_Noise", 42.0))
            raw_press = float(feats.get("Pressure", 4.5))
            raw_rpm = float(feats.get("RPM", 3000.0))
            raw_freq = float(feats.get("Frequency", 50.0))
            raw_load = float(feats.get("Load", 15.0))
            
            # Real-time AI prediction on live workstation GPU features
            try:
                live_pred = ai_engine.predict_active([raw_temp, raw_vib, raw_curr, raw_noise, raw_press, raw_rpm, raw_freq, raw_load])
                pred_rul = live_pred.get("predicted_rul_days", pred_rul)
            except Exception:
                pass
                
            vib_deg = min(1.0, max(0.0, (raw_vib - 0.20) / 1.60))
            temp_deg = min(1.0, max(0.0, (raw_temp - 50.0) / 45.0))
            health = round(max(0.0, 100.0 * (1.0 - (0.70 * vib_deg + 0.30 * temp_deg))), 1)
            stage_text, stage_color = get_status_color(health)
            
            is_live_mqtt = True
            mqtt_delta_t = live_stream.get("last_delta_t_ms", 1000.0)
            data_source_str = f"Workstation GPU via MQTT ({mqtt_delta_t:.0f}ms)"

    unit_clean = unit_system.lower()
    if unit_clean == "imperial":
        display_temp = round(from_canonical_units("temperature", raw_temp, "F"), 2)
        display_vib = round(from_canonical_units("vibration", raw_vib, "in/s"), 3)
        display_press = round(from_canonical_units("pressure", raw_press, "psi"), 2)
        display_load = round(from_canonical_units("load", raw_load, "lbf"), 2)
        units = {
            "temperature": "°F", "vibration": "in/s", "motor_current": "A", "acoustic_noise": "dB",
            "pressure": "psi", "rpm": "RPM", "frequency": "Hz", "load": "lbf"
        }
    elif unit_clean == "normalized":
        # Pure Dimensionless Z-Score representation
        import pandas as pd
        z_scores = ai_engine.scaler.transform(pd.DataFrame([{
            "Temperature": raw_temp, "Vibration": raw_vib, "Motor_Current": raw_curr,
            "Acoustic_Noise": raw_noise, "Pressure": raw_press, "RPM": raw_rpm,
            "Frequency": raw_freq, "Load": raw_load
        }])[FEATURE_COLS])[0]
        display_temp = round(float(z_scores[0]), 2)
        display_vib = round(float(z_scores[1]), 2)
        raw_curr = round(float(z_scores[2]), 2)
        raw_noise = round(float(z_scores[3]), 2)
        display_press = round(float(z_scores[4]), 2)
        raw_rpm = round(float(z_scores[5]), 2)
        raw_freq = round(float(z_scores[6]), 2)
        display_load = round(float(z_scores[7]), 2)
        units = {
            "temperature": "Z-Score (σ)", "vibration": "Z-Score (σ)", "motor_current": "Z-Score (σ)",
            "acoustic_noise": "Z-Score (σ)", "pressure": "Z-Score (σ)", "rpm": "Z-Score (σ)",
            "frequency": "Z-Score (σ)", "load": "Z-Score (σ)"
        }
    else:
        # Standard Metric / SI
        display_temp = round(raw_temp, 2)
        display_vib = round(raw_vib, 3)
        display_press = round(raw_press, 2)
        display_load = round(raw_load, 2)
        units = {
            "temperature": "°C", "vibration": "mm/s", "motor_current": "A", "acoustic_noise": "dB",
            "pressure": "bar", "rpm": "RPM", "frequency": "Hz", "load": "kN"
        }

    return {
        "machine_id": active_m_id,
        "machine_name": row.get("Machine_Name", "Turbine Motor"),
        "machine_type": row.get("Machine_Type", "Gas Turbine"),
        "location": row.get("Location", "Bay 4"),
        "current_idx": len(hist) - 1,
        "total_records": len(hist),
        "timestamp": str(row.get("Timestamp", "")),
        "temperature": display_temp,
        "vibration": display_vib,
        "motor_current": round(raw_curr, 2),
        "acoustic_noise": round(raw_noise, 2),
        "pressure": display_press,
        "rpm": round(raw_rpm, 1),
        "frequency": round(raw_freq, 2),
        "load": display_load,
        "units": units,
        "unit_system": unit_clean,
        "machine_health": health,
        "machine_status": stage_text,
        "actual_rul_days": int(row.get("Remaining_Useful_Life_Days", 0)),
        "predicted_rul_days": pred_rul,
        "active_ai_model": row.get("Active_AI_Model", ai_engine.active_model_name),
        "inference_latency_ms": row.get("Inference_Latency_MS", 1.2),
        "model_version": row.get("Model_Version", "1.0"),
        "alert_status": row.get("Maintenance_Status", "Healthy"),
        "active_event": row.get("Active_Event", "None"),
        "active_fault": row.get("Active_Fault", "None"),
        "subcomponents": row.get("Subcomponents", {}),
        "early_warning": row.get("Early_Warning", {}),
        "auto_play": sim_state.auto_play,
        "simulation_speed": sim_state.simulation_speed,
        "data_source": data_source_str,
        "mqtt_live": is_live_mqtt,
        "mqtt_delta_t_ms": mqtt_delta_t
    }

@app.get("/api/early_warning")
def get_early_warning_analysis():
    active_m_id = fleet_manager.active_machine_id
    hist = sim_state.history_records.get(active_m_id, [])
    if not hist:
        generate_next_telemetry_step(active_m_id)
        hist = sim_state.history_records[active_m_id]
    row = hist[-1]
    sim = fleet_manager.get_active_simulator()
    return early_warning_engine.evaluate_early_failure(row, sim.config)

@app.get("/api/history")
def get_history_trends():
    active_m_id = fleet_manager.active_machine_id
    records = sim_state.history_records.get(active_m_id, []).copy()
    if not records:
        generate_next_telemetry_step(active_m_id)
        records = sim_state.history_records[active_m_id].copy()

    def make_trend(col):
        vals = [float(r.get(col, 0.0)) for r in records]
        if not vals:
            vals = [0.0]
        window = vals[-50:] if len(vals) > 50 else vals
        future_vals = get_future_trend(window, steps=20)
        return {"actual": vals, "predicted_future": future_vals}

    return {
        "machine_id": active_m_id,
        "records": records,
        "temperature_trend": make_trend("Temperature"),
        "vibration_trend": make_trend("Vibration"),
        "motor_current_trend": make_trend("Motor_Current"),
        "acoustic_noise_trend": make_trend("Acoustic_Noise"),
        "pressure_trend": make_trend("Pressure"),
        "rpm_trend": make_trend("RPM"),
        "frequency_trend": make_trend("Frequency"),
        "load_trend": make_trend("Load"),
        "machine_health_trend": make_trend("Machine_Health"),
        "rul_trend": make_trend("Predicted_RUL")
    }

# ==========================================
# DIGITAL TWIN FAULT INJECTION
# ==========================================

class FaultInjectionRequest(BaseModel):
    fault_type: str
    duration_steps: int = 25
    machine_id: Optional[str] = None

@app.post("/api/simulator/fault")
def inject_simulator_fault(req: FaultInjectionRequest):
    target_id = req.machine_id if req.machine_id else fleet_manager.active_machine_id
    sim = fleet_manager.simulators.get(target_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Machine not found")
    res = sim.inject_fault(req.fault_type, req.duration_steps)
    return res

class ClearFaultRequest(BaseModel):
    machine_id: Optional[str] = None

@app.post("/api/simulator/clear_fault")
def clear_simulator_fault(req: Optional[ClearFaultRequest] = None):
    target_id = req.machine_id if (req and req.machine_id) else fleet_manager.active_machine_id
    sim = fleet_manager.simulators.get(target_id)
    if sim:
        sim.clear_fault()
    return {"status": "success", "message": f"Cleared active faults on {target_id}"}

# ==========================================
# MULTI-MODEL BENCHMARK & HOT-SWAP
# ==========================================

@app.get("/api/models/benchmark")
def get_candidate_models_benchmark():
    return {
        "active_model": ai_engine.active_model_name,
        "model_version": ai_engine.model_version,
        "last_trained": ai_engine.last_trained_timestamp,
        "benchmarks": ai_engine.benchmarks
    }

class SelectModelRequest(BaseModel):
    model_name: str

@app.post("/api/models/select")
def set_active_inference_model(req: SelectModelRequest):
    res = ai_engine.set_active_model(req.model_name)
    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    return res

# ==========================================
# DATA DRIFT & RELIABILITY MONITORING
# ==========================================

@app.get("/api/drift/status")
def get_drift_status():
    active_m_id = fleet_manager.active_machine_id
    hist = sim_state.history_records.get(active_m_id, [])
    # Evaluate drift on recent 50 samples
    window = hist[-60:] if len(hist) > 60 else hist
    drift_result = drift_detector.evaluate_drift(window)
    drift_result["machine_id"] = active_m_id
    return drift_result

# ==========================================
# REGENERATIVE AI & GOVERNANCE LAYER
# ==========================================

@app.get("/api/regenerative/status")
def get_regenerative_status():
    return regenerative_pipeline.get_pipeline_status()

@app.post("/api/regenerative/retrain")
def trigger_regenerative_retraining():
    active_m_id = fleet_manager.active_machine_id
    hist = sim_state.history_records.get(active_m_id, [])
    res = regenerative_pipeline.trigger_retraining(hist)
    return res

class DeployCandidateRequest(BaseModel):
    candidate_name: str
    approver_name: str = "Lead Reliability Engineer"
    notes: Optional[str] = ""

@app.post("/api/regenerative/deploy")
def deploy_approved_candidate(req: DeployCandidateRequest):
    res = regenerative_pipeline.deploy_candidate_model(
        candidate_name=req.candidate_name,
        approver_name=req.approver_name,
        notes=req.notes or ""
    )
    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    return res

# ==========================================
# CMMS & MAINTENANCE WORK ORDERS
# ==========================================

@app.get("/api/cmms/work_orders")
def get_work_orders():
    return {"work_orders": get_all_work_orders()}

class CreateWorkOrderRequest(BaseModel):
    machine_id: str
    priority: str
    action: str
    assigned_role: str
    parts: List[str]

@app.post("/api/cmms/create_order")
def create_manual_work_order(req: CreateWorkOrderRequest):
    sim = fleet_manager.simulators.get(req.machine_id, fleet_manager.get_active_simulator())
    order = {
        "order_id": f"WO-{datetime.datetime.now().strftime('%Y%m')}-{os.urandom(2).hex().upper()}",
        "machine_id": req.machine_id,
        "machine_name": sim.config["name"],
        "status": "OPEN",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "priority": req.priority,
        "maintenance_type": "Manual Engineering Dispatch",
        "recommended_action": req.action,
        "next_inspection_window": "Inspect within 24-72 hours",
        "assigned_role": req.assigned_role,
        "estimated_duration_hours": 4,
        "required_parts": req.parts,
        "latest_health": sim.health,
        "predicted_rul_days": sim.rul,
        "financial_savings_usd": 12500
    }
    WORK_ORDERS.insert(0, order)
    return {"status": "success", "work_order": order}

@app.get("/api/maintenance")
def get_maintenance_status():
    active_m_id = fleet_manager.active_machine_id
    hist = sim_state.history_records.get(active_m_id, [])
    if not hist:
        generate_next_telemetry_step(active_m_id)
        hist = sim_state.history_records[active_m_id]

    row = hist[-1]
    return {
        "machine_id": active_m_id,
        "machine_name": row.get("Machine_Name", "Turbine Motor Unit A1"),
        "predicted_rul_days": int(row.get("Predicted_RUL", 0)),
        "machine_health": float(row.get("Machine_Health", 100.0)),
        "maintenance_status": row.get("Maintenance_Status", "Healthy"),
        "recommended_action": row.get("Recommended_Action", "Continue Normal Operation"),
        "inspection_priority": row.get("Inspection_Priority", "Low"),
        "next_inspection_window": row.get("Next_Inspection_Window", "Routine inspection"),
        "action_type": row.get("Action_Type", "Routine Maintenance"),
        "critical_subcomponents": row.get("Critical_Subcomponents", []),
        "subcomponents": row.get("Subcomponents", {}),
        "financial_analysis": row.get("Financial_Analysis", {}),
        "timestamp": str(row.get("Timestamp", "")),
        "active_ai_model": row.get("Active_AI_Model", ai_engine.active_model_name),
        "model_version": row.get("Model_Version", "1.0")
    }

class PredictRequest(BaseModel):
    temperature: float = 62.0
    temperature_unit: str = "C"      # "C", "F", "K"
    vibration: float = 0.20
    vibration_unit: str = "mm/s"     # "mm/s", "in/s", "ips"
    motor_current: float = 8.0
    current_unit: str = "A"          # "A", "mA"
    acoustic_noise: float = 42.0
    pressure: float = 4.5
    pressure_unit: str = "bar"       # "bar", "psi", "kpa", "mpa"
    rpm: float = 3000.0
    speed_unit: str = "rpm"          # "rpm", "hz"
    frequency: float = 50.0
    freq_unit: str = "Hz"
    load: float = 15.0
    load_unit: str = "kN"            # "kN", "lbf", "tonne"
    model_name: Optional[str] = None

@app.post("/api/predict")
def predict_custom_telemetry(req: PredictRequest):
    # Automatically normalize any incoming industrial unit into canonical physical scale
    canonical_payload = normalize_industrial_payload(req.dict())
    rul, latency = ai_engine.predict_rul(canonical_payload, model_name=req.model_name)
    return {
        "predicted_rul_days": rul,
        "inference_latency_ms": latency,
        "model_used": req.model_name or ai_engine.active_model_name,
        "canonical_normalized_telemetry": canonical_payload
    }

@app.get("/api/units/schema")
def get_units_schema():
    return {
        "canonical_si_units": {
            "temperature": "°C (Celsius)",
            "vibration": "mm/s (RMS Velocity)",
            "motor_current": "A (Amperes)",
            "acoustic_noise": "dB (Decibels)",
            "pressure": "bar (Bar)",
            "rpm": "RPM (Revolutions Per Minute)",
            "frequency": "Hz (Hertz)",
            "load": "kN (Kilonewtons)"
        },
        "supported_input_units": {
            "temperature": ["°C (Celsius)", "°F (Fahrenheit)", "K (Kelvin)"],
            "vibration": ["mm/s (Metric RMS)", "in/s or ips (Imperial Velocity)", "m/s²", "µm"],
            "pressure": ["bar", "psi (Pounds/sq inch)", "kPa", "MPa", "atm"],
            "rpm": ["RPM", "Hz", "rad/s"],
            "load": ["kN", "lbf (Pounds-force)", "tonne", "kgf"],
            "motor_current": ["A", "mA", "kA"]
        },
        "dimensionless_normalization": "Z-Score standardization: z = (x_canonical - mu) / sigma"
    }

@app.get("/api/logs")
def get_recent_logs(unit_system: str = "metric"):
    active_m_id = fleet_manager.active_machine_id
    hist = sim_state.history_records.get(active_m_id, [])
    recent = hist[-15:] if hist else []

    formatted = []
    unit_clean = unit_system.lower()
    for r in recent:
        raw_t = float(r.get("Temperature", 62.0))
        raw_v = float(r.get("Vibration", 0.20))
        raw_c = float(r.get("Motor_Current", 8.0))
        raw_p = float(r.get("Pressure", 4.5))

        if unit_clean == "imperial":
            disp_t = round(from_canonical_units("temperature", raw_t, "F"), 1)
            disp_v = round(from_canonical_units("vibration", raw_v, "in/s"), 3)
            disp_p = round(from_canonical_units("pressure", raw_p, "psi"), 1)
            t_unit, v_unit, p_unit = "°F", "in/s", "psi"
        elif unit_clean == "normalized":
            disp_t = round((raw_t - 62.0) / 0.6, 2)
            disp_v = round((raw_v - 0.20) / 0.04, 2)
            disp_p = round((raw_p - 4.5) / 0.25, 2)
            t_unit, v_unit, p_unit = "σ", "σ", "σ"
        else:
            disp_t = round(raw_t, 1)
            disp_v = round(raw_v, 3)
            disp_p = round(raw_p, 2)
            t_unit, v_unit, p_unit = "°C", "mm/s", "bar"

        formatted.append({
            "timestamp": str(r.get("Timestamp", "")),
            "temperature": disp_t,
            "vibration": disp_v,
            "motor_current": round(raw_c, 2),
            "pressure": disp_p,
            "predicted_rul": int(r.get("Predicted_RUL", 0)),
            "machine_health": round(float(r.get("Machine_Health", 100.0)), 1),
            "status": r.get("Maintenance_Status") or r.get("Machine_Status", "Healthy"),
            "units": {"temperature": t_unit, "vibration": v_unit, "pressure": p_unit}
        })
    return {"logs": formatted}

class ControlAction(BaseModel):
    action: str  # "start", "pause", "next", "reset", "set_speed"
    speed: float = 1.0

@app.post("/api/control")
def control_simulation(action: ControlAction):
    if action.action == "start":
        sim_state.auto_play = True
    elif action.action == "pause":
        sim_state.auto_play = False
    elif action.action == "next":
        for m_id in FLEET_CONFIGS:
            generate_next_telemetry_step(m_id)
    elif action.action == "reset":
        for m_id in FLEET_CONFIGS:
            fleet_manager.simulators[m_id].reset()
            sim_state.history_records[m_id] = []
            sim_state.prev_smoothed_rul[m_id] = None
            generate_next_telemetry_step(m_id)
        sim_state.auto_play = False
    elif action.action == "set_speed":
        sim_state.simulation_speed = action.speed

    active_hist = sim_state.history_records.get(fleet_manager.active_machine_id, [])
    return {
        "current_idx": len(active_hist) - 1,
        "auto_play": sim_state.auto_play,
        "simulation_speed": sim_state.simulation_speed
    }

# Legacy endpoint backwards compatibility for model evaluation view
@app.get("/api/model")
def get_legacy_model_evaluation():
    active_bm = ai_engine.benchmarks.get(ai_engine.active_model_name, {})
    return {
        "algorithm": ai_engine.active_model_name,
        "n_estimators": 100,
        "dataset_size": 3500,
        "train_size": 2800,
        "test_size": 700,
        "mae": active_bm.get("mae", 28.5),
        "rmse": active_bm.get("rmse", 39.2),
        "r2_score": active_bm.get("r2_score", 0.865),
        "feature_importance": active_bm.get("feature_importance", []),
        "scatter_plot": {"actual": [250, 200, 150, 80, 20], "predicted": [245, 203, 148, 85, 18]},
        "residuals": [5, -3, 2, -5, 2]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
