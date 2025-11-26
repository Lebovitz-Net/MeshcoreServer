# src/bridge/events/event_emitter.py

"""
EventEmitter for lifecycle + system events.
Used by dispatch_registry to signal things like config_complete, message_received, etc.
"""

from collections import defaultdict
from typing import Callable, Dict, Set, Any

class EventEmitter:
    def __init__(self):
        self._listeners: Dict[str, Set[Callable]] = defaultdict(set)

    def on_event(self, event_type: str, fn: Callable):
        """
        Subscribe to a named event.
        Returns an unsubscribe function.
        """
        self._listeners[event_type].add(fn)

        def unsubscribe():
            self._listeners[event_type].discard(fn)
        return unsubscribe

    def emit_event(self, event_type: str, payload: Any):
        """
        Emit an event to all subscribers.
        """
        subs = self._listeners.get(event_type)
        if not subs:
            return
        for fn in list(subs):
            try:
                fn(payload)
            except Exception as err:
                print(f"[eventEmitter] Listener for {event_type} failed: {err}")

    def enable_console_event_logger(self):
        """
        Utility: log all events to console (for dev/debug).
        """
        def logger(payload):
            print("[eventEmitter]", payload)
        self.on_event("*", logger)

# ✅ create a global emitter instance if you want singleton behavior
event_emitter = EventEmitter()
