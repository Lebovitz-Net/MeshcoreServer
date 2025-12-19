import asyncio
import time
import traceback
from asyncio import get_running_loop
from src.meshcore.meshcore_connection import MeshcoreConnection
from meshcore_py import EventEmitter, Constants

# src/meshcore_handler.py

# Global node state cache
node_state: dict[str, dict] = {}  # key: nodeId, value: {"config": ..., "lastSeen": ..., "metadata": ...}


def update_node_state(node_id: str, updates: dict | None = None) -> None:
    """
    Update or cache node state (e.g., config, metadata).
    """
    if updates is None:
        updates = {}
    current = node_state.get(node_id, {})
    node_state[node_id] = {**current, **updates}


def get_node_state(node_id: str) -> dict:
    """
    Get current state for a node.
    Returns an empty dict if the node has not been seen yet.
    """
    return node_state.get(node_id, {})


class MeshcoreHandler(EventEmitter):
    def __init__(self, dispatcher):
        super().__init__()
        self.host = None
        self.port = None
        self.conn_id = None
        self.tcp = MeshcoreConnection()
        self.base_emit = self.tcp.emit
        def wrapper(event_name, data=None):
            self.handle_tcp_emit(event_name, data)
            return self.base_emit(event_name, data)
        self.tcp.emit = wrapper
        self.dispatcher = dispatcher
        self._response_map = self._build_response_map()

    def start_meshcore(self, net_params: dict, opts: dict = None):
        opts = opts or {}
        self.host = net_params["host"]
        self.port = net_params["port"]
        self.conn_id = net_params["connId"]     

    def _build_response_map(self):
        response_codes = Constants.ResponseCodes
        push_codes = Constants.PushCodes
        all_codes = {
            **{k: v for k, v in vars(response_codes).items() if not k.startswith("__")},
            **{k: v for k, v in vars(push_codes).items() if not k.startswith("__")},
        }
        return {value: key for key, value in all_codes.items()}

    def handle_tcp_emit(self, event_name, data=None):
        if isinstance(event_name, int):
            # Meshcore numeric events
            if event_name in (10, 5, 4, 0):
                # noMoreMessages, selfInfo, EndOfContacts, Ok
                self.emit("ok", {"connId": self.conn_id, "data": data})
            elif event_name == 1:
                self.emit("err", {"connId": self.conn_id, "data": data})

            # Normalize into routing/session
            type_name = self._response_map.get(event_name)  # e.g. "CHANNEL_INFO"
            sub_packet = {
                "type": type_name,  # dispatcher will snake_case it
                "data": data, 
                "meta": {
                    "currentIP": self.tcp.get_current_ip_address(),
                    "connId": self.conn_id,
                    "source": "meshcore",
                    "timestamp": int(time.time() * 1000),
            }}
            self.dispatcher.dispatch_packet(sub_packet)

        else:
            # String event names (Meshtastic / internal events)
            if event_name == "rx":
                pass
            elif event_name == "tx":
                self.emit("tx", {"connId": self.conn_id, "data": data})
            elif event_name == "connected":
                self.emit("connected", {
                    "connId": self.conn_id,
                    "host": self.host,
                    "port": self.port,
                })
            elif event_name == "disconnected":
                self.emit("disconnected", {
                    "connId": self.conn_id,
                    "host": self.host,
                    "port": self.port,
                })

    def ingest(self, type_, data: dict):
        meta = data.get("meta", {})
        try:
            # Route + update session state
            self.dispatcher.dispatch_packet({"type": type_, "data": data})
            # update_node_state(meta.get("connId"), {
            #     "lastSeen": int(time.time() * 1000),
            #     "metadata": {"source": "meshcore"}
            # })
        except Exception as err:
            print("[meshcoreIngest] Error responding to packet:", type_)
            traceback.print_exc() 

    async def connect(self, host, port, timeout_ms: int = 5000):
        loop = get_running_loop()
        fut = loop.create_future()
        self.host = host
        self.port = port

        def on_connected(info):
            if not fut.done():
                fut.set_result(info)

        def on_error(err):
            if not fut.done():
                fut.set_exception(err)

        # Attach listeners first
        self.on("connected", on_connected)
        self.once("error", on_error)
        # Then initiate TCP connect
        await self.tcp.connect(self.host, self.port)

        try:
            return await asyncio.wait_for(fut, timeout=timeout_ms / 1000)
        except asyncio.TimeoutError:
            self.off("connected", on_connected)
            raise TimeoutError(f"connected timeout after {timeout_ms}ms")

    # --- Shutdown ---
    def shutdown(self):
        """Gracefully shutdown TCP connection and handler itself."""
        print("[MeshcoreHandler] Shutting down...")

        # Shutdown TCP connection (cascades into MeshcoreRequests and CommandQueue)
        if self.tcp:
            try:
                self.tcp.shutdown()
                print("[MeshcoreHandler] TCP connection shut down.")
            except Exception as e:
                print(f"[MeshcoreHandler] Error shutting down TCP connection: {e}")
            finally:
                self.tcp = None

        # Clear event listeners
        try:
            super().close()
            print("[MeshcoreHandler] EventEmitter closed.")
        except Exception as e:
            print(f"[MeshcoreHandler] Error closing EventEmitter: {e}")

        print("[MeshcoreHandler] Shutdown complete.")
