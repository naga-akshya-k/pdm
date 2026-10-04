"""
Production-Oriented Industrial MQTT Ingestion Consumer.
Subscribes to broker topics, parses industrial tag payloads, tracks timing jitter,
and routes valid packets into the central time-series predictive maintenance pipeline.
"""

import json
import time
import datetime
import logging
import threading
from typing import Dict, Any, Optional, Callable
import paho.mqtt.client as mqtt

from .tag_mapper import IndustrialTagMapper
from .watchdog import TelemetryWatchdog
from backend.data.validation import DataQualityValidator

logger = logging.getLogger("pdm.mqtt")

class IndustrialMQTTConsumer:
    def __init__(
        self,
        broker_host: str = "127.0.0.1",
        broker_port: int = 1883,
        topic: str = "plant/bay4/+/telemetry",
        nominal_interval_ms: float = 1000.0,
        pipeline_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.nominal_interval_ms = nominal_interval_ms
        self.pipeline_callback = pipeline_callback

        self.tag_mapper = IndustrialTagMapper()
        self.validator = DataQualityValidator()
        self.watchdog = TelemetryWatchdog()

        self.client: Optional[mqtt.Client] = None
        self._lock = threading.RLock()
        self.is_connected = False
        self.is_running = False

        self.packet_count = 0
        self.last_arrival_time = None
        self.last_delta_t_ms = None
        self.jitter_history = []

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info(f"MQTT Connected to broker at {self.broker_host}:{self.broker_port}")
            with self._lock:
                self.is_connected = True
            client.subscribe(self.topic, qos=1)
        else:
            logger.warning(f"MQTT Connection failed with code {rc}")
            with self._lock:
                self.is_connected = False

    def _on_disconnect(self, client, userdata, rc, properties=None):
        logger.warning(f"MQTT Disconnected from broker (rc={rc})")
        with self._lock:
            self.is_connected = False

    def _on_message(self, client, userdata, msg):
        now = time.time()
        try:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)
        except Exception as e:
            logger.error(f"Failed to decode MQTT JSON payload: {e}")
            return

        self.process_incoming_packet(data, arrival_time=now)

    def process_incoming_packet(self, data: Dict[str, Any], arrival_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Processes an incoming industrial telemetry packet:
        1. Timing and jitter validation
        2. Machine and Tag ID identification
        3. Feature mapping and unit canonicalization
        4. Forwarding to unified downstream pipeline callback
        """
        if arrival_time is None:
            arrival_time = time.time()

        with self._lock:
            self.packet_count += 1
            if self.last_arrival_time is not None:
                delta_t = (arrival_time - self.last_arrival_time) * 1000.0
                jitter = abs(delta_t - self.nominal_interval_ms)
                self.last_delta_t_ms = round(delta_t, 1)
                self.jitter_history.append(jitter)
                if len(self.jitter_history) > 30:
                    self.jitter_history.pop(0)
            else:
                self.last_delta_t_ms = self.nominal_interval_ms

            self.last_arrival_time = arrival_time

        # 1. Extract Machine ID & Flags
        machine_id = str(data.get("machine_id", "MCH-802X"))
        is_simulation = bool(data.get("is_simulation", False))
        is_replay = bool(data.get("is_replay", False))

        # 2. Update Watchdog
        self.watchdog.record_packet(machine_id, is_simulation=is_simulation, is_replay=is_replay)

        # 3. Extract Tags
        tags_dict = data.get("tags")
        if not tags_dict:
            # Handle single tag schema e.g. {"machine_id": "...", "tag_id": "...", "value": 2.37}
            if "tag_id" in data and "value" in data:
                tags_dict = {data["tag_id"]: data["value"]}
            else:
                # Flat schema fallback
                tags_dict = {
                    k: v for k, v in data.items()
                    if k not in ["machine_id", "timestamp", "sampling_interval_ms", "sequence_id", "is_simulation", "is_replay"]
                }

        # 4. Map Tags to Standard Internal Features
        raw_features, audit = self.tag_mapper.map_payload(tags_dict)

        # 5. Timestamp and Physical Bounds Validation
        ts_dt, ts_str = self.validator.parse_timestamp(data.get("timestamp"))
        cleaned_features, qual_flags = self.validator.validate_features(
            machine_id=machine_id,
            features=raw_features,
            timestamp_dt=ts_dt,
            units_map=audit.get("raw_units", {})
        )

        packet_envelope = {
            "machine_id": machine_id,
            "timestamp": ts_str,
            "features": cleaned_features,
            "raw_tags": tags_dict,
            "data_quality": qual_flags["data_quality"],
            "quality_flags": qual_flags,
            "audit": audit,
            "is_simulation": is_simulation,
            "is_replay": is_replay,
            "delta_t_ms": self.last_delta_t_ms,
            "arrival_time": arrival_time
        }

        # 6. Pass into downstream pipeline if registered
        if self.pipeline_callback:
            try:
                self.pipeline_callback(packet_envelope)
            except Exception as e:
                logger.error(f"Error in pipeline callback: {e}", exc_info=True)

        return packet_envelope

    def start(self):
        """Starts background MQTT network loop."""
        if self.is_running:
            return
        try:
            try:
                self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pdm_industrial_consumer")
            except Exception:
                self.client = mqtt.Client(client_id="pdm_industrial_consumer")

            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            self.client.reconnect_delay_set(min_delay=1, max_delay=10)

            self.client.connect_async(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            self.is_running = True
            logger.info("Industrial MQTT Consumer loop started.")
        except Exception as e:
            logger.warning(f"Could not connect to MQTT broker ({self.broker_host}:{self.broker_port}): {e}")

    def stop(self):
        if self.client and self.is_running:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass
            self.is_running = False
            self.is_connected = False

    def get_status(self) -> Dict[str, Any]:
        avg_jitter = round(float(sum(self.jitter_history) / len(self.jitter_history)), 1) if self.jitter_history else 0.0
        watchdog_status = self.watchdog.get_status()
        return {
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "topic": self.topic,
            "is_connected": self.is_connected,
            "is_running": self.is_running,
            "packet_count": self.packet_count,
            "last_delta_t_ms": self.last_delta_t_ms,
            "avg_jitter_ms": avg_jitter,
            "watchdog": watchdog_status
        }
