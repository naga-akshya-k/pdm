# Company Workstation Remote Desktop Deployment Guide
## Asset: Turbine Motor Unit A1 (`MCH-802X`)

This predictive maintenance platform is configured for **Turbine Motor Unit A1 (`MCH-802X`)**. It receives real sensor streams via **MQTT** using standardized industrial **Tag IDs**, executes real-time AI Remaining Useful Life (RUL) inference, and detects anomalies with cadence timing validation.

---

### 1. How to Launch on the Remote Desktop Workstation
Inside the Windows Remote Desktop session:
1. Open the project folder `pdm`.
2. Double-click `start_workstation.bat`.
3. The script will automatically:
   - Launch the FastAPI Backend and AI engine on port `8001`.
   - Launch the React Dashboard on port `5173`.
   - Open your browser to `http://localhost:5173`.

---

### 2. MQTT Telemetry Protocol & Tag IDs
The company data pipeline should publish telemetry over MQTT:

- **MQTT Broker**: `localhost:1883` (or workstation IP)
- **MQTT Topic**: `plant/bay4/turbine_motor/MCH-802X/telemetry`
- **Nominal Sampling Cadence ($\Delta t$)**: `1000 ms` (1 Hz)
- **Watchdog Timeout**: `3.0 seconds` (if telemetry pauses, the dashboard safely reverts to digital twin simulation)

#### Standard Industrial Tag ID Mapping Table:

| Tag ID | Measured Physical Parameter | Internal Feature | Unit | Normal Bounds | Critical Threshold |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `TURB_MTR_DE_VIB_RMS` | Drive-End Bearing Radial Vibration RMS | `Vibration` | mm/s | 0.10 – 0.80 | $\ge 1.80$ |
| `TURB_MTR_VIB_FREQ_01` | Dominant Rotational Frequency | `Frequency` | Hz | 48.0 – 52.0 | $\ge 75.0$ |
| `TURB_MTR_STATOR_TEMP` | Stator Core Winding Temperature | `Temperature` | °C | 40.0 – 70.0 | $\ge 95.0$ |
| `TURB_MTR_PHASE_CURRENT`| 3-Phase Stator Motor Current | `Motor_Current` | A | 8.0 – 14.0 | $\ge 22.0$ |
| `TURB_MTR_ACOUSTIC_DB` | Ultrasonic Acoustic Noise Emission | `Acoustic_Noise`| dB | 40.0 – 65.0 | $\ge 88.0$ |
| `TURB_MTR_LUBE_OIL_PRES`| Lube Oil Feed Supply Pressure | `Pressure` | bar | 3.5 – 5.5 | $\le 2.2$ |
| `TURB_MTR_SHAFT_SPEED` | Tachometer Rotor Shaft Speed | `RPM` | RPM | 2950 – 3050 | $\le 2600$ |
| `TURB_MTR_KW_LOAD` | Shaft Active Operating Load | `Load` | % | 20.0 – 90.0 | $\ge 105.0$ |

#### Sample JSON Payload Format:
```json
{
  "machine_id": "MCH-802X",
  "timestamp": "2026-09-23T12:00:00.000Z",
  "sampling_interval_ms": 1000,
  "sequence_id": 101,
  "tags": {
    "TURB_MTR_DE_VIB_RMS": 0.32,
    "TURB_MTR_VIB_FREQ_01": 50.0,
    "TURB_MTR_STATOR_TEMP": 58.5,
    "TURB_MTR_PHASE_CURRENT": 9.2,
    "TURB_MTR_ACOUSTIC_DB": 48.0,
    "TURB_MTR_LUBE_OIL_PRES": 4.6,
    "TURB_MTR_SHAFT_SPEED": 3000.0,
    "TURB_MTR_KW_LOAD": 55.0
  }
}
```

---

### 3. Testing the Ingestion Stream
To test the pipeline without live plant hardware connected:
```bash
# In terminal, run the mock publisher:
python scripts/test_gpu_sender.py --interval 1.0

# To test fault detection and early warning alert:
python scripts/test_gpu_sender.py --interval 1.0 --fault
```

---

### 4. API Endpoints
- **Live Tag Inspector API**: `http://localhost:8001/api/tags/live`
- **MQTT Gateway Diagnostics**: `http://localhost:8001/api/mqtt/status`
- **Current Telemetry**: `http://localhost:8001/api/current`
- **Interactive Swagger Docs**: `http://localhost:8001/docs`
