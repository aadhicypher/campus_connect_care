import yaml
from topology.topology_builder import build_topology

with open("config.yaml") as f:
    config = yaml.safe_load(f)

topology = build_topology(config["devices"])

for device, data in topology.items():
    print(f"\nDevice: {device}")
    print(f"IP: {data['ip']}")
    print(f"Neighbors: {data['neighbors']}")
    print(f"MAC count: {data['mac_count']}")
