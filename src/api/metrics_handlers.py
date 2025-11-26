# handlers/metrics_handlers.py
from flask import jsonify, request
from api_utils import safe
from src.db.query_handlers import query_handlers

@safe
def get_telemetry(id):
    return jsonify(query_handlers["listTelemetryForNode"](id))

@safe
def get_events(id):
    event_type = request.args.get("type")
    return jsonify(query_handlers["listEventsForNode"](id, event_type))

@safe
def get_metrics():
    return jsonify(query_handlers["getVoltageStats"]())

handlers = {
    "getTelemetry": get_telemetry,
    "getEvents": get_events,
    "getMetrics": get_metrics,
}
