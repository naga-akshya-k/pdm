import joblib
import pandas as pd
import numpy as np
import os

class PredictiveMaintenanceModel:
    def __init__(self, model_path="models/rf_rul_model.pkl", scaler_path="models/scaler.pkl"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.exists(model_path):
            alt_model = os.path.join(base_dir, model_path)
            if os.path.exists(alt_model):
                model_path = alt_model
        if not os.path.exists(scaler_path):
            alt_scaler = os.path.join(base_dir, scaler_path)
            if os.path.exists(alt_scaler):
                scaler_path = alt_scaler

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
        else:
            self.model = None
            self.scaler = None

    def predict_rul(self, temperature, vibration, current):
        if not self.model or not self.scaler:
            return 0
            
        df = pd.DataFrame({
            "Temperature": [temperature],
            "Vibration": [vibration],
            "Motor_Current": [current]
        })
        
        X_scaled = self.scaler.transform(df)
        rul_pred = self.model.predict(X_scaled)[0]
        return max(0, int(rul_pred))

def get_future_trend(history_values, steps=20):
    """
    Extrapolates the next `steps` values based on polynomial trend fitting.
    Ensures seamless connection at index 0 to history_values[-1] with growing future uncertainty.
    """
    if len(history_values) < 2:
        return [history_values[-1]] * steps if history_values else [0] * steps
        
    x = np.arange(len(history_values))
    y = np.array(history_values)
    last_val = float(y[-1])
    
    # Fit recent trend (degree 2 polynomial if enough points, else linear)
    window = min(30, len(history_values))
    deg = 2 if window >= 10 else 1
    try:
        coef = np.polyfit(x[-window:], y[-window:], deg)
        poly1d_fn = np.poly1d(coef)
    except:
        coef = np.polyfit(x, y, 1)
        poly1d_fn = np.poly1d(coef)
        
    future_x = np.arange(len(history_values) - 1, len(history_values) - 1 + steps)
    base_future = poly1d_fn(future_x)
    
    # Offset base_future so future_y[0] matches last_val exactly for seamless connection
    offset = last_val - base_future[0]
    base_future = base_future + offset
    
    # Estimate noise / standard deviation from recent residuals
    recent_residuals = y[-window:] - poly1d_fn(x[-window:])
    std_dev = float(np.std(recent_residuals)) if len(recent_residuals) > 1 else 0.5
    std_dev = max(0.15, min(std_dev, 2.5))
    
    # Project into future with growing uncertainty fan
    np.random.seed(42)  # Fixed seed for consistent rendering across polling intervals
    future_y = [round(last_val, 2)]
    for i in range(1, steps):
        uncertainty_factor = (i / steps) * 0.75
        noise = float(np.random.normal(0, std_dev * uncertainty_factor))
        future_y.append(round(float(base_future[i] + noise), 2))
        
    return future_y
