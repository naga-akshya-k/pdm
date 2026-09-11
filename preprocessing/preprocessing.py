import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

def load_data(filepath="datasets/sensor_data.csv"):
    if not os.path.exists(filepath):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alt_path = os.path.join(base_dir, filepath)
        if os.path.exists(alt_path):
            filepath = alt_path
    return pd.DataFrame(pd.read_csv(filepath))

def preprocess_data(df, is_training=True):
    # Missing value handling (Forward Fill)
    df.ffill(inplace=True)
    
    # Feature columns
    feature_cols = ["Temperature", "Vibration", "Motor_Current"]
    
    # Resolve model directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    scaler_path = os.path.join(models_dir, "scaler.pkl")
    
    if is_training:
        target_col = "Remaining_Useful_Life_Days"
        X = df[feature_cols]
        y = df[target_col]
        
        # Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Feature Scaling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Save the scaler for inference
        joblib.dump(scaler, scaler_path)
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    else:
        # Inference mode
        scaler = joblib.load(scaler_path)
        X = df[feature_cols]
        X_scaled = scaler.transform(X)
        return X_scaled

