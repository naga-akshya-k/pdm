"""
Industrial Tag Mapping Engine.
Configuration-driven translation of industrial SCADA/PLC Tag IDs to standardized internal feature names.
"""

import os
import yaml
from typing import Dict, Any, Tuple, Optional

class IndustrialTagMapper:
    def __init__(self, config_path: str = "config/tag_mapping.yaml"):
        self.config_path = config_path
        self.tags = {}
        self.generic_mapping = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
                self.tags = cfg.get("tags", {})
                self.generic_mapping = cfg.get("generic_sensor_mapping", {})
        else:
            # Fallback default registry
            self.tags = {
                "TURB_MTR_DE_VIB_RMS": {"feature_name": "Vibration", "unit": "mm/s", "valid_min": 0.0, "valid_max": 25.0},
                "TURB_MTR_VIB_FREQ_01": {"feature_name": "Frequency", "unit": "Hz", "valid_min": 10.0, "valid_max": 200.0},
                "TURB_MTR_STATOR_TEMP": {"feature_name": "Temperature", "unit": "°C", "valid_min": -10.0, "valid_max": 180.0},
                "TURB_MTR_PHASE_CURRENT": {"feature_name": "Motor_Current", "unit": "A", "valid_min": 0.0, "valid_max": 100.0},
                "TURB_MTR_ACOUSTIC_DB": {"feature_name": "Acoustic_Noise", "unit": "dB", "valid_min": 10.0, "valid_max": 130.0},
                "TURB_MTR_LUBE_OIL_PRES": {"feature_name": "Pressure", "unit": "bar", "valid_min": 0.0, "valid_max": 20.0},
                "TURB_MTR_SHAFT_SPEED": {"feature_name": "RPM", "unit": "RPM", "valid_min": 0.0, "valid_max": 6000.0},
                "TURB_MTR_KW_LOAD": {"feature_name": "Load", "unit": "%", "valid_min": 0.0, "valid_max": 150.0},
            }

    def map_payload(self, tags_dict: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        Maps raw input tags into canonical feature dictionary.
        Returns:
            canonical_features: { "Vibration": 0.32, "Temperature": 58.5, ... }
            audit_metadata: { "recognized_tags": [...], "unrecognized_tags": [...], "raw_units": {...} }
        """
        canonical_features = {}
        raw_units = {}
        recognized = []
        unrecognized = []

        upper_lookup = {str(k).upper(): (k, v) for k, v in tags_dict.items()}

        for tag_id, meta in self.tags.items():
            feat_name = meta["feature_name"]
            expected_unit = meta.get("unit", "")
            
            # 1. Match direct Tag ID
            if tag_id in upper_lookup:
                orig_key, val = upper_lookup[tag_id]
                try:
                    canonical_features[feat_name] = float(val)
                    raw_units[feat_name] = expected_unit
                    recognized.append(tag_id)
                except (ValueError, TypeError):
                    pass
            # 2. Match direct feature name if present
            elif feat_name in tags_dict:
                try:
                    canonical_features[feat_name] = float(tags_dict[feat_name])
                    raw_units[feat_name] = expected_unit
                    recognized.append(feat_name)
                except (ValueError, TypeError):
                    pass

        # Identify unrecognized keys
        for k in tags_dict.keys():
            if str(k).upper() not in self.tags and k not in canonical_features:
                unrecognized.append(k)

        audit_metadata = {
            "recognized_tags": recognized,
            "unrecognized_tags": unrecognized,
            "raw_units": raw_units
        }
        return canonical_features, audit_metadata
