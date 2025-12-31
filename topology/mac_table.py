from .snmp_client import snmp_walk

# Bridge MAC address table
BRIDGE_MAC_TABLE = "1.3.6.1.2.1.17.4.3.1.2"

def get_mac_table(ip, community):
    mac_entries = snmp_walk(ip, community, BRIDGE_MAC_TABLE)
    return mac_entries
