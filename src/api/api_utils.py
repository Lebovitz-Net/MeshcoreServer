# src/api/api_utils.py
import json
import hashlib
import re
from aiohttp import web
from functools import wraps


def safe(fn):
    """
    Decorator that wraps all API handlers and ensures:
    - Exceptions are caught
    - Errors are logged
    - A JSON error response is returned
    """
    @wraps(fn)
    async def wrapper(request, *args, **kwargs):
        try:
            return await fn(request, *args, **kwargs)
        except web.HTTPException:
            raise
        except Exception as err:
            print(f"[safe] Error: {err}")
            return web.json_response({"error": "Internal server error"}, status=500)
    return wrapper


def safe_json(data):
    """
    Convert sqlite Row objects or lists of Rows into JSON-serializable structures.
    Handles:
    - sqlite3.Row
    - lists/tuples of rows
    - nested dicts
    - primitives
    """
    if data is None:
        return None

    # sqlite3.Row or similar
    if hasattr(data, "keys"):
        return {k: safe_json(data[k]) for k in data.keys()}

    # list or tuple
    if isinstance(data, (list, tuple)):
        return [safe_json(item) for item in data]

    # dict
    if isinstance(data, dict):
        return {k: safe_json(v) for k, v in data.items()}

    # primitives (int, str, float, bool, None)
    return data


def generate_message_id(message_obj):
    """
    Deterministic message ID generator.
    """
    raw = json.dumps(message_obj, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def extract_sender_and_mentions(msg: str) -> tuple[str, list[str]]:
    """
    Parse a message of the form 'sender: message @[user] ...'
    Returns (sender, mentions) where:
      - sender is lowercased and stripped
      - mentions is a list of unique lowercase usernames
    """
    if ":" not in msg:
        return None, []

    sender, message = msg.split(":", 1)
    mentions = list(set(m.lower() for m in re.findall(r"@(\w+)", message)))
    return sender.strip().lower(), mentions
