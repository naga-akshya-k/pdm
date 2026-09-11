import time
import pandas as pd
from typing import List, Dict

class RegenerativeAIPipeline:
    """
    Closed-Loop Regenerative AI & Model Governance Layer (Section 9 Architecture Spec).
    Manages automated drift-triggered retraining, candidate evaluation, engineering approval,
    and hot-deployment of updated model versions.
    """
    def __init__(self, ai_engine, drift_detector):
        self.ai_engine = ai_engine
        self.drift_detector = drift_detector
        self.pipeline_state = "IDLE"  # IDLE, RETRAINING, VALIDATION_REQUIRED, DEPLOYED
        self.candidate_benchmarks = {}
        self.last_pipeline_run = None
        self.version_history = [
            {
                "version": "1.0",
                "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "model_name": "Random Forest",
                "mae": 28.5,
                "rmse": 39.2,
                "r2_score": 0.865,
                "approver": "System Initializer",
                "notes": "Initial factory commissioning model"
            }
        ]
        self.current_version = "1.0"

    def trigger_retraining(self, recent_history_records: List[Dict]):
        """
        Step 3: Trigger controlled retraining of all candidate models
        using cumulative operational telemetry and synthetic physics augmentation.
        """
        self.pipeline_state = "RETRAINING"
        t0 = time.time()

        # Combine recent operational telemetry with physics baseline data
        base_df = self.ai_engine._generate_synthetic_training_data(n_samples=2500)
        
        if recent_history_records and len(recent_history_records) >= 15:
            # Map recent records to training format
            op_rows = []
            for r in recent_history_records:
                if "Remaining_Useful_Life_Days" in r:
                    op_rows.append({
                        "Temperature": float(r.get("Temperature", 62.0)),
                        "Vibration": float(r.get("Vibration", 0.20)),
                        "Motor_Current": float(r.get("Motor_Current", 8.0)),
                        "Acoustic_Noise": float(r.get("Acoustic_Noise", 42.0)),
                        "Pressure": float(r.get("Pressure", 4.5)),
                        "RPM": float(r.get("RPM", 3000.0)),
                        "Frequency": float(r.get("Frequency", 50.0)),
                        "Load": float(r.get("Load", 15.0)),
                        "Remaining_Useful_Life_Days": int(r.get("Remaining_Useful_Life_Days", 0))
                    })
            if op_rows:
                op_df = pd.DataFrame(op_rows)
                # Over-weight recent operational experiences for domain adaptation
                combined_df = pd.concat([base_df, op_df, op_df, op_df], ignore_index=True)
            else:
                combined_df = base_df
        else:
            combined_df = base_df

        # Step 4: Retrain and compare candidates on MAE, RMSE, R2, Latency
        benchmarks = self.ai_engine.train_all_models(combined_df)
        self.candidate_benchmarks = benchmarks
        self.pipeline_state = "VALIDATION_REQUIRED"
        self.last_pipeline_run = time.strftime("%Y-%m-%d %H:%M:%S")

        # Find top performing candidate
        best_candidate = max(benchmarks.values(), key=lambda x: x["r2_score"])

        return {
            "status": "success",
            "pipeline_state": self.pipeline_state,
            "duration_sec": round(time.time() - t0, 2),
            "candidates": benchmarks,
            "recommended_candidate": best_candidate["name"],
            "timestamp": self.last_pipeline_run
        }

    def get_pipeline_status(self):
        """Returns current status of the Regenerative AI pipeline and version history."""
        active_model = self.ai_engine.active_model_name
        current_bm = self.ai_engine.benchmarks.get(active_model, {})

        return {
            "pipeline_state": self.pipeline_state,
            "current_production_version": self.current_version,
            "active_model_name": active_model,
            "current_metrics": {
                "mae": current_bm.get("mae", 28.5),
                "rmse": current_bm.get("rmse", 39.2),
                "r2_score": current_bm.get("r2_score", 0.865),
                "latency_ms": current_bm.get("inference_latency_ms", 1.2)
            },
            "candidates": self.candidate_benchmarks if self.candidate_benchmarks else self.ai_engine.benchmarks,
            "version_history": self.version_history,
            "last_pipeline_run": self.last_pipeline_run
        }

    def deploy_candidate_model(self, candidate_name: str, approver_name: str = "Lead Reliability Engineer", notes: str = ""):
        """
        Step 6 & 7: Controlled deployment of approved candidate model under new version tag.
        """
        if candidate_name not in self.ai_engine.models:
            return {"status": "error", "message": f"Candidate {candidate_name} not found"}

        # Activate chosen model
        self.ai_engine.set_active_model(candidate_name)

        # Bump version (e.g. 1.0 -> 1.1)
        prev_major, prev_minor = self.current_version.split(".")
        new_version = f"{prev_major}.{int(prev_minor) + 1}"
        self.current_version = new_version
        self.ai_engine.model_version = new_version

        bm = self.ai_engine.benchmarks.get(candidate_name, {})
        version_entry = {
            "version": new_version,
            "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_name": candidate_name,
            "mae": bm.get("mae", 0.0),
            "rmse": bm.get("rmse", 0.0),
            "r2_score": bm.get("r2_score", 0.0),
            "approver": approver_name,
            "notes": notes if notes else f"Regenerative retraining deployment of {candidate_name}"
        }
        self.version_history.insert(0, version_entry)
        self.pipeline_state = "IDLE"

        return {
            "status": "success",
            "message": f"Successfully deployed {candidate_name} as Production Model v{new_version}",
            "deployed_version": new_version,
            "entry": version_entry
        }
