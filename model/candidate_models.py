import os
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import permutation_importance

FEATURE_COLS = [
    "Temperature",
    "Vibration",
    "Motor_Current",
    "Acoustic_Noise",
    "Pressure",
    "RPM",
    "Frequency",
    "Load"
]

TARGET_COL = "Remaining_Useful_Life_Days"

class MultiModelAIEngine:
    """
    Manages training, benchmarking, inference, and hot-swapping across 4 AI Candidate Models:
      1. Random Forest Regressor
      2. Gradient Boosting Regressor
      3. Multi-Layer Perceptron (MLP Neural Net)
      4. Support Vector Regressor (SVR)
    """
    def __init__(self, models_dir=None):
        if models_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.models_dir = os.path.join(base_dir, "models")
        else:
            self.models_dir = models_dir

        os.makedirs(self.models_dir, exist_ok=True)
        self.scaler_path = os.path.join(self.models_dir, "industrial_scaler.pkl")
        self.scaler = None
        self.models = {}
        self.benchmarks = {}
        self.active_model_name = "Random Forest"
        self.model_version = "1.0"
        self.last_trained_timestamp = None

        self._load_or_train_all_candidates()

    def _generate_synthetic_training_data(self, n_samples=3500):
        """Generates physics-aligned multi-channel training telemetry across fleet profiles."""
        np.random.seed(42)
        records = []
        
        # Base fleet types
        profiles = [
            {"t": 62.0, "v": 0.20, "c": 8.0, "n": 42.0, "p": 4.5, "rpm": 3000.0, "f": 50.0, "l": 15.0, "max_life": 365},
            {"t": 48.0, "v": 0.35, "c": 14.2, "n": 55.0, "p": 12.0, "rpm": 1450.0, "f": 24.2, "l": 8.5, "max_life": 300},
            {"t": 75.0, "v": 0.42, "c": 22.0, "n": 68.0, "p": 28.5, "rpm": 980.0, "f": 16.3, "l": 32.0, "max_life": 420},
            {"t": 38.0, "v": 0.12, "c": 5.5, "n": 38.0, "p": 6.0, "rpm": 12000.0, "f": 200.0, "l": 3.2, "max_life": 250},
        ]

        samples_per_profile = n_samples // len(profiles)
        for prof in profiles:
            max_life = prof["max_life"]
            days = np.linspace(1, max_life, samples_per_profile)
            for d in days:
                wear_frac = max(0.0, (d - max_life * 0.4) / (max_life * 0.6))
                p = wear_frac ** 1.7
                rul = max(0, int(max_life - d))

                temp = prof["t"] + 18.0 * p + np.random.normal(0, 0.4 + 1.2 * p)
                vib = prof["v"] + 4.5 * p + np.random.normal(0, 0.03 + 0.25 * p)
                curr = prof["c"] + 9.0 * p + np.random.normal(0, 0.06 + 0.35 * p)
                noise = prof["n"] + 32.0 * p + np.random.normal(0, 0.6 + 2.5 * p)
                pressure = prof["p"] * (1.0 - 0.28 * p) + np.random.normal(0, 0.2 + 0.6 * p)
                rpm = prof["rpm"] * (1.0 - 0.08 * p) + np.random.normal(0, 15.0)
                freq = prof["f"] * (1.0 + 0.12 * p) + np.random.normal(0, 0.25)
                load = prof["l"] * (1.0 + 0.20 * p) + np.random.normal(0, 0.3)

                records.append({
                    "Temperature": temp,
                    "Vibration": max(0.01, vib),
                    "Motor_Current": max(1.0, curr),
                    "Acoustic_Noise": max(20.0, noise),
                    "Pressure": max(0.1, pressure),
                    "RPM": max(50.0, rpm),
                    "Frequency": max(1.0, freq),
                    "Load": max(0.5, load),
                    "Remaining_Useful_Life_Days": rul
                })

        return pd.DataFrame(records)

    def train_all_models(self, df=None):
        """Trains and benchmarks all 4 candidate models with standardized metrics."""
        if df is None:
            df = self._generate_synthetic_training_data()

        X = df[FEATURE_COLS]
        y = df[TARGET_COL]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        joblib.dump(self.scaler, self.scaler_path)

        candidate_defs = {
            "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=14, random_state=42, n_jobs=-1),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=5, random_state=42),
            "MLP Neural Net": MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, early_stopping=True, alpha=0.01, random_state=42),
            "SVR (Support Vector)": SVR(C=100.0, epsilon=2.0, kernel="rbf")
        }

        benchmarks = {}
        for name, model in candidate_defs.items():
            t0 = time.time()
            model.fit(X_train_scaled, y_train)
            train_duration = time.time() - t0

            # Measure test inference latency
            t_infer = time.time()
            y_pred = model.predict(X_test_scaled)
            infer_latency_ms = round(((time.time() - t_infer) / len(X_test_scaled)) * 1000, 3)

            mae = float(mean_absolute_error(y_test, y_pred))
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
            r2 = float(r2_score(y_test, y_pred))

            # Feature importance calculation
            if hasattr(model, "feature_importances_"):
                imps = model.feature_importances_.tolist()
            else:
                # Permutation importance for SVR / MLP (subset for speed)
                perm = permutation_importance(model, X_test_scaled[:200], y_test.iloc[:200], n_repeats=3, random_state=42)
                imps = [max(0.0, float(x)) for x in perm.importances_mean]
                total = sum(imps) if sum(imps) > 0 else 1.0
                imps = [x / total for x in imps]

            feature_importance = [
                {"feature": feat, "importance": round(float(imp), 4)}
                for feat, imp in zip(FEATURE_COLS, imps)
            ]

            # Save model
            model_file = os.path.join(self.models_dir, f"candidate_{name.replace(' ', '_').lower()}.pkl")
            joblib.dump(model, model_file)
            self.models[name] = model

            benchmarks[name] = {
                "name": name,
                "mae": round(mae, 2),
                "rmse": round(rmse, 2),
                "r2_score": round(r2, 4),
                "inference_latency_ms": infer_latency_ms,
                "train_duration_sec": round(train_duration, 2),
                "feature_importance": feature_importance,
                "is_active": (name == self.active_model_name),
                "model_version": self.model_version
            }

        self.benchmarks = benchmarks
        self.last_trained_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return benchmarks

    def _load_or_train_all_candidates(self):
        """Loads saved models if available, otherwise runs training."""
        model_names = ["Random Forest", "Gradient Boosting", "MLP Neural Net", "SVR (Support Vector)"]
        all_exist = os.path.exists(self.scaler_path)
        for name in model_names:
            model_file = os.path.join(self.models_dir, f"candidate_{name.replace(' ', '_').lower()}.pkl")
            if not os.path.exists(model_file):
                all_exist = False
                break

        if all_exist:
            try:
                self.scaler = joblib.load(self.scaler_path)
                for name in model_names:
                    model_file = os.path.join(self.models_dir, f"candidate_{name.replace(' ', '_').lower()}.pkl")
                    self.models[name] = joblib.load(model_file)
                # Generate benchmark stats
                self.train_all_models()
            except Exception:
                self.train_all_models()
        else:
            self.train_all_models()

    def predict_rul(self, sensor_dict, model_name=None):
        """
        Runs RUL prediction using the specified or active candidate model.
        Accepts full 8-sensor dict or fallback 3-sensor dict.
        """
        target_model_name = model_name if model_name in self.models else self.active_model_name
        model = self.models.get(target_model_name)

        if not model or not self.scaler:
            return 0, 0.0

        # Construct vector for all 8 features
        row = {
            "Temperature": float(sensor_dict.get("Temperature", 62.0)),
            "Vibration": float(sensor_dict.get("Vibration", 0.20)),
            "Motor_Current": float(sensor_dict.get("Motor_Current", 8.0)),
            "Acoustic_Noise": float(sensor_dict.get("Acoustic_Noise", 42.0)),
            "Pressure": float(sensor_dict.get("Pressure", 4.5)),
            "RPM": float(sensor_dict.get("RPM", 3000.0)),
            "Frequency": float(sensor_dict.get("Frequency", 50.0)),
            "Load": float(sensor_dict.get("Load", 15.0))
        }

        df = pd.DataFrame([row])[FEATURE_COLS]
        X_scaled = self.scaler.transform(df)

        t0 = time.time()
        pred = model.predict(X_scaled)[0]
        latency_ms = round((time.time() - t0) * 1000, 3)

        return max(0, int(round(pred))), latency_ms

    def set_active_model(self, model_name: str):
        if model_name in self.models:
            self.active_model_name = model_name
            for k in self.benchmarks:
                self.benchmarks[k]["is_active"] = (k == model_name)
            return {"status": "success", "active_model": model_name}
        return {"status": "error", "message": f"Model {model_name} not available"}
