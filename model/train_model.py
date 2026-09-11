import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import numpy as np
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for folder in ['preprocessing', 'model', 'utils']:
    folder_path = os.path.join(base_dir, folder)
    if os.path.exists(folder_path) and folder_path not in sys.path:
        sys.path.append(folder_path)
if base_dir not in sys.path:
    sys.path.append(base_dir)

from preprocessing import load_data, preprocess_data

def train():
    print("Loading data...")
    df = load_data()
    
    print("Preprocessing data...")
    X_train_scaled, X_test_scaled, y_train, y_test = preprocess_data(df, is_training=True)
    
    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    print("Evaluating model...")
    y_train_pred = model.predict(X_train_scaled)
    y_pred = model.predict(X_test_scaled)
    
    train_r2 = r2_score(y_train, y_train_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    test_r2 = r2_score(y_test, y_pred)
    
    print(f"--- Evaluation Metrics ---")
    print(f"Training R²: {train_r2:.4f}")
    print(f"Testing R²:  {test_r2:.4f}")
    print(f"MAE:         {mae:.2f} Days")
    print(f"RMSE:        {rmse:.2f} Days")
    
    print("Saving trained model...")
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "rf_rul_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
