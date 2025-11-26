# handlers/config_handlers.py
from flask import jsonify, request
from api_utils import safe
from src.db.query_handlers import query_handlers

@safe
def get_full_config_handler():
    return jsonify(query_handlers["getFullConfig"]())

@safe
def get_config_handler(id):
    config = query_handlers["getConfig"](id)
    if not config:
        return jsonify({"error": "Config not found"}), 404
    return jsonify(config)

@safe
def list_all_configs_handler():
    return jsonify(query_handlers["listAllConfigs"]())

@safe
def get_module_config_handler(id):
    config = query_handlers["getModuleConfig"](id)
    if not config:
        return jsonify({"error": "Module config not found"}), 404
    return jsonify(config)

@safe
def list_all_module_configs_handler():
    return jsonify(query_handlers["listAllModuleConfigs"]())

@safe
def get_metadata_by_key_handler(key):
    meta = query_handlers["getMetadataByKey"](key)
    if not meta:
        return jsonify({"error": "Metadata not found"}), 404
    return jsonify(meta)

@safe
def list_all_metadata_handler():
    return jsonify(query_handlers["listAllMetadata"]())

@safe
def list_file_info_handler():
    return jsonify(query_handlers["listFileInfo"]())

# Export handlers in a dict for aggregator
handlers = {
    "getFullConfigHandler": get_full_config_handler,
    "getConfigHandler": get_config_handler,
    "listAllConfigsHandler": list_all_configs_handler,
    "getModuleConfigHandler": get_module_config_handler,
    "listAllModuleConfigsHandler": list_all_module_configs_handler,
    "getMetadataByKeyHandler": get_metadata_by_key_handler,
    "listAllMetadataHandler": list_all_metadata_handler,
    "listFileInfoHandler": list_file_info_handler,
}
