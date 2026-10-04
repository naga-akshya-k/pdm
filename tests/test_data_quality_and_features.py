"""
Unit Tests for Data Quality, Unit Normalization, and Feature Engineering.
"""

import datetime
from backend.data.validation import DataQualityValidator
from backend.features.time_domain import compute_time_domain_features
from backend.features.frequency_domain import compute_frequency_domain_features
from backend.features.trends import compute_trend_features
from backend.features.window_buffer import MachineWindowBuffer

def test_unit_normalization():
    validator = DataQualityValidator()
    # °F to °C
    c, u = validator.normalize_units("Temperature", 212.0, "degF")
    assert round(c, 1) == 100.0
    assert u == "°C"

    # psi to bar
    bar, u = validator.normalize_units("Pressure", 100.0, "psi")
    assert round(bar, 1) == 6.9
    assert u == "bar"

    # in/s to mm/s
    mms, u = validator.normalize_units("Vibration", 1.0, "in/s")
    assert round(mms, 1) == 25.4
    assert u == "mm/s"

def test_hardware_fault_vs_mechanical_anomaly():
    validator = DataQualityValidator()
    # Negative vibration RMS is physical impossible hardware error
    feats, flags = validator.validate_features("M1", {"Vibration": -2.5}, datetime.datetime.utcnow())
    assert flags["data_quality"] == "SENSOR_HARDWARE_FAULT"
    assert len(flags["sensor_hardware_errors"]) > 0

def test_time_domain_features():
    signal = [1.0, 2.0, 3.0, 4.0, 5.0]
    td = compute_time_domain_features(signal, prefix="sig_")
    assert td["sig_mean"] == 3.0
    assert td["sig_peak"] == 5.0
    assert td["sig_p2p"] == 4.0
    assert td["sig_rms"] > 3.0

def test_frequency_domain_features():
    # Construct 10 Hz pure sine wave
    import numpy as np
    t = np.linspace(0, 1, 100)
    sig = np.sin(2 * np.pi * 10 * t)
    fd = compute_frequency_domain_features(list(sig), sampling_rate_hz=100.0)
    assert abs(fd["dominant_freq"] - 10.0) <= 1.0
    assert fd["spectral_energy"] > 0.0

def test_trend_slope():
    sig = [10.0, 12.0, 14.0, 16.0, 18.0]
    tr = compute_trend_features(sig, dt_seconds=1.0)
    assert round(tr["slope"], 1) == 2.0
    assert tr["trend_direction"] == 1.0

def test_window_buffer():
    buf = MachineWindowBuffer(window_size=5)
    for i in range(5):
        buf.append_sample("M1", f"2026-10-04T12:00:0{i}Z", {"Vibration": 0.2 + i * 0.1, "Temperature": 50.0})
    extracted = buf.extract_window_features("M1")
    assert "Vibration_mean" in extracted
    assert "Vib_FFT_dominant_freq" in extracted
