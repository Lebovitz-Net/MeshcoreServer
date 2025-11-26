# src/bridge/events/overlay_emitter.py

"""
OverlayEmitter is a simple pub/sub for diagnostic overlays.
It lets the ingestion pipeline broadcast events (message, position, telemetry, etc.)
to any listeners (UI, logs, metrics dashboards).
"""

from typing import Callable, Any, Set

class OverlayEmitter:
    def __init__(self):
        self._listeners: Set[Callable[[str, Any], None]] = set()

    def subscribe_overlay(self, fn: Callable[[str, Any], None]):
        """
        Subscribe to overlay events.
        fn: callback(event_type, payload)
        Returns an unsubscribe function.
        """
        self._listeners.add(fn)

        def unsubscribe():
            self._listeners.discard(fn)
        return unsubscribe

    def emit_overlay(self, event_type: str, payload: Any):
        """
        Emit an overlay event to all subscribers.
        event_type: e.g. 'message', 'position', 'telemetry'
        payload: normalized subPacket
        """
        for fn in list(self._listeners):
            try:
                fn(event_type, payload)
            except Exception as err:
                print(f"[overlayEmitter] Listener error: {err}")

    def enable_console_overlay_logger(self):
        """
        Utility: log overlays to console (for dev/debug).
        """
        def logger(event_type: str, payload: Any):
            print(f"[overlayEmitter] {event_type}", {
                "from": getattr(payload, "fromNodeNum", None) or payload.get("fromNodeNum"),
                "to": getattr(payload, "toNodeNum", None) or payload.get("toNodeNum"),
                "device": getattr(payload, "device_id", None) or payload.get("device_id"),
                "data": getattr(payload, "data", None) or payload.get("data"),
                "meta": getattr(payload, "meta", None) or payload.get("meta"),
            })
        self.subscribe_overlay(logger)


# ✅ create a global instance if you want singleton behavior
overlay_emitter = OverlayEmitter()
