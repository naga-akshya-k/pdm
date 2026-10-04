"""
Evidence-Backed Industrial Fault Diagnosis Engine.
Evaluates multivariate sensor patterns and windowed features to attribute mechanical anomalies.
Requires explicit evidentiary threshold matching; otherwise outputs an uncommitted inspection alert.
"""

from typing import Dict, Any, List

class IndustrialFaultDiagnostician:
    def __init__(self):
        pass

    def diagnose_condition(self, features: Dict[str, Any], anomaly_status: str) -> Dict[str, Any]:
        """
        Diagnoses specific mechanical failure modes using physical evidentiary rules.
        """
        if anomaly_status == "NORMAL":
            return {
                "detected_fault": "Nominal / Healthy",
                "fault_category": "NONE",
                "confidence": 0.95,
                "evidence": ["All monitored channels operating within nominal physical design envelope."]
            }

        temp = float(features.get("Temperature", 62.0))
        vib = float(features.get("Vibration", 0.20))
        curr = float(features.get("Motor_Current", 8.0))
        noise = float(features.get("Acoustic_Noise", 42.0))
        pressure = float(features.get("Pressure", 4.5))
        rpm = float(features.get("RPM", 3000.0))
        freq = float(features.get("Frequency", 50.0))
        
        vib_kurtosis = float(features.get("Vibration_kurtosis", 3.0))
        vib_crest = float(features.get("Vibration_crest_factor", 1.0))
        temp_slope = float(features.get("Temperature_slope", 0.0))

        evidence = []
        candidate_faults = []

        # 1. Check for Bearing Race Spalling / Degradation
        bearing_ev = []
        if vib > 0.80:
            bearing_ev.append(f"Vibration RMS elevated at {vib:.2f} mm/s (threshold: 0.80 mm/s)")
        if noise > 65.0:
            bearing_ev.append(f"Ultrasonic acoustic friction elevated at {noise:.1f} dB (threshold: 65.0 dB)")
        if vib_kurtosis > 4.5 or vib_crest > 2.8:
            bearing_ev.append(f"Impact impulsiveness detected (Kurtosis: {vib_kurtosis:.1f}, Crest Factor: {vib_crest:.1f})")
        if len(bearing_ev) >= 2:
            candidate_faults.append(("Bearing Assembly Degradation", 0.88, bearing_ev, "MECHANICAL"))

        # 2. Check for Thermal Runaway / Stator Winding Breakdown
        thermal_ev = []
        if temp > 85.0:
            thermal_ev.append(f"Stator core temperature high at {temp:.1f} °C (threshold: 85.0 °C)")
        if curr > 14.5:
            thermal_ev.append(f"Motor phase current elevated at {curr:.1f} A (threshold: 14.5 A)")
        if temp_slope > 0.02:
            thermal_ev.append(f"Accelerated positive thermal slope ({temp_slope:.4f} °C/s)")
        if len(thermal_ev) >= 2:
            candidate_faults.append(("Thermal Runaway & Stator Overheating", 0.92, thermal_ev, "ELECTRICAL"))

        # 3. Check for Lube Oil Feed Pressure Loss
        lube_ev = []
        if pressure < 2.5:
            lube_ev.append(f"Lube oil supply pressure dropped to {pressure:.2f} bar (critical minimum: 2.5 bar)")
        if noise > 60.0:
            lube_ev.append(f"Boundary friction acoustic emission active ({noise:.1f} dB)")
        if len(lube_ev) >= 1 and pressure < 2.5:
            candidate_faults.append(("Lubrication Pressure Loss & Oil Starvation", 0.85, lube_ev, "HYDRAULIC"))

        # 4. Check for Dynamic Rotor Imbalance
        imbalance_ev = []
        if vib > 0.90 and 48.0 <= freq <= 52.0:
            imbalance_ev.append(f"Dominant vibration synchronized with 1X rotational speed ({freq:.1f} Hz)")
        if temp < 75.0 and noise < 65.0:
            imbalance_ev.append("Absence of high ultrasonic noise or thermal spikes rules out bearing spalling")
        if len(imbalance_ev) >= 2:
            candidate_faults.append(("Dynamic Rotor Imbalance", 0.81, imbalance_ev, "MECHANICAL"))

        # 5. Check for Cavitation Surge
        cav_ev = []
        if pressure < 3.2 and noise > 68.0:
            cav_ev.append(f"Low inlet pressure ({pressure:.2f} bar) coupled with high-frequency noise ({noise:.1f} dB)")
            candidate_faults.append(("Hydraulic Cavitation Surge", 0.80, cav_ev, "HYDRAULIC"))

        # Selection of best matching fault
        if candidate_faults:
            # Sort by confidence
            candidate_faults.sort(key=lambda x: x[1], reverse=True)
            chosen = candidate_faults[0]
            return {
                "detected_fault": chosen[0],
                "fault_category": chosen[3],
                "confidence": chosen[1],
                "evidence": chosen[2]
            }

        # If anomalous but evidence does not conclusively match known patterns
        return {
            "detected_fault": "Possible abnormal condition detected. Root cause requires inspection.",
            "fault_category": "UNSPECIFIED_ANOMALY",
            "confidence": 0.50,
            "evidence": [
                f"Multi-sensor vector departed from baseline, but spectral signature does not uniquely match a single mechanical profile."
            ]
        }
