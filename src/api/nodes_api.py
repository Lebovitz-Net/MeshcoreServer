from aiohttp import web
from src.api.api_utils import safe, safe_json

class NodesAPI:

    @safe
    async def list_nodes(self, request):
        return web.json_response(safe_json(self.query.list_nodes()))


    @safe
    async def get_node(self, request):
        node_id = request.match_info.get("id")
        node = self.query.get_node(node_id)
        return web.json_response(safe_json(node) if node else {"error": "Node not found"}, status=200 if node else 404)


    @safe
    async def delete_node(self, request):
        node_id = request.match_info.get("id")
        self.insert.delete_node(node_id)
        return web.json_response({"success": True})


    @safe
    async def list_channels(self, request):
        node_id = request.match_info.get("id")
        return web.json_response(safe_json(self.query.list_channels_for_node(node_id)))


    @safe
    async def list_connections(self, request):
        node_id = request.match_info.get("id")
        return web.json_response(safe_json(self.query.list_connections_for_node(node_id)))


    @safe
    async def get_packet_logs(self, request):
        node_id = request.match_info.get("id")
        limit = int(request.rel_url.query.get("limit", 100))
        return web.json_response(safe_json(self.query.list_recent_packet_logs_for_node(node_id, limit)))


    @safe
    async def get_telemetry(self, request):
        node_id = request.match_info.get("id")
        return web.json_response(safe_json(self.query.list_telemetry_for_node(node_id)))


    @safe
    async def get_events(self, request):
        node_id = request.match_info.get("id")
        event_type = request.rel_url.query.get("type")
        return web.json_response(safe_json(self.query.list_events_for_node(node_id, event_type)))


    @safe
    async def list_my_info(self, request):
        return web.json_response(safe_json(self.query.get_my_info()))

