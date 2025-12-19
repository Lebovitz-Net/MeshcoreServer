# startup_mqtt.py
import asyncio
import logging
from src.config.config import config
from src.handlers.mqtt_handler import MqttHandler

async def start_mqtt_server() -> MqttHandler | None:
    """Thin startup wrapper: instantiate handler and connect."""
    logging.info("[MQTT] ===== STARTING UP MQTT =====")
    broker_host = config["mqtt"].get("brokerHost", "")
    broker_port = config["mqtt"].get("brokerPort", 1883)
    node_id     = config["mqtt"].get("nodeId", "meshcore-node")

    handler = MqttHandler(broker=broker_host, options=config.get("mqttOptions", {}))
    try:
        # run connect in a thread to avoid blocking the event loop
        await handler.connect(node_id, broker_port)
        logging.info("[MQTT] Handler started successfully")
        return handler
    except Exception as e:
        logging.error(f"[MQTT] Startup failed: {e}")
        return None

async def shutdown_mqtt_server(handler: MqttHandler | None) -> None:
    """Thin shutdown wrapper: delegate to handler."""
    if handler:
        await asyncio.to_thread(handler.shutdown)
        logging.info("[MQTT] Handler shut down")
