from src.db.database import db

def _list_nodes_only():
    return db.execute("""
        SELECT num, label, last_seen, viaMqtt, hopsAway, lastHeard
        FROM nodes
        ORDER BY last_seen DESC
    """).fetchall()

def _get_node(num: int):
    return db.execute("""
        SELECT num, label, last_seen, viaMqtt, hopsAway, lastHeard, device_id
        FROM nodes
        WHERE num = ?
    """, (num,)).fetchone()

def _list_nodes():
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
    return db.execute(query).fetchall()

def _list_channels_for_node(num: int):
    return db.execute("""
        SELECT channelNum, nodeNum, name, role
        FROM channels
        WHERE nodeNum = ?
        ORDER BY name ASC
    """, (num,)).fetchall()

def _list_channels():
    return db.execute("""
        SELECT channelNum, nodeNum, name, role
        FROM channels
        ORDER BY name ASC
    """).fetchall()

def _list_connections_for_node(num: int):
    return db.execute("""
        SELECT connection_id, transport, status
        FROM connections
        WHERE num = ?
        ORDER BY connection_id ASC
    """, (num,)).fetchall()

def _list_connections():
    return db.execute("""
        SELECT connection_id, transport, status
        FROM connections
        ORDER BY connection_id ASC
    """).fetchall()

def _get_node_details(num: int):
    node = _get_node(num)
    channels = _list_channels_for_node(num)
    connections = _list_connections_for_node(num)
    return {**(node or {}), "channels": channels, "connections": connections}

def _get_my_info():
    return db.execute("""
        SELECT myNodeNum, name, shortname, type, options,
               publicKey, protocol, currentIP, connId, timestamp
        FROM my_info
        ORDER BY myNodeNum ASC
    """).fetchall()

# Exported dict of node queries
node_queries = {
    "list_nodes_only": _list_nodes_only,
    "get_node": _get_node,
    "list_nodes": _list_nodes,
    "list_channels_for_node": _list_channels_for_node,
    "list_channels": _list_channels,
    "list_connections_for_node": _list_connections_for_node,
    "list_connections": _list_connections,
    "get_node_details": _get_node_details,
    "get_my_info": _get_my_info,
}
