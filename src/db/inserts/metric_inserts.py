# src/meshtastic/utils/metric_inserts.py

import time
from src.meshtastic.utils.database import db


def _insert_telemetry(tel: dict) -> None:
    sql = """
        INSERT INTO telemetry (fromNodeNum, toNodeNum, metric, value, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """
    try:
        cursor = db.cursor()
        cursor.execute(
            sql,
            (
                tel.get("fromNodeNum"),
                tel.get("toNodeNum"),
                tel.get("metric"),
                tel.get("value"),
                tel.get("timestamp") or int(time.time() * 1000),
            ),
        )
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting telemetry: {err}")


def _insert_event_emission(event: dict) -> None:
    sql = """
        INSERT INTO event_emissions (num, event_type, details, timestamp)
        VALUES (?, ?, ?, ?)
    """
    try:
        cursor = db.cursor()
        cursor.execute(
            sql,
            (
                event.get("num"),
                event.get("event_type"),
                event.get("details"),
                event.get("timestamp"),
            ),
        )
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting event_emission: {err}")


def _insert_queue_status(qs: dict) -> None:
    sql = """
        INSERT INTO queue_status (
          num, res, free, maxlen, meshPacketId, timestamp, connId
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor = db.cursor()
        cursor.execute(
            sql,
            (
                qs.get("num"),
                qs.get("res"),
                qs.get("free"),
                qs.get("maxlen"),
                qs.get("meshPacketId"),
                qs.get("timestamp") or int(time.time() * 1000),
                qs.get("connId"),
            ),
        )
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting queue_status: {err}")


def _insert_device_metrics(metrics: dict) -> None:
    sql = """
        INSERT INTO device_metrics (
          fromNodeNum, toNodeNum, batteryLevel, txPower, uptime,
          cpuTemp, memoryUsage, timestamp
        ) VALUES (
          :fromNodeNum, :toNodeNum, :batteryLevel, :txPower, :uptime,
          :cpuTemp, :memoryUsage, :timestamp
        )
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, metrics)
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting device_metrics: {err}")


def _insert_environment_metrics(metrics: dict) -> None:
    sql = """
        INSERT INTO environment_metrics (
          fromNodeNum, toNodeNum, temperature, humidity, pressure,
          lightLevel, timestamp
        ) VALUES (
          :fromNodeNum, :toNodeNum, :temperature, :humidity, :pressure,
          :lightLevel, :timestamp
        )
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, metrics)
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting environment_metrics: {err}")


def _insert_air_quality_metrics(metrics: dict) -> None:
    sql = """
        INSERT INTO air_quality_metrics (
          fromNodeNum, toNodeNum, pm25, pm10, co2, voc, ozone, timestamp
        ) VALUES (
          :fromNodeNum, :toNodeNum, :pm25, :pm10, :co2, :voc, :ozone, :timestamp
        )
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, metrics)
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting air_quality_metrics: {err}")


def _insert_power_metrics(metrics: dict) -> None:
    sql = """
        INSERT INTO power_metrics (
          fromNodeNum, toNodeNum, voltage, current, power,
          energy, frequency, timestamp
        ) VALUES (
          :fromNodeNum, :toNodeNum, :voltage, :current, :power,
          :energy, :frequency, :timestamp
        )
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, metrics)
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting power_metrics: {err}")


def _insert_local_stats(metrics: dict) -> None:
    sql = """
        INSERT INTO local_stats (
          fromNodeNum, toNodeNum, snr, rssi, hopCount,
          linkQuality, packetLoss, timestamp
        ) VALUES (
          :fromNodeNum, :toNodeNum, :snr, :rssi, :hopCount,
          :linkQuality, :packetLoss, :timestamp
        )
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, metrics)
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting local_stats: {err}")


def _insert_health_metrics(metrics: dict) -> None:
    sql = """
        INSERT INTO health_metrics (
          fromNodeNum, toNodeNum, cpuTemp, diskUsage, memoryUsage,
          uptime, loadAvg, timestamp
        ) VALUES (
          :fromNodeNum, :toNodeNum, :cpuTemp, :diskUsage, :memoryUsage,
          :uptime, :loadAvg, :timestamp
        )
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, metrics)
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting health_metrics: {err}")


def _insert_host_metrics(metrics: dict) -> None:
    sql = """
        INSERT INTO host_metrics (
          fromNodeNum, toNodeNum, hostname, uptime, loadAvg,
          osVersion, bootTime, timestamp
        ) VALUES (
          :fromNodeNum, :toNodeNum, :hostname, :uptime, :loadAvg,
          :osVersion, :bootTime, :timestamp
        )
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, metrics)
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting host_metrics: {err}")


def _insert_metrics_handler(telemetry: dict) -> None:
    from_node_num = telemetry.get("fromNodeNum")
    to_node_num = telemetry.get("toNodeNum")
    time_val = telemetry.get("time")
    timestamp = (time_val * 1000) if time_val else int(time.time() * 1000)

    metric_groups = {
        "deviceMetrics": _insert_device_metrics,
        "environmentMetrics": _insert_environment_metrics,
        "airQualityMetrics": _insert_air_quality_metrics,
        "powerMetrics": _insert_power_metrics,
        "localStats": _insert_local_stats,
        "healthMetrics": _insert_health_metrics,
        "hostMetrics": _insert_host_metrics,
    }

    for group_name, insert_fn in metric_groups.items():
        metrics = telemetry.get(group_name)
        if metrics:
            try:
                insert_fn({"fromNodeNum": from_node_num, "toNodeNum": to_node_num, "timestamp": timestamp, **metrics})
            except Exception as err:
                print(f"[insertMetricsHandler] Failed to insert {group_name}: {err}")


# Exported object of insert functions
metric_inserts = {
    "insert_telemetry": _insert_telemetry,
    "insert_event_emission": _insert_event_emission,
    "insert_queue_status": _insert_queue_status,
    "insert_device_metrics": _insert_device_metrics,
    "insert_environment_metrics": _insert_environment_metrics,
    "insert_air_quality_metrics": _insert_air_quality_metrics,
    "insert_power_metrics": _insert_power_metrics,
    "insert_local_stats": _insert_local_stats,
    "insert_health_metrics": _insert_health_metrics,
    "insert_host_metrics": _insert_host_metrics,
    "insert_metrics_handler": _insert_metrics_handler,
}
