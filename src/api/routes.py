from aiohttp import web
from src.api.api_handlers import APIHandlers
from src.config.config import get_node_ip, set_node_ip

class RoutesRegistrar:
    def __init__(self, dispatcher, requests):
        # Instantiate the unified APIHandlers aggregator
        self.api = APIHandlers(dispatcher, requests)

    def register(self, app: web.Application):
        # --- Root ---
        app.router.add_get("/", self.api.health)

        # --- Runtime Config ---
        async def get_node_ip_route(request):
            return web.json_response({"ip": get_node_ip()})
        app.router.add_get("/api/v1/node-ip", get_node_ip_route)

        async def set_node_ip_route(request):
            body = await request.json()
            ip = body.get("ip")
            if not ip or ":" not in ip:
                return web.json_response(
                    {"error": 'Invalid IP format. Expected "host:port".'},
                    status=400,
                )
            set_node_ip(ip)
            return web.json_response({"success": True, "ip": ip})
        app.router.add_post("/api/v1/node-ip", set_node_ip_route)

        # --- System ---
        app.router.add_get("/api/v1/config", self.api.get_config)
        app.router.add_get("/api/v1/version", self.api.get_version)
        app.router.add_get("/api/v1/health", self.api.get_health)

        # --- Nodes ---
        app.router.add_get("/api/v1/nodes/{id}/connections", self.api.list_connections)
        app.router.add_get("/api/v1/nodes/{id}", self.api.get_node)
        app.router.add_delete("/api/v1/nodes/{id}", self.api.delete_node)
        app.router.add_get("/api/v1/nodes", self.api.list_nodes)
        app.router.add_get("/api/v1/channels/{id}", self.api.list_channels)

        # --- Messages ---
        app.router.add_get("/api/v1/messages", self.api.list_messages)
        app.router.add_post("/api/v1/messages", self.api.send_message)

        # --- My Info ---
        app.router.add_get("/api/v1/myinfo", self.api.list_my_info)

        # --- Contacts ---
        app.router.add_get("/api/v1/contacts", self.api.list_contacts)

        # --- Packets ---
        app.router.add_get("/api/v1/packets", self.api.list_packets)
        app.router.add_get("/api/v1/packets/{id}", self.api.get_packet)
        app.router.add_post("/api/v1/packets", self.api.inject_packet)

        # --- Metrics ---
        app.router.add_get("/api/v1/nodes/{id}/packet-logs", self.api.get_packet_logs)
        app.router.add_get("/api/v1/nodes/{id}/telemetry", self.api.get_telemetry)
        app.router.add_get("/api/v1/nodes/{id}/events", self.api.get_events)
        app.router.add_get("/api/v1/metrics", self.api.get_metrics)

        # --- Diagnostics & Logs ---
        app.router.add_get("/api/v1/logs", self.api.get_logs)

        # --- Config ---
        app.router.add_get("/api/v1/config/full", self.api.get_full_config)
        app.router.add_get("/api/v1/config/{id}", self.api.get_config)
        app.router.add_get("/api/v1/configs", self.api.list_all_configs)
        app.router.add_get("/api/v1/module-config/{id}", self.api.get_module_config)
        app.router.add_get("/api/v1/module-configs", self.api.list_all_module_configs)
        app.router.add_get("/api/v1/metadata/{key}", self.api.get_metadata_by_key)
        app.router.add_get("/api/v1/metadata", self.api.list_all_metadata)
        app.router.add_get("/api/v1/files", self.api.list_file_info)

        # --- Control ---
        app.router.add_post("/api/v1/restart", self.api.restart_services)
        app.router.add_post("/api/v1/reload-config", self.api.reload_config)
