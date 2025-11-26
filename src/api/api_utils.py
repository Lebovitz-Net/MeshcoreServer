# api_utils.py
import hashlib, re, time
from functools import wraps
from flask import jsonify

def safe(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as err:
            print(f"[safe] Error: {err}")
            return jsonify({"error": "Internal server error"}), 500
    return wrapper

def generate_message_id(packet: dict) -> str:
    base = "|".join([
        packet.get("protocol", "meshcore"),
        str(packet.get("sender")),
        packet.get("channel", "default"),
        str(packet.get("timestamp", int(time.time()*1000))),
        packet.get("text") or packet.get("message", "")
    ])
    return hashlib.sha256(base.encode()).hexdigest()[:16]

def extract_sender_and_mentions(msg: str) -> dict:
    if ":" not in msg:
        return {"sender": None, "message": msg, "mentions": None}
    sender, message = msg.split(":", 1)
    mentions = list(set(m.lower() for m in re.findall(r"@(\w+)", message)))
    return {"sender": sender.strip().lower(), "message": message.strip(), "mentions": mentions}
