import json
from db.insert_handlers import insertHandlers
from overlays.overlay_emitter import emitOverlay
from events.event_emitter import emitEvent


def handle_device_info(data: dict):
    print(".../dispatchConfigs DeviceInfo")


def handle_err(packet: dict):
    data, meta = packet["data"], packet["meta"]
    print(".../dispatchConfigs Error Code:", data.get("errCode"))


def handle_config(sub_packet: dict):
    meta, data = sub_packet["meta"], sub_packet["data"]
    config = data.get("config", {})
    if data and len(data.keys()):
        key, value = list(config.items())[0]
        insertHandlers.insertConfig({
            "fromNodeNum": meta["fromNodeNum"],
            "key": key,
            "data": json.dumps(value),
            "timestamp": meta["fromNodeNum"],
            "device_id": meta["device_id"],
            "connId": meta["connId"],
        })
    emitOverlay("config", sub_packet)
    emitEvent("configSet", sub_packet)


def handle_device(sub_packet: dict):
    print("[dispatchConfig] device")


def handle_security(sub_packet: dict):
    print("[dispatchConfig] security")


def handle_module_config(sub_packet: dict):
    meta, data = sub_packet["meta"], sub_packet["data"]
    config = data.get("moduleConfig", {})
    if not config:
        return
    key, value = list(config.items())[0]
    if not value or len(value.keys()) == 0:
        return

    insertHandlers.insertModuleConfig({
        "fromNodeNum": meta["fromNodeNum"],
        "key": key,
        "data": json.dumps(value),
        "timestamp": meta["fromNodeNum"],
        "device_id": meta["device_id"],
        "connId": meta["connId"],
    })

    emitOverlay("config", sub_packet)
    emitEvent("configSet", sub_packet)


def handle_device_ui_config(sub_packet: dict):
    print("[dispatchConfig] Ignoring DeviceUIConfig")


def handle_deviceui_config(sub_packet: dict):
    print("[dispatchConfig] Ignoring deviceuiConfig")


def handle_admin_message(sub_packet: dict):
    print("[dispatchConfig] Ignoring AdminMessage")
    emitOverlay("adminMessage", sub_packet)


def handle_routing_message(sub_packet: dict):
    print("[dispatchConfig] Ignoring Routing")
    emitOverlay("Routing", sub_packet)


def handle_route_discovery(sub_packet: dict):
    print("[dispatchConfig] RouteDiscovery")


def handle_routing(sub_packet: dict):
    print("[dispatchConfig] Routing")


def handle_metadata(sub_packet: dict):
    data, meta = sub_packet["data"], sub_packet["meta"]
    metadata = data.get("metadata", {})
    if not metadata or len(metadata.keys()) == 0:
        print("[dispatchRegistry] metadata object is empty", metadata)
        return

    insertHandlers.insertMetadata({
        **metadata,
        "canShutdown": 1 if metadata.get("canShutdown") else 0,
        "hasWifi": 1 if metadata.get("hasWifi") else 0,
        "hasBluetooth": 1 if metadata.get("hasBluetooth") else 0,
        "hasPKC": 1 if metadata.get("hasPKC") else 0,
        "num": meta["fromNodeNum"],
    })


def handle_device_metadata(sub_packet: dict):
    print("[dispatchConfig] ... DeviceMetadata", sub_packet)


def handle_file_info(sub_packet: dict):
    data, meta = sub_packet["data"], sub_packet["meta"]
    file_info = data.get("fileInfo", {})
    insertHandlers.insertFileInfo({
        "filename": file_info.get("fileName"),
        "size": file_info.get("sizeBytes"),
        "mime_type": file_info.get("mime_type"),
        "description": file_info.get("description"),
        "fromNodeNum": meta["fromNodeNum"],
        "device_id": meta["device_id"],
        "connId": meta["connId"],
        "timestamp": meta["timestamp"],
    })


def handle_mqtt_client_proxy_message(sub_packet: dict):
    # placeholder
    pass


def handle_key_verification(sub_packet: dict):
    print("[dispatchConfigs] KeyVerification")


def handle_key_verification_number_request(sub_packet: dict):
    print("[dispatchConfig] keyVerificationNumberRequest")


def handle_config_complete_id(sub_packet: dict):
    print("[dispatchConfig configComplete", sub_packet)
    emitEvent("configComplete")


dispatchConfigs = {
    "DeviceInfo": handle_device_info,
    "Err": handle_err,
    "config": handle_config,
    "device": handle_device,
    "security": handle_security,
    "moduleConfig": handle_module_config,
    "DeviceUIConfig": handle_device_ui_config,
    "deviceuiConfig": handle_deviceui_config,
    "adminMessage": handle_admin_message,
    "routingMessage": handle_routing_message,
    "RouteDiscovery": handle_route_discovery,
    "Routing": handle_routing,
    "metadata": handle_metadata,
    "DeviceMetadata": handle_device_metadata,
    "fileInfo": handle_file_info,
    "mqttClientProxyMessage": handle_mqtt_client_proxy_message,
    "KeyVerification": handle_key_verification,
    "keyVerificationNumberRequest": handle_key_verification_number_request,
    "configCompleteId": handle_config_complete_id,
}
