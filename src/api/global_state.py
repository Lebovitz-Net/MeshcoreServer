from global_state import global_state
from src.db.query_handlers import query_handlers

def init_services(config):
    print("🚀 Initializing backend services...")
    global_state.tcp_server = start_tcp_server(config)
    global_state.ws_server = start_ws_server(config)
    global_state.mqtt_handler = connect_mqtt(config)
    global_state.mesh = open_mesh_socket(config)
    start_ingestion_loop(config)
    print("✅ All services initialized.")

def teardown_services():
    print("⚠️  Tearing down services...")
    if global_state.mesh:
        global_state.mesh.end()
    if global_state.mqtt_handler:
        global_state.mqtt_handler.disconnect()
    if global_state.tcp_server:
        global_state.tcp_server.close()
    if global_state.ws_server:
        global_state.ws_server.close()
    if global_state.api_server:
        global_state.api_server.close()
    print("✅ Teardown complete.")
