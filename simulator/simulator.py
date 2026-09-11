import numpy as np
import datetime
import random

class RealTimeMachineSimulator:
    """
    Industrial Real-Time Machine Telemetry Simulator (365-Day Digital Twin SCADA Model).
    Models realistic industrial condition monitoring telemetry across 4 operational phases:
      - Phase 1 (Days 1–150, Healthy Operation): Stationary stochastic process with random walk micro-drift + Gaussian noise (zero upward trend). No flat lines.
      - Phase 2 (Days 151–260, Early Wear): Non-monotonic mean rise + variance growth.
      - Phase 3 (Days 261–330, Progressive Degradation): Accelerated wear, vibration oscillations, overload current peaks.
      - Phase 4 (Days 331–365+, Critical Stage): Severe instability, highest signal noise, random thermal spikes, health collapse.

    Digital Twin Health Concept:
      Health Index emerges dynamically from a cumulative multi-sensor wear score combining age,
      temperature deviation, vibration severity, motor current, acoustic noise, and signal instability.
      Strictly clamped between 0% and 100%.
    """
    def __init__(self, max_lifespan_days=365, degradation_factor=1.8, seed=None, degradation_start_day=None, degradation_speed=1.0):
        self.max_lifespan_days = max_lifespan_days
        self.degradation_factor = degradation_factor
        self.seed = seed
        self.degradation_start_day = degradation_start_day
        self.degradation_speed = degradation_speed
        self.reset(seed=self.seed)

    def reset(self, seed=None):
        """Resets the machine back to initial baseline state with unique machine parameters."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        self.current_step = 0
        self.health = 100.0
        self.cum_wear = 0.0  # Monotonic physical wear tracking accumulator
        self.start_time = datetime.datetime.now()
        
        # 1. Statistically unique target lifespan (330 to 400 days for 365-day baseline)
        self.target_lifespan = random.randint(330, 400)
        self.rul = float(self.target_lifespan)
        
        # 2. Wear Onset Day (Defaults to ~Day 150 for demo instance, randomized ~140-160 in training)
        if self.degradation_start_day is not None:
            self.start_wear_day = float(self.degradation_start_day)
        else:
            self.start_wear_day = round(float(self.target_lifespan) * random.uniform(0.38, 0.42), 1)  # ~Day 150 of 365
            
        # 3. Degradation Speed & Variance Coefficients
        self.speed = float(self.degradation_speed) * random.uniform(0.85, 1.15)
        self.var_coeff = random.uniform(0.85, 1.15)
        
        # 4. Statistically unique baseline operating parameters
        self.temp_base = random.uniform(61.2, 62.8)   # °C
        self.vib_base = random.uniform(0.18, 0.22)    # mm/s
        self.curr_base = random.uniform(7.8, 8.2)     # A
        self.noise_base = random.uniform(41.0, 43.0)  # dB
        
        # Random walk micro-drift initial state (Brownian motion for SCADA realism)
        self.temp_drift = 0.0
        self.vib_drift = 0.0
        self.curr_drift = 0.0
        self.noise_drift = 0.0
        
        # Base noise standard deviations during Healthy phase
        self.sigma_temp_base = random.uniform(0.22, 0.32)
        self.sigma_vib_base = random.uniform(0.018, 0.025)
        self.sigma_curr_base = random.uniform(0.035, 0.055)
        self.sigma_noise_base = random.uniform(0.45, 0.65)
        
        # Statistically unique degradation sensitivity rates
        self.k_temp = random.uniform(0.85, 1.15) * self.speed
        self.k_vib = random.uniform(0.85, 1.15) * self.speed
        self.k_curr = random.uniform(0.85, 1.15) * self.speed
        self.k_noise = random.uniform(0.85, 1.15) * self.speed
        
        self.spike_prob = random.uniform(0.15, 0.25)
        self.spike_mag = random.uniform(0.85, 1.25)
        
        self.active_event = "None"

    def _evaluate_stage(self):
        """Determines machine operational stage based on current health percentage."""
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
        """
        Advances the machine simulation by 1 step/day.
        Returns telemetry dictionary with guaranteed non-flat living data (even beyond Day 365)
        and monotonic cumulative health decay.
        """
        self.current_step += 1
        day = float(self.current_step)
        
        # Update mean-reverting Brownian micro-drift to guarantee zero flat lines
        self.temp_drift = 0.82 * self.temp_drift + np.random.normal(0, 0.15)
        self.vib_drift = 0.82 * self.vib_drift + np.random.normal(0, 0.010)
        self.curr_drift = 0.82 * self.curr_drift + np.random.normal(0, 0.025)
        self.noise_drift = 0.82 * self.noise_drift + np.random.normal(0, 0.30)
        
        # 1. Physical Signal Mean & Variance Calculation
        if day <= self.start_wear_day:
            # PHASE 1: HEALTHY OPERATION (Days 1 to start_wear_day, e.g. Day 150)
            # Stochastic SCADA telemetry with zero long-term trend (micro-drift + noise, NO flat lines)
            t_osc = 0.22 * np.sin(day * 0.12 * np.pi) + 0.14 * np.cos(day * 0.04 * np.pi)
            v_osc = 0.014 * np.sin(day * 0.15 * np.pi)
            
            temp_mean = self.temp_base + t_osc + self.temp_drift * 0.3
            vib_mean = self.vib_base + v_osc + self.vib_drift * 0.3
            curr_mean = self.curr_base + self.curr_drift * 0.3
            noise_mean = self.noise_base + self.noise_drift * 0.3
            
            sigma_t = self.sigma_temp_base
            sigma_v = self.sigma_vib_base
            sigma_c = self.sigma_curr_base
            sigma_n = self.sigma_noise_base
            
            self.active_event = "None"
            wear_fraction = 0.01 * (day / self.start_wear_day)
        else:
            # PHASES 2, 3, 4: WEAR & DEGRADATION (After Wear Onset, e.g. Day 151-365 and beyond Day 365)
            wear_span = max(1.0, float(self.target_lifespan) - self.start_wear_day)
            p = min(1.3, (day - self.start_wear_day) / wear_span)  # Allows continuous wear beyond Day 365
            
            # Non-monotonic growth in MEAN signal levels (mean trend + micro-drift + fluctuations)
            temp_mean = self.temp_base + (16.5 * self.k_temp) * (p ** 1.7) + 0.40 * np.sin(p * 8 * np.pi) + self.temp_drift * 0.5
            vib_mean = self.vib_base + (4.3 * self.k_vib) * (p ** 1.7) + 0.16 * np.sin(p * 10 * np.pi) + self.vib_drift * 0.5
            curr_mean = self.curr_base + (8.2 * self.k_curr) * (p ** 1.7) + self.curr_drift * 0.5
            noise_mean = self.noise_base + (33.0 * self.k_noise) * (p ** 1.7) + self.noise_drift * 0.5
            
            # HETEROSKEDASTIC VARIANCE GROWTH:
            # Healthy ±0.25°C -> Early Wear ±0.5°C -> Progressive ±1.2°C -> Critical ±2.5°C
            sigma_t = (self.sigma_temp_base + 2.3 * (p ** 1.5)) * self.var_coeff
            sigma_v = (self.sigma_vib_base + 0.38 * (p ** 1.8)) * self.var_coeff
            sigma_c = (self.sigma_curr_base + 0.48 * (p ** 1.5)) * self.var_coeff
            sigma_n = (self.sigma_noise_base + 4.2 * (p ** 1.5)) * self.var_coeff
            
            # Occasional anomaly spikes during wear phase
            if p > 0.40 and random.random() < self.spike_prob:
                temp_mean += random.uniform(1.2, 3.8) * self.spike_mag
                vib_mean += random.uniform(0.15, 0.65) * self.spike_mag
                curr_mean += random.uniform(0.6, 2.2) * self.spike_mag
                self.active_event = "Thermal Burst" if temp_mean > 70 else "Vibration Peak"
            else:
                self.active_event = "None"
                
            wear_fraction = p

        # 2. Sample Measured Telemetry with Growing Gaussian Noise (GUARANTEED UNIQUE VALUES EVERY DAY)
        temp_measured = max(20.0, temp_mean + np.random.normal(0, max(0.1, sigma_t)))
        vib_measured = max(0.05, vib_mean + np.random.normal(0, max(0.01, sigma_v)))
        curr_measured = max(4.0, curr_mean + np.random.normal(0, max(0.02, sigma_c)))
        noise_measured = max(30.0, noise_mean + np.random.normal(0, max(0.2, sigma_n)))
        
        # 3. Monotonic Physical Cumulative Wear Accumulation
        d_temp = max(0.0, (temp_measured - self.temp_base) / 15.0) ** 1.3
        d_vib = max(0.0, (vib_measured - self.vib_base) / 4.0) ** 1.3
        d_curr = max(0.0, (curr_measured - self.curr_base) / 7.2) ** 1.3
        d_noise = max(0.0, (noise_measured - self.noise_base) / 30.0) ** 1.3
        
        current_raw_wear = 0.30 * d_temp + 0.35 * d_vib + 0.20 * d_curr + 0.15 * d_noise
        current_raw_wear = max(current_raw_wear, wear_fraction * 0.95)
        
        # Accumulate monotonic physical wear (physical wear cannot spontaneously un-occur)
        self.cum_wear = max(self.cum_wear, current_raw_wear)
        
        if day <= self.start_wear_day:
            health_calc = 100.0 - (day / self.start_wear_day) * random.uniform(0.4, 1.2) + np.random.normal(0, 0.05)
        else:
            health_calc = 99.0 - (self.cum_wear * 99.0)
            
        # STRICT CLAMPING BETWEEN 0% AND 100%
        self.health = max(0.0, min(100.0, round(float(health_calc), 1)))
        
        # 4. Ground-Truth Remaining Useful Life (RUL)
        self.rul = max(0, int(self.target_lifespan - day))
        
        timestamp_str = (self.start_time + datetime.timedelta(days=self.current_step)).strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "Timestamp": timestamp_str,
            "Temperature": round(float(temp_measured), 2),
            "Vibration": round(float(vib_measured), 2),
            "Motor_Current": round(float(curr_measured), 2),
            "Acoustic_Noise": round(float(noise_measured), 2),
            "Machine_Health": round(float(self.health), 1),
            "Machine_Status": self._evaluate_stage(),
            "Remaining_Useful_Life_Days": int(self.rul),
            "Active_Event": self.active_event,
            "Day": int(self.current_step)
        }

# Alias for backwards compatibility
MachineSimulator = RealTimeMachineSimulator
