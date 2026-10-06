"""
Industrial Data Quality & Validation Engine.
Validates timestamps, monitors arrival cadence, applies unit normalization,
and distinguishes between sensor hardware failures vs genuine mechanical anomalies.
"""

import datetime
from typing import Dict, Any, Tuple, Optional

class DataQualityValidator:
    def __init__(self, tag_registry: Optional[Dict[str, Any]] = None):
        self.tag_registry = tag_registry or {}
        self.last_timestamp_by_machine = {}

    def parse_timestamp(self, ts_raw: Any) -> Tuple[datetime.datetime, str]:
        """Parses and standardizes incoming timestamp into ISO-8601 UTC."""
        if not ts_raw:
            now = datetime.datetime.utcnow()
            return now, now.isoformat() + "Z"
        
        if isinstance(ts_raw, (int, float)):
            # Epoch milliseconds or seconds
            if ts_raw > 1e11:
                dt = datetime.datetime.utcfromtimestamp(ts_raw / 1000.0)
            else:
                dt = datetime.datetime.utcfromtimestamp(ts_raw)
            return dt, dt.isoformat() + "Z"

        ts_str = str(ts_raw).strip()
        # Clean standard ISO strings
        try:
            clean_ts = ts_str.replace("Z", "+00:00")
            dt = datetime.datetime.fromisoformat(clean_ts)
            if dt.tzinfo is not None:
                dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            return dt, dt.isoformat() + "Z"
        except Exception:
            # Fallback format parsing
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
                try:
                    dt = datetime.datetime.strptime(ts_str, fmt)
                    if dt.tzinfo is not None:
                        dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                    return dt, dt.isoformat() + "Z"
                except Exception:
                    continue

        now = datetime.datetime.utcnow()
        return now, now.isoformat() + "Z"

    def normalize_units(self, feature_name: str, value: float, source_unit: Optional[str]) -> Tuple[float, str]:
        """
        Normalizes known engineering units to canonical industrial standards:
        Temperature -> °C, Pressure -> bar, Vibration -> mm/s
        """
        if source_unit is None or not source_unit:
            return value, ""

        u = source_unit.strip().lower()

        # Temperature: Fahrenheit to Celsius
        if feature_name == "Temperature" and ("f" in u or "degf" in u):
            celsius = (value - 32.0) * (5.0 / 9.0)
            return round(celsius, 2), "°C"

        # Pressure: psi to bar
        if feature_name == "Pressure" and "psi" in u:
            bar = value * 0.0689476
            return round(bar, 2), "bar"

        # Vibration velocity: inches per second (ips) to mm/s
        if feature_name == "Vibration" and ("ips" in u or "in/s" in u):
            mms = value * 25.4
            return round(mms, 3), "mm/s"

        return value, source_unit

    def validate_features(
        self,
        machine_id: str,
        features: Dict[str, float],
        timestamp_dt: datetime.datetime,
        units_map: Optional[Dict[str, str]] = None
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        Validates feature values, detects out-of-order or duplicate timestamps,
        flags hardware open/short sensor errors vs mechanical faults.
        """
        units_map = units_map or {}
        cleaned_features = {}
        flags = {
            "is_out_of_order": False,
            "sensor_hardware_errors": [],
            "data_quality": "GOOD"
        }

        # Timestamp sequencing check
        if timestamp_dt.tzinfo is not None:
            timestamp_dt = timestamp_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        if machine_id in self.last_timestamp_by_machine:
            last_dt = self.last_timestamp_by_machine[machine_id]
            if last_dt.tzinfo is not None:
                last_dt = last_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            if timestamp_dt <= last_dt:
                flags["is_out_of_order"] = True
                flags["data_quality"] = "SUSPECT_OUT_OF_ORDER"
        self.last_timestamp_by_machine[machine_id] = timestamp_dt

        # Feature validation
        for feat, val in features.items():
            # 1. Normalize unit if provided
            raw_unit = units_map.get(feat, "")
            norm_val, _ = self.normalize_units(feat, val, raw_unit)

            # 2. Check for physical impossibility (sensor disconnection or ADC short)
            # E.g. Negative vibration RMS or temperature below -50°C in industrial bay
            if feat == "Vibration" and norm_val < 0.0:
                flags["sensor_hardware_errors"].append(f"{feat}: Negative RMS impossible ({norm_val})")
                flags["data_quality"] = "SENSOR_HARDWARE_FAULT"
                norm_val = 0.0
            elif feat == "Temperature" and (norm_val < -40.0 or norm_val > 400.0):
                flags["sensor_hardware_errors"].append(f"{feat}: Physical thermocouple range exceeded ({norm_val})")
                flags["data_quality"] = "SENSOR_HARDWARE_FAULT"
            elif feat == "Motor_Current" and norm_val < 0.0:
                flags["sensor_hardware_errors"].append(f"{feat}: Current cannot be negative ({norm_val})")
                flags["data_quality"] = "SENSOR_HARDWARE_FAULT"
                norm_val = 0.0

            cleaned_features[feat] = norm_val

        return cleaned_features, flags
