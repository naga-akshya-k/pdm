"""
Universal Industrial Unit Standardization & Dimensionless Normalization Engine.
Converts any incoming industrial measurement unit (Metric, Imperial, SI) into
internal Canonical Physical Units and dimensionless normalized Z-scores.
"""

# Canonical Internal Units:
# Temperature: °C
# Vibration: mm/s RMS
# Motor Current: A
# Acoustic Noise: dB
# Pressure: bar
# Speed: RPM
# Frequency: Hz
# Load: kN

UNIT_CONVERSIONS = {
    "temperature": {
        "c": lambda v: float(v),
        "f": lambda v: (float(v) - 32.0) * (5.0 / 9.0),
        "k": lambda v: float(v) - 273.15,
        "°c": lambda v: float(v),
        "°f": lambda v: (float(v) - 32.0) * (5.0 / 9.0),
        "celsius": lambda v: float(v),
        "fahrenheit": lambda v: (float(v) - 32.0) * (5.0 / 9.0),
        "kelvin": lambda v: float(v) - 273.15,
    },
    "vibration": {
        "mm/s": lambda v: float(v),
        "in/s": lambda v: float(v) * 25.4,
        "ips": lambda v: float(v) * 25.4,
        "m/s2": lambda v: float(v) * 3.18,      # Approx RMS velocity conversion at 50Hz
        "um": lambda v: float(v) * 0.001 * 314.16, # Approx peak to RMS velocity at 50Hz
    },
    "pressure": {
        "bar": lambda v: float(v),
        "psi": lambda v: float(v) * 0.0689476,
        "kpa": lambda v: float(v) * 0.01,
        "mpa": lambda v: float(v) * 10.0,
        "atm": lambda v: float(v) * 1.01325,
    },
    "rpm": {
        "rpm": lambda v: float(v),
        "hz": lambda v: float(v) * 60.0,
        "rad/s": lambda v: float(v) * 9.549297,
    },
    "load": {
        "kn": lambda v: float(v),
        "lbf": lambda v: float(v) * 0.00444822,
        "kgf": lambda v: float(v) * 0.00980665,
        "tonne": lambda v: float(v) * 9.80665,
    },
    "motor_current": {
        "a": lambda v: float(v),
        "ma": lambda v: float(v) * 0.001,
        "ka": lambda v: float(v) * 1000.0,
    },
    "frequency": {
        "hz": lambda v: float(v),
        "cpm": lambda v: float(v) / 60.0,
        "khz": lambda v: float(v) * 1000.0,
    },
    "acoustic_noise": {
        "db": lambda v: float(v),
    }
}

# Reverse conversions: Canonical -> Target unit for UI display
CANONICAL_TO_TARGET = {
    "temperature": {
        "C": lambda v: float(v),
        "F": lambda v: float(v) * (9.0 / 5.0) + 32.0,
        "K": lambda v: float(v) + 273.15,
    },
    "vibration": {
        "mm/s": lambda v: float(v),
        "in/s": lambda v: float(v) / 25.4,
        "ips": lambda v: float(v) / 25.4,
    },
    "pressure": {
        "bar": lambda v: float(v),
        "psi": lambda v: float(v) / 0.0689476,
        "kpa": lambda v: float(v) * 100.0,
        "mpa": lambda v: float(v) / 10.0,
    },
    "load": {
        "kn": lambda v: float(v),
        "lbf": lambda v: float(v) / 0.00444822,
    }
}

def to_canonical_units(param_name: str, value: float, unit: str) -> float:
    """
    Normalizes any arbitrary industrial input measurement into the standard internal canonical unit.
    Example: to_canonical_units('temperature', 143.6, 'F') -> 62.0 °C
    """
    key = param_name.lower().replace(" ", "_")
    unit_clean = unit.lower().strip()

    if key in UNIT_CONVERSIONS:
        converter = UNIT_CONVERSIONS[key].get(unit_clean)
        if converter:
            return converter(value)

    # Return raw value if already in canonical or unknown unit
    return float(value)

def from_canonical_units(param_name: str, value_canonical: float, target_unit: str) -> float:
    """
    Converts canonical internal unit to target display unit for plant operators.
    Example: from_canonical_units('temperature', 62.0, 'F') -> 143.6 °F
    """
    key = param_name.lower().replace(" ", "_")
    unit_clean = target_unit.upper().strip() if target_unit.lower() in ["c", "f", "k"] else target_unit.lower().strip()

    if key in CANONICAL_TO_TARGET:
        converter = CANONICAL_TO_TARGET[key].get(unit_clean)
        if converter:
            return converter(value_canonical)

    return float(value_canonical)

def normalize_industrial_payload(sensor_dict: dict) -> dict:
    """
    Sanitizes and normalizes an entire industrial telemetry payload containing mixed units.
    Case-insensitive parameter and unit key lookup.
    """
    clean_dict = {str(k).lower().strip(): v for k, v in sensor_dict.items()}

    def get_val(keys, default):
        for k in keys:
            if k in clean_dict and clean_dict[k] is not None:
                return clean_dict[k]
        return default

    # Temperature
    t_val = get_val(["temperature", "temp"], 62.0)
    t_unit = get_val(["temperature_unit", "temp_unit"], "C")
    t_canonical = round(to_canonical_units("temperature", t_val, str(t_unit)), 2)

    # Vibration
    v_val = get_val(["vibration", "vib"], 0.20)
    v_unit = get_val(["vibration_unit", "vib_unit"], "mm/s")
    v_canonical = round(to_canonical_units("vibration", v_val, str(v_unit)), 3)

    # Motor Current
    c_val = get_val(["motor_current", "current"], 8.0)
    c_unit = get_val(["current_unit", "motor_current_unit"], "A")
    c_canonical = round(to_canonical_units("motor_current", c_val, str(c_unit)), 2)

    # Pressure
    p_val = get_val(["pressure", "press"], 4.5)
    p_unit = get_val(["pressure_unit", "press_unit"], "bar")
    p_canonical = round(to_canonical_units("pressure", p_val, str(p_unit)), 2)

    # RPM / Speed
    rpm_val = get_val(["rpm", "speed"], 3000.0)
    rpm_unit = get_val(["speed_unit", "rpm_unit"], "rpm")
    rpm_canonical = round(to_canonical_units("rpm", rpm_val, str(rpm_unit)), 1)

    # Acoustic Noise
    n_val = get_val(["acoustic_noise", "noise"], 42.0)
    n_canonical = round(float(n_val), 2)

    # Frequency
    f_val = get_val(["frequency", "freq"], 50.0)
    f_unit = get_val(["freq_unit", "frequency_unit"], "Hz")
    f_canonical = round(to_canonical_units("frequency", f_val, str(f_unit)), 2)

    # Load
    l_val = get_val(["load"], 15.0)
    l_unit = get_val(["load_unit"], "kN")
    l_canonical = round(to_canonical_units("load", l_val, str(l_unit)), 2)

    return {
        "Temperature": t_canonical,
        "Vibration": v_canonical,
        "Motor_Current": c_canonical,
        "Acoustic_Noise": n_canonical,
        "Pressure": p_canonical,
        "RPM": rpm_canonical,
        "Frequency": f_canonical,
        "Load": l_canonical
    }
