"""
IP Addressing and Network Configuration Module for TalentSync

Implements CIDR notation, subnetting, DNS resolution, and IP allocation
for the distributed microservices network.
"""

import ipaddress
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
from dataclasses import dataclass
import hashlib


class Region(Enum):
    """Geographic regions for data centers"""
    CAMEROON_CENTRAL = ("cameroon-central", "10.0.0.0/16")
    CAMEROON_WEST = ("cameroon-west", "10.1.0.0/16")
    CAMEROON_NORTH = ("cameroon-north", "10.2.0.0/16")
    

@dataclass
class SubnetConfig:
    """Configuration for a subnet"""
    region: str
    service_type: str
    cidr_block: str
    gateway: str
    broadcast: str
    available_ips: List[str]
    dns_servers: List[str]


class IPAddressManager:
    """
    Manages IP addressing for the distributed network
    Handles CIDR blocks, subnetting, DNS resolution, and IP allocation
    """
    
    def __init__(self):
        self.region_networks: Dict[str, ipaddress.IPv4Network] = {}
        self.service_subnets: Dict[str, SubnetConfig] = {}
        self.ip_allocations: Dict[str, str] = {}  # node_id -> IP
        self.dns_records: Dict[str, str] = {}  # domain -> IP
        self.node_dns_mapping: Dict[str, str] = {}  # node_id -> DNS name
        self.nat_table: Dict[str, Tuple[str, int]] = {}  # external_ip -> (internal_ip, port)
        self.firewall_rules: List[Dict] = []
        
    def initialize_regions(self):
        """Initialize regional networks based on Region enum"""
        for region in Region:
            name, cidr = region.value
            self.region_networks[name] = ipaddress.IPv4Network(cidr)
            print(f"[IP] Initialized region: {name} ({cidr})")
    
    def create_service_subnets(self, region: str, num_subnets: int = 4) -> Dict[str, SubnetConfig]:
        """
        Create subnets for different services within a region
        Returns mapping of service_type -> SubnetConfig
        """
        if region not in self.region_networks:
            raise ValueError(f"Unknown region: {region}")
        
        region_network = self.region_networks[region]
        service_types = ["user-service", "project-service", "chat-service", "payment-service"]
        subnets = {}
        
        # Subdivide region network into /24 subnets for each service
        subnet_list = list(region_network.subnets(new_prefix=24))
        
        for i, service_type in enumerate(service_types[:len(subnet_list)]):
            if i >= len(subnet_list):
                break
                
            subnet = subnet_list[i]
            subnet_key = f"{region}_{service_type}"
            
            # Reserve first IP as gateway, last as broadcast
            available_ips = [str(ip) for ip in subnet.hosts()][1:-1]  # Exclude gateway and broadcast
            
            config = SubnetConfig(
                region=region,
                service_type=service_type,
                cidr_block=str(subnet),
                gateway=str(list(subnet.hosts())[0]),
                broadcast=str(subnet.broadcast_address),
                available_ips=available_ips,
                dns_servers=["10.0.0.1", "10.0.0.2"]
            )
            
            self.service_subnets[subnet_key] = config
            subnets[service_type] = config
            
            print(f"[IP] Created subnet for {service_type} in {region}: {subnet}")
        
        return subnets
    
    def allocate_ip(self, node_id: str, region: str, service_type: str) -> Optional[str]:
        """
        Allocate an IP address to a node
        Returns the assigned IP or None if no IPs available
        """
        # Normalize service type name
        service_key = service_type.lower().replace("_", "-")
        subnet_key = f"{region}_{service_key}"
        
        if subnet_key not in self.service_subnets:
            return None
        
        subnet = self.service_subnets[subnet_key]
        
        if not subnet.available_ips:
            print(f"[IP] WARNING: No available IPs in {subnet_key}")
            return None
        
        assigned_ip = subnet.available_ips.pop(0)
        self.ip_allocations[node_id] = assigned_ip
        
        # Create DNS name and register
        dns_name = self._generate_dns_name(node_id, region)
        self.node_dns_mapping[node_id] = dns_name
        self.dns_records[dns_name] = assigned_ip
        
        print(f"[IP] Allocated {assigned_ip} to {node_id} (DNS: {dns_name})")
        return assigned_ip
    
    def _generate_dns_name(self, node_id: str, region: str) -> str:
        """Generate a DNS name for a node"""
        # Format: service-id.region.talentsync.local
        parts = node_id.split("-")
        service_name = "-".join(parts[:-1]) if len(parts) > 1 else node_id
        instance_num = parts[-1] if len(parts) > 1 else "1"
        
        return f"{service_name}-{instance_num}.{region}.talentsync.local"
    
    def resolve_dns(self, dns_name: str) -> Optional[str]:
        """
        Simulate DNS resolution
        Returns IP address for the given DNS name
        """
        if dns_name in self.dns_records:
            return self.dns_records[dns_name]
        return None
    
    def get_node_ip(self, node_id: str) -> Optional[str]:
        """Get the IP address assigned to a node"""
        return self.ip_allocations.get(node_id)
    
    def get_node_dns(self, node_id: str) -> Optional[str]:
        """Get the DNS name for a node"""
        return self.node_dns_mapping.get(node_id)
    
    def setup_nat(self, internal_ip: str, external_ip: str, port: int = 8080):
        """
        Setup Network Address Translation (NAT) rule
        Maps external IP to internal IP and port
        """
        self.nat_table[external_ip] = (internal_ip, port)
        print(f"[NAT] Configured: {external_ip} -> {internal_ip}:{port}")
    
    def translate_address(self, external_ip: str) -> Optional[Tuple[str, int]]:
        """Translate external IP to internal IP and port"""
        return self.nat_table.get(external_ip)
    
    def add_firewall_rule(self, 
                         source_ip: str, 
                         dest_ip: str, 
                         port: int, 
                         protocol: str = "tcp",
                         action: str = "allow"):
        """Add a firewall rule"""
        rule = {
            'source': source_ip,
            'destination': dest_ip,
            'port': port,
            'protocol': protocol,
            'action': action
        }
        self.firewall_rules.append(rule)
        print(f"[FIREWALL] Added rule: {source_ip} -> {dest_ip}:{port} ({action})")
    
    def check_firewall(self, source_ip: str, dest_ip: str, port: int, protocol: str = "tcp") -> bool:
        """Check if a connection is allowed by firewall rules"""
        for rule in self.firewall_rules:
            if self._rule_matches(rule, source_ip, dest_ip, port, protocol):
                return rule['action'] == 'allow'
        # Default allow if no rules match
        return True
    
    def _rule_matches(self, rule: Dict, source_ip: str, dest_ip: str, port: int, protocol: str) -> bool:
        """Check if a rule matches the given connection parameters"""
        source_match = (rule['source'] == source_ip or 
                       rule['source'] == '0.0.0.0/0' or
                       self._ip_in_subnet(source_ip, rule['source']))
        
        dest_match = (rule['destination'] == dest_ip or 
                     rule['destination'] == '0.0.0.0/0' or
                     self._ip_in_subnet(dest_ip, rule['destination']))
        
        port_match = rule['port'] == port or rule['port'] == 0  # 0 = any port
        protocol_match = rule['protocol'] == protocol or rule['protocol'] == 'all'
        
        return source_match and dest_match and port_match and protocol_match
    
    def _ip_in_subnet(self, ip: str, cidr: str) -> bool:
        """Check if an IP is in a CIDR subnet"""
        try:
            return ipaddress.IPv4Address(ip) in ipaddress.IPv4Network(cidr)
        except:
            return False
    
    def get_network_topology(self) -> Dict:
        """Get complete network topology information"""
        return {
            'regions': {name: str(net) for name, net in self.region_networks.items()},
            'subnets': {key: {
                'cidr': subnet.cidr_block,
                'gateway': subnet.gateway,
                'available_ips': len(subnet.available_ips)
            } for key, subnet in self.service_subnets.items()},
            'allocations': self.ip_allocations,
            'dns_records': self.dns_records,
            'nat_rules': self.nat_table,
            'firewall_rules': self.firewall_rules
        }
    
    def print_network_info(self):
        """Print detailed network topology information"""
        print("\n" + "="*70)
        print(" "*15 + "NETWORK TOPOLOGY & IP ADDRESSING")
        print("="*70)
        
        print("\n[REGIONAL NETWORKS]")
        for region, network in self.region_networks.items():
            print(f"  {region:20s}: {str(network):20s} (Hosts: {network.num_addresses - 2})")
        
        print("\n[SERVICE SUBNETS]")
        for subnet_key, subnet in self.service_subnets.items():
            print(f"  {subnet_key:30s}: {subnet.cidr_block:20s} (Available: {len(subnet.available_ips)})")
            print(f"    Gateway: {subnet.gateway:18s} | Broadcast: {subnet.broadcast}")
        
        print("\n[NODE IP ALLOCATIONS]")
        for node_id, ip in self.ip_allocations.items():
            dns = self.node_dns_mapping.get(node_id, "N/A")
            print(f"  {node_id:25s}: {ip:15s} -> {dns}")
        
        if self.nat_table:
            print("\n[NAT TABLE]")
            for ext_ip, (int_ip, port) in self.nat_table.items():
                print(f"  {ext_ip:15s} -> {int_ip}:{port}")
        
        if self.firewall_rules:
            print("\n[FIREWALL RULES]")
            for i, rule in enumerate(self.firewall_rules, 1):
                print(f"  {i}. {rule['source']:15s} -> {rule['destination']:15s} "
                      f":{rule['port']:5d} ({rule['action'].upper()})")
        
        print("="*70 + "\n")


class NetworkPacket:
    """Represents a network packet with routing information"""
    
    def __init__(self, 
                 packet_id: str,
                 source_ip: str,
                 dest_ip: str,
                 source_node: str,
                 dest_node: str,
                 payload_size: int = 1024):
        self.packet_id = packet_id
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.source_node = source_node
        self.dest_node = dest_node
        self.payload_size = payload_size
        self.checksum = hashlib.md5(
            f"{packet_id}{source_ip}{dest_ip}".encode()
        ).hexdigest()
        self.ttl = 64  # Time To Live
        self.created_at = None
        self.delivered_at = None
    
    def __str__(self):
        return f"Packet({self.packet_id[:8]}... {self.source_ip} -> {self.dest_ip})"
