
## Architecture

### Microservices
- **User Service**: Handles registration, authentication, and profiles
- **Project Service**: Manages projects, tasks, and team assignments
- **Chat Service**: Real-time messaging (WebSocket simulation)
- **Payment Service**: Escrow payments with blockchain validation

### Distributed Concepts Implemented
1. **Horizontal Scalability**: Multiple replicas per service
2. **Load Balancing**: Least-loaded, round-robin, and random strategies
3. **Fault Tolerance**: Automatic failover and recovery
4. **Service Discovery**: Dynamic routing to healthy nodes
5. **Distributed Storage**: PostgreSQL (data) + Redis (cache) simulation
6. **Blockchain Validation**: Task proof-of-work verification

## How to Run

### Prerequisites
- Python 3.8+
- No external dependencies (uses only standard library)

### Execution
```bash
python main.py