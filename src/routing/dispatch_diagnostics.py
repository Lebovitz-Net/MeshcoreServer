import json
from db.insert_handlers import insertHandlers
from events.overlay_emitter import emitOverlay
from meshcore.utils.string_utils import decode_node_info

insert_log_record = insertHandlers.insertLogRecord
insert_trace_data = insertHandlers.insertTraceData


def log_record_message(data: dict, meta: dict):
    conn_id, from_node_num, to_node_num, timestamp = (
        meta.get("connId"),
        meta.get("fromNodeNum"),
        meta.get("toNodeNum"),
        meta.get("timestamp"),
    )

    insertHandlers.insertLogRecord({
        "message": data.get("message"),
        "time": data.get("time"),
        "fromNodeNum": from_node_num,
        "toNodeNum": to_node_num,
        "timestamp": timestamp,
        "connId": conn_id,
    })


def handle_log_rx_data(packet: dict):
    data, meta = packet["data"]["data"], packet["data"]["meta"]
    shaped = {
        "fromNodeNum": 0,
        "decodeType": 0,
        "message": json.dumps(packet.get("data", {}).get("data")),
        "timestamp": meta["timestamp"],
        "connId": meta["connId"],
    }
    insert_log_record(shaped)


def handle_trace_data(packet: dict):
    try:
        insert_trace_data(packet)
        print("[dispatchDiagnostics] TraceData inserted:", packet["data"]["meta"]["connId"])
    except Exception as err:
        print("[dispatchDiagnostics] Failed to insert TraceData:", err)


def handle_log_record(sub_packet: dict):
    data, meta = sub_packet["data"], sub_packet["meta"]
    print(".../LogRecord ", sub_packet, decode_node_info(data.get("message")))
    log_record_message(data, meta)
    emitOverlay("LogMessage", sub_packet)


def handle_log_record_lower(sub_packet: dict):
    data, meta = sub_packet["data"], sub_packet["meta"]
    print(".../logRecord ", sub_packet)
    log_record_message(data, meta)
    emitOverlay("logMessage", sub_packet)


dispatchDiagnostics = {
    "LogRxData": handle_log_rx_data,
    "TraceData": handle_trace_data,
    "LogRecord": handle_log_record,
    "logRecord": handle_log_record_lower,
}
