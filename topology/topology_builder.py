from .lldp_discovery import discover_lldp_neighbors
from .mac_table import get_mac_table

def build_topology(devices):
    topology = {}

    for device in devices:
        name = device["name"]
        ip = device["ip"]
        community = device["community"]

        topology[name] = {
            "ip": ip,
            "neighbors": discover_lldp_neighbors(ip, community),
            "mac_count": len(get_mac_table(ip, community))
        }

    return topology
