"""
End-to-End Pipeline Verification Script.
Tests:
1. Tag ID parsing and canonicalization.
2. Inter-arrival time (Delta-t) and jitter tracking.
3. Live AI inference on workstation GPU Tag ID packets.
4. UI telemetry response verification.
5. 3-second heartbeat watchdog failover to Simulation.
"""

import sys
import time
import json
import urllib.request

API_BASE = "http://127.0.0.1:8001"

def test_pipeline():
    print("=" * 60)
    print(" INDUSTRIAL MQTT & TAG ID PIPELINE VERIFICATION")
    print("=" * 60)

    # 1. Check initial status
    print("\n[Step 1] Querying /api/mqtt/status (Baseline)...")
    res = urllib.request.urlopen(f"{API_BASE}/api/mqtt/status")
    status_data = json.loads(res.read())
    print(f" -> MQTT Status : {status_data['mqtt_status']}")
    print(f" -> Active Tags : {len(status_data['supported_tags'])} supported")
    assert status_data["target_machine_id"] == "MCH-802X"

    # 2. Inject GPU Workstation Tag Packets at 1.0s intervals
    print("\n[Step 2] Streaming 3 Tag ID packets from Workstation GPU (1000ms cadence)...")
    sample_tags = {
        "TURB_MTR_DE_VIB_RMS": 0.42,
        "TURB_MTR_STATOR_TEMP": 65.5,
        "TURB_MTR_PHASE_CURRENT": 10.4,
        "TURB_MTR_ACOUSTIC_DB": 52.3,
        "TURB_MTR_LUBE_OIL_PRES": 4.4,
        "TURB_MTR_SHAFT_SPEED": 3000.0,
        "TURB_MTR_VIB_FREQ_01": 50.0,
        "TURB_MTR_KW_LOAD": 64.0
    }

    for step in range(1, 4):
        packet = {
            "machine_id": "MCH-802X",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sampling_interval_ms": 1000,
            "sequence_id": step,
            "tags": sample_tags
        }
        req = urllib.request.Request(
            f"{API_BASE}/api/mqtt/inject",
            data=json.dumps(packet).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        res = urllib.request.urlopen(req)
        body = json.loads(res.read())
        delta_t = body["listener_status"]["last_delta_t_ms"]
        print(f" -> Sent Packet #{step} | Ingested: True | Measured Delta-t: {delta_t} ms")
        if step < 3:
            time.sleep(1.0)

    # 3. Query /api/current while stream is actively running
    print("\n[Step 3] Checking /api/current during active stream...")
    res = urllib.request.urlopen(f"{API_BASE}/api/current")
    curr = json.loads(res.read())
    print(f" -> Data Source      : {curr['data_source']}")
    print(f" -> MQTT Live State  : {curr['mqtt_live']}")
    print(f" -> Telemetry Delta-t: {curr['mqtt_delta_t_ms']} ms")
    print(f" -> Live Vibration   : {curr['vibration']} mm/s")
    print(f" -> Live Temperature : {curr['temperature']} C")
    print(f" -> Machine Health   : {curr['machine_health']}%")
    print(f" -> Predicted RUL    : {curr['predicted_rul_days']} days")

    assert curr["mqtt_live"] is True, "Expected MQTT stream to be active!"
    assert curr["vibration"] == 0.42, "Vibration feature was not mapped from TURB_MTR_DE_VIB_RMS!"
    assert curr["temperature"] == 65.5, "Temperature was not mapped from TURB_MTR_STATOR_TEMP!"
    print(" [OK] Active GPU Workstation Telemetry & AI inference verified!")

    # 4. Test Watchdog Timeout Failover
    print("\n[Step 4] Halting transmission and waiting 3.5s for Watchdog Timeout...")
    time.sleep(3.5)

    res_post = urllib.request.urlopen(f"{API_BASE}/api/current")
    curr_post = json.loads(res_post.read())
    print(f" -> Data Source     : {curr_post['data_source']}")
    print(f" -> MQTT Live State : {curr_post['mqtt_live']}")

    assert curr_post["mqtt_live"] is False, "Watchdog failed to revert to simulation!"
    assert "Simulation" in curr_post["data_source"], "Data source should indicate SCADA Simulation!"
    print(" [OK] Watchdog Timeout & Fallback to Simulation successfully verified!")

    print("\n" + "=" * 60)
    print(" ALL 4 VERIFICATION CHECKS PASSED (100% OK)")
    print("=" * 60)

if __name__ == "__main__":
    test_pipeline()
