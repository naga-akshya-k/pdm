"""
Industrial MQTT Telemetry Ingestion Gateway.
Subscribes to workstation GPU telemetry, verifies sampling cadence, calculates jitter,
enforces 3-second heartbeat watchdog, and canonicalizes Tag IDs.
"""

import os
import json
import time
import datetime
import logging
import threading
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt

try:
    from tag_mapping import normalize_tag_payload, TURBINE_TAG_REGISTRY
except ImportError:
    from .tag_mapping import normalize_tag_payload, TURBINE_TAG_REGISTRY

logger = logging.getLogger("pdm.mqtt")


class IndustrialMQTTListener:
    """
    Thread-safe asynchronous MQTT subscriber for industrial workstation GPU sensor streams.
    """
    def __init__(
        self,
        broker_host: Optional[str] = None,
        broker_port: Optional[int] = None,
        topic: str = "plant/bay4/turbine_motor/+/telemetry",
        nominal_interval_ms: float = 1000.0,
        heartbeat_timeout_s: float = 3.0,
    ):
        self.broker_host = broker_host or os.getenv("MQTT_BROKER_HOST", "127.0.0.1")
        self.broker_port = int(broker_port or os.getenv("MQTT_BROKER_PORT", "1883"))
        self.topic = topic
        self.nominal_interval_ms = nominal_interval_ms
        self.heartbeat_timeout_s = heartbeat_timeout_s

        self.client: Optional[mqtt.Client] = None
        self._lock = threading.RLock()
        self.is_connected = False
        self.is_running = False

        # Timing and jitter tracking
        self.last_packet_arrival_time: Optional[float] = None
        self.last_delta_t_ms: Optional[float] = None
        self.jitter_window = []  # Last 30 jitter samples
        self.packet_count = 0
        self.dropped_or_out_of_order_count = 0

        # Latest received data
        self.latest_raw_packet: Optional[Dict[str, Any]] = None
        self.latest_features: Optional[Dict[str, float]] = None
        self.latest_audit: Dict[str, Any] = {}
        self.active_machine_id = "MCH-802X"

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info(f"MQTT Connected successfully to broker at {self.broker_host}:{self.broker_port}")
            with self._lock:
                self.is_connected = True
            client.subscribe(self.topic, qos=1)
            logger.info(f"Subscribed to topic: {self.topic}")
        else:
            logger.warning(f"MQTT Connection failed with return code {rc}")
            with self._lock:
                self.is_connected = False

    def _on_disconnect(self, client, userdata, rc, properties=None):
        logger.warning(f"MQTT Disconnected from broker (rc={rc})")
        with self._lock:
            self.is_connected = False

    def _process_payload(self, data: Dict[str, Any], arrival_time: Optional[float] = None):
        if arrival_time is None:
            arrival_time = time.time()

        with self._lock:
            self.packet_count += 1

            # 1. Timing & Jitter Cadence Calculation
            if self.last_packet_arrival_time is not None:
                delta_t = (arrival_time - self.last_packet_arrival_time) * 1000.0  # ms
                jitter = abs(delta_t - self.nominal_interval_ms)

                self.last_delta_t_ms = round(delta_t, 1)
                self.jitter_window.append(jitter)
                if len(self.jitter_window) > 30:
                    self.jitter_window.pop(0)

                # Check out-of-order arrival
                if delta_t < 10.0:
                    self.dropped_or_out_of_order_count += 1
            else:
                self.last_delta_t_ms = self.nominal_interval_ms

            self.last_packet_arrival_time = arrival_time

            # 2. Extract Tags & Canonicalize Features
            tags_dict = data.get("tags", {})
            if not tags_dict:
                # Flat format fallback
                tags_dict = {
                    k: v for k, v in data.items() 
                    if k not in ["machine_id", "timestamp", "sampling_interval_ms", "sequence_id"]
                }

            features, audit = normalize_tag_payload(tags_dict)

            # Metadata enrichment
            self.active_machine_id = str(data.get("machine_id", "MCH-802X"))
            self.latest_raw_packet = data
            self.latest_features = features
            self.latest_audit = audit

    def _on_message(self, client, userdata, msg):
        arrival_time = time.time()
        try:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)
        except Exception as e:
            logger.error(f"Failed to parse MQTT JSON payload: {e}")
            return

        self._process_payload(data, arrival_time)

    def inject_payload(self, data: Dict[str, Any]):
        """Directly ingest a telemetry packet (used for HTTP test injection or direct pipeline feed)."""
        self._process_payload(data)

    def start(self):
        """Starts asynchronous MQTT background thread."""
        if self.is_running:
            return

        try:
            # Paho MQTT v2 compatibility
            try:
                self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pdm_fastapi_backend")
            except Exception:
                self.client = mqtt.Client(client_id="pdm_fastapi_backend")

            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            # Reconnection backoff
            self.client.reconnect_delay_set(min_delay=1, max_delay=10)

            # Non-blocking connection attempt
            logger.info(f"Connecting MQTT client to {self.broker_host}:{self.broker_port}...")
            self.client.connect_async(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            self.is_running = True
        except Exception as e:
            logger.warning(f"Could not start MQTT client (broker might be offline): {e}")

    def stop(self):
        """Stops background network thread."""
        if self.client and self.is_running:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass
            self.is_running = False
            self.is_connected = False

    def configure(self, broker_host: Optional[str] = None, broker_port: Optional[int] = None, topic: Optional[str] = None) -> Dict[str, Any]:
        """Dynamically reconfigures broker connection parameters and reconnects."""
        self.stop()
        with self._lock:
            if broker_host:
                self.broker_host = broker_host.strip()
            if broker_port:
                self.broker_port = int(broker_port)
            if topic:
                self.topic = topic.strip()
            self.last_packet_arrival_time = None
        self.start()
        logger.info(f"MQTT Listener reconfigured to {self.broker_host}:{self.broker_port}, topic: {self.topic}")
        return self.get_status()

    def is_stream_active(self) -> bool:
        """
        Returns True if MQTT packets have been received within the heartbeat timeout window.
        Returns False if stream has stalled or not yet connected.
        """
        with self._lock:
            if self.last_packet_arrival_time is None:
                return False
            elapsed_since_packet = time.time() - self.last_packet_arrival_time
            return elapsed_since_packet <= self.heartbeat_timeout_s

    def get_live_telemetry(self) -> Optional[Dict[str, Any]]:
        """Returns the latest normalized telemetry if stream is active, else None."""
        with self._lock:
            if not self.is_stream_active() or self.latest_features is None:
                return None
            return {
                "machine_id": self.active_machine_id,
                "features": self.latest_features.copy(),
                "last_delta_t_ms": self.last_delta_t_ms,
                "packet_count": self.packet_count,
                "audit": self.latest_audit.copy()
            }

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive diagnostic status for /api/mqtt/status."""
        with self._lock:
            now = time.time()
            elapsed_s = round(now - self.last_packet_arrival_time, 2) if self.last_packet_arrival_time else None
            avg_jitter = round(sum(self.jitter_window) / len(self.jitter_window), 1) if self.jitter_window else 0.0

            active = self.is_stream_active()

            if active:
                status_str = "STREAM_ACTIVE"
            elif self.is_connected:
                status_str = "CONNECTED_IDLE"
            else:
                status_str = "DISCONNECTED"

            return {
                "mqtt_status": status_str,
                "is_connected": self.is_connected,
                "is_stream_active": active,
                "broker_address": f"{self.broker_host}:{self.broker_port}",
                "subscribed_topic": self.topic,
                "target_machine_id": self.active_machine_id,
                "total_packets_received": self.packet_count,
                "nominal_interval_ms": self.nominal_interval_ms,
                "last_delta_t_ms": self.last_delta_t_ms,
                "average_jitter_ms": avg_jitter,
                "seconds_since_last_packet": elapsed_s,
                "heartbeat_timeout_seconds": self.heartbeat_timeout_s,
                "active_tag_count": len(self.latest_audit.get("recognized_tags", [])),
                "supported_tags": list(TURBINE_TAG_REGISTRY.keys()),
            }


# Global singleton listener instance
mqtt_listener = IndustrialMQTTListener()
