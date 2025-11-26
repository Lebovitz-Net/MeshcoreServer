# handlers/diagnostics_handlers.py
from flask import jsonify, request
from api_utils import safe
from src.db.query_handlers import query_handlers
from src.db.insert_handlers import insert_handlers

@safe
def get_logs_handler():
    limit = int(request.args.get("limit", 200))
    return jsonify(query_handlers["listLogs"](limit))

@safe
def reload_config_handler():
    return jsonify(query_handlers["getFullConfig"]())

@safe
def list_packets_handler():
    limit = int(request.args.get("limit", 100))
    return jsonify(query_handlers["listPacketLogs"](limit))

@safe
def get_packet_handler(id):
    pkt = query_handlers["getPacketLogById"](id)
    if not pkt:
        return jsonify({"error": "Packet not found"}), 404
    return jsonify(pkt)

@safe
def inject_packet_handler():
    result = insert_handlers["injectPacketLog"](request.json)
    return jsonify({"success": True, "result": result})

handlers = {
    "getLogsHandler": get_logs_handler,
    "reloadConfigHandler": reload_config_handler,
    "listPacketsHandler": list_packets_handler,
    "getPacketHandler": get_packet_handler,
    "injectPacketHandler": inject_packet_handler,
}
