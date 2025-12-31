from .snmp_client import snmp_walk

# LLDP remote systems OID
LLDP_REMOTE_SYSNAME = "1.0.8802.1.1.2.1.4.1.1.9"

def discover_lldp_neighbors(ip, community):
    neighbors = []

    entries = snmp_walk(ip, community, LLDP_REMOTE_SYSNAME)

    for oid, value in entries:
        neighbors.append(value)

    return neighbors
