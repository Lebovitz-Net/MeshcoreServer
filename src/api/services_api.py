# src/api/services_manager.py
import time

class ServicesManager:

    def teardown_services(self):
        """Tear down backend services (placeholder)."""
        print("⚠️  Tearing down services...")
        # Add explicit shutdown calls here if needed, e.g. meshcore.shutdown(), mqtt.shutdown(), etc.
        print("✅ Teardown complete.")

    def init_services(self, config):
        """Initialize backend services (placeholder)."""
        print("🚀 Initializing backend services...")
        # Add explicit startup calls here if needed, e.g. start_tcp_server(config), start_ws_server(config), etc.
        print("✅ All services initialized.")

    def shutdown(self, signal="manual"):
        """Gracefully shut down services when a signal is received."""
        print(f"\n⚠️  Received {signal}, shutting down gracefully...")
        self.teardown_services()

    def restart_services(self):
        """Restart backend services by tearing down and reinitializing with fresh config."""
        print("🔄 Restarting backend services...")
        self.teardown_services()
        time.sleep(1)
        config = self.query.get_full_config()
        self.init_services(config)
        print("✅ Restart complete.")
        return {"restarted": True, "timestamp": int(time.time() * 1000)}
