# src/events/emitters.py
from sse import broadcast_event

def emit_node_update(node: dict):
    """
    Emit a node update event over SSE.
    """
    node_id = node.get("num") or node.get("device_id") or "unknown"
    broadcast_event({"type": "node", "node": node})

def emit_channel_update(channel: dict):
    """
    Emit a channel update event over SSE.
    """
    channel_id = channel.get("channel_num") or channel.get("index") or "unknown"
    broadcast_event({"type": "channel", "channel": channel})

def emit_message_update(message: dict):
    """
    Emit a message update event over SSE.
    """
    message_id = message.get("messageId") or "unknown"
    broadcast_event({"type": "message", "message": message})
