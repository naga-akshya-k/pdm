"""
Interactive Workstation GPU Telemetry Stream Simulator.
Streams real-time Turbine Motor Tag ID packets to the platform for testing.
"""

import time
import json
import random
import datetime
import urllib.request
import argparse

def run_stream(seconds=60, interval=1.0, fault=False):
    print("=" * 65)
    print(" WORKSTATION GPU TELEMETRY STREAM SIMULATOR")
    print(f" Target Endpoint : http://127.0.0.1:8001/api/mqtt/inject")
    print(f" Asset           : Turbine Motor Unit A1 (MCH-802X)")
    print(f" Stream Cadence  : {interval * 1000:.0f} ms (Delta-t)")
    print(f" Stream Duration : {seconds} seconds ({int(seconds / interval)} packets)")
    print(f" Operating State : {'FAULT / DEGRADATION INJECTION' if fault else 'NORMAL NOMINAL STREAM'}")
    print("=" * 65)
    print("\nStarting transmission... Check your browser at http://localhost:5173 !\n")

    start_time = time.time()
    step = 1

    base_vib = 0.35 if not fault else 2.45
    base_temp = 62.5 if not fault else 89.2
    base_curr = 9.8 if not fault else 18.5
    base_noise = 49.0 if not fault else 78.0
    base_pres = 4.5 if not fault else 3.1
    base_rpm = 3000.0 if not fault else 2910.0
    base_freq = 50.0 if not fault else 62.5
    base_load = 58.0 if not fault else 92.0

    while time.time() - start_time < seconds:
        packet = {
            "machine_id": "MCH-802X",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "sampling_interval_ms": int(interval * 1000),
            "sequence_id": step,
            "tags": {
                "TURB_MTR_DE_VIB_RMS": round(base_vib + random.gauss(0, 0.02), 3),
                "TURB_MTR_VIB_FREQ_01": round(base_freq + random.gauss(0, 0.2), 1),
                "TURB_MTR_STATOR_TEMP": round(base_temp + random.gauss(0, 0.4), 1),
                "TURB_MTR_PHASE_CURRENT": round(base_curr + random.gauss(0, 0.1), 2),
                "TURB_MTR_ACOUSTIC_DB": round(base_noise + random.gauss(0, 0.5), 1),
                "TURB_MTR_LUBE_OIL_PRES": round(base_pres + random.gauss(0, 0.05), 2),
                "TURB_MTR_SHAFT_SPEED": round(base_rpm + random.gauss(0, 4.0), 1),
                "TURB_MTR_KW_LOAD": round(base_load + random.gauss(0, 0.5), 1)
            }
        }

        try:
            req = urllib.request.Request(
                "http://127.0.0.1:8001/api/mqtt/inject",
                data=json.dumps(packet).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            res = urllib.request.urlopen(req, timeout=3)
            data = json.loads(res.read())
            listener = data.get("listener_status", {})
            dt = listener.get("last_delta_t_ms", 1000.0)
            
            vib = packet["tags"]["TURB_MTR_DE_VIB_RMS"]
            temp = packet["tags"]["TURB_MTR_STATOR_TEMP"]
            curr = packet["tags"]["TURB_MTR_PHASE_CURRENT"]
            
            print(f"[{time.strftime('%H:%M:%S')}] Packet #{step:03d} -> Transmitted | "
                  f"Vib: {vib:.3f} mm/s | Temp: {temp:.1f} C | Current: {curr:.1f} A | Dt: {dt:.1f} ms")
        except Exception as e:
            print(f"Transmission error: {e}")

        step += 1
        time.sleep(interval)

    print("\nTransmission complete! 3-second watchdog will now revert to Digital Twin Simulation.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=45, help="Duration to stream in seconds (default: 45s)")
    parser.add_argument("--interval", type=float, default=1.0, help="Cadence interval in seconds (default: 1.0s)")
    parser.add_argument("--fault", action="store_true", help="Inject high-vibration bearing fault")
    args = parser.parse_args()
    run_stream(seconds=args.seconds, interval=args.interval, fault=args.fault)
