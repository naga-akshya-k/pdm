# Enterprise Industrial Predictive Maintenance Platform (PdM v2.4)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Bundler-Vite-646CFF?logo=vite)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/AI%2FML-Scikit--Learn-F7931E?logo=scikit-learn)](https://scikit-learn.org/)
[![Plotly](https://img.shields.io/badge/Visualization-Plotly-3F4F75?logo=plotly)](https://plotly.com/)
[![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS-38B2D8?logo=tailwindcss)](https://tailwindcss.com/)

An enterprise-grade, dynamic **Industrial Predictive Maintenance and Reliability Platform** featuring Physics-Based Digital Twin telemetry, Multi-Model AI inference & hot-swapping, statistical data/concept drift detection (KS-tests & PSI), closed-loop Regenerative AI retraining with governance sign-off, early failure P-F curve diagnostics, and ISO 13374 Condition-Based CMMS work orders.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    INDUSTRIAL PLANT FLEET                                       │
│   • MCH-802X: Gas Turbine Generator         • PMP-401B: Centrifugal Slurry Pump                 │
│   • CMP-605C: Reciprocating Gas Compressor  • CNC-900D: Precision High-Speed Spindle            │
└────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           PHYSICS-BASED DIGITAL TWIN SCADA TELEMETRY                            │
│   • 8 Telemetry Channels: Temp, Vibration RMS, Motor Current, Acoustic Noise, Pressure,         │
│     RPM, Vibration Frequency, Operating Load                                                    │
│   • Dynamic Fault Injection: Bearing Micro-Spalling, Thermal Runaway, Cavitation, Imbalance     │
│   • Subcomponent Decay: Bearing Assembly, Stator, Rotor Balance, Cooling, Hydraulic Seals       │
└────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    UNIVERSAL TWO-STAGE NORMALIZATION & UNIT STANDARDIZATION                     │
│   Stage 1: Unit Canonicalization (Converts °F → °C, psi → bar, in/s → mm/s, lbf → kN)           │
│   Stage 2: Dimensionless Standardization (z = (x - μ) / σ  ∈ [-3.0σ, +3.0σ])                    │
└────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                 │
         ┌───────────────────────────────────────┴───────────────────────────────────────┐
         ▼                                                                               ▼
┌──────────────────────────────────┐                                   ┌──────────────────────────────────┐
│   EARLY FAILURE & P-F ENGINE     │                                   │     STATISTICAL DRIFT STUDIO     │
│ • Non-Linear P-F Curve Mapping   │                                   │ • 2-Sample KS Hypothesis Tests   │
│   (P1: 45-90d → P2: 15-45d →     │                                   │ • Population Stability Index     │
│    P3: 3-14d → P4: 0-4h → F)     │                                   │   (PSI feature divergence)       │
│ • ISO 10816 Vibration Severity   │                                   │ • Historical Drift Time-Series   │
│ • Root-Cause Sensor Attribution  │                                   │ • Exportable Audit Report (JSON) │
│ • Operator Action Checklist      │                                   └────────────────┬─────────────────┘
└────────────────┬─────────────────┘                                                    │
                 │                                                                      ▼
                 ▼                                                     ┌──────────────────────────────────┐
┌──────────────────────────────────┐                                   │   REGENERATIVE AI & GOVERNANCE   │
│     MULTI-MODEL AI/ML ENGINE     │                                   │ • Automated Model Retraining     │
│ • Random Forest Regressor        │                                   │ • Candidate Leaderboard & Delta  │
│ • Gradient Boosting Regressor    │◄──────────────────────────────────┤ • Engineering Sign-off Workflow  │
│ • Multi-Layer Perceptron (MLP)   │                                   │ • Hot-Deployment & Versioning    │
│ • Support Vector Regressor (SVR) │                                   │   (v1.0 → v1.1 → v2.0)           │
│ • 1-Click Runtime Hot-Swapping   │                                   └──────────────────────────────────┘
└────────────────┬─────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           CMMS MAINTENANCE & WORK ORDER DISPATCHER                              │
│   • ISO 13374 Condition-Based Servicing Matrix (Low, Moderate, Urgent, Critical)                │
│   • Financial Risk ROI: Unplanned Downtime Cost ($USD) vs Preventive Repair Cost & Net Savings  │
│   • Automated Work Order Dispatching with Technician Roles, Spare Parts, and Window Duration    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Features

### 1. 🏭 Multi-Asset Plant Fleet & Fault Sandbox
- Supports 4 industrial machine profiles:
  - `MCH-802X`: Gas Turbine Generator Unit A1 (Power Gen Bay 4)
  - `PMP-401B`: Centrifugal Slurry Pump B2 (Mineral Line 2)
  - `CMP-605C`: Reciprocating Gas Compressor C3 (Petrochemical Unit 1)
  - `CNC-900D`: High-Speed Precision Milling Spindle D4 (Aerospace Cell 3)
- Real-time fault injection: **Bearing Degradation**, **Thermal Runaway**, **Cavitation Surge**, and **Rotor Imbalance**.

### 2. 🚨 Early Failure Detection & ISO 10816 Standards
- **Non-Linear P-F Interval Curve**: Maps degradation from Potential Failure point $P$ to Functional Failure $F$, providing **15 to 90 days of warning lead time**.
- **ISO 10816 Vibration Severity**: Categorizes vibration into Zone A (Good), Zone B (Acceptable), Zone C (Alert), and Zone D (Danger).
- **Multi-Sensor Root Cause Attribution**: Computes percentage contribution of each sensor channel to anomalies.
- **Operator Action Protocols**: Generates checkable maintenance inspection checklists.

### 3. 🧠 Multi-Model AI Predictive Engine
- Benchmarks 4 candidate algorithms side-by-side:
  - **Random Forest Regressor**
  - **Gradient Boosting Regressor**
  - **Multi-Layer Perceptron (MLP Neural Net)**
  - **Support Vector Regressor (SVR with RBF Kernel)**
- Evaluates $R^2$, MAE (Days), RMSE, and inference latency ($\text{ms}$).
- **1-Click Live Model Hot-Swapping** without server restarts.

### 4. 📈 Statistical Model Drift Studio (KS-Test & PSI)
- Evaluates 2-Sample Kolmogorov-Smirnov (KS) hypothesis tests and Population Stability Index (PSI).
- Categorizes Covariate Shift vs. Concept Drift and tracks historical drift timelines.
- 1-click **Export Engineering Audit Report** in structured JSON format.

### 5. 🔄 Closed-Loop Regenerative AI & Model Governance
- Automated drift-triggered retraining on live operational wear data.
- Candidate leaderboard with accuracy delta comparisons ($\Delta R^2$).
- Human-in-the-loop engineering approval and hot-deployment with version tags (`v1.0` $\rightarrow$ `v1.1` $\rightarrow$ `v2.0`).

### 6. 🛠️ CMMS Work Orders & Financial Downtime ROI
- ISO 13374 Condition-Based Servicing policy.
- Automated work order generation with assigned technician roles, spare parts kits, and duration windows.
- Calculates Potential Unplanned Downtime Cost ($USD) vs. Planned Preventive Servicing Cost and Net Cost Avoidance.

### 7. 🌐 Universal Multi-Unit Normalization
- Supports **Metric (`°C, mm/s, bar, kN`)**, **Imperial (`°F, in/s [ips], psi, lbf`)**, and **Dimensionless Z-Scores (`σ`)**.
- Ingestion API automatically normalizes mixed unit payloads.

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Node.js 18+ and npm

### 1. Clone Repository
```bash
git clone https://github.com/naga-akshya-k/pdm.git
cd pdm
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend daemon on port 8001
uvicorn main:app --host 127.0.0.1 --port 8001
```
*API & Swagger Docs available at `http://127.0.0.1:8001/docs`.*

### 3. Frontend Setup
```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite dev server on port 5173
npm run dev -- --port 5173
```
*Operations Dashboard available at `http://localhost:5173`.*

---

## 📁 Repository Structure

```
predictive_maintenance/
├── main.py                     # FastAPI REST API orchestrator & SCADA clock loop
├── simulator/
│   ├── industrial_simulator.py # Multi-asset physics digital twin & fault injector
│   └── simulator.py            # Base single-machine degradation simulator
├── model/
│   ├── candidate_models.py     # Multi-Model AI engine (RF, GBR, MLP, SVR)
│   ├── early_warning_engine.py # P-F curve diagnostics & ISO 10816 standards
│   ├── drift_detector.py       # Statistical KS-tests & PSI drift detector
│   ├── regenerative_ai.py      # Retraining pipeline & model governance
│   └── maintenance_engine.py   # CMMS work orders & financial ROI calculator
├── preprocessing/
│   ├── preprocessing.py        # Z-score standardization & train/test pipeline
│   └── unit_converter.py       # Universal multi-unit conversion engine
├── datasets/
│   ├── sensor_data.csv         # 91,250 run-to-failure telemetry records
│   └── dataset_generator.py    # Synthetic degradation dataset generator
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TopBar.jsx      # Header with universal scale switcher
│   │   │   ├── Sidebar.jsx     # Navigation tabs & SCADA loop controls
│   │   │   ├── Plot.jsx        # Shared Plotly factory component
│   │   │   ├── LiveChart.jsx   # Interactive live telemetry & forecast chart
│   │   │   ├── SensorTable.jsx # Telemetry event log table
│   │   │   └── ErrorBoundary.jsx # React crash prevention wrapper
│   │   ├── pages/
│   │   │   ├── FleetView.jsx          # Plant fleet condition & fault console
│   │   │   ├── EarlyWarningView.jsx   # P-F curve & ISO 10816 diagnostics
│   │   │   ├── Dashboard.jsx          # 8-channel digital twin telemetry
│   │   │   ├── ModelBenchmark.jsx     # AI model comparison & hot-swapping
│   │   │   ├── DriftMonitor.jsx       # Reliability & drift studio (PSI/KS)
│   │   │   ├── RegenerativeStudio.jsx # Closed-loop retraining & governance
│   │   │   └── WorkOrders.jsx         # CMMS work orders & financial ROI
│   │   ├── services/api.js     # Axios API client
│   │   ├── App.jsx             # Root application orchestrator
│   │   └── main.jsx            # React root mount
│   └── package.json
├── requirements.txt
└── README.md
```

---

## 📜 License
This project is licensed under the MIT License.
