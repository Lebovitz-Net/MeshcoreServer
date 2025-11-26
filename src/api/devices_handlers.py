# handlers/devices_handlers.py
from flask import jsonify
from api_utils import safe
from src.db.query_handlers import query_handlers

@safe
def list_devices_handler():
    return jsonify(query_handlers["listDevices"]())

@safe
def get_device_handler(device_id):
    device = query_handlers["getDevice"](device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    settings = query_handlers["getDeviceSetting"](device_id)
    return jsonify({**device, "settings": settings})

@safe
def get_device_setting_handler(device_id, config_type):
    setting = query_handlers["listDeviceSettings"](device_id, config_type)
    if not setting:
        return jsonify({"error": "Setting not found"}), 404
    return jsonify(setting)

handlers = {
    "listDevicesHandler": list_devices_handler,
    "getDeviceHandler": get_device_handler,
    "getDeviceSettingHandler": get_device_setting_handler,
}
