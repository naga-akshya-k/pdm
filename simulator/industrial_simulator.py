import numpy as np
import datetime
import random

FLEET_CONFIGS = {
    "MCH-802X": {
        "name": "Turbine Motor Unit A1",
        "type": "Gas Turbine Generator",
        "location": "Power Generation Hall - Bay 4",
        "max_lifespan_days": 100,
        "base_temp": 62.0,      # °C
        "base_vib": 0.20,       # mm/s RMS
        "base_curr": 8.0,       # Amps
        "base_noise": 42.0,     # dB
        "base_pressure": 4.5,   # bar
        "base_rpm": 3000.0,     # RPM
        "base_freq": 50.0,      # Hz
        "base_load": 15.0,      # kN
    }
}

class IndustrialMachineSimulator:
    """
    Physics-based Industrial Digital Twin SCADA Telemetry Simulator.
    Simulates multi-channel physical degradation, component health, and interactive mechanical faults.
    """
    def __init__(self, machine_id="MCH-802X", seed=None, degradation_speed=1.0):
        self.machine_id = machine_id if machine_id in FLEET_CONFIGS else "MCH-802X"
        self.config = FLEET_CONFIGS[self.machine_id]
        self.seed = seed
        self.degradation_speed = degradation_speed
        self.reset(seed=self.seed)

    def reset(self, seed=None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.current_step = 0
        self.health = 100.0
        self.cum_wear = 0.0
        self.start_time = datetime.datetime.now()
        
        # Subcomponent Health Tracking (0% to 100%)
        self.subcomponents = {
            "bearing_assembly": 100.0,
            "stator_windings": 100.0,
            "rotor_balance": 100.0,
            "cooling_system": 100.0,
            "hydraulic_seals": 100.0
        }

        # Lifespan & Wear schedule (Day 50 Wear Inception Contract)
        self.target_lifespan = int(self.config["max_lifespan_days"] * random.uniform(0.95, 1.05))
        self.rul = float(self.target_lifespan)
        self.start_wear_day = 50.0  # Uniform until Day 50, then wear begins and increases steeply

        # Baseline parameters
        self.temp_base = self.config["base_temp"] * random.uniform(0.98, 1.02)
        self.vib_base = self.config["base_vib"] * random.uniform(0.95, 1.05)
        self.curr_base = self.config["base_curr"] * random.uniform(0.97, 1.03)
        self.noise_base = self.config["base_noise"] * random.uniform(0.98, 1.02)
        self.pressure_base = self.config["base_pressure"] * random.uniform(0.97, 1.03)
        self.rpm_base = self.config["base_rpm"] * random.uniform(0.99, 1.01)
        self.freq_base = self.config["base_freq"] * random.uniform(0.99, 1.01)
        self.load_base = self.config["base_load"] * random.uniform(0.98, 1.02)

        # Mean-reverting micro-drift state
        self.drifts = {
            "temp": 0.0, "vib": 0.0, "curr": 0.0, "noise": 0.0,
            "pressure": 0.0, "rpm": 0.0, "freq": 0.0, "load": 0.0
        }

        # Active injected fault state
        self.active_fault = "None"
        self.fault_duration_remaining = 0
        self.active_event = "None"

    def inject_fault(self, fault_type: str, duration_steps: int = 25):
        """
        Dynamically injects mechanical fault scenarios into the digital twin.
        Supported faults:
          - 'bearing_degradation'
          - 'thermal_runaway'
          - 'cavitation'
          - 'rotor_imbalance'
        """
        valid_faults = ["bearing_degradation", "thermal_runaway", "cavitation", "rotor_imbalance"]
        if fault_type in valid_faults:
            self.active_fault = fault_type
            self.fault_duration_remaining = duration_steps
            return {"status": "success", "injected_fault": fault_type, "duration_steps": duration_steps}
        return {"status": "error", "message": f"Unknown fault type. Valid options: {valid_faults}"}

    def clear_fault(self):
        self.active_fault = "None"
        self.fault_duration_remaining = 0
        self.active_event = "None"

    def _evaluate_stage(self):
        if self.health >= 80.0:
            return "Healthy"
        elif self.health >= 60.0:
            return "Slight Wear"
        elif self.health >= 40.0:
            return "Moderate Wear"
        elif self.health >= 15.0:
            return "Critical"
        else:
            return "Failure"

    def step(self):
        """Advances digital twin simulation by 1 operational step/day."""
        self.current_step += 1
        day = float(self.current_step)

        # Update mean-reverting Brownian micro-drifts
        for k in self.drifts:
            self.drifts[k] = 0.82 * self.drifts[k] + np.random.normal(0, 0.08)

        # Base wear progression (Uniform until Day 50, then increases slightly, then steeply high)
        wear_span = max(1.0, float(self.target_lifespan) - self.start_wear_day)
        if day <= self.start_wear_day:
            p = 0.0  # Completely uniform flat baseline before fault inception
            sigma_mult = 1.0
        else:
            p_rel = (day - self.start_wear_day) / wear_span
            p = min(1.5, (p_rel ** 1.6))  # Starts slightly, then curves steeply upward
            sigma_mult = 1.0 + 2.5 * p

        # Compute natural physical degradation means
        t_mean = self.temp_base + (22.0 * (p ** 1.6)) + self.drifts["temp"] * 0.4
        v_mean = self.vib_base + (4.5 * (p ** 1.6)) + self.drifts["vib"] * 0.1
        c_mean = self.curr_base + (9.5 * (p ** 1.6)) + self.drifts["curr"] * 0.3
        n_mean = self.noise_base + (35.0 * (p ** 1.6)) + self.drifts["noise"] * 0.5
        p_mean = self.pressure_base - (self.pressure_base * 0.30 * (p ** 1.6)) + self.drifts["pressure"] * 0.2
        rpm_mean = self.rpm_base - (self.rpm_base * 0.08 * (p ** 1.6)) + self.drifts["rpm"] * 10.0
        f_mean = self.freq_base + (self.freq_base * 0.12 * (p ** 1.6)) + self.drifts["freq"] * 0.5
        load_mean = self.load_base + (self.load_base * 0.20 * (p ** 1.6)) + self.drifts["load"] * 0.3

        # Fault Injection Overrides
        fault_name = "None"
        if self.fault_duration_remaining > 0 and self.active_fault != "None":
            self.fault_duration_remaining -= 1
            if self.active_fault == "bearing_degradation":
                v_mean *= 3.2
                f_mean *= 1.75
                n_mean += 22.0
                t_mean += 8.5
                fault_name = "Bearing Micro-Spalling Fault"
            elif self.active_fault == "thermal_runaway":
                t_mean += 32.0
                c_mean += 4.8
                fault_name = "Thermal Cooling Runaway"
            elif self.active_fault == "cavitation":
                p_mean *= 0.38
                n_mean += 28.0
                v_mean *= 2.4
                fault_name = "Hydraulic Cavitation Surge"
            elif self.active_fault == "rotor_imbalance":
                v_mean *= 2.9
                c_mean *= 1.85
                load_mean *= 1.5
                rpm_mean *= 0.92
                fault_name = "Rotor Eccentric Imbalance"

            if self.fault_duration_remaining <= 0:
                self.active_fault = "None"
        else:
            # Stochastic industrial burst anomalies during wear
            if p > 0.45 and random.random() < 0.20:
                t_mean += random.uniform(2.0, 5.0)
                v_mean += random.uniform(0.3, 0.8)
                fault_name = "Transient Thermal / Vibration Burst"

        self.active_event = fault_name

        # Sample Measured Telemetry with Heteroskedastic Noise
        temp = max(15.0, t_mean + np.random.normal(0, 0.28 * sigma_mult))
        vib = max(0.02, v_mean + np.random.normal(0, 0.025 * sigma_mult))
        curr = max(2.0, c_mean + np.random.normal(0, 0.045 * sigma_mult))
        noise = max(25.0, n_mean + np.random.normal(0, 0.55 * sigma_mult))
        pressure = max(0.5, p_mean + np.random.normal(0, 0.15 * sigma_mult))
        rpm = max(100.0, rpm_mean + np.random.normal(0, 15.0 * sigma_mult))
        freq = max(5.0, f_mean + np.random.normal(0, 0.20 * sigma_mult))
        load = max(1.0, load_mean + np.random.normal(0, 0.25 * sigma_mult))

        # Update Subcomponent Health Decay (Uniform 100% until Day 50, then smooth wear progression)
        decay_factor = min(100.0, p * 100.0)
        bearing_fault_penalty = 55.0 if self.active_fault == "bearing_degradation" else 0.0
        thermal_fault_penalty = 50.0 if self.active_fault == "thermal_runaway" else 0.0
        hydraulic_fault_penalty = 55.0 if self.active_fault == "cavitation" else 0.0
        rotor_fault_penalty = 50.0 if self.active_fault == "rotor_imbalance" else 0.0

        self.subcomponents["bearing_assembly"] = max(0.0, min(100.0, 100.0 - decay_factor * 0.95 - bearing_fault_penalty))
        self.subcomponents["cooling_system"] = max(0.0, min(100.0, 100.0 - decay_factor * 0.70 - thermal_fault_penalty))
        self.subcomponents["stator_windings"] = max(0.0, min(100.0, 100.0 - decay_factor * 0.75 - thermal_fault_penalty * 0.5))
        self.subcomponents["hydraulic_seals"] = max(0.0, min(100.0, 100.0 - decay_factor * 0.65 - hydraulic_fault_penalty))
        self.subcomponents["rotor_balance"] = max(0.0, min(100.0, 100.0 - decay_factor * 0.90 - rotor_fault_penalty))

        # Overall Machine Health as harmonic mean of subcomponents & overall wear
        min_sub = min(self.subcomponents.values())
        avg_sub = sum(self.subcomponents.values()) / len(self.subcomponents)
        overall_health = 0.60 * avg_sub + 0.40 * min_sub
        self.health = max(0.0, min(100.0, round(float(overall_health), 1)))

        # Ground-Truth Remaining Useful Life (RUL)
        self.rul = max(0, int(self.target_lifespan - day))

        timestamp_str = (self.start_time + datetime.timedelta(days=self.current_step)).strftime("%Y-%m-%d %H:%M:%S")

        return {
            "Machine_ID": self.machine_id,
            "Machine_Name": self.config["name"],
            "Machine_Type": self.config["type"],
            "Location": self.config["location"],
            "Timestamp": timestamp_str,
            "Day": int(self.current_step),
            "Temperature": round(float(temp), 2),
            "Vibration": round(float(vib), 3),
            "Motor_Current": round(float(curr), 2),
            "Acoustic_Noise": round(float(noise), 2),
            "Pressure": round(float(pressure), 2),
            "RPM": round(float(rpm), 1),
            "Frequency": round(float(freq), 2),
            "Load": round(float(load), 2),
            "Machine_Health": round(float(self.health), 1),
            "Degradation_Index": round(float(max(0.0, 100.0 - self.health)), 1),
            "Machine_Status": self._evaluate_stage(),
            "Remaining_Useful_Life_Days": int(self.rul),
            "Active_Event": self.active_event,
            "Active_Fault": self.active_fault,
            "Subcomponents": {k: round(v, 1) for k, v in self.subcomponents.items()}
        }

class FleetSimulatorManager:
    """Manages all industrial assets across the plant floor."""
    def __init__(self):
        self.simulators = {
            m_id: IndustrialMachineSimulator(machine_id=m_id)
            for m_id in FLEET_CONFIGS
        }
        self.active_machine_id = "MCH-802X"

    def get_active_simulator(self) -> IndustrialMachineSimulator:
        return self.simulators[self.active_machine_id]

    def set_active_machine(self, machine_id: str):
        if machine_id in self.simulators:
            self.active_machine_id = machine_id
            return {"status": "success", "active_machine_id": machine_id}
        return {"status": "error", "message": f"Machine {machine_id} not found in fleet"}

    def get_fleet_summary(self):
        summary = []
        for m_id, sim in self.simulators.items():
            summary.append({
                "machine_id": m_id,
                "name": sim.config["name"],
                "type": sim.config["type"],
                "location": sim.config["location"],
                "health": sim.health,
                "status": sim._evaluate_stage(),
                "rul_days": sim.rul,
                "current_day": sim.current_step,
                "active_fault": sim.active_fault,
                "active_event": sim.active_event,
                "is_active": (m_id == self.active_machine_id)
            })
        return summary
