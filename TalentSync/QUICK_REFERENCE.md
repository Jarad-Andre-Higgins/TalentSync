# Quick Reference Guide - TalentSync IP Addressing & Animation

## Running the Simulation

```bash
cd "d:\Distributed System\Me\TalentSync"
python main.py
```

## What You'll See

### 1. Network Topology Display
```
[NETWORK TOPOLOGY & IP ADDRESSING]
Regional Networks:
  cameroon-central: 10.0.0.0/16
  cameroon-west: 10.1.0.0/16
  cameroon-north: 10.2.0.0/16

Service Subnets:
  cameroon-central_user-service: 10.0.0.0/24
  cameroon-central_project-service: 10.0.1.0/24
  ...
```

### 2. Live Network Visualization
```
USER_SERVICE
──────────────────────────────────────────────────────────
  ● user-service-1  CPU:[▓▓▓░░░░░░░░░░░░░░░░] 15.0% MEM:[▓░░░░░░░░░░░░░░░░░░] 8.0%
  ● user-service-2  CPU:[░░░░░░░░░░░░░░░░░░░░]  0.0% MEM:[░░░░░░░░░░░░░░░░░░░░] 0.0%
```

### 3. Animated Request Routing
```
[00:00.045] → REGISTER_USER routed to user-service-1
[ROUTED] REGISTER_USER → user-service-1 (10.0.0.2:8001) (CPU: 2.0%)
```

### 4. Real-Time Metrics Dashboard
```
REAL-TIME METRICS DASHBOARD

Performance Metrics:
  Total Requests:        61
  Successful:            58  ✓
  Failed:                 1  ✗
  Success Rate:   [████████████░░] 95.08%
  Avg Latency:    1277.01ms

System Health:
  Healthy Nodes:      9/9
  Availability:  [████████] 100.0%
```

## Key IP Addresses

| Service | Node | Region | IP Address | Port | DNS |
|---------|------|--------|-----------|------|-----|
| User | user-service-1 | cameroon-central | 10.0.0.2 | 8001 | user-service-1.cameroon-central.talentsync.local |
| User | user-service-2 | cameroon-west | 10.1.0.2 | 8001 | user-service-2.cameroon-west.talentsync.local |
| Project | project-service-1 | cameroon-central | 10.0.1.2 | 8002 | project-service-1.cameroon-central.talentsync.local |
| Project | project-service-2 | cameroon-west | 10.1.1.2 | 8002 | project-service-2.cameroon-west.talentsync.local |
| Chat | chat-service-1 | cameroon-central | 10.0.2.2 | 8003 | chat-service-1.cameroon-central.talentsync.local |
| Chat | chat-service-2 | cameroon-west | 10.1.2.2 | 8003 | chat-service-2.cameroon-west.talentsync.local |
| Chat | chat-service-3 | cameroon-north | 10.2.2.2 | 8003 | chat-service-3.cameroon-north.talentsync.local |
| Payment | payment-service-1 | cameroon-central | 10.0.3.2 | 8004 | payment-service-1.cameroon-central.talentsync.local |
| Payment | payment-service-2 | cameroon-west | 10.1.3.2 | 8004 | payment-service-2.cameroon-west.talentsync.local |

## Animation Features

### Color Coding
- 🟢 **Green**: Healthy status, successful operations
- 🔴 **Red**: Failures, critical issues
- 🟡 **Yellow**: Warnings, high load (60-80%)
- 🔵 **Cyan**: Active requests
- ⚪ **Bold**: Important events

### Status Indicators
- `●` - Node is healthy
- `○` - Node is down
- `✓` - Request completed successfully
- `✗` - Request failed
- `→` - Request being routed
- `⚙` - Request processing
- `↻` - Node recovery
- `⚡` - Node failure

## IP Addressing Features

### CIDR Blocks
- **Regional**: `/16` networks (65,534 usable hosts each)
- **Service Subnets**: `/24` subnets (254 usable hosts each)
- **Gateway**: First IP in each subnet (e.g., `10.0.0.1`)
- **Broadcast**: Last IP in each subnet (e.g., `10.0.0.255`)

### DNS Resolution
Format: `{service}-{instance}.{region}.talentsync.local`
```python
# Example DNS lookups
resolve_dns("user-service-1.cameroon-central.talentsync.local")  # Returns: 10.0.0.2
resolve_dns("chat-service-3.cameroon-north.talentsync.local")    # Returns: 10.2.2.2
```

### Service Discovery
- Automatic IP allocation during node registration
- DNS name generation based on node ID and region
- Load balancing considers node health and CPU usage
- Automatic failover to healthy replicas

## Simulation Workflow

### STEP 1: Network Initialization
- Create 3 regional networks with /16 CIDR blocks
- Initialize IP addressing manager
- Setup animation engine

### STEP 2: Node Creation & Registration
- Create 9 microservice nodes across 4 services
- Allocate unique IPs from service subnets
- Register DNS names
- Display network topology

### STEP 3: Basic Workflow Simulation
- User registration
- Project creation
- Task assignment
- Real-time chat messaging
- Payment processing with blockchain validation

### STEP 4: High-Traffic Load Balancing
- Send 50 concurrent requests
- Observe load distribution across nodes
- Watch CPU/memory metrics update in real-time

### STEP 5: Fault Tolerance Demo
- Simulate node failure
- Watch automatic failover to healthy replicas
- Demonstrate node recovery

### STEP 6: Final Metrics
- Network summary with IP details
- Per-service performance metrics
- Blockchain validation records
- System health verification

## Customization

### Enable/Disable Animation
```python
# In main.py, line 18
network = DistributedNetwork(
    load_balancing_strategy="least_loaded",
    enable_animation=True  # Set to False for quiet mode
)
```

### Modify IP Ranges
```python
# In ip_addressing.py, Region enum (line 11-15)
class Region(Enum):
    CAMEROON_CENTRAL = ("cameroon-central", "10.0.0.0/16")   # Customize here
    CAMEROON_WEST = ("cameroon-west", "10.1.0.0/16")
    CAMEROON_NORTH = ("cameroon-north", "10.2.0.0/16")
```

### Change Service Ports
```python
# In main.py
user_node1 = ServiceNode(
    "user-service-1",
    ServiceType.USER_SERVICE,
    cpu_capacity=4,
    memory_capacity=8,
    max_requests_per_sec=50,
    region="cameroon-central",
    port=9001  # Change port here
)
```

## Performance Metrics Explained

| Metric | Meaning | Good Range |
|--------|---------|-----------|
| **Success Rate** | % of requests completed successfully | > 95% |
| **Avg Latency** | Average request processing time | < 100ms |
| **Healthy Nodes** | Number of operational nodes | = Total Nodes |
| **CPU Usage** | Average CPU across all nodes | < 30% |
| **Memory Usage** | Average memory across all nodes | < 40% |
| **Availability** | % uptime across cluster | > 99% |

## Troubleshooting

### "No available nodes" error
- Check that nodes are registered with `network.register_service()`
- Verify nodes are marked as healthy
- Check if CPU/memory are below thresholds

### Animation not showing
- Ensure terminal supports ANSI colors (most modern terminals do)
- Run with `enable_animation=True` in DistributedNetwork
- Try a different terminal emulator if colors don't display

### Slow simulation
- Animation rendering can be CPU-intensive
- Set `enable_animation=False` for faster execution
- Reduce number of requests in `simulate_high_traffic()`

## Learning Resources

### Concepts Demonstrated
1. ✓ Microservices architecture patterns
2. ✓ Horizontal scaling and replication
3. ✓ Load balancing strategies
4. ✓ Fault tolerance & high availability
5. ✓ IP addressing & subnetting (CIDR notation)
6. ✓ DNS-based service discovery
7. ✓ Distributed data storage
8. ✓ Blockchain task validation
9. ✓ Real-time messaging (WebSocket simulation)
10. ✓ Network monitoring & visualization

### Further Reading
- CIDR Notation: RFC 4632
- Load Balancing: AWS/Azure Documentation
- Microservices: Martin Fowler's Microservices Guide
- Distributed Systems: "Designing Data-Intensive Applications" by Martin Kleppmann

---

**Version**: 1.0 | **Last Updated**: November 17, 2025
