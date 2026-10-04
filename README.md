# Industrial-Grade Predictive Maintenance Platform (PdM v3)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Bundler-Vite-646CFF?logo=vite)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/AI%2FML-Scikit--Learn-F7931E?logo=scikit-learn)](https://scikit-learn.org/)
[![MQTT](https://img.shields.io/badge/Ingestion-Paho--MQTT-660066?logo=eclipse)](https://mqtt.org/)
[![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS-38B2D8?logo=tailwindcss)](https://tailwindcss.com/)

An industrial-grade, time-series **Predictive Maintenance Decision Support Platform** engineered for shared GPU workstation and edge deployments. The platform processes high-cadence mechanical SCADA and PLC sensor streams, applies sliding-window feature engineering, detects statistical anomalies, diagnoses equipment degradation with transparent physical evidence, estimates Remaining Useful Life (RUL) with confidence intervals, monitors data drift, and provides human-in-the-loop MLOps governance.

---

## 🏛️ System Architecture

```text
Industrial Machine (Real Plant Sensor / Edge PLC / SCADA)
        ↓
MQTT Broker (Topic: plant/bay4/+/telemetry)
        ↓
MQTT Consumer (Paho-MQTT v2)
        ↓
Industrial Tag ID Mapping (config/tag_mapping.yaml)
        ↓
Data Validation & Unit Normalization (backend/data/validation.py)
        ↓
Time-Series SQLite Storage (backend/data/storage.py)
        ↓
Sliding Window Buffer & Alignment (backend/features/window_buffer.py)
        ↓
Feature Engineering (Time-Domain, FFT Frequency, Trend Slopes)
        ↓
Anomaly Detection (Isolation Forest & Multi-Z Scores)
        ↓
Fault Diagnosis (Evidence-Backed Attribution Engine)
        ↓
Machine Health Estimation (ISO 10816 Severity Standard)
        ↓
RUL Prediction (Bounded Confidence Interval & Calibration Audit)
        ↓
Drift Monitoring (2-Sample KS-Tests & Population Stability Index)
        ↓
Explainable Maintenance Recommendations (Evidence, Action, Priority)
        ↓
FastAPI Backend (Port 8001)
        ↓
React 19 Operator Dashboard (Port 5173 / 8001)
```

The **exact same downstream time-series ML pipeline processes real MQTT telemetry, simulated digital-twin streams, and historical dataset replays**.

---

## 🚀 Operating Modes & Watchdog Safety

Every session clearly indicates the active operating mode in the header:
- `REAL INDUSTRIAL DATA`: Telemetry actively ingested from factory edge sensors via MQTT.
- `SIMULATION`: Digital twin physics simulator generating non-linear degradation and fault injections.
- `HISTORICAL REPLAY`: Recorded historical run-to-failure telemetry replayed through the same ingestion gateway.

> [!IMPORTANT]
> **Watchdog Safety Policy**: If real MQTT machine telemetry drops for more than **3.0 seconds**, the platform does **NOT** silently mask it with simulation. Instead, it triggers a prominent `REAL TELEMETRY OFFLINE` communication alarm.

---

## 🏷️ Industrial Tag ID Mapping

Incoming SCADA tags are configuration-driven via [`config/tag_mapping.yaml`](config/tag_mapping.yaml):

| Standard Industrial Tag ID | Measured Physical Parameter | Standard Feature | Unit | Normal Bounds | Alert Threshold |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `TURB_MTR_DE_VIB_RMS` | Drive-End Bearing Radial Vibration RMS | `Vibration` | mm/s | 0.10 – 0.80 | $\ge 1.80$ |
| `TURB_MTR_VIB_FREQ_01` | Dominant Rotational Frequency | `Frequency` | Hz | 48.0 – 52.0 | $\ge 75.0$ |
| `TURB_MTR_STATOR_TEMP` | Stator Core Winding Temperature | `Temperature` | °C | 40.0 – 70.0 | $\ge 95.0$ |
| `TURB_MTR_PHASE_CURRENT`| 3-Phase Stator Motor Current | `Motor_Current` | A | 8.0 – 14.0 | $\ge 22.0$ |
| `TURB_MTR_ACOUSTIC_DB` | Ultrasonic Acoustic Emission | `Acoustic_Noise`| dB | 40.0 – 65.0 | $\ge 88.0$ |
| `TURB_MTR_LUBE_OIL_PRES`| Lube Oil Supply Pressure | `Pressure` | bar | 3.5 – 5.5 | $\le 2.2$ |
| `TURB_MTR_SHAFT_SPEED` | Tachometer Rotor Shaft Speed | `RPM` | RPM | 2900 – 3100 | $\le 2600$ |
| `TURB_MTR_KW_LOAD` | Shaft Active Operating Load | `Load` | % | 10.0 – 90.0 | $\ge 105.0$ |

### Sample MQTT Ingestion Payload
```json
{
  "timestamp": "2026-10-04T21:30:15.250Z",
  "machine_id": "MCH-802X",
  "tags": {
    "TURB_MTR_DE_VIB_RMS": 0.42,
    "TURB_MTR_VIB_FREQ_01": 50.1,
    "TURB_MTR_STATOR_TEMP": 64.2,
    "TURB_MTR_PHASE_CURRENT": 8.9,
    "TURB_MTR_ACOUSTIC_DB": 46.5,
    "TURB_MTR_LUBE_OIL_PRES": 4.4,
    "TURB_MTR_SHAFT_SPEED": 3005.0,
    "TURB_MTR_KW_LOAD": 52.0
  }
}
```

---

## 🧠 Machine Learning & Diagnostic Architecture

### 1. Sliding-Window Feature Engineering
- **Time-Domain**: Mean, RMS, Variance, Skewness, Kurtosis, Peak, Peak-to-Peak, Crest Factor.
- **Frequency-Domain (FFT)**: Dominant spectral peak, total harmonic energy, spectral centroid.
- **Dynamic Trend**: Rolling linear slope ($dy/dt$), rate of change, directional indicator.

### 2. Anomaly Detection
- Blends **Isolation Forest** multivariate decision boundaries with multidimensional **Z-score** distances.
- Classifies telemetry into **`NORMAL`**, **`WARNING`**, or **`CRITICAL`**, reporting top contributing sensor channels.

### 3. Evidence-Backed Fault Diagnosis
- Attributions are only made when physical evidence thresholds are met:
  - **Bearing Degradation**: High Vibration RMS + elevated acoustic noise + Kurtosis $> 4.5$ or Crest Factor $> 2.8$.
  - **Thermal Runaway**: High Stator Temperature ($> 85^\circ\text{C}$) + Phase Current $> 14.5\text{ A}$ + positive thermal slope.
  - **Lube Oil Starvation**: Low Oil Pressure ($< 2.5\text{ bar}$) + friction acoustic spike.
  - **Rotor Imbalance**: Vibration synchronized with 1X rotational frequency without thermal/acoustic surges.
- If evidence is weak: Outputs *"Possible abnormal condition detected. Root cause requires inspection."*

### 4. Scientifically Honest RUL
- If calibrated historical failure data is present: Returns a **bounded confidence interval** (e.g. `12–18 days, 85% confidence`).
- If uncalibrated: Transparently disclaims: *"Calibrated RUL requires historical failure events. Operating on Condition-Based Risk & Health Index."*

### 5. ISO 10816 Vibration Severity Standard
Evaluates vibration RMS for Class II & III machinery:
- **Zone A**: $< 0.28\text{ mm/s}$ (Good / Newly Commissioned)
- **Zone B**: $0.28 - 0.71\text{ mm/s}$ (Acceptable for Unrestricted Operation)
- **Zone C**: $0.71 - 1.80\text{ mm/s}$ (Unsatisfactory / Early Warning)
- **Zone D**: $> 1.80\text{ mm/s}$ (Critical Danger / Shutdown Recommended)

---

## 📈 Continuous Drift Monitoring

Strictly separates:
1. **Data Drift**: Evaluated across continuous feature distributions using **2-Sample Kolmogorov-Smirnov (KS) tests** and **Population Stability Index (PSI)**.
2. **Concept Drift**: Shifts in physical input-to-degradation relationships.
3. **Model Performance Drift**: Monitored using actual overhaul and maintenance outcome feedback (MAE, RMSE, false alarm rate).

---

## 🔄 MLOps & Model Governance

Continuous model improvement follows a rigorous human-in-the-loop lifecycle:
```text
Data Drift Detected / Scheduled Retraining
                   ↓
Train Candidate Model on Accumulated Operational Wear Data
                   ↓
Evaluate Candidate Against Active Production Model (ΔMAE, ΔR²)
                   ↓
Candidate Set to WAITING_FOR_ENGINEER_APPROVAL
                   ↓
Engineer Review & Sign-Off Gate
                   ↓
Promote Candidate to PRODUCTION (v1.0 → v1.1 → v2.0)
                   ↓
One-Click Version Rollback to Previous Stable Version
```

---

## 🛠️ Explainable Maintenance Recommendations

Replaces over-engineered CMMS ticketing with actionable, evidence-supported servicing advice:

```text
Machine: MCH-802X
Operating Condition: WARNING
Detected Condition: Bearing Assembly Degradation
Evidence:
  • Vibration RMS elevated at 1.45 mm/s (threshold: 0.80 mm/s)
  • Ultrasonic acoustic friction elevated at 74.0 dB (threshold: 65.0 dB)
  • Impact impulsiveness detected (Kurtosis: 5.2, Crest Factor: 3.1)
  • ISO 10816 Vibration Severity: Zone C (Unsatisfactory / Early Warning)
  • Machine Health Score: 52.4 / 100
Severity: HIGH
Priority: HIGH
Recommended Action: Schedule targeted maintenance inspection on Turbine Motor Unit A1. Focus check: Bearing Assembly Degradation.
Suggested Window: Urgent: Complete diagnostic inspection within 3–5 days
Confidence: 88%
```

---

## 🌐 REST API Endpoints

### System & MQTT
- `GET /api/system/status`: Overall system health, active mode, watchdog alarm.
- `GET /api/mqtt/status`: MQTT connection, packet count, arrival cadence, jitter.
- `POST /api/mqtt/inject`: Ingest custom JSON telemetry payload directly.
- `POST /api/mqtt/config`: Dynamically reconfigure broker IP, port, or topic.
- `GET /api/tags/live`: Live industrial tag values, units, and physical bounds.

### Fleet & Telemetry
- `GET /api/machines`: List all plant assets with health and anomaly statuses.
- `GET /api/machines/{machine_id}/telemetry` (alias `GET /api/current`): Latest telemetry, health, anomaly, and RUL.
- `GET /api/machines/{machine_id}/history` (alias `GET /api/history`): Recent time-series history for charts.
- `POST /api/fleet/select`: Select active monitored machine.

### Diagnostics & Maintenance
- `GET /api/early_warning`: P-F curve, ISO 10816 severity zone, operator checklist.
- `GET /api/maintenance`: Explainable maintenance recommendation and supporting evidence.
- `GET /api/drift/status`: KS-tests, PSI scores, and data drift flags.
- `POST /api/drift/recalibrate`: Recalibrate baseline distributions to post-maintenance regime.

### MLOps Governance
- `GET /api/models`: Model registry versions and benchmark leaderboard.
- `POST /api/mlops/retrain`: Train candidate model on accumulated operational wear data.
- `POST /api/models/{version}/approve`: Engineer approval gate to promote candidate to production.
- `POST /api/models/{version}/rollback`: Roll back active model to previous stable version.

### Simulation & Replay
- `POST /api/simulation/start`: Start digital twin clock loop.
- `POST /api/simulation/stop`: Pause digital twin clock loop.
- `POST /api/simulator/fault`: Inject mechanical fault (bearing, thermal, cavitation, imbalance).
- `POST /api/simulation/replay`: Replay historical CSV dataset through the ingestion gateway.

---

## 💻 Installation & Quickstart

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Node.js 18+ and npm

### 1. Clone & Set Up Backend
```bash
git clone https://github.com/naga-akshya-k/pdm.git
cd pdm

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Build Frontend & Launch Platform
```bash
# Build React production bundle
cd frontend && npm install && npm run build && cd ..

# Launch unified server (FastAPI serves both API and React Dashboard on Port 8001)
python3 -u -m uvicorn main:app --host 0.0.0.0 --port 8001
```

- **Operations Dashboard**: `http://localhost:8001/`
- **Swagger Interactive API Documentation**: `http://localhost:8001/docs`

---

## 🧪 Testing

Run the comprehensive unit and integration test suite:

```bash
pytest tests/
```

Test coverage includes:
- MQTT ingestion, tag mapping, and watchdog timeout alarms.
- Timestamp validation, unit normalization, and sensor fault classification.
- Time-domain, FFT frequency-domain, and dynamic trend feature extraction.
- Anomaly detection, evidence-backed diagnosis, ISO 10816 severity, and bounded RUL.
- KS-test and PSI data drift monitoring.
- MLOps candidate training, engineer approval gates, and production rollbacks.
- FastAPI REST endpoints.

---

## 📜 Industrial Safety Notice

This platform is a **decision-support system for reliability and maintenance engineers**. It does **not** autonomously execute hardware control commands or emergency stop (E-STOP) sequences. All operational and maintenance decisions must be reviewed and authorized by qualified plant personnel.
