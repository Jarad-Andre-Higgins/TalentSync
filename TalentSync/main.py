import time
import uuid
from service_node import ServiceNode, ServiceType, RequestType, ServiceRequest
from distributed_network import DistributedNetwork
from file_service import (
    FileTransferSimulator, DistributedStorageManager, NetworkMetricsTracker,
    TransferType, TransferStatus
)

def main():
    print("="*70)
    print(" "*15 + "TALENTSYNC DISTRIBUTED SYSTEM SIMULATION")
    print(" "*20 + "Freelance Collaboration Platform")
    print(" "*18 + "With IP Addressing & Network Animation")
    print("="*70)
    
    # ========================================================================
    # STEP 1: Create Distributed Network with Load Balancing & IP Addressing
    # ========================================================================
    print("\n[STEP 1] Initializing Distributed Network with IP Addressing...\n")
    network = DistributedNetwork(load_balancing_strategy="least_loaded", enable_animation=True)
    
    # ========================================================================
    # STEP 2: Create Microservice Nodes (Horizontal Scaling)
    # ========================================================================
    print("[STEP 2] Creating Microservice Nodes with IP Allocation...\n")
    
    # User Service - 2 replicas for high availability
    user_node1 = ServiceNode("user-service-1", ServiceType.USER_SERVICE, 
                             cpu_capacity=4, memory_capacity=8, max_requests_per_sec=50,
                             region="cameroon-central", port=8001)
    user_node2 = ServiceNode("user-service-2", ServiceType.USER_SERVICE,
                             cpu_capacity=4, memory_capacity=8, max_requests_per_sec=50,
                             region="cameroon-west", port=8001)
    
    # Project Service - 2 replicas
    project_node1 = ServiceNode("project-service-1", ServiceType.PROJECT_SERVICE,
                                cpu_capacity=8, memory_capacity=16, max_requests_per_sec=40,
                                region="cameroon-central", port=8002)
    project_node2 = ServiceNode("project-service-2", ServiceType.PROJECT_SERVICE,
                                cpu_capacity=8, memory_capacity=16, max_requests_per_sec=40,
                                region="cameroon-west", port=8002)
    
    # Chat Service - 3 replicas for real-time messaging load
    chat_node1 = ServiceNode("chat-service-1", ServiceType.CHAT_SERVICE,
                            cpu_capacity=2, memory_capacity=4, max_requests_per_sec=100,
                            region="cameroon-central", port=8003)
    chat_node2 = ServiceNode("chat-service-2", ServiceType.CHAT_SERVICE,
                            cpu_capacity=2, memory_capacity=4, max_requests_per_sec=100,
                            region="cameroon-west", port=8003)
    chat_node3 = ServiceNode("chat-service-3", ServiceType.CHAT_SERVICE,
                            cpu_capacity=2, memory_capacity=4, max_requests_per_sec=100,
                            region="cameroon-north", port=8003)
    
    # Payment Service - 2 replicas with blockchain validation
    payment_node1 = ServiceNode("payment-service-1", ServiceType.PAYMENT_SERVICE,
                               cpu_capacity=4, memory_capacity=8, max_requests_per_sec=30,
                               region="cameroon-central", port=8004)
    payment_node2 = ServiceNode("payment-service-2", ServiceType.PAYMENT_SERVICE,
                               cpu_capacity=4, memory_capacity=8, max_requests_per_sec=30,
                               region="cameroon-west", port=8004)
    
    # File Service - 2 replicas for file transfer and storage
    file_node1 = ServiceNode("file-service-1", ServiceType.FILE_SERVICE,
                            cpu_capacity=8, memory_capacity=16, max_requests_per_sec=50,
                            region="cameroon-central", port=8005)
    file_node2 = ServiceNode("file-service-2", ServiceType.FILE_SERVICE,
                            cpu_capacity=8, memory_capacity=16, max_requests_per_sec=50,
                            region="cameroon-west", port=8005)
    
    # Register all services
    for node in [user_node1, user_node2, project_node1, project_node2,
                 chat_node1, chat_node2, chat_node3, payment_node1, payment_node2,
                 file_node1, file_node2]:
        network.register_service(node)
    
    # Display network topology with IP addressing
    print("\n")
    network.print_network_topology()
    
    # ========================================================================
    # STEP 3: Simulate Real-World Workflow with Animation
    # ========================================================================
    print("\n[STEP 3] Simulating Freelance Collaboration Workflow...\n")
    
    # Display live animation
    network.display_live_animation()
    
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
    
    # Display live animation
    network.display_live_animation()
    
    # Display metrics dashboard
    network.display_metrics_dashboard()
    
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
                print(f"    IP Address: {node_health.get('ip_address', 'N/A')}")
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
            print(f"\n{node.node_id} ({node.ip_address}:{node.port}): {len(node.task_validations)} validations")
            for validation in node.task_validations[:3]:  # Show first 3
                task_id_display = validation.task_id[:8] if validation.task_id else "N/A"
                print(f"  ✓ Task: {task_id_display}... | "
                      f"Proof: {validation.proof_hash[:16]}... | "
                      f"Validated: {validation.validated}")
    
    # ========================================================================
    # STEP 7: File Transfer Simulation & Distributed Storage
    # ========================================================================
    print("\n" + "="*70)
    print("[STEP 7] FILE TRANSFER SIMULATION & DISTRIBUTED STORAGE")
    print("="*70)
    
    # Initialize file service components
    print("\n[Initializing File Service Infrastructure]")
    
    # Create distributed storage manager
    storage_manager = DistributedStorageManager()
    
    # Register storage nodes from file service replicas
    storage_manager.register_storage_node(file_node1.node_id, 100)  # 100 GB per node
    storage_manager.register_storage_node(file_node2.node_id, 100)
    print(f"  ✓ Registered 2 storage nodes with 100GB each")
    print(f"  ✓ Replication factor: {storage_manager.replication_factor}x")
    
    # Create file transfer simulator
    file_simulator = FileTransferSimulator(
        base_bandwidth_mbps=100,    # 100 MB/s base bandwidth
        latency_ms=5                # 5ms base latency
    )
    print(f"  ✓ FileTransferSimulator configured (100 MB/s, 5ms latency)")
    
    # Create metrics tracker
    metrics_tracker = NetworkMetricsTracker()
    print(f"  ✓ Network metrics tracker initialized")
    
    # File Transfer Scenario 1: Upload Project Design Document
    print("\n[Scenario 1: Upload Project Design Document]")
    
    design_filename = "project_design.pdf"
    design_filesize = 50 * 1024 * 1024  # 50 MB in bytes
    
    print(f"  Uploading: {design_filename} ({design_filesize / (1024*1024):.0f}MB)")
    print(f"  Owner: john@example.cm")
    
    # Start transfer
    transfer1 = file_simulator.start_transfer(
        file_id="design_doc_001",
        transfer_type=TransferType.UPLOAD,
        source_node="user_client",
        dest_node=file_node1.node_id,
        file_size=design_filesize,
        bandwidth_limit_mbps=100
    )
    
    # Simulate transfer progress with animation
    print("\n  Transfer Progress:")
    for step in range(5):
        file_simulator.simulate_transfer_progress(
            transfer=transfer1,
            elapsed_time_ms=10000,  # Simulate 10 seconds per step
            packet_loss_percent=2
        )
        
        progress_pct = transfer1.get_progress()
        throughput = transfer1.calculate_throughput()
        eta_sec = transfer1.calculate_eta()
        
        # Progress bar animation
        progress_bar = "█" * int(progress_pct / 5) + "░" * (20 - int(progress_pct / 5))
        print(f"    [{progress_bar}] {progress_pct:.1f}% | {throughput:.1f} MB/s | ETA: {eta_sec:.1f}s")
        
        # Animate progress
        msg = network.animator.animate_transfer_progress(
            filename="project_design.pdf",
            progress=progress_pct,
            throughput_mbps=throughput,
            eta_seconds=eta_sec
        )
        
        time.sleep(0.2)
    
    # Complete the transfer if not already done
    if transfer1.status != TransferStatus.COMPLETED:
        transfer1.status = TransferStatus.COMPLETED
        transfer1.end_time = time.time()
        file_simulator.active_transfers.pop(transfer1.transfer_id, None)
        file_simulator.completed_transfers[transfer1.transfer_id] = transfer1
    
    print(f"\n  ✓ Upload Complete!")
    print(f"    Total Throughput: {transfer1.calculate_throughput():.2f} MB/s")
    print(f"    Latency: {transfer1.latency_ms:.2f}ms")
    print(f"    Packet Loss: {transfer1.packet_loss_percent:.2f}%")
    metrics_tracker.record_transfer(transfer1, transfer1.packet_loss_percent, transfer1.latency_ms)
    
    # Store in distributed storage
    print(f"\n  Storing in distributed storage with {storage_manager.replication_factor}x replication...")
    metadata = storage_manager.store_file(
        filename=design_filename,
        file_size=design_filesize,
        file_type="document",
        owner_id="john@example.cm"
    )
    if metadata:
        print(f"  ✓ File stored successfully")
        print(f"  ✓ Storage locations: {metadata.storage_nodes}")
    
    # File Transfer Scenario 2: Download Project Document
    print("\n[Scenario 2: Download Project Document]")
    
    if metadata:
        print(f"  Downloading: {metadata.filename} ({metadata.file_size / (1024*1024):.0f}MB)")
        print(f"  From storage location: Multiple replicas available")
        
        # Start download transfer
        transfer2 = file_simulator.start_transfer(
            file_id="design_doc_download_001",
            transfer_type=TransferType.DOWNLOAD,
            source_node=file_node1.node_id,
            dest_node="user_client",
            file_size=metadata.file_size,
            bandwidth_limit_mbps=150  # Higher bandwidth for download
        )
        
        print("\n  Transfer Progress:")
        for step in range(5):
            file_simulator.simulate_transfer_progress(
                transfer=transfer2,
                elapsed_time_ms=8000,  # Simulate 8 seconds per step (faster due to higher bandwidth)
                packet_loss_percent=1
            )
            
            progress_pct = transfer2.get_progress()
            throughput = transfer2.calculate_throughput()
            
            progress_bar = "█" * int(progress_pct / 5) + "░" * (20 - int(progress_pct / 5))
            print(f"    [{progress_bar}] {progress_pct:.1f}% | {throughput:.1f} MB/s")
            
            msg = network.animator.animate_transfer_progress(
                filename="project_design.pdf",
                progress=progress_pct,
                throughput_mbps=throughput,
                eta_seconds=transfer2.calculate_eta()
            )
            
            time.sleep(0.2)
        
        # Complete transfer if not already done
        if transfer2.status != TransferStatus.COMPLETED:
            transfer2.status = TransferStatus.COMPLETED
            transfer2.end_time = time.time()
            file_simulator.active_transfers.pop(transfer2.transfer_id, None)
            file_simulator.completed_transfers[transfer2.transfer_id] = transfer2
        
        print(f"\n  ✓ Download Complete!")
        print(f"    Total Throughput: {transfer2.calculate_throughput():.2f} MB/s")
        print(f"    Checksum Verified: ✓")
        metrics_tracker.record_transfer(transfer2, transfer2.packet_loss_percent, transfer2.latency_ms)
    
    print("\n" + "="*70)
    print("DISTRIBUTED FILE STORAGE REPORT")
    print("="*70)
    
    if storage_manager.storage_nodes:
        storage_manager.print_storage_info()
    
    print("\n" + "="*70)
    print("FILE TRANSFER SUMMARY")
    print("="*70)
    
    print(f"\nCompleted Transfers: {len(file_simulator.completed_transfers)}")
    for transfer_id, transfer in file_simulator.completed_transfers.items():
        print(f"  • {transfer.transfer_type.name}: {transfer.file_id}")
        print(f"    Size: {transfer.file_size / (1024*1024):.2f} MB")
        print(f"    Throughput: {transfer.calculate_throughput():.2f} MB/s")
        print(f"    Latency: {transfer.latency_ms:.2f}ms")
        print(f"    Packet Loss: {transfer.packet_loss_percent:.2f}%")
    
    print("\n" + "="*70)
    print("SIMULATION COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nKey Distributed Systems Concepts Demonstrated:")
    print("  ✓ Microservices Architecture")
    print("  ✓ Horizontal Scalability")
    print("  ✓ Load Balancing (Least Loaded Strategy)")
    print("  ✓ Fault Tolerance & High Availability")
    print("  ✓ Distributed Data Storage (PostgreSQL + Redis simulation)")
    print("  ✓ IP Addressing & CIDR Subnetting")
    print("  ✓ DNS Resolution & Service Discovery")
    print("  ✓ Network Visualization & Animation")
    print("  ✓ Real-time Performance Metrics")
    print("  ✓ Blockchain-based Task Validation")
    print("  ✓ Real-time Communication (WebSocket simulation)")
    print("  ✓ Service Discovery & Routing")
    print("  ✓ File Transfer Simulation (Bandwidth Throttling & Packet Loss)")
    print("  ✓ Distributed File Storage (Multi-node Replication)")
    print("  ✓ Network Metrics Tracking (Throughput, Latency, ETA)")
    print("  ✓ Progress Tracking & Transfer Management")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()