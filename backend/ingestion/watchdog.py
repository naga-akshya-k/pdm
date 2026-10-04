"""
MQTT Watchdog & Telemetry Mode Monitor.
Enforces industrial communication watchdog timeout (3.0s).
Ensures that if real telemetry pauses, a REAL TELEMETRY OFFLINE alarm is triggered,
preventing simulated data from ever being silently mistaken for real plant data.
"""

import time
import threading
from typing import Dict, Any, Optional

class TelemetryWatchdog:
    def __init__(self, timeout_seconds: float = 3.0):
        self.timeout_seconds = timeout_seconds
        self.last_packet_time: Optional[float] = None
        self.current_mode: str = "SIMULATION"  # REAL INDUSTRIAL DATA | SIMULATION | HISTORICAL REPLAY
        self.active_machine_id: str = "MCH-802X"
        self._lock = threading.RLock()

    def record_packet(self, machine_id: str, is_simulation: bool = False, is_replay: bool = False):
        with self._lock:
            self.last_packet_time = time.time()
            self.active_machine_id = machine_id
            if is_replay:
                self.current_mode = "HISTORICAL REPLAY"
            elif is_simulation:
                self.current_mode = "SIMULATION"
            else:
                self.current_mode = "REAL INDUSTRIAL DATA"

    def set_mode(self, mode: str):
        with self._lock:
            if mode in ["REAL INDUSTRIAL DATA", "SIMULATION", "HISTORICAL REPLAY"]:
                self.current_mode = mode

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            now = time.time()
            if self.last_packet_time is None:
                is_live = False
                seconds_since_last = None
            else:
                seconds_since_last = round(now - self.last_packet_time, 2)
                is_live = seconds_since_last <= self.timeout_seconds

            # If in real mode and timeout exceeded, trigger offline alarm
            is_offline_alarm = (self.current_mode == "REAL INDUSTRIAL DATA" and not is_live)

            return {
                "current_mode": self.current_mode,
                "is_stream_live": is_live,
                "seconds_since_last_packet": seconds_since_last,
                "watchdog_timeout_seconds": self.timeout_seconds,
                "real_telemetry_offline_alarm": is_offline_alarm,
                "alarm_message": "REAL TELEMETRY OFFLINE — Check sensor/edge gateway connectivity." if is_offline_alarm else None,
                "active_machine_id": self.active_machine_id
            }
