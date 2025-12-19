import asyncio
from aiohttp import web
from src.server.server import create_app

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

async def main():
    app = create_app()
    port = 8000
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    print(f"🚀 Server running at http://0.0.0.0:{port}")

    try:
        # Run forever until Ctrl+C
        await asyncio.Future()
    except asyncio.CancelledError:
        # This is expected when the loop is stopped
        pass
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔻 Keyboard interrupt, shutting down gracefully...")
