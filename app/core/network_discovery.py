#!/usr/bin/env python3
"""
Network Discovery Module for Initial Setup
Detects firewall interfaces, validates connectivity, and discovers topology
"""

import subprocess
import re
import socket
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

import paramiko

from app.db.connection import get_connection


@dataclass
class NetworkInterface:
    name: str  # em0, em1, ens33
    ip_address: str
    subnet_mask: str = "255.255.255.0"
    interface_type: str = "UNKNOWN"  # WAN, LAN, OPT1, etc.
    is_dhcp_enabled: bool = False
    subnet_cidr: str = ""
    
    def __post_init__(self):
        if self.ip_address and not self.subnet_cidr:
            self.subnet_cidr = self._calculate_cidr()
    
    def _calculate_cidr(self) -> str:
        """Calculate CIDR from IP and mask"""
        try:
            ip_parts = self.ip_address.split('.')
            mask_parts = self.subnet_mask.split('.')
            network = '.'.join(str(int(ip_parts[i]) & int(mask_parts[i])) for i in range(4))
            # Count bits in mask
            bits = sum(bin(int(x)).count('1') for x in mask_parts)
            return f"{network}/{bits}"
        except:
            return f"{self.ip_address}/24"


@dataclass
class LocalNetworkInfo:
    ip_address: str
    interface: str
    gateway: str
    is_dhcp: bool
    dns_servers: List[str]
    
    def to_dict(self):
        return asdict(self)


class NetworkDiscovery:
    def __init__(self):
        self.local_info: Optional[LocalNetworkInfo] = None
        self.firewall_interfaces: List[NetworkInterface] = []
        self.errors: List[str] = []
        
    def discover_local_network(self) -> Tuple[bool, str]:
        """
        Discover local PC network configuration
        Returns: (success, message)
        """
        try:
            # Get IP and Gateway
            result = subprocess.run(
                ['ip', 'route', 'get', '1.1.1.1'],
                capture_output=True, text=True, timeout=5
            )
            
            ip_address = None
            interface = None
            gateway = None
            
            for line in result.stdout.split('\n'):
                if 'src' in line:
                    match = re.search(r'src\s+(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        ip_address = match.group(1)
                    match = re.search(r'dev\s+(\S+)', line)
                    if match:
                        interface = match.group(1)
            
            # Get default gateway
            result = subprocess.run(
                ['ip', 'route'], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'default via' in line:
                    match = re.search(r'default via\s+(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        gateway = match.group(1)
                        break
            
            if not gateway:
                return False, "NO_GATEWAY"
            
            if not ip_address:
                return False, "NO_IP_ADDRESS"
            
            # Check if DHCP or Static
            is_dhcp = self._check_dhcp_status(interface)
            
            # Get DNS
            dns_servers = self._get_dns_servers()
            
            self.local_info = LocalNetworkInfo(
                ip_address=ip_address,
                interface=interface,
                gateway=gateway,
                is_dhcp=is_dhcp,
                dns_servers=dns_servers
            )
            
            return True, "SUCCESS"
            
        except Exception as e:
            self.errors.append(f"Local discovery error: {str(e)}")
            return False, f"ERROR: {str(e)}"
    
    def _check_dhcp_status(self, interface: str) -> bool:
        """Check if interface uses DHCP"""
        try:
            # Check dhclient or NetworkManager
            result = subprocess.run(
                ['cat', f'/var/lib/dhcp/dhclient.{interface}.leases'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                return True
        except:
            pass
        
        # Alternative: check ip address show for dynamic flag
        try:
            result = subprocess.run(
                ['ip', 'addr', 'show', interface],
                capture_output=True, text=True, timeout=2
            )
            if 'dynamic' in result.stdout:
                return True
        except:
            pass
        
        return False
    
    def _get_dns_servers(self) -> List[str]:
        """Get DNS servers from resolv.conf"""
        dns = []
        try:
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        parts = line.split()
                        if len(parts) >= 2:
                            dns.append(parts[1])
        except:
            pass
        return dns
    
    def ping_test(self, host: str, timeout: int = 3) -> bool:
        """Test if host is reachable"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout), host],
                capture_output=True, timeout=timeout + 2
            )
            return result.returncode == 0
        except:
            return False
    
    def discover_firewall_interfaces(
        self, 
        firewall_ip: str, 
        username: str, 
        password: str
    ) -> Tuple[bool, str]:
        """
        SSH to pfSense and discover all interfaces
        Returns: (success, message)
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=firewall_ip,
                username=username,
                password=password,
                look_for_keys=False,
                allow_agent=False,
                timeout=10
            )
            
            # Get interface configuration
            stdin, stdout, stderr = ssh.exec_command('ifconfig -a')
            ifconfig_output = stdout.read().decode()
            
            # Parse interfaces
            self.firewall_interfaces = self._parse_ifconfig(ifconfig_output)
            
            # Get DHCP server status for each interface
            self._check_dhcp_status_on_interfaces(ssh)
            
            ssh.close()
            
            if not self.firewall_interfaces:
                return False, "NO_INTERFACES_FOUND"
            
            return True, f"Found {len(self.firewall_interfaces)} interfaces"
            
        except paramiko.AuthenticationException:
            return False, "AUTH_FAILED"
        except paramiko.SSHException as e:
            return False, f"SSH_ERROR: {str(e)}"
        except Exception as e:
            self.errors.append(f"Firewall discovery error: {str(e)}")
            return False, f"ERROR: {str(e)}"
    
    def _parse_ifconfig(self, output: str) -> List[NetworkInterface]:
        """Parse ifconfig output to extract interfaces"""
        interfaces = []
        
        # Split by interface blocks
        blocks = re.split(r'\n(?=\w+:)', output)
        
        for block in blocks:
            lines = block.strip().split('\n')
            if not lines:
                continue
            
            # First line has interface name and flags
            first_line = lines[0]
            iface_match = re.match(r'^(\w+):', first_line)
            if not iface_match:
                continue
            
            iface_name = iface_match.group(1)
            
            # Skip loopback
            if iface_name == 'lo0':
                continue
            
            # Find IP address
            ip_address = None
            subnet_mask = "255.255.255.0"
            
            for line in lines:
                # IPv4 address
                inet_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', line)
                if inet_match:
                    ip_address = inet_match.group(1)
                
                # Netmask
                mask_match = re.search(r'netmask\s+(0x[0-9a-f]+)', line, re.I)
                if mask_match:
                    hex_mask = mask_match.group(1)
                    mask_int = int(hex_mask, 16)
                    subnet_mask = '.'.join(str((mask_int >> (8 * i)) & 0xFF) for i in [3, 2, 1, 0])
            
            if ip_address:
                # Determine type based on name or IP
                iface_type = self._classify_interface(iface_name, ip_address)
                
                interfaces.append(NetworkInterface(
                    name=iface_name,
                    ip_address=ip_address,
                    subnet_mask=subnet_mask,
                    interface_type=iface_type
                ))
        
        return interfaces
    
    def _classify_interface(self, name: str, ip: str) -> str:
        """Classify interface as WAN, LAN, OPT1, etc."""
        name_lower = name.lower()
        
        if 'wan' in name_lower or name_lower == 'em0':
            return 'WAN'
        elif 'lan' in name_lower or name_lower == 'em1':
            return 'LAN'
        elif 'opt1' in name_lower or name_lower == 'em2':
            return 'OPT1'
        elif 'opt2' in name_lower or name_lower == 'em3':
            return 'OPT2'
        elif ip.startswith('127.'):
            return 'LOOPBACK'
        else:
            return 'UNKNOWN'
    
    def _check_dhcp_status_on_interfaces(self, ssh):
        """Check which interfaces have DHCP server enabled"""
        try:
            stdin, stdout, stderr = ssh.exec_command('cat /var/dhcpd/var/db/dhcpd.leases | head -5')
            # Just checking if file exists and has content
            dhcpd_running = len(stdout.read().decode().strip()) > 0
            
            # Mark LAN-like interfaces as potentially having DHCP
            for iface in self.firewall_interfaces:
                if iface.interface_type in ['LAN', 'OPT1', 'OPT2']:
                    iface.is_dhcp_enabled = dhcpd_running
        except:
            pass
    
    def validate_pc_in_firewall(self, firewall_ip: str, username: str, password: str) -> Tuple[bool, str]:
        """
        Check if Master PC IP appears in firewall DHCP leases
        Returns: (found_in_dhcp, message)
        """
        if not self.local_info:
            return False, "Local info not discovered"
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=firewall_ip,
                username=username,
                password=password,
                look_for_keys=False,
                allow_agent=False,
                timeout=10
            )
            
            # Get DHCP leases
            stdin, stdout, stderr = ssh.exec_command(
                'cat /var/dhcpd/var/db/dhcpd.leases'
            )
            leases_output = stdout.read().decode()
            ssh.close()
            
            # Search for PC IP in leases
            pc_ip = self.local_info.ip_address
            ip_pattern = rf'lease\s+{re.escape(pc_ip)}\s+{{'
            
            if re.search(ip_pattern, leases_output):
                return True, "PC found in DHCP leases"
            else:
                return False, "PC not found in DHCP leases (Manual IP suspected)"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def test_switch_connectivity(
        self, 
        switch_ip: str, 
        username: str, 
        password: str
    ) -> Tuple[bool, str, dict]:
        """
        Test SSH connectivity to switch and detect type
        Returns: (success, switch_type, details)
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=switch_ip,
                username=username,
                password=password,
                look_for_keys=False,
                allow_agent=False,
                timeout=10
            )
            
            # Try Open vSwitch command
            stdin, stdout, stderr = ssh.exec_command('sudo ovs-vsctl show')
            ovs_output = stdout.read().decode()
            
            if ovs_output and 'Bridge' in ovs_output:
                # Parse OVS details
                bridge_name = self._parse_ovs_bridge(ovs_output)
                ssh.close()
                return True, "Open vSwitch", {
                    "bridge": bridge_name,
                    "raw_output": ovs_output[:500]
                }
            
            # Try Cisco-style command
            stdin, stdout, stderr = ssh.exec_command('show version')
            version_output = stdout.read().decode()
            
            if 'Cisco' in version_output or 'IOS' in version_output:
                ssh.close()
                return True, "Cisco", {"version": version_output[:200]}
            
            ssh.close()
            return True, "Unknown", {}
            
        except paramiko.AuthenticationException:
            return False, "AUTH_FAILED", {}
        except Exception as e:
            return False, f"ERROR: {str(e)}", {}
    
    def _parse_ovs_bridge(self, output: str) -> str:
        """Extract bridge name from ovs-vsctl show output"""
        match = re.search(r'Bridge\s+"?(\w+)"?', output)
        return match.group(1) if match else "unknown"
    
    def save_to_database(self) -> bool:
        """Save discovered configuration to database"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Clear old data first (if any)
            cur.execute("DELETE FROM managed_switches")
            cur.execute("DELETE FROM firewall_interfaces")
            cur.execute("DELETE FROM network_setup")
            
            # Save network setup
            if self.local_info:
                cur.execute("""
                    INSERT INTO network_setup 
                    (setup_completed, master_pc_ip, master_pc_interface, gateway_ip)
                    VALUES (TRUE, %s, %s, %s)
                """, (
                    self.local_info.ip_address,
                    self.local_info.interface,
                    self.local_info.gateway
                ))
            
            # Save firewall interfaces
            interface_id_map = {}
            for i, iface in enumerate(self.firewall_interfaces):
                cur.execute("""
                    INSERT INTO firewall_interfaces 
                    (interface_name, interface_type, ip_address, subnet_mask, is_dhcp_enabled, subnet_cidr)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    iface.name,
                    iface.interface_type,
                    iface.ip_address,
                    iface.subnet_mask,
                    iface.is_dhcp_enabled,
                    iface.subnet_cidr
                ))
                interface_id_map[iface.interface_type] = cur.fetchone()[0]
            
            conn.commit()
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            self.errors.append(f"Database save error: {str(e)}")
            return False
    
    def load_from_database(self) -> bool:
        """Load configuration from database"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Check if setup is completed
            cur.execute("SELECT setup_completed, master_pc_ip, master_pc_interface, gateway_ip FROM network_setup LIMIT 1")
            setup_row = cur.fetchone()
            
            if not setup_row or not setup_row[0]:
                return False
            
            self.local_info = LocalNetworkInfo(
                ip_address=setup_row[1],
                interface=setup_row[2],
                gateway=setup_row[3],
                is_dhcp=False,  # Not stored, will rediscover
                dns_servers=[]
            )
            
            # Load firewall interfaces
            cur.execute("SELECT interface_name, interface_type, ip_address, subnet_mask, is_dhcp_enabled, subnet_cidr FROM firewall_interfaces")
            rows = cur.fetchall()
            
            self.firewall_interfaces = [
                NetworkInterface(
                    name=row[0],
                    interface_type=row[1],
                    ip_address=row[2],
                    subnet_mask=row[3],
                    is_dhcp_enabled=row[4],
                    subnet_cidr=row[5]
                ) for row in rows
            ]
            
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            self.errors.append(f"Database load error: {str(e)}")
            return False
    
    def is_setup_complete(self) -> bool:
        """Check if network setup is already done"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT setup_completed FROM network_setup LIMIT 1")
            row = cur.fetchone()
            cur.close()
            conn.close()
            return row is not None and row[0] is True
        except:
            return False


# Singleton instance for app-wide use
network_discovery = NetworkDiscovery()
