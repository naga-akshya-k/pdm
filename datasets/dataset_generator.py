import pandas as pd
import datetime
import sys
import os
import random

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
simulator_dir = os.path.join(base_dir, "simulator")
if simulator_dir not in sys.path:
    sys.path.append(simulator_dir)
if base_dir not in sys.path:
    sys.path.append(base_dir)

from simulator import MachineSimulator

def generate_dataset(num_machines=250, records_per_machine=365, output_path="datasets/sensor_data.csv"):
    total_records = num_machines * records_per_machine
    print(f"Generating synthetic training dataset: {num_machines} machines × {records_per_machine} steps ({total_records} total records)...")
    
    start_time = datetime.datetime.now()
    records = []
    
    for m in range(num_machines):
        random.seed(m * 17 + 42)
        
        # 1. Randomize wear onset between Day 140 and Day 160
        degrad_start = random.uniform(140.0, 160.0)
        
        # 2. Randomize degradation speed (Slow = 0.75, Medium = 1.0, Rapid = 1.35)
        speed = random.choice([0.75, 1.0, 1.35])
        
        simulator = MachineSimulator(
            max_lifespan_days=records_per_machine,
            seed=m * 17 + 42,
            degradation_start_day=degrad_start,
            degradation_speed=speed
        )
        machine_start = start_time + datetime.timedelta(days=m * 40)
        current_time = machine_start
        
        for _ in range(records_per_machine):
            data = simulator.step()
            data["Timestamp"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            records.append(data)
            current_time += datetime.timedelta(days=1)
            
    df = pd.DataFrame(records)
    
    # Reorder columns
    cols = ["Timestamp", "Temperature", "Vibration", "Motor_Current", "Machine_Health", "Machine_Status", "Remaining_Useful_Life_Days"]
    df = df[cols]
    
    # Introduce synthetic missing values (2%) for preprocessing validation
    for col in ["Temperature", "Vibration", "Motor_Current"]:
        mask = pd.Series([True] * len(df)).sample(frac=0.02, random_state=42).index
        df.loc[mask, col] = None
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset saved to {output_path}")
    
    # Also update data/sensor_data.csv if path exists or for compatibility
    alt_data_path = os.path.join(base_dir, "data", "sensor_data.csv")
    os.makedirs(os.path.dirname(alt_data_path), exist_ok=True)
    df.to_csv(alt_data_path, index=False)
    print(f"Dataset also copied to {alt_data_path}")

if __name__ == "__main__":
    generate_dataset()
