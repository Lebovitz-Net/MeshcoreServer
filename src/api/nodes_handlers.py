# handlers/nodes_handlers.py
from flask import jsonify, request
from api_utils import safe
from src.db.query_handlers import query_handlers
from src.db.insert_handlers import insert_handlers

@safe
def list_nodes_handler():
    return jsonify(query_handlers["listNodes"]())

@safe
def get_node_handler(id):
    node = query_handlers["getNode"](id)
    if not node:
        return jsonify({"error": "Node not found"}), 404
    return jsonify(node)

@safe
def delete_node_handler(id):
    insert_handlers["deleteNode"](id)
    return jsonify({"success": True})

@safe
def list_channels(id):
    return jsonify(query_handlers["listChannelsForNode"](id))

@safe
def list_connections(id):
    return jsonify(query_handlers["listConnectionsForNode"](id))

@safe
def get_packet_logs(id):
    limit = int(request.args.get("limit", 100))
    return jsonify(query_handlers["listRecentPacketLogsForNode"](id, limit))

@safe
def get_telemetry(id):
    return jsonify(query_handlers["listTelemetryForNode"](id))

@safe
def get_events(id):
    event_type = request.args.get("type")
    return jsonify(query_handlers["listEventsForNode"](id, event_type))

@safe
def list_my_info_handler():
    rows = query_handlers["getMyInfo"]()
    print("...listMyInfoHandler nodes", [row["name"] for row in rows])
    return jsonify(rows)

handlers = {
    "listNodesHandler": list_nodes_handler,
    "getNodeHandler": get_node_handler,
    "deleteNodeHandler": delete_node_handler,
    "listChannels": list_channels,
    "listConnections": list_connections,
    "getPacketLogs": get_packet_logs,
    "getTelemetry": get_telemetry,
    "getEvents": get_events,
    "listMyInfoHandler": list_my_info_handler,
}
