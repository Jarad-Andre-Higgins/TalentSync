import time
import uuid
from service_node import ServiceNode, ServiceType, RequestType, ServiceRequest
from distributed_network import DistributedNetwork

def main():
    print("="*70)
    print(" "*15 + "TALENTSYNC DISTRIBUTED SYSTEM SIMULATION")
    print(" "*20 + "Freelance Collaboration Platform")
    print("="*70)
    
    # ========================================================================
    # STEP 1: Create Distributed Network with Load Balancing
    # ========================================================================
    print("\n[STEP 1] Initializing Distributed Network...\n")
    network = DistributedNetwork(load_balancing_strategy="least_loaded")
    
    # ========================================================================
    # STEP 2: Create Microservice Nodes (Horizontal Scaling)
    # ========================================================================
    print("[STEP 2] Creating Microservice Nodes...\n")
    
    # User Service - 2 replicas for high availability
    user_node1 = ServiceNode("user-service-1", ServiceType.USER_SERVICE, 
                             cpu_capacity=4, memory_capacity=8, max_requests_per_sec=50,
                             region="cameroon-central")
    user_node2 = ServiceNode("user-service-2", ServiceType.USER_SERVICE,
                             cpu_capacity=4, memory_capacity=8, max_requests_per_sec=50,
                             region="cameroon-west")
    
    # Project Service - 2 replicas
    project_node1 = ServiceNode("project-service-1", ServiceType.PROJECT_SERVICE,
                                cpu_capacity=8, memory_capacity=16, max_requests_per_sec=40,
                                region="cameroon-central")
    project_node2 = ServiceNode("project-service-2", ServiceType.PROJECT_SERVICE,
                                cpu_capacity=8, memory_capacity=16, max_requests_per_sec=40,
                                region="cameroon-west")
    
    # Chat Service - 3 replicas for real-time messaging load
    chat_node1 = ServiceNode("chat-service-1", ServiceType.CHAT_SERVICE,
                            cpu_capacity=2, memory_capacity=4, max_requests_per_sec=100,
                            region="cameroon-central")
    chat_node2 = ServiceNode("chat-service-2", ServiceType.CHAT_SERVICE,
                            cpu_capacity=2, memory_capacity=4, max_requests_per_sec=100,
                            region="cameroon-west")
    chat_node3 = ServiceNode("chat-service-3", ServiceType.CHAT_SERVICE,
                            cpu_capacity=2, memory_capacity=4, max_requests_per_sec=100,
                            region="cameroon-north")
    
    # Payment Service - 2 replicas with blockchain validation
    payment_node1 = ServiceNode("payment-service-1", ServiceType.PAYMENT_SERVICE,
                               cpu_capacity=4, memory_capacity=8, max_requests_per_sec=30,
                               region="cameroon-central")
    payment_node2 = ServiceNode("payment-service-2", ServiceType.PAYMENT_SERVICE,
                               cpu_capacity=4, memory_capacity=8, max_requests_per_sec=30,
                               region="cameroon-west")
    
    # Register all services
    for node in [user_node1, user_node2, project_node1, project_node2,
                 chat_node1, chat_node2, chat_node3, payment_node1, payment_node2]:
        network.register_service(node)
    
    # ========================================================================
    # STEP 3: Simulate Real-World Workflow
    # ========================================================================
    print("\n[STEP 3] Simulating Freelance Collaboration Workflow...\n")
    
    # Scenario: Freelancer Registration & Project Assignment
    print("--- Scenario: New Freelancer Joins Platform ---")
    
    # 1. Freelancer registers
    register_request = ServiceRequest(
        request_id=str(uuid.uuid4()),
        request_type=RequestType.REGISTER_USER,
        service_type=ServiceType.USER_SERVICE,
        payload={'email': 'john@example.cm', 'name': 'John Kamga', 'role': 'freelancer'}
    )
    network.route_request(register_request)
    network.process_all_requests()
    
    time.sleep(0.1)
    
    # 2. Client creates a project
    print("\n--- Scenario: Client Creates Project ---")
    create_project_request = ServiceRequest(
        request_id=str(uuid.uuid4()),
        request_type=RequestType.CREATE_PROJECT,
        service_type=ServiceType.PROJECT_SERVICE,
        payload={'title': 'Mobile App Development', 'client_id': 'client-123'}
    )
    network.route_request(create_project_request)
    network.process_all_requests()
    
    time.sleep(0.1)
    
    # 3. Task assignment
    print("\n--- Scenario: Assigning Task to Freelancer ---")
    assign_task_request = ServiceRequest(
        request_id=str(uuid.uuid4()),
        request_type=RequestType.ASSIGN_TASK,
        service_type=ServiceType.PROJECT_SERVICE,
        payload={'project_id': 'proj-123', 'freelancer_id': 'freelancer-456', 
                'description': 'Build authentication module'}
    )
    network.route_request(assign_task_request)
    network.process_all_requests()
    
    time.sleep(0.1)
    
    # 4. Real-time chat communication
    print("\n--- Scenario: Team Communication via Chat ---")
    for i in range(3):
        chat_request = ServiceRequest(
            request_id=str(uuid.uuid4()),
            request_type=RequestType.SEND_MESSAGE,
            service_type=ServiceType.CHAT_SERVICE,
            payload={'channel_id': 'proj-123-chat', 'sender_id': f'user-{i}',
                    'content': f'Message {i+1}'}
        )
        network.route_request(chat_request)
    
    network.process_all_requests(requests_per_node=3)
    
    time.sleep(0.1)
    
    # 5. Payment processing with blockchain validation
    print("\n--- Scenario: Process Payment with Blockchain Validation ---")
    payment_request = ServiceRequest(
        request_id=str(uuid.uuid4()),
        request_type=RequestType.PROCESS_PAYMENT,
        service_type=ServiceType.PAYMENT_SERVICE,
        payload={'client_id': 'client-123', 'freelancer_id': 'freelancer-456', 
                'amount': 50000}  # 50,000 FCFA
    )
    network.route_request(payment_request)
    
    validate_request = ServiceRequest(
        request_id=str(uuid.uuid4()),
        request_type=RequestType.VALIDATE_TASK,
        service_type=ServiceType.PAYMENT_SERVICE,
        payload={'task_id': 'task-789', 'freelancer_id': 'freelancer-456',
                'client_id': 'client-123'}
    )
    network.route_request(validate_request)
    network.process_all_requests()
    
    # ========================================================================
    # STEP 4: Demonstrate Load Balancing with High Traffic
    # ========================================================================
    print("\n[STEP 4] Simulating High Traffic Load Balancing...\n")
    
    request_distribution = {
        RequestType.REGISTER_USER: 0.15,
        RequestType.AUTHENTICATE: 0.25,
        RequestType.CREATE_PROJECT: 0.10,
        RequestType.SEND_MESSAGE: 0.35,
        RequestType.PROCESS_PAYMENT: 0.10,
        RequestType.VALIDATE_TASK: 0.05
    }
    
    print(f"Generating 50 concurrent requests...\n")
    network.simulate_high_traffic(50, request_distribution)
    
    # Process all requests
    print("\nProcessing requests across all nodes...")
    for _ in range(10):
        network.process_all_requests(requests_per_node=5)
        time.sleep(0.05)
    
    # ========================================================================
    # STEP 5: Demonstrate Fault Tolerance
    # ========================================================================
    print("\n[STEP 5] Demonstrating Fault Tolerance...\n")
    
    print("Simulating failure of user-service-1...")
    network.demonstrate_fault_tolerance("user-service-1")
    
    # Create new requests - should route to user-service-2
    print("\nRouting new requests (should go to user-service-2)...")
    for i in range(3):
        auth_request = ServiceRequest(
            request_id=str(uuid.uuid4()),
            request_type=RequestType.AUTHENTICATE,
            service_type=ServiceType.USER_SERVICE,
            payload={'user_id': f'user-{i}'}
        )
        network.route_request(auth_request)
    
    network.process_all_requests()
    
    # Recover the failed node
    print("\nRecovering user-service-1...")
    network.recover_node("user-service-1")
    time.sleep(0.1)
    
    # ========================================================================
    # STEP 6: Display Performance Metrics
    # ========================================================================
    print("\n[STEP 6] Performance Metrics & Statistics\n")
    
    # Network summary
    network.print_network_summary()
    
    # Detailed service metrics
    print("\n" + "="*70)
    print("DETAILED SERVICE METRICS")
    print("="*70)
    
    for service_type in [ServiceType.USER_SERVICE, ServiceType.PROJECT_SERVICE, 
                        ServiceType.CHAT_SERVICE, ServiceType.PAYMENT_SERVICE]:
        health = network.get_service_health(service_type)
        if 'error' not in health:
            print(f"\n{service_type.name}:")
            print(f"  Total Nodes: {health['total_nodes']}")
            print(f"  Healthy Nodes: {health['healthy_nodes']}")
            
            for node_health in health['nodes']:
                print(f"\n  Node: {node_health['node_id']}")
                print(f"    Status: {'HEALTHY' if node_health['is_healthy'] else 'FAILED'}")
                print(f"    CPU Usage: {node_health['cpu_usage_percent']}%")
                print(f"    Memory Usage: {node_health['memory_usage_percent']}%")
                print(f"    Active Requests: {node_health['active_requests']}")
                print(f"    Queued Requests: {node_health['queued_requests']}")
    
    # Payment service blockchain validations
    print("\n" + "="*70)
    print("BLOCKCHAIN VALIDATION RECORDS (Payment Service)")
    print("="*70)
    
    for node in [payment_node1, payment_node2]:
        if node.task_validations:
            print(f"\n{node.node_id}: {len(node.task_validations)} validations")
            for validation in node.task_validations[:3]:  # Show first 3
                task_id_display = validation.task_id[:8] if validation.task_id else "N/A"
                print(f"  ✓ Task: {task_id_display}... | "
                      f"Proof: {validation.proof_hash[:16]}... | "
                      f"Validated: {validation.validated}")
    
    print("\n" + "="*70)
    print("SIMULATION COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nKey Distributed Systems Concepts Demonstrated:")
    print("  ✓ Microservices Architecture")
    print("  ✓ Horizontal Scalability")
    print("  ✓ Load Balancing (Least Loaded Strategy)")
    print("  ✓ Fault Tolerance & High Availability")
    print("  ✓ Distributed Data Storage (PostgreSQL + Redis simulation)")
    print("  ✓ Blockchain-based Task Validation")
    print("  ✓ Real-time Communication (WebSocket simulation)")
    print("  ✓ Service Discovery & Routing")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()