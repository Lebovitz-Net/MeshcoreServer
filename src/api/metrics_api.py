from aiohttp import web
from src.api.api_utils import safe, safe_json

class MetricsAPI:

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
    async def get_metrics(self, request):
        return web.json_response(safe_json(self.query.get_voltage_stats()))


