"""
Unit Tests for Industrial MQTT Ingestion, Tag Mapping, and Watchdog.
"""

import time
import pytest
from backend.ingestion.tag_mapper import IndustrialTagMapper
from backend.ingestion.watchdog import TelemetryWatchdog
from backend.ingestion.mqtt_consumer import IndustrialMQTTConsumer

def test_tag_mapper_exact_tags():
    mapper = IndustrialTagMapper()
    raw = {
        "TURB_MTR_DE_VIB_RMS": 0.32,
        "TURB_MTR_STATOR_TEMP": 65.4,
        "TURB_MTR_PHASE_CURRENT": 9.1
    }
    feats, audit = mapper.map_payload(raw)
    assert feats["Vibration"] == 0.32
    assert feats["Temperature"] == 65.4
    assert feats["Motor_Current"] == 9.1
    assert "TURB_MTR_DE_VIB_RMS" in audit["recognized_tags"]

def test_tag_mapper_fallback_case_insensitive():
    mapper = IndustrialTagMapper()
    raw = {
        "turb_mtr_de_vib_rms": 0.45,
        "unknown_tag": 12.3
    }
    feats, audit = mapper.map_payload(raw)
    assert feats["Vibration"] == 0.45
    assert "unknown_tag" in audit["unrecognized_tags"]

def test_watchdog_timeout_and_offline_alarm():
    watchdog = TelemetryWatchdog(timeout_seconds=0.2)
    # Record real packet
    watchdog.record_packet("MCH-802X", is_simulation=False)
    st = watchdog.get_status()
    assert st["current_mode"] == "REAL INDUSTRIAL DATA"
    assert st["is_stream_live"] is True
    assert st["real_telemetry_offline_alarm"] is False

    # Wait past timeout
    time.sleep(0.3)
    st_after = watchdog.get_status()
    assert st_after["is_stream_live"] is False
    assert st_after["real_telemetry_offline_alarm"] is True
    assert "REAL TELEMETRY OFFLINE" in st_after["alarm_message"]

def test_mqtt_consumer_packet_routing():
    received = []
    def callback(envelope):
        received.append(envelope)

    consumer = IndustrialMQTTConsumer(pipeline_callback=callback)
    payload = {
        "machine_id": "TEST-01",
        "tags": {
            "TURB_MTR_DE_VIB_RMS": 0.55,
            "TURB_MTR_STATOR_TEMP": 58.0
        }
    }
    consumer.process_incoming_packet(payload)
    assert len(received) == 1
    assert received[0]["machine_id"] == "TEST-01"
    assert received[0]["features"]["Vibration"] == 0.55
