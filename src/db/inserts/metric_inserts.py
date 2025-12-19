# src/db/inserts/metric_inserts.py

import time

class MetricInserts:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    """
    Provides telemetry and metric insert handlers.
    Expects `self.db` to be a valid database connection.
    """

    def insert_telemetry(self, tel: dict) -> None:
        sql = """
            INSERT INTO telemetry (fromNodeNum, toNodeNum, metric, value, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            cursor = self.db.cursor()
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
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting telemetry: {err}")

    def insert_event_emission(self, event: dict) -> None:
        sql = """
            INSERT INTO event_emissions (num, event_type, details, timestamp)
            VALUES (?, ?, ?, ?)
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(
                sql,
                (
                    event.get("num"),
                    event.get("event_type"),
                    event.get("details"),
                    event.get("timestamp"),
                ),
            )
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting event_emission: {err}")

    def insert_queue_status(self, qs: dict) -> None:
        sql = """
            INSERT INTO queue_status (
              num, res, free, maxlen, meshPacketId, timestamp, connId
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor = self.db.cursor()
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
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting queue_status: {err}")

    def insert_device_metrics(self, metrics: dict) -> None:
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
            cursor = self.db.cursor()
            cursor.execute(sql, metrics)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting device_metrics: {err}")

    def insert_environment_metrics(self, metrics: dict) -> None:
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
            cursor = self.db.cursor()
            cursor.execute(sql, metrics)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting environment_metrics: {err}")

    def insert_air_quality_metrics(self, metrics: dict) -> None:
        sql = """
            INSERT INTO air_quality_metrics (
              fromNodeNum, toNodeNum, pm25, pm10, co2, voc, ozone, timestamp
            ) VALUES (
              :fromNodeNum, :toNodeNum, :pm25, :pm10, :co2, :voc, :ozone, :timestamp
            )
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(sql, metrics)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting air_quality_metrics: {err}")

    def insert_power_metrics(self, metrics: dict) -> None:
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
            cursor = self.db.cursor()
            cursor.execute(sql, metrics)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting power_metrics: {err}")

    def insert_local_stats(self, metrics: dict) -> None:
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
            cursor = self.db.cursor()
            cursor.execute(sql, metrics)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting local_stats: {err}")

    def insert_health_metrics(self, metrics: dict) -> None:
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
            cursor = self.db.cursor()
            cursor.execute(sql, metrics)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting health_metrics: {err}")

    def insert_host_metrics(self, metrics: dict) -> None:
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
            cursor = self.db.cursor()
            cursor.execute(sql, metrics)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting host_metrics: {err}")

    def insert_metrics_handler(self, telemetry: dict) -> None:
        """
        Dispatches grouped metrics to the appropriate insert_* method.
        """
        from_node_num = telemetry.get("fromNodeNum")
        to_node_num = telemetry.get("toNodeNum")
        time_val = telemetry.get("time")
        timestamp = (time_val * 1000) if time_val else int(time.time() * 1000)

        metric_groups = {
            "deviceMetrics": self.insert_device_metrics,
            "environmentMetrics": self.insert_environment_metrics,
            "airQualityMetrics": self.insert_air_quality_metrics,
            "powerMetrics": self.insert_power_metrics,
            "localStats": self.insert_local_stats,
            "healthMetrics": self.insert_health_metrics,
            "hostMetrics": self.insert_host_metrics,
        }

        for group_name, insert_fn in metric_groups.items():
            metrics = telemetry.get(group_name)
            if metrics:
                try:
                    insert_fn({
                        "fromNodeNum": from_node_num,
                        "toNodeNum": to_node_num,
                        "timestamp": timestamp,
                        **metrics,
                    })
                except Exception as err:
                    print(f"[insertMetricsHandler] Failed to insert {group_name}: {err}")
