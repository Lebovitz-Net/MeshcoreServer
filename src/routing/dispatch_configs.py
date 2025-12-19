# src/routing/dispatch_configs.py

import json
from .dispatch_utils import normalize_packet


class DispatchConfigs:
    def device_info(self, packet: dict):
        data, meta = packet["data"], packet["meta"]
        print(".../dispatchConfigs DeviceInfo")

    def err(self, packet: dict):
        data, meta = packet["data"], packet["meta"]
        print(".../dispatchConfigs Err")

    def config(self, sub_packet: dict):
        meta, data = sub_packet["meta"], sub_packet["data"]
        config = data.get("config", {})
        if data and len(data.keys()):
            key, value = list(config.items())[0]
            self.insert_handlers.insertConfig({
                "fromNodeNum": meta["fromNodeNum"],
                "key": key,
                "data": json.dumps(value),
                "timestamp": meta["fromNodeNum"],
                "device_id": meta["device_id"],
                "connId": meta["connId"],
            })

    def device(self, sub_packet: dict):
        print("[dispatchConfig] device")

    def security(self, sub_packet: dict):
        print("[dispatchConfig] security")

    def module_config(self, packet: dict):
        data, meta = packet["data"], packet["meta"]

        config = data.get("moduleConfig", {})
        if not config:
            return
        key, value = list(config.items())[0]
        if not value or len(value.keys()) == 0:
            return

        self.insert_handlers.insertModuleConfig({
            "fromNodeNum": meta["fromNodeNum"],
            "key": key,
            "data": json.dumps(value),
            "timestamp": meta["fromNodeNum"],
            "device_id": meta["device_id"],
            "connId": meta["connId"],
        })

    def device_ui_config(self, sub_packet: dict):
        print("[dispatchConfig] Ignoring DeviceUIConfig")

    def deviceuiconfig(self, sub_packet: dict):
        print("[dispatchConfig] Ignoring deviceuiConfig")

    def admin_message(self, sub_packet: dict):
        print("[dispatchConfig] Ignoring AdminMessage")

    def routing_message(self, sub_packet: dict):
        print("[dispatchConfig] Ignoring Routing")

    def route_discovery(self, sub_packet: dict):
        print("[dispatchConfig] RouteDiscovery")

    def routing(self, sub_packet: dict):
        print("[dispatchConfig] Routing")

    def metadata(self, packet: dict):
        data, meta = packet["data"], packet["meta"]

        metadata = data.get("metadata", {})
        if not metadata or len(metadata.keys()) == 0:
            print("[dispatchRegistry] metadata object is empty", metadata)
            return

        self.insert_handlers.insertMetadata({
            **metadata,
            "canShutdown": 1 if metadata.get("canShutdown") else 0,
            "hasWifi": 1 if metadata.get("hasWifi") else 0,
            "hasBluetooth": 1 if metadata.get("hasBluetooth") else 0,
            "hasPKC": 1 if metadata.get("hasPKC") else 0,
            "num": meta["fromNodeNum"],
        })

    def device_metadata(self, sub_packet: dict):
        print("[dispatchConfig] ... DeviceMetadata", sub_packet)

    def file_info(self, sub_packet: dict):
        data, meta = sub_packet["data"], sub_packet["meta"]
        file_info = data.get("fileInfo", {})
        self.insert_handlers.insertFileInfo({
            "filename": file_info.get("fileName"),
            "size": file_info.get("sizeBytes"),
            "mime_type": file_info.get("mime_type"),
            "description": file_info.get("description"),
            "fromNodeNum": meta["fromNodeNum"],
            "device_id": meta["device_id"],
            "connId": meta["connId"],
            "timestamp": meta["timestamp"],
        })

    def mqtt_client_proxy_message(self, sub_packet: dict):
        # placeholder
        pass

    def key_verification(self, sub_packet: dict):
        print("[dispatchConfigs] KeyVerification")

    def key_verification_number_request(self, sub_packet: dict):
        print("[dispatchConfig] keyVerificationNumberRequest")

    def config_complete_id(self, sub_packet: dict):
        print("[dispatchConfig] configComplete", sub_packet)
