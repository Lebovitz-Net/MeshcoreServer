import json
import logging
import paho.mqtt.client as mqtt
import asyncio
import socket

logging.basicConfig(level=logging.INFO)

class MqttHandler:
    def __init__(self, broker: str, options: dict = None):
        self.broker = broker
        self.options = options or {}
        self.client = None
        self.node_id = None

    async def connect(self, node_id: str, port: int = 1883, keepalive: int = 60,
                      retries: int = 3, delay: int = 5):
        """Async-friendly connect to MQTT broker with retry logic and DNS check."""
        logging.info(f"[MQTT] Server Startup - Connecting to {self.broker}")
        self.node_id = node_id
        self.client = mqtt.Client(client_id=node_id)

        # Apply options (username/password, TLS, etc.)
        if "username" in self.options and "password" in self.options:
            self.client.username_pw_set(
                self.options["username"], self.options["password"]
            )
        if "tls" in self.options:
            self.client.tls_set(**self.options["tls"])

        # Event handlers
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # DNS pre-check
        try:
            socket.getaddrinfo(self.broker, port)
        except socket.gaierror as e:
            raise ConnectionError(f"DNS resolution failed for {self.broker}:{port} ({e})")

        # Retry loop
        for attempt in range(1, retries + 1):
            try:
                self.client.connect(self.broker, port=port, keepalive=keepalive)
                self.client.loop_start()
                return
            except Exception as e:
                logging.error(f"[MQTT] Connect attempt {attempt} failed: {e}")
                await asyncio.sleep(delay)  # async-friendly sleep
        raise ConnectionError(f"Failed to connect to MQTT broker {self.broker}:{port}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info(f"[MQTT] Connected to {self.broker}")
            # Subscriptions
            self.subscribe("meshcore/test", qos=1)
            self.subscribe("meshcore/ingest", qos=1)
            self.subscribe(f"meshcore/{self.node_id}/downlink", qos=1)
            self.subscribe("meshcore/+/uplink", qos=1)  # ✅ fixed wildcard

            # Test publish
            self.publish("meshcore/test", "Hello MeshCore!", qos=1)
        else:
            logging.error(f"[MQTT] Connection failed: {mqtt.error_string(rc)}")

    def _on_disconnect(self, client, userdata, rc):
        logging.warning(f"[MQTT] Connection closed (code {rc})")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        parts = topic.split("/")
        node_id = parts[1] if len(parts) > 2 else None

        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            payload = msg.payload.decode("utf-8")

        if topic.endswith("/uplink") and node_id:
            logging.info(f"[MQTT] Uplink from {node_id}: {payload}")
            # TODO: process uplink payload
        elif topic.endswith("/downlink") and node_id:
            logging.info(f"[MQTT] Downlink for {node_id}: {payload}")
            # TODO: forward payload into MeshCore
        else:
            logging.info(f"[MQTT] Other message: {topic} {payload}")

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logging.info("[MQTT] Disconnected")

    def subscribe(self, topic: str, qos: int = 0):
        if self.client:
            result, mid = self.client.subscribe(topic, qos=qos)
            if result == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"[MQTT] Subscribed to {topic} id {mid}")
            else:
                logging.error(f"[MQTT] Subscribe error: {mqtt.error_string(result)}")

    def publish(self, topic: str, payload, qos: int = 0, retain: bool = False):
        if self.client:
            result, mid = self.client.publish(topic, payload, qos=qos, retain=retain)
            if result == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"[MQTT] Published to {topic}: {payload} id {mid}")
            else:
                logging.error(f"[MQTT] Publish error: {mqtt.error_string(result)}")

    def set_on_message(self, callback):
        if self.client:
            self.client.on_message = callback

    def set_on_connect(self, callback):
        if self.client:
            self.client.on_connect = callback

    def set_on_disconnect(self, callback):
        if self.client:
            self.client.on_disconnect = callback

    async def shutdown(self):
        """Async, graceful shutdown of MQTT client."""
        logging.info("[MQTT] Shutting down...")
        try:
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
                logging.info("[MQTT] Client disconnected.")
        except Exception as e:
            logging.error(f"[MQTT] Error during shutdown: {e}")
        finally:
            self.client = None
        logging.info("[MQTT] Shutdown complete.")
