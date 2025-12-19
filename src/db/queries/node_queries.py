# src/db/queries/node_queries.py

class NodeQueries:
    """
    Provides node- and topology-related query handlers.
    Expects `self.db` to be a valid database connection.
    """

    def list_nodes_only(self):
        return self.db.execute(
            """
            SELECT num, label, last_seen, viaMqtt, hopsAway, lastHeard
            FROM nodes
            ORDER BY last_seen DESC
            """
        ).fetchall()

    def get_node(self, num: int):
        return self.db.execute(
            """
            SELECT num, label, last_seen, viaMqtt, hopsAway, lastHeard, device_id
            FROM nodes
            WHERE num = ?
            """,
            (num,),
        ).fetchone()

    def list_nodes(self):
        query = """
            SELECT
              n.num AS nodeNum,
              n.label,
              n.device_id,
              n.last_seen,
              n.viaMqtt,
              n.hopsAway,
              n.lastHeard,

              u.contactId,
              u.name AS userName,
              u.shortName AS userShortName,
              u.publicKey,
              u.timestamp AS userTimestamp,
              u.protocol AS userProtocol,
              u.options AS userOptions,
              u.position AS userPosition,

              m.timestamp AS metricsTimestamp,
              m.batteryLevel,
              m.txPower,
              m.uptime,
              m.cpuTemp,
              m.memoryUsage,

              p.latitude AS positionLat,
              p.longitude AS positionLon,
              p.altitude AS positionAlt,
              p.timestamp AS positionTimestamp,
              p.toNodeNum

            FROM nodes n
            LEFT JOIN users u ON u.nodeNum = n.num
            LEFT JOIN device_metrics m ON m.fromNodeNum = n.num
              AND m.timestamp = (
                SELECT MAX(timestamp)
                FROM device_metrics
                WHERE fromNodeNum = n.num
              )
            LEFT JOIN positions p ON p.fromNodeNum = n.num
              AND p.timestamp = (
                SELECT MAX(timestamp)
                FROM positions
                WHERE fromNodeNum = n.num
              )
        """
        return self.db.execute(query).fetchall()

    def list_channels_for_node(self, num: int):
        return self.db.execute(
            """
            SELECT channelNum, nodeNum, name, role
            FROM channels
            WHERE nodeNum = ?
            ORDER BY name ASC
            """,
            (num,),
        ).fetchall()

    def list_channels(self):
        return self.db.execute(
            """
            SELECT channelNum, nodeNum, name, role
            FROM channels
            ORDER BY name ASC
            """
        ).fetchall()

    def list_connections_for_node(self, num: int):
        return self.db.execute(
            """
            SELECT connection_id, transport, status
            FROM connections
            WHERE num = ?
            ORDER BY connection_id ASC
            """,
            (num,),
        ).fetchall()

    def list_connections(self):
        return self.db.execute(
            """
            SELECT connection_id, transport, status
            FROM connections
            ORDER BY connection_id ASC
            """
        ).fetchall()

    def get_node_details(self, num: int):
        node = self.get_node(num)
        channels = self.list_channels_for_node(num)
        connections = self.list_connections_for_node(num)
        return {**(node or {}), "channels": channels, "connections": connections}

    def get_my_info(self):
        return self.db.execute(
            """
            SELECT myNodeNum, name, shortname, type, options,
                   publicKey, protocol, currentIP, connId, timestamp
            FROM my_info
            ORDER BY myNodeNum ASC
            """
        ).fetchall()
