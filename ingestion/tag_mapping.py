"""
Industrial Tag Mapping & Schema Validator.
Maps company SCADA/PLC Tag IDs to internal AI feature names for Turbine Motor MCH-802X.
"""

from typing import Dict, Any, Tuple, Optional

# Standard Tag ID Registry for Turbine Motor Unit A1 (MCH-802X)
TURBINE_TAG_REGISTRY = {
    "TURB_MTR_DE_VIB_RMS": {
        "feature_name": "Vibration",
        "description": "Drive-End Bearing Radial Vibration RMS",
        "unit": "mm/s",
        "normal_min": 0.10,
        "normal_max": 0.80,
        "crit_threshold": 1.80,
    },
    "TURB_MTR_VIB_FREQ_01": {
        "feature_name": "Frequency",
        "description": "Dominant Rotational Spectral Frequency",
        "unit": "Hz",
        "normal_min": 48.0,
        "normal_max": 52.0,
        "crit_threshold": 75.0,
    },
    "TURB_MTR_STATOR_TEMP": {
        "feature_name": "Temperature",
        "description": "Stator Winding Core Temperature",
        "unit": "°C",
        "normal_min": 40.0,
        "normal_max": 70.0,
        "crit_threshold": 95.0,
    },
    "TURB_MTR_PHASE_CURRENT": {
        "feature_name": "Motor_Current",
        "description": "3-Phase Motor Stator Current",
        "unit": "A",
        "normal_min": 8.0,
        "normal_max": 14.0,
        "crit_threshold": 22.0,
    },
    "TURB_MTR_ACOUSTIC_DB": {
        "feature_name": "Acoustic_Noise",
        "description": "High-Frequency Ultrasonic Acoustic Emission",
        "unit": "dB",
        "normal_min": 40.0,
        "normal_max": 65.0,
        "crit_threshold": 88.0,
    },
    "TURB_MTR_LUBE_OIL_PRES": {
        "feature_name": "Pressure",
        "description": "Bearing Lube Oil Feed Pressure",
        "unit": "bar",
        "normal_min": 3.5,
        "normal_max": 5.5,
        "crit_threshold": 2.2,
    },
    "TURB_MTR_SHAFT_SPEED": {
        "feature_name": "RPM",
        "description": "Tachometer Rotational Shaft Speed",
        "unit": "RPM",
        "normal_min": 2950.0,
        "normal_max": 3050.0,
        "crit_threshold": 2600.0,
    },
    "TURB_MTR_KW_LOAD": {
        "feature_name": "Load",
        "description": "Shaft Active Operating Power Load",
        "unit": "%",
        "normal_min": 20.0,
        "normal_max": 90.0,
        "crit_threshold": 105.0,
    },
}

FEATURE_TO_TAG_MAP = {
    meta["feature_name"]: tag_id for tag_id, meta in TURBINE_TAG_REGISTRY.items()
}


def normalize_tag_payload(tags_dict: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    Translates raw incoming tag dictionary to internal feature dictionary.
    Supports exact tag IDs, lowercased tag IDs, or direct feature names as fallback.
    Returns (feature_dict, audit_info).
    """
    mapped_features = {}
    audit = {
        "recognized_tags": [],
        "missing_tags": [],
        "unrecognized_tags": [],
    }

    lookup = {str(k).upper(): v for k, v in tags_dict.items()}

    for tag_id, meta in TURBINE_TAG_REGISTRY.items():
        feat_name = meta["feature_name"]
        val = None

        if tag_id in lookup:
            val = lookup[tag_id]
            audit["recognized_tags"].append(tag_id)
        elif tag_id.lower() in tags_dict:
            val = tags_dict[tag_id.lower()]
            audit["recognized_tags"].append(tag_id)
        elif feat_name in tags_dict:
            val = tags_dict[feat_name]
            audit["recognized_tags"].append(f"direct:{feat_name}")
        elif feat_name.lower() in tags_dict:
            val = tags_dict[feat_name.lower()]
            audit["recognized_tags"].append(f"direct:{feat_name.lower()}")
        else:
            audit["missing_tags"].append(tag_id)
            val = (meta["normal_min"] + meta["normal_max"]) / 2.0

        try:
            mapped_features[feat_name] = round(float(val), 3)
        except (ValueError, TypeError):
            mapped_features[feat_name] = round((meta["normal_min"] + meta["normal_max"]) / 2.0, 3)

    return mapped_features, audit
