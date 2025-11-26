from db.insert_handlers import insertHandlers
from events.overlay_emitter import emitOverlay


def handle_queue_status(sub_packet: dict):
    data, meta = sub_packet["data"], sub_packet["meta"]
    from_node_num, timestamp, device_id = meta["fromNodeNum"], meta["timestamp"], meta["device_id"]
    queue_status, conn_id = data["queueStatus"], data["connId"]

    insertHandlers.insertQueueStatus({
        "num": from_node_num,
        "device_id": device_id,
        "res": queue_status.get("res"),
        "free": queue_status.get("free"),
        "maxlen": queue_status.get("maxlen"),
        "meshPacketId": queue_status.get("meshPacketId"),
        "connId": conn_id,
        "timestamp": timestamp,
    })


def handle_telemetry(sub_packet: dict):
    data = sub_packet["data"]
    from_node_num = sub_packet.get("fromNodeNum")
    to_node_num = sub_packet.get("toNodeNum")
    conn_id = sub_packet.get("connId")
    timestamp = sub_packet.get("timestamp")

    insertHandlers.insertMetricsHandler({
        "fromNodeNum": from_node_num,
        "toNodeNum": to_node_num,
        "conn_id": conn_id,
        "timestamp": timestamp,
        **data,
    })

    emitOverlay("telemetry", sub_packet)


def handle_host_metrics(sub_packet: dict):
    print("[dispatchMetrics] HostMetrics")


dispatchMetrics = {
    "queueStatus": handle_queue_status,
    "telemetry": handle_telemetry,
    "HostMetrics": handle_host_metrics,
}
