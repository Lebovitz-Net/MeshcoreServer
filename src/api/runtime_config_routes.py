# src/api/config_routes.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from config import get_node_ip, set_node_ip

router = APIRouter()

@router.get("/node-ip")
async def get_node_ip_route():
    """
    GET current node IP
    """
    return {"ip": get_node_ip()}

@router.post("/node-ip")
async def set_node_ip_route(request: Request):
    """
    POST new node IP
    Body: { "ip": "192.168.1.99:4403" }
    """
    body = await request.json()
    ip = body.get("ip")

    if not ip or not isinstance(ip, str) or ":" not in ip:
        return JSONResponse(
            status_code=400,
            content={"error": 'Invalid IP format. Expected "host:port".'}
        )

    set_node_ip(ip)
    return {"success": True, "ip": ip}
