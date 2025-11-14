from typing import Dict, List, Optional, Tuple
import time
import random
from service_node import (
    ServiceNode, ServiceRequest, ServiceType, RequestType, 
    RequestStatus
)
from collections import defaultdict
from enum import Enum, auto

class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = auto()
    LEAST_LOADED = auto()
    RANDOM = auto()

class DistributedNetwork:
    """
    Manages the distributed TalentSync microservices network
    Handles load balancing, service discovery, and fault tolerance
    """
    
    def __init__(self, load_balancing_strategy: str = "least_loaded"):
        self.services: Dict[ServiceType, List[ServiceNode]] = defaultdict(list)
        self.all_nodes: Dict[str, ServiceNode] = {}
        self.load_balancing_strategy = load_balancing_strategy
        self.round_robin_counters: Dict[ServiceType, int] = defaultdict(int)
        
        # Network metrics
        self.total_requests_routed = 0
        self.failed_routing_attempts = 0
        self.service_discoveries = 0
        
    def register_service(self, node: ServiceNode):
        """Register a microservice node in the network"""
        self.services[node.service_type].append(node)
        self.all_nodes[node.node_id] = node
        print(f"[NETWORK] Registered {node.service_type.name} ({node.node_id}) in {node.region}")
    
    def connect_services(self, node1_id: str, node2_id: str):
        """Establish connection between two microservices"""
        if node1_id in self.all_nodes and node2_id in self.all_nodes:
            node1 = self.all_nodes[node1_id]
            node2 = self.all_nodes[node2_id]
            
            node1.add_service_connection(node2.service_type, node2_id)
            node2.add_service_connection(node1.service_type, node1_id)
            return True
        return False
    
    def _select_node_round_robin(self, service_type: ServiceType) -> Optional[ServiceNode]:
        """Select node using round-robin strategy"""
        nodes = self.services.get(service_type, [])
        if not nodes:
            return None
        
        healthy_nodes = [n for n in nodes if n.is_healthy and n.can_accept_request()]
        if not healthy_nodes:
            return None
        
        counter = self.round_robin_counters[service_type]
        selected = healthy_nodes[counter % len(healthy_nodes)]
        self.round_robin_counters[service_type] += 1
        
        return selected
    
    def _select_node_least_loaded(self, service_type: ServiceType) -> Optional[ServiceNode]:
        """Select node with least current load"""
        nodes = self.services.get(service_type, [])
        if not nodes:
            return None
        
        healthy_nodes = [n for n in nodes if n.is_healthy and n.can_accept_request()]
        if not healthy_nodes:
            return None
        
        # Select node with lowest CPU usage
        return min(healthy_nodes, key=lambda n: n.cpu_usage)
    
    def _select_node_random(self, service_type: ServiceType) -> Optional[ServiceNode]:
        """Select random healthy node"""
        nodes = self.services.get(service_type, [])
        if not nodes:
            return None
        
        healthy_nodes = [n for n in nodes if n.is_healthy and n.can_accept_request()]
        if not healthy_nodes:
            return None
        
        return random.choice(healthy_nodes)
    
    def route_request(self, request: ServiceRequest) -> Optional[str]:
        """
        Route request to appropriate service node using load balancing
        Returns the node_id that accepted the request, or None if routing failed
        """
        self.service_discoveries += 1
        
        # Select node based on load balancing strategy
        if self.load_balancing_strategy == "round_robin":
            node = self._select_node_round_robin(request.service_type)
        elif self.load_balancing_strategy == "random":
            node = self._select_node_random(request.service_type)
        else:  # least_loaded (default)
            node = self._select_node_least_loaded(request.service_type)
        
        if not node:
            self.failed_routing_attempts += 1
            print(f"[ROUTING FAILED] No available {request.service_type.name} node")
            return None
        
        # Submit request to selected node
        if node.submit_request(request):
            self.total_requests_routed += 1
            print(f"[ROUTED] {request.request_type.name} → {node.node_id} "
                  f"(CPU: {node.cpu_usage:.1f}%)")
            return node.node_id
        else:
            # Request was queued
            self.total_requests_routed += 1
            print(f"[QUEUED] {request.request_type.name} → {node.node_id} "
                  f"(Queue: {len(node.request_queue)})")
            return node.node_id
    
    def process_all_requests(self, requests_per_node: int = 1):
        """Process requests across all active nodes"""
        for node in self.all_nodes.values():
            if node.is_healthy and (node.active_requests or node.request_queue):
                node.process_requests(requests_per_node)
    
    def get_service_health(self, service_type: ServiceType) -> Dict:
        """Get health status for all nodes of a service type"""
        nodes = self.services.get(service_type, [])
        if not nodes:
            return {'error': 'Service not found'}
        
        return {
            'service_type': service_type.name,
            'total_nodes': len(nodes),
            'healthy_nodes': len([n for n in nodes if n.is_healthy]),
            'nodes': [n.get_health_status() for n in nodes]
        }
    
    def get_network_statistics(self) -> Dict:
        """Get comprehensive network statistics"""
        total_nodes = len(self.all_nodes)
        healthy_nodes = len([n for n in self.all_nodes.values() if n.is_healthy])
        
        total_processed = sum(n.total_requests_processed for n in self.all_nodes.values())
        total_failed = sum(n.failed_requests for n in self.all_nodes.values())
        
        avg_cpu = sum(n.cpu_usage for n in self.all_nodes.values()) / total_nodes if total_nodes > 0 else 0
        avg_memory = sum(n.memory_usage for n in self.all_nodes.values()) / total_nodes if total_nodes > 0 else 0
        
        return {
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'unhealthy_nodes': total_nodes - healthy_nodes,
            'total_requests_routed': self.total_requests_routed,
            'failed_routing_attempts': self.failed_routing_attempts,
            'total_requests_processed': total_processed,
            'total_failed_requests': total_failed,
            'success_rate_percent': (
                (total_processed / (total_processed + total_failed) * 100)
                if (total_processed + total_failed) > 0 else 0
            ),
            'average_cpu_usage_percent': round(avg_cpu, 2),
            'average_memory_usage_percent': round(avg_memory, 2),
            'service_types': len(self.services),
            'load_balancing_strategy': self.load_balancing_strategy
        }
    
    def simulate_high_traffic(
        self, 
        num_requests: int, 
        request_distribution: Dict[RequestType, float]
    ) -> List[ServiceRequest]:
        """
        Simulate high traffic scenario
        request_distribution: Dict mapping RequestType to probability (must sum to 1.0)
        """
        import uuid
        
        requests = []
        request_types = list(request_distribution.keys())
        probabilities = list(request_distribution.values())
        
        for i in range(num_requests):
            request_type = random.choices(request_types, weights=probabilities)[0]
            
            # Determine service type based on request type
            if request_type in [RequestType.REGISTER_USER, RequestType.AUTHENTICATE, RequestType.UPDATE_PROFILE]:
                service_type = ServiceType.USER_SERVICE
            elif request_type in [RequestType.CREATE_PROJECT, RequestType.ASSIGN_TASK, RequestType.UPDATE_TASK]:
                service_type = ServiceType.PROJECT_SERVICE
            elif request_type in [RequestType.SEND_MESSAGE, RequestType.CREATE_CHANNEL]:
                service_type = ServiceType.CHAT_SERVICE
            else:
                service_type = ServiceType.PAYMENT_SERVICE
            
            # Create mock payload
            payload = {
                'simulation_id': i,
                'timestamp': time.time()
            }
            
            request = ServiceRequest(
                request_id=str(uuid.uuid4()),
                request_type=request_type,
                service_type=service_type,
                payload=payload
            )
            
            requests.append(request)
            self.route_request(request)
        
        return requests
    
    def demonstrate_fault_tolerance(self, node_id: str):
        """Demonstrate fault tolerance by failing a node"""
        if node_id in self.all_nodes:
            node = self.all_nodes[node_id]
            node.simulate_failure()
            
            # Show redistribution
            print(f"\n[FAULT TOLERANCE] Traffic will be redistributed to other "
                  f"{node.service_type.name} nodes")
    
    def recover_node(self, node_id: str):
        """Recover a failed node"""
        if node_id in self.all_nodes:
            self.all_nodes[node_id].recover()
    
    def print_network_summary(self):
        """Print a summary of the network state"""
        stats = self.get_network_statistics()
        
        print("\n" + "="*70)
        print(" "*20 + "TALENTSYNC NETWORK SUMMARY")
        print("="*70)
        print(f"Total Nodes: {stats['total_nodes']} "
              f"(Healthy: {stats['healthy_nodes']}, Unhealthy: {stats['unhealthy_nodes']})")
        print(f"Load Balancing: {stats['load_balancing_strategy'].upper()}")
        print(f"Total Requests Routed: {stats['total_requests_routed']}")
        print(f"Total Requests Processed: {stats['total_requests_processed']}")
        print(f"Success Rate: {stats['success_rate_percent']:.2f}%")
        print(f"Average CPU Usage: {stats['average_cpu_usage_percent']:.2f}%")
        print(f"Average Memory Usage: {stats['average_memory_usage_percent']:.2f}%")
        print("="*70 + "\n")
        
        # Service breakdown
        for service_type in self.services:
            nodes = self.services[service_type]
            print(f"\n{service_type.name}:")
            for node in nodes:
                health = "✓" if node.is_healthy else "✗"
                print(f"  {health} {node.node_id}: "
                      f"CPU={node.cpu_usage:.1f}%, "
                      f"Requests={node.total_requests_processed}, "
                      f"Queue={len(node.request_queue)}")