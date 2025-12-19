from aiohttp import web
import aiohttp_cors
from flask import app
import logging

from handlers.meshcore_handler import MeshcoreHandler
from handlers.meshtastic_handler import MeshtasticHandler
from src.server.startup_meshcore import start_meshcore, shutdown_meshcore
from src.server.startup_meshtastic import start_meshtastic, shutdown_meshtastic
from src.server.startup_mqtt import start_mqtt_server, shutdown_mqtt_server
from src.api.routes import RoutesRegistrar
from routing.dispatch_packet import DispatchPacket
from .sse_emitter import SSEEmitter
from src.handlers.requests import Requests

async def startup(app: web.Application):

    # Create SSEEmitter and register route
    request = Requests (timeout_ms=10000)
    sse_emitter = SSEEmitter(app, path="/events")
    dispatcher =  DispatchPacket(sse_emitter, request)

    meshcore_handler = MeshcoreHandler(dispatcher)
    meshtastic_handler = MeshtasticHandler(dispatcher)
    # set up the requester and initialize the command queue
    request.start_requests(meshcore_handler, meshtastic_handler)

    # routes
    routes = RoutesRegistrar(dispatcher, request)
    routes.register(app)


    # app["meshtastic"] = await start_meshtastic(meshtastic_handler, request)
    app["meshcore"] = await start_meshcore(meshcore_handler, request)
    app["mqtt_client"] = await start_mqtt_server()
    app["routes"] = routes
    app["sse_emitter"] = sse_emitter

    print("✅ completed startups")


async def shutdown(app: web.Application):
    print("🔻 Shutting down...")

    if "mqtt_client" in app:
        shutdown_mqtt_server(app["mqtt_client"])
        print("MQTT client shut down.")

    if "meshcore" in app:
        shutdown_meshcore(app["meshcore"]["meshcore"])
        print("Meshcore shut down.")

    if "meshtastic" in app:
        shutdown_meshtastic(app["meshtastic"])
        print("Meshtastic shut down.")

    if "requests" in app:
        requests = app["requests"]
        if request:
            try:
                request.shutdown()
            except Exception as e:
                print(f"[MeshcoreConnection] Error shutting down requests: {e}")
            finally:
                request = None
        print("Meshcore requests shut down.")

    app["sse_emitter"].shutdown()
    app["routes"].api.shutdown("shutdown")
    print("SSE and services shut down.")
    print("✅ Server shutdown complete.")


def create_app() -> web.Application:
    app = web.Application()

    # hooks
    app.on_startup.append(startup)
    app.on_cleanup.append(shutdown)

    # CORS
    cors = aiohttp_cors.setup(app, defaults={
        "http://localhost:5173": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    for route in list(app.router.routes()):
        cors.add(route)

    return app
