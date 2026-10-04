"""
Time-Domain Statistical & Vibration Feature Extraction.
Computes RMS, Variance, Kurtosis, Skewness, Peak, Peak-to-Peak, and Crest Factor.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Any

def compute_time_domain_features(signal: List[float], prefix: str = "") -> Dict[str, float]:
    """
    Computes statistical and dynamic time-domain indicators over a numeric 1D time series.
    """
    if not signal or len(signal) < 2:
        val = float(signal[0]) if signal else 0.0
        return {
            f"{prefix}mean": val,
            f"{prefix}rms": val,
            f"{prefix}std": 0.0,
            f"{prefix}peak": val,
            f"{prefix}p2p": 0.0,
            f"{prefix}kurtosis": 3.0,
            f"{prefix}skewness": 0.0,
            f"{prefix}crest_factor": 1.0,
        }

    arr = np.array(signal, dtype=float)
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))
    rms_val = float(np.sqrt(np.mean(arr ** 2)))
    peak_val = float(np.max(np.abs(arr)))
    p2p_val = float(np.max(arr) - np.min(arr))

    # Higher-order statistical moments
    skew_val = float(stats.skew(arr)) if std_val > 1e-6 else 0.0
    kurt_val = float(stats.kurtosis(arr, fisher=False)) if std_val > 1e-6 else 3.0  # Pearson kurtosis (Normal = 3.0)

    # Dimensionless vibration ratios
    crest_factor = float(peak_val / rms_val) if rms_val > 1e-6 else 1.0

    return {
        f"{prefix}mean": round(mean_val, 4),
        f"{prefix}rms": round(rms_val, 4),
        f"{prefix}std": round(std_val, 4),
        f"{prefix}peak": round(peak_val, 4),
        f"{prefix}p2p": round(p2p_val, 4),
        f"{prefix}kurtosis": round(kurt_val, 4),
        f"{prefix}skewness": round(skew_val, 4),
        f"{prefix}crest_factor": round(crest_factor, 4),
    }
