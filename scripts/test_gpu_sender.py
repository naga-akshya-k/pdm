"""
Mock Workstation GPU Telemetry Publisher.
Simulates company workstation GPU sending real industrial Tag ID packets over MQTT
with precise delta-t timing and optional mechanical wear injection.
"""

import time
import json
import random
import datetime
import argparse
import paho.mqtt.client as mqtt

def generate_telemetry_packet(step: int, fault: bool = False) -> dict:
    # Base parameters for Turbine Motor MCH-802X
    base_vib = 0.28 if not fault else 2.45
    base_temp = 52.0 if not fault else 88.5
    base_curr = 9.2 if not fault else 18.0
    base_noise = 48.0 if not fault else 78.0
    base_pres = 4.6 if not fault else 3.1
    base_rpm = 3000.0 if not fault else 2910.0
    base_freq = 50.0 if not fault else 62.5
    base_load = 55.0 if not fault else 92.0

    return {
        "machine_id": "MCH-802X",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "sampling_interval_ms": 1000,
        "sequence_id": step,
        "tags": {
            "TURB_MTR_DE_VIB_RMS": round(base_vib + random.gauss(0, 0.02), 3),
            "TURB_MTR_VIB_FREQ_01": round(base_freq + random.gauss(0, 0.2), 1),
            "TURB_MTR_STATOR_TEMP": round(base_temp + random.gauss(0, 0.4), 2),
            "TURB_MTR_PHASE_CURRENT": round(base_curr + random.gauss(0, 0.1), 2),
            "TURB_MTR_ACOUSTIC_DB": round(base_noise + random.gauss(0, 0.5), 1),
            "TURB_MTR_LUBE_OIL_PRES": round(base_pres + random.gauss(0, 0.05), 2),
            "TURB_MTR_SHAFT_SPEED": round(base_rpm + random.gauss(0, 5.0), 1),
            "TURB_MTR_KW_LOAD": round(base_load + random.gauss(0, 0.5), 1),
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Industrial GPU Workstation MQTT Publisher")
    parser.add_argument("--broker", default="127.0.0.1", help="MQTT Broker IP address")
    parser.add_argument("--port", type=int, default=1883, help="MQTT Broker Port")
    parser.add_argument("--topic", default="plant/bay4/turbine_motor/MCH-802X/telemetry", help="MQTT Topic")
    parser.add_argument("--interval", type=float, default=1.0, help="Transmission interval in seconds (default: 1.0s)")
    parser.add_argument("--count", type=int, default=100, help="Number of packets to send (0 = infinite)")
    parser.add_argument("--fault", action="store_true", help="Inject critical bearing fault into packets")
    args = parser.parse_args()

    print(f"============================================================")
    print(f" Industrial GPU Workstation Telemetry Sender")
    print(f" Target Broker : {args.broker}:{args.port}")
    print(f" MQTT Topic    : {args.topic}")
    print(f" Cadence (Δt)  : {args.interval * 1000:.0f} ms ({1.0/args.interval:.1f} Hz)")
    print(f" Operating Mode: {'CRITICAL FAULT' if args.fault else 'NORMAL HEALTHY'}")
    print(f"============================================================")

    client = mqtt.Client(client_id="workstation_gpu_sender")
    try:
        client.connect(args.broker, args.port, 60)
        client.loop_start()
        print("Connected to MQTT Broker successfully!\n")
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
        print("Tip: Ensure Mosquitto or an MQTT broker is running on the workstation.")
        return

    step = 1
    t_start = time.time()
    try:
        while True:
            t_now = time.time()
            packet = generate_telemetry_packet(step, fault=args.fault)
            payload_str = json.dumps(packet)
            
            client.publish(args.topic, payload_str, qos=1)

            vib = packet["tags"]["TURB_MTR_DE_VIB_RMS"]
            temp = packet["tags"]["TURB_MTR_STATOR_TEMP"]
            curr = packet["tags"]["TURB_MTR_PHASE_CURRENT"]
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Step #{step:04d} | "
                  f"Vib: {vib:.3f} mm/s | Temp: {temp:.1f} °C | Current: {curr:.1f} A -> Published")

            step += 1
            if args.count > 0 and step > args.count:
                break

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nPublisher stopped by user.")
    finally:
        client.loop_stop()
        client.disconnect()
        print(f"Done. Sent {step - 1} packets in {time.time() - t_start:.1f}s.")

if __name__ == "__main__":
    main()
