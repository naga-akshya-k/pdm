import datetime
import uuid

# In-memory CMMS Work Order database
WORK_ORDERS = []

def get_maintenance_recommendation(predicted_rul, machine_health=100.0, active_event="None", subcomponents=None, machine_info=None):
    """
    Enhanced Industrial Maintenance Decision Engine (ISO 13374 Condition-Based Maintenance standard).
    Maps RUL, Machine Health, Subcomponents, and Active Events to deterministic servicing guidelines,
    component failure risks, and downtime cost impacts.
    """
    rul = float(predicted_rul)
    health = float(machine_health)
    
    if subcomponents is None:
        subcomponents = {
            "bearing_assembly": health,
            "stator_windings": health,
            "rotor_balance": health,
            "cooling_system": health,
            "hydraulic_seals": health
        }

    # Determine weakest subcomponents
    critical_subcomponents = [
        comp.replace("_", " ").title()
        for comp, score in subcomponents.items()
        if score < 50.0
    ]

    if health < 15.0 or rul < 20:
        status = "Critical"
        recommendation = "Immediate shutdown and overhaul required before catastrophic mechanical failure."
        priority = "Critical"
        window = "Emergency: Stop machine within 0–4 hours"
        action_type = "Corrective Replacement"
        downtime_risk_usd = 45000
        preventive_cost_usd = 8500
    elif rul < 60 or health < 40.0:
        status = "Warning"
        recommendation = "Accelerated wear detected. Schedule urgent component replacement and alignment check."
        priority = "Urgent"
        window = "Perform servicing within 3–5 days"
        action_type = "Urgent Component Servicing"
        downtime_risk_usd = 28000
        preventive_cost_usd = 4200
    elif rul < 150 or health < 65.0:
        status = "Preventive Maintenance"
        recommendation = "Initiate planned preventive maintenance cycle. Inspect lubrication, seals, and bearing play."
        priority = "High"
        window = "Schedule maintenance within 14–21 days"
        action_type = "Preventive Servicing"
        downtime_risk_usd = 15000
        preventive_cost_usd = 2100
    elif rul <= 260 or health < 82.0:
        status = "Monitor"
        recommendation = "Minor degradation trend observed. Increase telemetry sampling and vibration monitoring frequency."
        priority = "Moderate"
        window = "Inspect within 30–45 days"
        action_type = "Condition Monitoring Inspection"
        downtime_risk_usd = 6000
        preventive_cost_usd = 800
    else:
        status = "Healthy"
        recommendation = "Operating within nominal design envelope. Continue standard operational cycle."
        priority = "Low"
        window = "Routine inspection within 90–120 days"
        action_type = "Routine Maintenance"
        downtime_risk_usd = 0
        preventive_cost_usd = 350

    # Override for severe active anomaly events
    if active_event not in ["None", "", None] and priority in ["Low", "Moderate"]:
        priority = "High"
        recommendation = f"Active anomaly ({active_event}): Dispatch field technician for immediate diagnostic scan."
        window = "Inspect within 24-48 hours"
        action_type = f"Anomaly Response: {active_event}"
        downtime_risk_usd += 5000

    result = {
        "maintenance_status": status,
        "recommended_action": recommendation,
        "inspection_priority": priority,
        "next_inspection_window": window,
        "action_type": action_type,
        "critical_subcomponents": critical_subcomponents,
        "financial_analysis": {
            "estimated_unplanned_downtime_loss_usd": downtime_risk_usd,
            "estimated_preventive_servicing_cost_usd": preventive_cost_usd,
            "net_roi_savings_usd": max(0, downtime_risk_usd - preventive_cost_usd)
        }
    }

    return result

def auto_generate_cmms_work_order(machine_id, machine_name, maint_recommendation, telemetry):
    """Generates an automated ISO 13374 CMMS Work Order when priority is High, Urgent, or Critical."""
    order_id = f"WO-{datetime.datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:5].upper()}"
    
    parts_map = {
        "Critical": ["Full Ceramic Bearing Kit", "Primary Rotor Seal Set", "Synthetic High-Viscosity Lubricant"],
        "Urgent": ["Precision Roller Bearings", "Gasket & Seal Pack"],
        "High": ["Filtration Cartridge", "Lubricant Top-Up"],
        "Moderate": ["Sensor Calibration Pack"],
        "Low": ["Standard Filter Inspection Kit"]
    }

    priority = maint_recommendation.get("inspection_priority", "Moderate")
    
    order = {
        "order_id": order_id,
        "machine_id": machine_id,
        "machine_name": machine_name,
        "status": "OPEN",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "priority": priority,
        "maintenance_type": maint_recommendation.get("action_type", "Inspection"),
        "recommended_action": maint_recommendation.get("recommended_action", ""),
        "next_inspection_window": maint_recommendation.get("next_inspection_window", ""),
        "assigned_role": "Senior Reliability Engineer" if priority in ["Critical", "Urgent"] else "Plant Maintenance Tech",
        "estimated_duration_hours": 8 if priority == "Critical" else (4 if priority == "Urgent" else 2),
        "required_parts": parts_map.get(priority, ["Standard Inspection Pack"]),
        "latest_health": telemetry.get("Machine_Health", 100.0),
        "predicted_rul_days": telemetry.get("Predicted_RUL", 300),
        "financial_savings_usd": maint_recommendation.get("financial_analysis", {}).get("net_roi_savings_usd", 0)
    }

    WORK_ORDERS.insert(0, order)
    # Cap total stored work orders
    if len(WORK_ORDERS) > 50:
        WORK_ORDERS.pop()

    return order

def get_all_work_orders():
    # If empty, populate initial historical work order sample
    if not WORK_ORDERS:
        WORK_ORDERS.extend([
            {
                "order_id": "WO-202609-A8F12",
                "machine_id": "MCH-802X",
                "machine_name": "Turbine Motor Unit A1",
                "status": "OPEN",
                "created_at": "2026-09-01 08:30:00",
                "priority": "Moderate",
                "maintenance_type": "Condition Monitoring Inspection",
                "recommended_action": "Routine bearing vibration spectrum analysis and grease replenishment.",
                "next_inspection_window": "Inspect within 30–45 days",
                "assigned_role": "Plant Maintenance Tech",
                "estimated_duration_hours": 2,
                "required_parts": ["Synthetic High-Viscosity Lubricant"],
                "latest_health": 88.5,
                "predicted_rul_days": 240,
                "financial_savings_usd": 5200
            }
        ])
    return WORK_ORDERS
