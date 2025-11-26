# handlers/system_handlers.py
from flask import jsonify
from api_utils import safe
from config.config import config

@safe
def health():
    return "MeshManager v2 is running"

@safe
def get_config():
    return jsonify(config)

@safe
def get_version():
    return jsonify({"version": "1.0.0", "buildDate": __import__("datetime").datetime.utcnow().isoformat()})

@safe
def get_health():
    import time
    return jsonify({"status": "ok", "uptime": time.time()})

handlers = {
    "health": health,
    "getConfig": get_config,
    "getVersion": get_version,
    "getHealth": get_health,
}
