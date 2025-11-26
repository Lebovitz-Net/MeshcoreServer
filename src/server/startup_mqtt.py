# src/mqtt_startup.py
import time
import paho.mqtt.client as mqtt
from config import config

def start_mqtt_server():
    """
    Start the MQTT bridge client.
    Connects to broker, subscribes to ingest topic, returns the client.
    """

    # Generate unique client ID
    client_id = f"mqtt-bridge-{int(time.time() * 1000)}"

    # Create client with MQTT v3.1.1
    client = mqtt.Client(
        client_id=client_id,
        protocol=mqtt.MQTTv311,
        clean_session=True
    )

    # Configure keepalive
    client.keepalive = 60

    # Optional: set callbacks
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"[MQTT] Connected to broker {config['mqtt']['brokerUrl']} as {client_id}")
            # Subscribe once connected
            client.subscribe(config["mqtt"]["subTopic"], qos=1)
        else:
            print(f"[MQTT] Connection failed with code {rc}")

    def on_message(client, userdata, msg):
        print(f"[MQTT] Received on {msg.topic}: {msg.payload.decode(errors='replace')}")

    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to broker
    broker_url = config["mqtt"]["brokerUrl"]
    if broker_url:
        client.connect(broker_url)
    else:
        print("[MQTT] No broker URL configured")

    # Start network loop in background thread
    client.loop_start()

    return client
