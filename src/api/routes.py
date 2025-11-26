# routes.py
from flask import Flask, request, jsonify
from handlers import api_handlers
from config.config import get_node_ip, set_node_ip

def register_routes(app: Flask):
    # --- Root ---
    app.add_url_rule("/", "health", api_handlers["health"], methods=["GET"])

    # --- Runtime Config ---
    @app.route("/api/v1/node-ip", methods=["GET"])
    def get_node_ip_route():
        return jsonify({"ip": get_node_ip()})

    @app.route("/api/v1/node-ip", methods=["POST"])
    def set_node_ip_route():
        ip = request.json.get("ip")
        if not ip or ":" not in ip:
            return jsonify({"error": 'Invalid IP format. Expected "host:port".'}), 400
        set_node_ip(ip)
        return jsonify({"success": True, "ip": ip})

    # --- System ---
    app.add_url_rule("/api/v1/config", "getConfig", api_handlers["getConfig"], methods=["GET"])
    app.add_url_rule("/api/v1/version", "getVersion", api_handlers["getVersion"], methods=["GET"])
    app.add_url_rule("/api/v1/health", "getHealth", api_handlers["getHealth"], methods=["GET"])

    # --- Nodes ---
    app.add_url_rule("/api/v1/nodes/<id>/connections", "listConnections", api_handlers["listConnections"], methods=["GET"])
    app.add_url_rule("/api/v1/nodes/<id>", "getNodeHandler", api_handlers["getNodeHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/nodes/<id>", "deleteNodeHandler", api_handlers["deleteNodeHandler"], methods=["DELETE"])
    app.add_url_rule("/api/v1/nodes", "listNodesHandler", api_handlers["listNodesHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/channels/<id>", "listChannels", api_handlers["listChannels"], methods=["GET"])

    # --- Messages ---
    app.add_url_rule("/api/v1/messages", "listMessagesHandler", api_handlers["listMessagesHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/messages", "sendMessageHandler", api_handlers["sendMessageHandler"], methods=["POST"])

    # --- My Info ---
    app.add_url_rule("/api/v1/myinfo", "listMyInfoHandler", api_handlers["listMyInfoHandler"], methods=["GET"])

    # --- Contacts ---
    app.add_url_rule("/api/v1/contacts", "listContactsHandler", api_handlers["listContactsHandler"], methods=["GET"])

    # --- Packets ---
    app.add_url_rule("/api/v1/packets", "listPacketsHandler", api_handlers["listPacketsHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/packets/<id>", "getPacketHandler", api_handlers["getPacketHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/packets", "injectPacketHandler", api_handlers["injectPacketHandler"], methods=["POST"])

    # --- Metrics ---
    app.add_url_rule("/api/v1/nodes/<id>/packet-logs", "getPacketLogs", api_handlers["getPacketLogs"], methods=["GET"])
    app.add_url_rule("/api/v1/nodes/<id>/telemetry", "getTelemetry", api_handlers["getTelemetry"], methods=["GET"])
    app.add_url_rule("/api/v1/nodes/<id>/events", "getEvents", api_handlers["getEvents"], methods=["GET"])
    app.add_url_rule("/api/v1/metrics", "getMetrics", api_handlers["getMetrics"], methods=["GET"])

    # --- Diagnostics & Logs ---
    app.add_url_rule("/api/v1/logs", "getLogsHandler", api_handlers["getLogsHandler"], methods=["GET"])

    # --- Config ---
    app.add_url_rule("/api/v1/config/full", "getFullConfigHandler", api_handlers["getFullConfigHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/config/<id>", "getConfigHandler", api_handlers["getConfigHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/configs", "listAllConfigsHandler", api_handlers["listAllConfigsHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/module-config/<id>", "getModuleConfigHandler", api_handlers["getModuleConfigHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/module-configs", "listAllModuleConfigsHandler", api_handlers["listAllModuleConfigsHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/metadata/<key>", "getMetadataByKeyHandler", api_handlers["getMetadataByKeyHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/metadata", "listAllMetadataHandler", api_handlers["listAllMetadataHandler"], methods=["GET"])
    app.add_url_rule("/api/v1/files", "listFileInfoHandler", api_handlers["listFileInfoHandler"], methods=["GET"])

    # --- Control ---
    app.add_url_rule("/api/v1/restart", "restartServicesHandler", api_handlers["restartServicesHandler"], methods=["POST"])
    app.add_url_rule("/api/v1/reload-config", "reloadConfigHandler", api_handlers["reloadConfigHandler"], methods=["POST"])
