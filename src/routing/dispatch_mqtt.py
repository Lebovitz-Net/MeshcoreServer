from db.insert_handlers import insertHandlers
from events.overlay_emitter import emitOverlay
from events.event_emitter import emitEvent
from meshcore.utils.string_utils import decode_python_string


def handle_mqtt(sub_packet: dict):
    print("[dispatchMqtt] mqtt", sub_packet)
    # Example extension:
    # data, meta = sub_packet.get("data"), sub_packet.get("meta")
    # decoded = decode_python_string(data.get("payload", ""))
    # insertHandlers.insertMqttMessage({"payload": decoded, **meta})
    # emitOverlay("mqtt", sub_packet)
    # emitEvent("mqttReceived", sub_packet)


dispatchMqtt = {
    "mqtt": handle_mqtt
}
