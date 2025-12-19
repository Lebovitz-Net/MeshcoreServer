from aiohttp import web
from src.api.api_utils import safe, safe_json

class DiagnosticsAPI:

    @safe
    async def get_logs(self, request):
        limit = int(request.rel_url.query.get("limit", 200))
        return web.json_response(safe_json(self.query.list_logs(limit)))


    @safe
    async def reload_config(self, request):
        return web.json_response(safe_json(self.query.get_full_config()))


    @safe
    async def list_packets(self, request):
        limit = int(request.rel_url.query.get("limit", 100))
        return web.json_response(safe_json(self.query.list_packet_logs(limit)))


    @safe
    async def get_packet(self, request):
        pkt_id = request.match_info.get("id")
        pkt = self.query.get_packet_log(pkt_id)
        return web.json_response(safe_json(pkt) if pkt else {"error": "Packet not found"}, status=200 if pkt else 404)


    @safe
    async def inject_packet(self, request):
        body = await request.json()
        result = self.insert.inject_packet_log(body)
        return web.json_response({"success": True, "result": safe_json(result)})

