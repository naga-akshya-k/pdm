"""
Industrial Time-Series Storage Layer.
Provides SQLite persistence for raw telemetry streams, windowed feature records,
anomaly/health inferences, and MLOps model registry metadata.
"""

import os
import json
import sqlite3
import datetime
import threading
from typing import Dict, Any, List, Optional, Tuple

class TimeSeriesStorage:
    def __init__(self, db_path: str = "data/pdm_timeseries.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=15.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            # Raw Telemetry Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raw_telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    machine_id TEXT NOT NULL,
                    tag_id TEXT NOT NULL,
                    sensor_type TEXT,
                    value REAL NOT NULL,
                    unit TEXT,
                    quality TEXT DEFAULT 'GOOD',
                    is_simulation INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_machine_time ON raw_telemetry(machine_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_tag ON raw_telemetry(tag_id)")

            # Processed Window Inferences Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_inferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    machine_id TEXT NOT NULL,
                    features_json TEXT NOT NULL,
                    health_score REAL,
                    anomaly_score REAL,
                    anomaly_status TEXT,
                    fault_diagnosis TEXT,
                    confidence REAL,
                    estimated_rul REAL,
                    rul_lower REAL,
                    rul_upper REAL,
                    maintenance_action TEXT,
                    maintenance_priority TEXT,
                    data_source TEXT DEFAULT 'REAL',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inferences_machine_time ON processed_inferences(machine_id, timestamp)")

            # MLOps Model Registry Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_registry (
                    version TEXT PRIMARY KEY,
                    model_name TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    trained_at TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    status TEXT NOT NULL, -- 'PRODUCTION', 'CANDIDATE', 'ARCHIVED'
                    approved_by TEXT,
                    notes TEXT
                )
            """)
            conn.commit()

    def insert_raw_telemetry(self, records: List[Dict[str, Any]]):
        """Batch inserts raw sensor readings."""
        if not records:
            return
        query = """
            INSERT INTO raw_telemetry (timestamp, machine_id, tag_id, sensor_type, value, unit, quality, is_simulation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                r.get("timestamp", datetime.datetime.utcnow().isoformat() + "Z"),
                str(r.get("machine_id", "UNKNOWN")),
                str(r.get("tag_id", "RAW")),
                r.get("sensor_type", ""),
                float(r.get("value", 0.0)),
                r.get("unit", ""),
                r.get("quality", "GOOD"),
                1 if r.get("is_simulation", False) else 0
            )
            for r in records
        ]
        with self._lock, self._get_connection() as conn:
            conn.cursor().executemany(query, rows)
            conn.commit()

    def insert_inference(self, inference: Dict[str, Any]):
        """Persists a complete ML pipeline decision snapshot."""
        query = """
            INSERT INTO processed_inferences (
                timestamp, machine_id, features_json, health_score, anomaly_score,
                anomaly_status, fault_diagnosis, confidence, estimated_rul,
                rul_lower, rul_upper, maintenance_action, maintenance_priority, data_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        features_json = json.dumps(inference.get("features", {}))
        with self._lock, self._get_connection() as conn:
            conn.cursor().execute(query, (
                inference.get("timestamp", datetime.datetime.utcnow().isoformat() + "Z"),
                str(inference.get("machine_id", "UNKNOWN")),
                features_json,
                inference.get("health_score"),
                inference.get("anomaly_score"),
                inference.get("anomaly_status"),
                inference.get("fault_diagnosis"),
                inference.get("confidence"),
                inference.get("estimated_rul"),
                inference.get("rul_lower"),
                inference.get("rul_upper"),
                inference.get("maintenance_action"),
                inference.get("maintenance_priority"),
                inference.get("data_source", "REAL")
            ))
            conn.commit()

    def get_recent_inferences(self, machine_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves recent inference history for dashboard charting."""
        query = """
            SELECT * FROM processed_inferences
            WHERE machine_id = ?
            ORDER BY id DESC
            LIMIT ?
        """
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (machine_id, limit))
            rows = cursor.fetchall()
            results = []
            for r in reversed(rows):
                item = dict(r)
                item["features"] = json.loads(item["features_json"])
                results.append(item)
            return results

    def get_recent_raw(self, machine_id: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Retrieves recent raw telemetry readings."""
        query = """
            SELECT * FROM raw_telemetry
            WHERE machine_id = ?
            ORDER BY id DESC
            LIMIT ?
        """
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (machine_id, limit))
            rows = cursor.fetchall()
            return [dict(r) for r in reversed(rows)]
