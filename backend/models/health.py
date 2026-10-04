"""
Machine Health Index & ISO 10816 Standard Assessment Engine.
Computes an explainable normalized 0–100 Health Score based on ISO vibration severity,
anomaly penalties, and component degradation factors.
"""

from typing import Dict, Any, Tuple

class IndustrialHealthEvaluator:
    def __init__(self):
        pass

    def evaluate_iso_10816(self, vibration_rms: float, machine_class: str = "Class III") -> Dict[str, str]:
        """
        ISO 10816 Vibration Severity Standard evaluation.
        Zone A: Good / Newly Commissioned
        Zone B: Acceptable for Unrestricted Long-Term Operation
        Zone C: Unsatisfactory / Restricted Operation (Early Warning)
        Zone D: Critical Danger / High Risk of Mechanical Damage
        """
        v = float(vibration_rms)
        if v < 0.28:
            zone = "Zone A"
            status = "Good / Newly Commissioned"
            color = "#10B981"
            base_score = 100.0 - (v / 0.28) * 10.0
        elif v < 0.71:
            zone = "Zone B"
            status = "Acceptable for Unrestricted Long-Term Operation"
            color = "#3B82F6"
            base_score = 90.0 - ((v - 0.28) / (0.71 - 0.28)) * 20.0
        elif v < 1.80:
            zone = "Zone C"
            status = "Unsatisfactory / Restricted Operation (Early Warning)"
            color = "#F59E0B"
            base_score = 70.0 - ((v - 0.71) / (1.80 - 0.71)) * 30.0
        else:
            zone = "Zone D"
            status = "Critical Danger / High Risk of Damage"
            color = "#EF4444"
            base_score = max(5.0, 40.0 - min(35.0, (v - 1.80) * 15.0))

        return {
            "zone": zone,
            "status": status,
            "color": color,
            "iso_score": round(base_score, 1)
        }

    def compute_health_index(
        self,
        features: Dict[str, float],
        anomaly_score: float,
        subcomponents: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Computes the consolidated, explainable Machine Health Index (0-100).
        """
        vib = float(features.get("Vibration", 0.20))
        temp = float(features.get("Temperature", 62.0))
        pressure = float(features.get("Pressure", 4.5))

        iso_info = self.evaluate_iso_10816(vib)
        iso_score = iso_info["iso_score"]

        # Anomaly penalty (0 to 40 points)
        anomaly_penalty = float(anomaly_score) * 40.0

        # Thermal penalty (if temperature exceeds 70°C)
        thermal_penalty = max(0.0, (temp - 70.0) * 0.8) if temp > 70.0 else 0.0

        # Pressure penalty (if pressure falls below 3.5 bar)
        pressure_penalty = max(0.0, (3.5 - pressure) * 10.0) if pressure < 3.5 else 0.0

        # Combined raw health score
        health = iso_score - (anomaly_penalty * 0.5) - thermal_penalty - pressure_penalty
        health = float(max(5.0, min(100.0, health)))

        # Subcomponents tracking
        if not subcomponents:
            subcomponents = {
                "bearing_assembly": round(max(5.0, min(100.0, health * 0.98)), 1),
                "stator_windings": round(max(5.0, min(100.0, 100.0 - thermal_penalty * 2)), 1),
                "rotor_balance": round(max(5.0, min(100.0, iso_score)), 1),
                "cooling_system": round(max(5.0, min(100.0, 100.0 - thermal_penalty * 1.5)), 1),
                "hydraulic_seals": round(max(5.0, min(100.0, 100.0 - pressure_penalty * 3)), 1),
            }

        status_text = "Healthy" if health >= 80.0 else ("Monitor" if health >= 60.0 else ("Degraded" if health >= 35.0 else "Critical"))

        return {
            "health_index": round(health, 1),
            "status": status_text,
            "iso_10816": iso_info,
            "subcomponents": subcomponents,
            "penalties": {
                "anomaly_deduction": round(anomaly_penalty * 0.5, 1),
                "thermal_deduction": round(thermal_penalty, 1),
                "pressure_deduction": round(pressure_penalty, 1)
            }
        }
