"""
Sliding Window Buffer & Multivariate Feature Aggregator.
Maintains sliding time-series windows per machine, aligns multivariate channels,
and extracts tabular engineered features for downstream ML inference.
"""

from collections import deque
import threading
from typing import Dict, Any, List, Optional
from .time_domain import compute_time_domain_features
from .frequency_domain import compute_frequency_domain_features
from .trends import compute_trend_features

ALL_CORE_SENSORS = [
    "Temperature",
    "Vibration",
    "Motor_Current",
    "Acoustic_Noise",
    "Pressure",
    "RPM",
    "Frequency",
    "Load"
]

class MachineWindowBuffer:
    def __init__(self, window_size: int = 10, sampling_rate_hz: float = 1.0):
        self.window_size = window_size
        self.sampling_rate_hz = sampling_rate_hz
        self._lock = threading.RLock()
        # Ring buffers per machine: { machine_id: { sensor_name: deque(maxlen=window_size) } }
        self.buffers: Dict[str, Dict[str, deque]] = {}
        self.timestamps: Dict[str, deque] = {}

    def append_sample(self, machine_id: str, timestamp_str: str, features: Dict[str, float]) -> bool:
        """
        Appends a synchronized measurement vector into the machine's sliding buffer.
        Returns True if window buffer has reached minimum required capacity.
        """
        with self._lock:
            if machine_id not in self.buffers:
                self.buffers[machine_id] = {s: deque(maxlen=self.window_size) for s in ALL_CORE_SENSORS}
                self.timestamps[machine_id] = deque(maxlen=self.window_size)

            self.timestamps[machine_id].append(timestamp_str)
            for sensor in ALL_CORE_SENSORS:
                val = features.get(sensor)
                if val is not None:
                    self.buffers[machine_id][sensor].append(float(val))
                elif len(self.buffers[machine_id][sensor]) > 0:
                    # Impute with last known value
                    self.buffers[machine_id][sensor].append(self.buffers[machine_id][sensor][-1])
                else:
                    self.buffers[machine_id][sensor].append(0.0)

            # Return True if we have at least 3 samples to extract trends/moments
            return len(self.timestamps[machine_id]) >= 3

    def extract_window_features(self, machine_id: str) -> Dict[str, float]:
        """
        Extracts full set of multivariate time-domain, frequency-domain,
        and trend features across all active channels for the specified machine.
        """
        with self._lock:
            if machine_id not in self.buffers:
                return {}

            mach_buf = self.buffers[machine_id]
            extracted = {}

            # 1. Base instantaneous values (latest in window)
            for sensor in ALL_CORE_SENSORS:
                series = list(mach_buf[sensor])
                last_val = series[-1] if series else 0.0
                extracted[sensor] = round(last_val, 4)

                # Time-domain statistical moments
                td = compute_time_domain_features(series, prefix=f"{sensor}_")
                extracted.update(td)

                # Trend slope
                tr = compute_trend_features(series, dt_seconds=1.0 / self.sampling_rate_hz, prefix=f"{sensor}_")
                extracted.update(tr)

            # 2. FFT frequency domain specifically for vibration
            vib_series = list(mach_buf["Vibration"])
            fd = compute_frequency_domain_features(vib_series, sampling_rate_hz=self.sampling_rate_hz, prefix="Vib_FFT_")
            extracted.update(fd)

            return extracted

    def get_window_depth(self, machine_id: str) -> int:
        with self._lock:
            return len(self.timestamps.get(machine_id, []))
