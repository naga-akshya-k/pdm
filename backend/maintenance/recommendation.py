"""
Explainable Industrial Maintenance Recommendation Engine.
Generates evidence-backed servicing recommendations and prioritizations
without over-engineered CMMS technician dispatches or parts-kit generation.
"""

from typing import Dict, Any, List

class MaintenanceRecommendationEngine:
    def __init__(self):
        pass

    def generate_recommendation(
        self,
        machine_id: str,
        machine_name: str,
        health_info: Dict[str, Any],
        anomaly_info: Dict[str, Any],
        fault_info: Dict[str, Any],
        rul_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Translates real-time AI and physics assessments into an explainable maintenance recommendation.
        """
        health = float(health_info.get("health_index", 100.0))
        anomaly_status = anomaly_info.get("anomaly_status", "NORMAL")
        anomaly_score = float(anomaly_info.get("anomaly_score", 0.0))
        detected_fault = fault_info.get("detected_fault", "Nominal / Healthy")
        fault_evidence = fault_info.get("evidence", [])
        rul_days = rul_info.get("estimated_rul_days", 300)

        # 1. Determine Severity and Priority
        if health < 25.0 or anomaly_status == "CRITICAL" or rul_days < 10:
            severity = "CRITICAL"
            priority = "CRITICAL"
            timeframe = "Immediate: Inspect and plan controlled shutdown within 0–4 operating hours"
            action = f"Immediate shutdown inspection of {machine_name}. Perform overhaul on identified fault: {detected_fault}."
        elif health < 55.0 or anomaly_status == "WARNING" or rul_days < 45:
            severity = "HIGH"
            priority = "HIGH"
            timeframe = "Urgent: Complete diagnostic inspection within 3–5 days"
            action = f"Schedule targeted maintenance inspection on {machine_name}. Focus check: {detected_fault}."
        elif health < 75.0 or rul_days < 120:
            severity = "MODERATE"
            priority = "MEDIUM"
            timeframe = "Next planned maintenance turnaround or within 14–21 days"
            action = f"Inspect mechanical lubrication and alignment during next available servicing window."
        else:
            severity = "LOW"
            priority = "LOW"
            timeframe = "Routine quarterly inspection cycle (within 90–120 days)"
            action = f"Continue nominal operation. Maintain standard SCADA condition monitoring."

        # Consolidated evidence list
        evidence_list = []
        for ev in fault_evidence:
            evidence_list.append(ev)
        
        iso_zone = health_info.get("iso_10816", {}).get("zone", "Zone A")
        iso_status = health_info.get("iso_10816", {}).get("status", "Good")
        evidence_list.append(f"ISO 10816 Vibration Severity: {iso_zone} ({iso_status})")
        evidence_list.append(f"Machine Health Score: {health:.1f} / 100")
        if rul_info.get("rul_calibrated", False):
            evidence_list.append(f"Model-projected RUL: {rul_info.get('rul_interval_lower')}-{rul_info.get('rul_interval_upper')} days")

        # Confidence is determined by diagnosis and data quality
        conf = float(fault_info.get("confidence", 0.85))

        return {
            "machine_id": machine_id,
            "machine_name": machine_name,
            "condition": anomaly_status,
            "severity": severity,
            "priority": priority,
            "detected_issue": detected_fault,
            "evidence": evidence_list,
            "recommended_action": action,
            "suggested_timeframe": timeframe,
            "confidence": round(conf, 2),
            "estimated_rul_days": rul_days
        }
