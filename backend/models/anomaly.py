"""
Industrial Anomaly Detection Engine.
Combines Isolation Forest statistical outliers with multidimensional Mahalanobis / Z-score deviations
to produce continuous anomaly scores and classifications (Normal, Warning, Critical).
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List, Tuple, Optional

class IndustrialAnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42,
            n_jobs=1
        )
        self.is_fitted = False
        self.feature_names = [
            "Temperature", "Vibration", "Motor_Current", "Acoustic_Noise",
            "Pressure", "RPM", "Frequency", "Load"
        ]
        self._fit_default_baseline()

    def _fit_default_baseline(self):
        """Fits Isolation Forest on nominal physics-aligned operating data."""
        np.random.seed(42)
        n_samples = 600
        # Normal nominal ranges for typical industrial machinery
        data = np.zeros((n_samples, len(self.feature_names)))
        data[:, 0] = np.random.normal(62.0, 1.2, n_samples)  # Temp
        data[:, 1] = np.random.normal(0.20, 0.04, n_samples) # Vib
        data[:, 2] = np.random.normal(8.0, 0.3, n_samples)   # Current
        data[:, 3] = np.random.normal(42.0, 1.5, n_samples)  # Acoustic
        data[:, 4] = np.random.normal(4.5, 0.2, n_samples)   # Pressure
        data[:, 5] = np.random.normal(3000.0, 10.0, n_samples) # RPM
        data[:, 6] = np.random.normal(50.0, 0.4, n_samples)  # Frequency
        data[:, 7] = np.random.normal(15.0, 0.5, n_samples)  # Load

        self.model.fit(data)
        self.is_fitted = True

        self.baseline_means = np.mean(data, axis=0)
        self.baseline_stds = np.std(data, axis=0) + 1e-6

    def evaluate_anomaly(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates a window/instantaneous feature vector.
        Returns:
            anomaly_score: float in [0.0, 1.0] (0 = fully nominal, 1.0 = severe anomaly)
            anomaly_status: 'NORMAL', 'WARNING', or 'CRITICAL'
            top_deviations: list of (sensor, z_score) explaining the score
        """
        vec = []
        deviations = []
        for i, feat in enumerate(self.feature_names):
            val = float(features.get(feat, self.baseline_means[i]))
            vec.append(val)
            z = abs((val - self.baseline_means[i]) / self.baseline_stds[i])
            deviations.append((feat, round(z, 2)))

        X = np.array([vec])
        # Isolation Forest decision_function: higher is normal, lower is anomalous
        raw_score = float(self.model.decision_function(X)[0])
        # Map raw decision score into normalized [0.0, 1.0] anomaly metric
        # Typically raw_score is between -0.3 (very anomalous) and +0.25 (very normal)
        norm_anomaly_score = float(np.clip(0.5 - (raw_score * 1.8), 0.0, 1.0))

        # Max z-score factor
        deviations.sort(key=lambda x: x[1], reverse=True)
        max_z = deviations[0][1] if deviations else 0.0

        # Blended anomaly metric with physics deviation
        if max_z > 4.5:
            norm_anomaly_score = max(norm_anomaly_score, min(1.0, 0.5 + (max_z - 4.5) * 0.1))

        if norm_anomaly_score >= 0.72 or max_z >= 6.0:
            status = "CRITICAL"
        elif norm_anomaly_score >= 0.45 or max_z >= 3.0:
            status = "WARNING"
        else:
            status = "NORMAL"

        return {
            "anomaly_score": round(norm_anomaly_score, 3),
            "anomaly_status": status,
            "max_z_score": round(max_z, 2),
            "contributing_sensors": deviations[:3]
        }
