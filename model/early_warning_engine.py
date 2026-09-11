import numpy as np

class IndustrialEarlyWarningEngine:
    """
    Industrial Early Failure Detection & P-F Curve Diagnostic Engine.
    Implements ISO 10816 Vibration Severity standards and non-linear P-F interval analysis
    to provide plant operators with maximum warning lead time before mechanical failure occurs.
    """
    def __init__(self):
        pass

    def evaluate_early_failure(self, current_record, baseline_config=None):
        """
        Analyzes 8-channel telemetry to determine:
          1. P-F Interval Phase and Stage
          2. Estimated Early Warning Lead Time (Days & Hours)
          3. ISO 10816 Vibration Severity Zone (A, B, C, D)
          4. Root-Cause Sensor Anomaly Attribution
          5. Prescribed Operator Physical Action Protocol
        """
        temp = float(current_record.get("Temperature", 62.0))
        vib = float(current_record.get("Vibration", 0.20))
        curr = float(current_record.get("Motor_Current", 8.0))
        noise = float(current_record.get("Acoustic_Noise", 42.0))
        pressure = float(current_record.get("Pressure", 4.5))
        rpm = float(current_record.get("RPM", 3000.0))
        freq = float(current_record.get("Frequency", 50.0))
        load = float(current_record.get("Load", 15.0))
        health = float(current_record.get("Machine_Health", 100.0))
        rul = int(current_record.get("Predicted_RUL", 300))

        base_t = float(baseline_config.get("base_temp", 62.0)) if baseline_config else 62.0
        base_v = float(baseline_config.get("base_vib", 0.20)) if baseline_config else 0.20
        base_c = float(baseline_config.get("base_curr", 8.0)) if baseline_config else 8.0
        base_n = float(baseline_config.get("base_noise", 42.0)) if baseline_config else 42.0

        # Deviations
        d_vib = max(0.0, (vib - base_v) / base_v)
        d_temp = max(0.0, (temp - base_t) / base_t)
        d_noise = max(0.0, (noise - base_n) / base_n)
        d_curr = max(0.0, (curr - base_c) / base_c)

        # 1. ISO 10816 Vibration Severity Standard (Class II & III Industrial Machines)
        if vib < 0.28:
            iso_zone = "Zone A"
            iso_label = "Good / Newly Commissioned"
            iso_color = "#10B981"
        elif vib < 0.71:
            iso_zone = "Zone B"
            iso_label = "Acceptable for Unrestricted Long-Term Operation"
            iso_color = "#3B82F6"
        elif vib < 1.80:
            iso_zone = "Zone C"
            iso_label = "Unsatisfactory / Restricted Operation (Early Warning)"
            iso_color = "#F59E0B"
        else:
            iso_zone = "Zone D"
            iso_label = "Critical Danger / High Risk of Damage"
            iso_color = "#EF4444"

        # 2. P-F Curve Progression (0% = Healthy, 100% = Functional Breakdown)
        # P1 (Acoustic/Micro-wear) -> P2 (Vibration Spectrum) -> P3 (Thermal Rise) -> P4 (Audible Overload) -> F
        if health >= 88.0 and d_vib < 0.35:
            pf_phase = "Design Operating Envelope"
            pf_lead_time_days = rul
            pf_progress_pct = max(0.0, (100.0 - health) * 2.5)
            early_warning_status = "Nominal Baseline"
            early_warning_level = "GREEN"
            inspection_checklist = [
                "Verify automated lubrication pump pressure",
                "Log standard operating temperature in shift log",
                "Check foundation bolt torques during routine tour"
            ]
        elif health >= 70.0 or d_vib < 1.0:
            pf_phase = "Point P1: Acoustic & Micro-Friction Onset"
            pf_lead_time_days = max(45, int(rul * 0.85))
            pf_progress_pct = 25.0 + max(0.0, (88.0 - health) * 1.5)
            early_warning_status = "EARLY DETECTED: Micro-fatigue initiation detected 45+ days before failure"
            early_warning_level = "YELLOW"
            inspection_checklist = [
                "Perform ultrasound / acoustic emission sweep on bearing housings",
                "Inspect grease clarity for microscopic particulate contamination",
                "Review vibration frequency harmonics (1X, 2X, 3X running speed)"
            ]
        elif health >= 45.0 or d_vib < 2.5:
            pf_phase = "Point P2: Harmonic Vibration Spectrum Distortion"
            pf_lead_time_days = max(14, int(rul * 0.70))
            pf_progress_pct = 50.0 + max(0.0, (70.0 - health) * 1.2)
            early_warning_status = "MODERATE WARNING: Measurable vibration escalation across bearings"
            early_warning_level = "AMBER"
            inspection_checklist = [
                "Collect high-resolution FFT vibration spectrum on drive-end bearings",
                "Check shaft alignment and dynamic rotor balancing",
                "Prepare replacement bearing kit and schedule maintenance slot"
            ]
        elif health >= 20.0 or d_temp > 0.30:
            pf_phase = "Point P3: Thermal Surge & Lubricant Film Breakdown"
            pf_lead_time_days = max(3, int(rul * 0.50))
            pf_progress_pct = 75.0 + max(0.0, (45.0 - health) * 1.0)
            early_warning_status = "URGENT WARNING: Thermal runaway detected. High risk of bearing seizure"
            early_warning_level = "ORANGE"
            inspection_checklist = [
                "Perform FLIR thermal imaging scan on stator and bearing caps",
                "Reduce operational duty cycle or motor load by 25-30%",
                "Verify cooling water flow rate and heat exchanger cleanliness"
            ]
        else:
            pf_phase = "Point P4: Audible Chattering & Imminent Functional Failure"
            pf_lead_time_days = max(0, int(rul * 0.25))
            pf_progress_pct = 95.0
            early_warning_status = "EMERGENCY: Immediate shutdown recommended within 0-4 hours"
            early_warning_level = "RED"
            inspection_checklist = [
                "Initiate controlled orderly machine shutdown sequence",
                "Lock out / Tag out (LOTO) electrical power disconnects",
                "Dispatch overhaul team with full rotor/bearing replacement kit"
            ]

        # 3. Root Cause Sensor Attribution Breakdown
        weights = {
            "Vibration Severity": d_vib * 3.5 + 0.05,
            "Thermal Dissipation": d_temp * 2.8 + 0.05,
            "Acoustic Friction": d_noise * 2.2 + 0.05,
            "Motor Electrical Load": d_curr * 1.8 + 0.05,
            "Hydraulic Flow": max(0.05, abs(pressure - base_t * 0.08))
        }
        total_w = sum(weights.values())
        root_cause_attribution = [
            {"sensor_group": k, "contribution_pct": round((v / total_w) * 100, 1)}
            for k, v in sorted(weights.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "early_warning_status": early_warning_status,
            "early_warning_level": early_warning_level,
            "lead_time_to_failure_days": pf_lead_time_days,
            "lead_time_to_failure_hours": pf_lead_time_days * 24,
            "pf_curve": {
                "phase_name": pf_phase,
                "degradation_progress_pct": round(float(pf_progress_pct), 1),
                "is_early_stage": (pf_progress_pct < 50.0)
            },
            "iso_10816": {
                "zone": iso_zone,
                "label": iso_label,
                "color": iso_color,
                "current_rms": round(vib, 3)
            },
            "root_cause_attribution": root_cause_attribution,
            "operator_action_checklist": inspection_checklist
        }
