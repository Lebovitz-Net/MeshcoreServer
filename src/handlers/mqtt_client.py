import json
import paho.mqtt.client as mqtt


class MqttHandler:
    def __init__(self, broker: str, options: dict = None):
        self.broker = broker
        self.options = options or {}
        self.client = None

    def connect(self, node_id: str):
        # Create client
        self.client = mqtt.Client()

        # Apply options (username/password, TLS, etc.)
        if "username" in self.options and "password" in self.options:
            self.client.username_pw_set(
                self.options["username"], self.options["password"]
            )
        if "tls" in self.options:
            self.client.tls_set(**self.options["tls"])

        # Event handlers
        self.client.on_connect = lambda client, userdata, flags, rc: self._on_connect(
            node_id, rc
        )
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # Connect
        self.client.connect(self.broker)
        self.client.loop_start()

    def _on_connect(self, node_id: str, rc: int):
        if rc == 0:
            print(f"[MQTT] Connected to {self.broker}")
            # Subscriptions
            self.client.subscribe("meshcore/test", qos=1)
            self.client.subscribe("meshcore/ingest", qos=1)
            self.client.subscribe(f"meshcore/{node_id}/downlink", qos=1)
            self.client.subscribe("meshcore/+/uplink", qos=1)

            # Test publish
            self.client.publish("meshcore/test", "Hello MeshCore!", qos=1)
        else:
            print(f"[MQTT] Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        print("[MQTT] Connection closed")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        parts = topic.split("/")
        node_id = parts[1] if len(parts) > 1 else None

        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            payload = msg.payload.decode("utf-8")

        if topic.endswith("/uplink"):
            print(f"[MQTT] Uplink from {node_id}: {payload}")
            # TODO: process uplink payload (store, forward, etc.)
        elif topic.endswith("/downlink"):
            print(f"[MQTT] Downlink for {node_id}: {payload}")
            # TODO: forward payload into MeshCore
        else:
            print(f"[MQTT] Other message: {topic} {payload}")

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            print("[MQTT] Disconnected")

    def subscribe(self, topic: str, qos: int = 0):
        if self.client:
            result, mid = self.client.subscribe(topic, qos=qos)
            if result == mqtt.MQTT_ERR_SUCCESS:
                print(f"[MQTT] Subscribed to {topic}")
            else:
                print(f"[MQTT] Subscribe error: {result}")

    def publish(self, topic: str, payload, qos: int = 0, retain: bool = False):
        if self.client:
            result, mid = self.client.publish(topic, payload, qos=qos, retain=retain)
            if result == mqtt.MQTT_ERR_SUCCESS:
                print(f"[MQTT] Published to {topic}: {payload}")
            else:
                print(f"[MQTT] Publish error: {result}")

    def set_on_message(self, callback):
        if self.client:
            self.client.on_message = callback

    def set_on_connect(self, callback):
        if self.client:
            self.client.on_connect = callback

    def set_on_disconnect(self, callback):
        if self.client:
            self.client.on_disconnect = callback
