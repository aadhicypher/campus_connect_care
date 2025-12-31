from pysnmp.hlapi import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    nextCmd
)

def snmp_walk(ip, community, oid):
    result = []

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, 161), timeout=2, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False):

        if errorIndication or errorStatus:
            break

        for varBind in varBinds:
            result.append((str(varBind[0]), str(varBind[1])))

    return result
