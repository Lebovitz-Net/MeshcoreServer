# src/routing/dispatch_diagnostics.py

import json
from src.meshcore.string_utils import decode_node_info

class DispatchDiagnostics:

    def log_record_message(self, data: dict, meta: dict):
        conn_id, from_node_num, to_node_num, timestamp = (
            meta.get("connId"),
            meta.get("fromNodeNum"),
            meta.get("toNodeNum"),
            meta.get("timestamp"),
        )

        self.insert_handlers.insert_log_record ({
            "message": data.get("message"),
            "time": data.get("time"),
            "fromNodeNum": from_node_num,
            "toNodeNum": to_node_num,
            "timestamp": timestamp,
            "connId": conn_id,
        })

    def log_rx_data(self, packet: dict):
        data, meta = packet["data"], packet["meta"]
        last_snr, last_rssi = data["lastSnr"], data["lastRssi"]
        shaped = {
            "fromNodeNum": 0,
            "decodeType": 0,
            "message": data["raw"].hex(),
            "timestamp": json.dumps({
                "lastSnr": last_snr,
                "lastRssi": last_rssi,
                "timestamp": meta["timestamp"],
            }),
            "connId": meta["connId"],
        }
        self.insert_handlers.insert_log_record(shaped)

    def trace_data(self, packet: dict):
        data, meta = packet["data"], packet["meta"]

        try:
            self.insert_handlers.insert_trace_data(packet)
            print(
                "[dispatchDiagnostics] TraceData inserted:",
                meta["connId"],
            )
        except Exception as err:
            print("[dispatchDiagnostics] Failed to insert TraceData:", err)

    def log_record(self, sub_packet: dict):
        data, meta = sub_packet["data"], sub_packet["meta"]
        print(".../LogRecord ", sub_packet, decode_node_info(data.get("message")))
        self.log_record_message(data, meta)

    def logrecord(self, sub_packet: dict):
        data, meta = sub_packet["data"], sub_packet["meta"]
        print(".../logRecord ", sub_packet)
        self.log_record_message(data, meta)
