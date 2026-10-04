"""
Frequency-Domain FFT Feature Extraction.
Computes spectral energy, dominant frequency peak, and spectral centroid from raw signals.
"""

import numpy as np
from typing import Dict, List

def compute_frequency_domain_features(signal: List[float], sampling_rate_hz: float = 1.0, prefix: str = "") -> Dict[str, float]:
    """
    Performs FFT analysis over a time-series window to extract spectral characteristics.
    """
    n = len(signal)
    if n < 4:
        return {
            f"{prefix}dominant_freq": 0.0,
            f"{prefix}spectral_energy": 0.0,
            f"{prefix}spectral_centroid": 0.0,
        }

    arr = np.array(signal, dtype=float)
    # Remove DC component (mean centering)
    arr_centered = arr - np.mean(arr)

    # Compute Fast Fourier Transform
    fft_vals = np.fft.rfft(arr_centered)
    fft_magnitudes = np.abs(fft_vals)
    freqs = np.fft.rfftfreq(n, d=1.0 / sampling_rate_hz)

    # Total spectral power / energy
    spectral_energy = float(np.sum(fft_magnitudes ** 2) / n)

    # Dominant peak frequency (excluding zero-frequency bin)
    if len(fft_magnitudes) > 1:
        peak_idx = int(np.argmax(fft_magnitudes[1:])) + 1
        dominant_freq = float(freqs[peak_idx])
    else:
        dominant_freq = 0.0

    # Spectral centroid (center of mass of the spectrum)
    sum_mag = np.sum(fft_magnitudes)
    if sum_mag > 1e-6:
        spectral_centroid = float(np.sum(freqs * fft_magnitudes) / sum_mag)
    else:
        spectral_centroid = 0.0

    return {
        f"{prefix}dominant_freq": round(dominant_freq, 3),
        f"{prefix}spectral_energy": round(spectral_energy, 4),
        f"{prefix}spectral_centroid": round(spectral_centroid, 3),
    }
