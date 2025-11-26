# services_manager.py
import time
from global_state import global_state
from src.db.query_handlers import query_handlers

def teardown_services():
    print("⚠️  Tearing down services...")

    if global_state.mesh:
        print("Closing Mesh TCP connection...")
        global_state.mesh.end()

    if global_state.mqtt_handler:
        print("Disconnecting MQTT...")
        global_state.mqtt_handler.disconnect()

    if global_state.tcp_server:
        print("Closing TCP server...")
        global_state.tcp_server.close()

    if global_state.ws_server:
        print("Closing WebSocket server...")
        global_state.ws_server.close()

    if global_state.api_server:
        print("Closing API server...")
        global_state.api_server.close()

    print("✅ Teardown complete.")

def init_services(config):
    print("🚀 Initializing backend services...")

    # Replace with your actual service initializers
    global_state.tcp_server = start_tcp_server(config)
    global_state.ws_server = start_ws_server(config)
    global_state.mqtt_handler = connect_mqtt(config)
    global_state.mesh = open_mesh_socket(config)
    start_ingestion_loop(config)

    print("✅ All services initialized.")

def shutdown(signal="manual"):
    print(f"\n⚠️  Received {signal}, shutting down gracefully...")
    teardown_services()

def restart_services():
    print("🔄 Restarting backend services...")
    teardown_services()
    time.sleep(1)
    config = query_handlers["getFullConfig"]()
    init_services(config)
    print("✅ Restart complete.")
    return {"restarted": True, "timestamp": int(time.time()*1000)}
