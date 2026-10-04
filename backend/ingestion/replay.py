"""
Historical Industrial Telemetry Replay Engine.
Replays recorded run-to-failure plant sensor datasets through the exact same
ingestion and feature extraction pipeline as real-time MQTT streams.
"""

import os
import time
import pandas as pd
import threading
from typing import Dict, Any, Optional, Callable

class HistoricalTelemetryReplayer:
    def __init__(
        self,
        csv_path: str = "datasets/sensor_data.csv",
        ingest_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        machine_id: str = "MCH-802X"
    ):
        self.csv_path = csv_path
        self.ingest_callback = ingest_callback
        self.machine_id = machine_id

        self.is_replaying = False
        self.playback_speed = 1.0
        self.current_index = 0
        self.total_rows = 0
        self.thread = None
        self._lock = threading.RLock()

        self._load_data()

    def _load_data(self):
        if os.path.exists(self.csv_path):
            try:
                # Load first 1000 rows for smooth demo playback
                self.df = pd.read_csv(self.csv_path, nrows=1000)
                self.total_rows = len(self.df)
            except Exception:
                self.df = pd.DataFrame()
                self.total_rows = 0
        else:
            self.df = pd.DataFrame()
            self.total_rows = 0

    def start_replay(self, speed: float = 1.0):
        with self._lock:
            if self.is_replaying:
                return
            self.is_replaying = True
            self.playback_speed = max(0.1, float(speed))
            self.thread = threading.Thread(target=self._replay_loop, daemon=True)
            self.thread.start()

    def stop_replay(self):
        with self._lock:
            self.is_replaying = False

    def _replay_loop(self):
        while self.is_replaying and self.total_rows > 0:
            row = self.df.iloc[self.current_index]
            packet = {
                "machine_id": self.machine_id,
                "timestamp": str(row.get("Timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))),
                "is_replay": True,
                "is_simulation": False,
                "tags": {
                    "TURB_MTR_STATOR_TEMP": float(row.get("Temperature", 62.0)),
                    "TURB_MTR_DE_VIB_RMS": float(row.get("Vibration", 0.20)),
                    "TURB_MTR_PHASE_CURRENT": float(row.get("Motor_Current", 8.0)),
                    "TURB_MTR_ACOUSTIC_DB": 42.0 + float(row.get("Vibration", 0.20)) * 20.0,
                    "TURB_MTR_LUBE_OIL_PRES": 4.5,
                    "TURB_MTR_SHAFT_SPEED": 3000.0,
                    "TURB_MTR_VIB_FREQ_01": 50.0,
                    "TURB_MTR_KW_LOAD": 50.0
                }
            }

            if self.ingest_callback:
                self.ingest_callback(packet)

            with self._lock:
                self.current_index = (self.current_index + 1) % self.total_rows

            sleep_duration = max(0.05, 1.0 / self.playback_speed)
            time.sleep(sleep_duration)

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "is_replaying": self.is_replaying,
                "current_index": self.current_index,
                "total_rows": self.total_rows,
                "playback_speed": self.playback_speed,
                "dataset_file": self.csv_path
            }
