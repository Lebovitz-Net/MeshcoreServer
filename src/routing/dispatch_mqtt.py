# src/routing/dispatch_mqtt.py
from src.meshcore.string_utils import decode_python_string


class DispatchMqtt:
    def mqtt(self, sub_packet: dict):
        print("[dispatchMqtt] mqtt", sub_packet)

        # Example extension:
        # data, meta = sub_packet.get("data"), sub_packet.get("meta")
        # decoded = decode_python_string(data.get("payload", ""))
        # self.insert_handlers.insertMqttMessage({"payload": decoded, **meta})
        # self.emit("mqtt", sub_packet)
        # self.overlay.emit("mqttReceived", sub_packet)
