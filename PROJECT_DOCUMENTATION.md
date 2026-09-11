# Industrial Predictive Maintenance Platform
## Comprehensive Software Engineering, AI/ML & System Design Technical Master Reference Document

---

## Executive Summary & Architecture Overview

This platform is an enterprise-grade industrial predictive maintenance solution designed to monitor mechanical assets in real time, predict Remaining Useful Life (RUL) using ensemble machine learning, translate failure predictions into actionable servicing policies using an intelligent Maintenance Decision Engine, detect equipment degradation before failure occurs, and provide interactive visual analytics to plant operators.

### System Architecture Flow Diagram (Single AI Model + Decision Engine)
```
Real Machine ──①──> IoT Sensor ──②──> MQTT/Kafka ──③──> FastAPI Backend
                                                            │
                                                            ▼
                                                 ④ Preprocessing Pipeline
                                                            │
                                                            ▼
                                                 ⑤ Random Forest RUL Model
                                                    (rf_rul_model.pkl)
                                                            │
                                                            ▼
                                                 ⑥ Predicted RUL (Days)
                                                            │
                                                            ▼
                                                 ⑦ Maintenance Decision Engine
                                                    (maintenance_engine.py)
                                                            │
                                                            ▼
                                                 ⑧ Status + Recommendation + Priority
                                                            │
                                                            ▼
                                                 ⑨ REST API (/api/current & /api/maintenance)
                                                            │
                                                            ▼
                                                 ⑩ React Dashboard Visualizer (4 Views)
```

---

# PART 1: Module-by-Module Source Code Breakdown

---

## 1. Backend Modules (Python / FastAPI / Scikit-Learn)

### 1.1 `main.py`
* **File Path**: [main.py](file:///c:/Users/shiva/.gemini/antigravity/scratch/predictive_maintenance/main.py)
1. **Why this file exists**: Primary orchestrator and entry point for the backend REST API service.
2. **What problem it solves**: Connects telemetry simulation, feature preprocessing, single Random Forest ML inference, decision engine evaluation, and async HTTP request handling.
3. **Classes and Functions Present**:
   - `SimulationState` (Class): Holds runtime simulation state (`auto_play`, `simulation_speed`, `history_records`).
   - `PredictRequest` (Pydantic Class): Schema validator for single-point prediction HTTP payloads.
   - `ControlAction` (Pydantic Class): Schema validator for simulation control actions.
   - `generate_next_telemetry_step()`: Ticks simulator by 1 step, predicts RUL via ML model, evaluates Maintenance Decision Engine, and appends to history.
   - Route Handlers: `get_status()`, `get_current()`, `get_history()`, `get_maintenance_status()`, `predict_rul()`, `get_model_evaluation()`, `get_logs()`, `control_simulation()`.
4. **Input and Output of Key Functions**:
   - `generate_next_telemetry_step()`: **Input**: None. **Output**: Telemetry record dict with `Predicted_RUL`, `Maintenance_Status`, `Recommended_Action`, `Inspection_Priority`, and `Next_Inspection_Window`.
   - `get_maintenance_status()`: **Input**: None. **Output**: JSON dict (`predicted_rul_days`, `machine_health`, `maintenance_status`, `recommended_action`, `inspection_priority`, `next_inspection_window`).
5. **How Data Flows Through This File**:
   `simulation_clock_loop` $\rightarrow$ `generate_next_telemetry_step()` $\rightarrow$ `sim_engine.step()` $\rightarrow$ `model_service.predict_rul()` $\rightarrow$ `get_maintenance_recommendation()` $\rightarrow$ `sim_state.history_records` $\rightarrow$ REST routes $\rightarrow$ HTTP JSON responses.
6. **Which Other Files Call It**: Executed directly by Uvicorn server (`uvicorn main:app --reload`).
7. **Which Files It Depends On**: `simulator/simulator.py`, `model/predict.py`, `model/maintenance_engine.py`, `preprocessing/preprocessing.py`, `utils/utils.py`.
8. **Why Implementation Was Chosen**: FastAPI handles concurrent async HTTP requests and background tasks on a single event loop without thread locking.
9. **What Would Happen If Removed**: The backend REST service vanishes; the frontend receives connection timeouts.
10. **Possible Future Improvements**: Replace in-memory array storage with TimescaleDB; add WebSockets for push streaming.

---

### 1.2 `simulator/simulator.py`
* **File Path**: [simulator/simulator.py](file:///c:/Users/shiva/.gemini/antigravity/scratch/predictive_maintenance/simulator/simulator.py)
1. **Why this file exists**: Real-time physical machine simulation engine.
2. **What problem it solves**: Generates continuous mechanical sensor stream data, degradation trends, random industrial anomaly events, single-source-of-truth Machine Health, and dynamic non-linear ground-truth RUL countdowns without physical equipment.
3. **Classes and Functions Present**:
   - `RealTimeMachineSimulator(max_lifespan_days=1000, degradation_factor=1.8)`: Main engine state machine.
   - `reset()`: Re-initializes baseline machine state ($T=35^\circ\text{C}, V=0.20\text{ mm/s}, I=8.0\text{ A}, H=100\%, \text{RUL}=1000\text{ days}$).
   - `_evaluate_stage()`, `_trigger_random_event()`, `step()`.
4. **Input and Output**: **Output**: Clean physical telemetry output ($T, V, I, H, \text{RUL}_{\text{actual}}$) with Gaussian noise.

---

### 1.3 `model/maintenance_engine.py`
* **File Path**: [model/maintenance_engine.py](file:///c:/Users/shiva/.gemini/antigravity/scratch/predictive_maintenance/model/maintenance_engine.py)
1. **Why this file exists**: Rule-based decision support layer for preventive maintenance scheduling.
2. **What problem it solves**: Translates the ML predicted Remaining Useful Life (RUL) and current machine operating health into actionable industrial maintenance recommendations, inspection priorities, and next servicing windows.
3. **Classes and Functions Present**:
   - `get_maintenance_recommendation(predicted_rul, machine_health=100.0, active_event="None")`: Evaluates threshold decision logic and returns servicing recommendations.
4. **Input and Output**:
   - **Input**: `predicted_rul` (float), `machine_health` (float), `active_event` (str).
   - **Output**: Dictionary (`maintenance_status`, `recommended_action`, `inspection_priority`, `next_inspection_window`).
5. **Why Implementation Was Chosen**: In enterprise industrial PDM systems, machine learning models predict failure timing, while rule-based decision engines apply company-specific maintenance policies. This eliminates duplicate ML models and provides deterministic servicing guidelines.

---

## 2. Frontend Modules (React + Vite + Plotly)

### 2.1 Pages & Display Components Summary

| File Path | Primary Role | Key Components / Libraries Used | Data Inputs | Output / Render |
| :--- | :--- | :--- | :--- | :--- |
| [Dashboard.jsx](file:///c:/Users/shiva/.gemini/antigravity/scratch/predictive_maintenance/frontend/src/pages/Dashboard.jsx) | Live Telemetry & Failure RUL Monitoring | `GaugeCard`, `MetricCard`, `LiveChart`, `SensorTable` | `currentData`, `historyData`, `logs` | Single-page grid layout for live operations |
| [Analytics.jsx](file:///c:/Users/shiva/.gemini/antigravity/scratch/predictive_maintenance/frontend/src/pages/Analytics.jsx) | Historical & Trend Projections | `AnalyticsCharts` | `historyData` | Multi-chart comparative trend analysis view |
| [Maintenance.jsx](file:///c:/Users/shiva/.gemini/antigravity/scratch/predictive_maintenance/frontend/src/pages/Maintenance.jsx) | Engineer Maintenance Decision Support View | `MaintenanceDashboard` | `maintenanceData`, `historyData` | RUL card, status badge, recommended action, inspection priority card & 5 trend charts |
| [Evaluation.jsx](file:///c:/Users/shiva/.gemini/antigravity/scratch/predictive_maintenance/frontend/src/pages/Evaluation.jsx) | Model Diagnostics View | `ModelEvaluation` | `modelData` | ML metrics, scatter plot, and residual histogram |
| [TopBar.jsx](file:///c:/Users/shiva/.gemini/antigravity/scratch/predictive_maintenance/frontend/src/components/TopBar.jsx) | Global System Header Bar | `lucide-react` | `backendStatus`, `statusData` | Machine metadata, live clock, status badge |
| [Sidebar.jsx](file:///c:/Users/shiva/.gemini/antigravity/scratch/predictive_maintenance/frontend/src/components/Sidebar.jsx) | Navigation & Control Panel | `StatusBadge`, `lucide-react` | `currentData`, `speed`, `autoPlay` | 4-tab menu (Dashboard, Analytics, Maintenance, Evaluation), speed slider |
| [MaintenanceDashboard.jsx](file:///c:/Users/shiva/.gemini/antigravity/scratch/predictive_maintenance/frontend/src/components/MaintenanceDashboard.jsx) | Maintenance Decision Dashboard | `MetricCard`, `StatusBadge`, `react-plotly.js` | `maintenanceData`, `historyData` | Predicted RUL, Status, Action, Priority cards & 5 real-time trend plots |

---

# PART 2: System Architecture & Tech Stack Deep-Dive

---

## 1. Maintenance Decision Engine Policy Matrix

The `Maintenance Decision Engine` maps predicted RUL and operating health to actionable servicing guidelines:

| Predicted RUL | Maintenance Status | Recommended Action | Inspection Priority | Next Inspection Window |
| :--- | :--- | :--- | :--- | :--- |
| **> 700 Days** | Healthy | Continue Normal Operation | Low | Routine inspection within 180 days |
| **400 – 700 Days** | Monitor | Increase monitoring frequency | Moderate | Inspect within 90 days |
| **150 – 400 Days** | Preventive Maintenance | Schedule maintenance | High | Schedule maintenance within 30 days |
| **30 – 150 Days** | Warning | Maintenance required soon | Urgent | Perform servicing within 7 days |
| **< 30 Days** | Critical | Immediate maintenance | Critical | Stop machine before failure |

---

## 2. Single AI Model + Decision Support Layer Architecture

The platform uses **one machine learning model** and **one decision engine**:
1. **Random Forest RUL Model (`models/rf_rul_model.pkl`)**:
   - **Question Answered**: *"How long before the machine is likely to fail?"*
   - **Method**: Machine learning regression on normalized telemetry streams ($R^2 = 0.9999$).
2. **Maintenance Decision Engine (`model/maintenance_engine.py`)**:
   - **Question Answered**: *"What should engineers do based on that prediction?"*
   - **Method**: Policy rule engine translating predicted RUL into servicing actions, priorities, and inspection schedules.

---

# PART 3: Comprehensive Interview Q&A

### Q1: Explain your entire project in 5 minutes.
> "This project is an enterprise-grade Industrial Predictive Maintenance Platform engineered to monitor mechanical assets in real time, predict Remaining Useful Life (RUL) using ensemble machine learning, translate predictions into servicing guidelines via a Maintenance Decision Engine, and visualize industrial health metrics on an interactive executive dashboard.
> 
> The architecture consists of three core layers:
> 1. Physics Telemetry Simulator: Models non-linear thermal, vibration, and current degradation curves (P-F curve), injects stochastic anomaly events, derives Machine Health as single source of truth, and dynamically computes ground-truth failure RUL.
> 2. FastAPI & Scikit-Learn Backend: An async Python microservice featuring a single pre-trained Random Forest Regressor ($R^2 = 0.9999$, MAE = 1.98 Days) that predicts RUL from telemetry, coupled with a Maintenance Decision Engine that maps predicted RUL into maintenance status, recommended actions, inspection priorities, and servicing windows.
> 3. React + Vite Dashboard: Built with Tailwind CSS and Plotly.js, featuring a 1000ms decoupled polling loop across 4 navigation views (Live Monitoring, Historical Analytics, Maintenance Decision Support, and Model Diagnostics)."

---

### Q2: Why does the system use only ONE AI model instead of two?
> "In real industrial predictive maintenance applications, machine learning models are trained to solve complex physical regression tasks (predicting Remaining Useful Life).
> 
> Training a second ML model to predict maintenance days creates unnecessary redundancy and potential contradictions between two models.
> 
> Instead, standard industrial PdM architecture uses a single AI model to predict RUL, and an intelligent rule-based Maintenance Decision Engine to convert that RUL prediction into plant servicing policy guidelines. This produces a cleaner, deterministic, and enterprise-aligned predictive maintenance system."

---

### Q3: What questions does this system answer for plant operators?
> "1. *'When will this equipment fail?'* $\rightarrow$ Answered by the Random Forest RUL Predictor (`Predicted_RUL`).
> 2. *'What should the engineering team do about it?'* $\rightarrow$ Answered by the Maintenance Decision Engine (`Recommended_Action`, `Inspection_Priority`, `Next_Inspection_Window`)."
