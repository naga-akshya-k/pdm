"""
Trend & Dynamics Feature Extraction.
Computes rolling linear slopes, rate of change, and acceleration over the sliding window.
"""

import numpy as np
from typing import Dict, List

def compute_trend_features(signal: List[float], dt_seconds: float = 1.0, prefix: str = "") -> Dict[str, float]:
    """
    Computes first-order derivative (slope / rate of change) and trend acceleration.
    """
    n = len(signal)
    if n < 2:
        return {
            f"{prefix}slope": 0.0,
            f"{prefix}rate_of_change": 0.0,
            f"{prefix}trend_direction": 0.0,
        }

    arr = np.array(signal, dtype=float)
    t = np.arange(n) * dt_seconds

    # Linear regression slope: dy / dt
    t_mean = np.mean(t)
    arr_mean = np.mean(arr)
    denom = np.sum((t - t_mean) ** 2)

    if denom > 1e-6:
        slope = float(np.sum((t - t_mean) * (arr - arr_mean)) / denom)
    else:
        slope = 0.0

    # Total net delta / total elapsed time
    total_time = (n - 1) * dt_seconds
    roc = float((arr[-1] - arr[0]) / total_time) if total_time > 0 else 0.0

    # Direction: +1 if increasing, -1 if decreasing, 0 if flat
    direction = 1.0 if slope > 0.001 else (-1.0 if slope < -0.001 else 0.0)

    return {
        f"{prefix}slope": round(slope, 5),
        f"{prefix}rate_of_change": round(roc, 5),
        f"{prefix}trend_direction": direction,
    }
