# src/meshtastic/utils/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === API URL ===
API_URL = os.getenv("API_URL", "https://meshtastic.local")

# === Device connection (bridge <-> node) ===
current_ip_host = os.getenv("NODE_IP_HOST", "192.168.1.52")
current_ip_port = int(os.getenv("NODE_IP_PORT", "4403"))
_current_ip = f"{current_ip_host}:{current_ip_port}"

# === WebSocket server (UI <-> bridge) ===
current_ws_host = os.getenv("WS_HOST", "localhost")
current_ws_port = int(os.getenv("WS_PORT", "3000"))
current_ws_url = f"ws://{current_ws_host}:{current_ws_port}"

# === Utility functions ===
def get_node_ip() -> str:
    return _current_ip

def set_node_ip(ip: str):
    global _current_ip
    _current_ip = ip

def get_api_url(addr: str = current_ws_url) -> str:
    return f"http://{addr}/api/v1"

known_nodes = [
    {"name": "KD1MU Router", "ip": "192.168.2.1"},
    {"name": "Node Alpha", "ip": "192.168.2.78"},
    {"name": "Node Bravo", "ip": "192.168.2.102"},
]

def get_ws_url(input_str: str) -> str:
    import re
    if re.match(r"^wss?://", input_str):
        return input_str
    if re.match(r"^!?[a-f0-9]{8}$", input_str, re.IGNORECASE):
        clean_id = re.sub(r"^!", "", input_str)
        return f"{current_ws_url}/{clean_id}"
    return current_ws_url

# === Unified config object ===
config = {
    "api": {
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": int(os.getenv("API_PORT", "8080")),
    },
    "websocket": {
        "host": current_ws_host,
        "port": current_ws_port,
    },
    "mqtt": {
        "brokerUrl": os.getenv("MQTT_BROKER_URL", ""),
        "subTopic": "mesh/ingest",
        "pubOptions": {"qos": 1},
    },
    "tcp": {
        "host": os.getenv("TCP_HOST", "0.0.0.0"),
        "port": int(os.getenv("TCP_PORT", "1337")),
    },
    "node": {
        "host": current_ip_host,
        "port": current_ip_port,
    },
}

NODE_TYPES = {
    "MESHTASTIC": 0,
    "MESHCORE": 1,
}
