import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from enum import Enum, auto
import hashlib

class ServiceType(Enum):
    """Types of microservices in TalentSync platform"""
    USER_SERVICE = auto()
    PROJECT_SERVICE = auto()
    CHAT_SERVICE = auto()
    PAYMENT_SERVICE = auto()
    NOTIFICATION_SERVICE = auto()
    FILE_SERVICE = auto()

class RequestStatus(Enum):
    """Status of service requests"""
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()

class RequestType(Enum):
    """Types of requests handled by services"""
    # User Service
    REGISTER_USER = auto()
    AUTHENTICATE = auto()
    UPDATE_PROFILE = auto()
    
    # Project Service
    CREATE_PROJECT = auto()
    ASSIGN_TASK = auto()
    UPDATE_TASK = auto()
    
    # Chat Service
    SEND_MESSAGE = auto()
    CREATE_CHANNEL = auto()
    
    # Payment Service
    PROCESS_PAYMENT = auto()
    VALIDATE_TASK = auto()
    RELEASE_ESCROW = auto()
    
    # File Service
    UPLOAD_FILE = auto()
    DOWNLOAD_FILE = auto()
    DELETE_FILE = auto()
    LIST_FILES = auto()

@dataclass
class ServiceRequest:
    """Represents a request to a microservice"""
    request_id: str
    request_type: RequestType
    service_type: ServiceType
    payload: Dict
    status: RequestStatus = RequestStatus.PENDING
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    processing_time: float = 0.0
    node_id: Optional[str] = None
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    source_port: int = 0
    dest_port: int = 0

@dataclass
class TaskValidation:
    """Blockchain-inspired task validation record"""
    validation_id: str
    task_id: str
    freelancer_id: str
    client_id: str
    proof_hash: str
    timestamp: float
    validated: bool = False

class ServiceNode:
    """Represents a microservice node in the distributed TalentSync system"""
    
    def __init__(
        self,
        node_id: str,
        service_type: ServiceType,
        cpu_capacity: int,
        memory_capacity: int,
        max_requests_per_sec: int,
        region: str = "cameroon-central",
        ip_address: Optional[str] = None,
        dns_name: Optional[str] = None,
        port: int = 8080
    ):
        self.node_id = node_id
        self.service_type = service_type
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.max_requests_per_sec = max_requests_per_sec
        self.region = region
        self.ip_address = ip_address
        self.dns_name = dns_name
        self.port = port
        
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.current_requests_per_sec = 0
        
        self.active_requests: Dict[str, ServiceRequest] = {}
        self.completed_requests: Dict[str, ServiceRequest] = {}
        self.request_queue: List[ServiceRequest] = []
        
        self.data_store: Dict[str, any] = {}
        self.cache: Dict[str, any] = {}
        self.task_validations: List[TaskValidation] = []
        
        self.total_requests_processed = 0
        self.failed_requests = 0
        self.total_processing_time = 0.0
        self.uptime_start = time.time()
        self.is_healthy = True
        
        self.service_connections: Dict[ServiceType, List[str]] = {}
        
    def add_service_connection(self, service_type: ServiceType, node_id: str):
        """Register connection to another microservice"""
        if service_type not in self.service_connections:
            self.service_connections[service_type] = []
        if node_id not in self.service_connections[service_type]:
            self.service_connections[service_type].append(node_id)
    
    def _calculate_processing_time(self, request_type: RequestType) -> float:
        """Calculate processing time based on request complexity"""
        processing_times = {
            RequestType.REGISTER_USER: 0.05,
            RequestType.AUTHENTICATE: 0.02,
            RequestType.UPDATE_PROFILE: 0.03,
            RequestType.CREATE_PROJECT: 0.08,
            RequestType.ASSIGN_TASK: 0.04,
            RequestType.UPDATE_TASK: 0.03,
            RequestType.SEND_MESSAGE: 0.01,
            RequestType.CREATE_CHANNEL: 0.05,
            RequestType.PROCESS_PAYMENT: 0.15,
            RequestType.VALIDATE_TASK: 0.20,
            RequestType.RELEASE_ESCROW: 0.12,
        }
        base_time = processing_times.get(request_type, 0.05)
        load_factor = 1 + (self.cpu_usage / 100)
        return base_time * load_factor
    
    def can_accept_request(self) -> bool:
        """Check if node can accept new requests"""
        if not self.is_healthy:
            return False
        if len(self.active_requests) >= self.max_requests_per_sec:
            return False
        if self.cpu_usage > 90 or self.memory_usage > 90:
            return False
        return True
    
    def submit_request(self, request: ServiceRequest) -> bool:
        """Submit a request to this service node"""
        if not self.can_accept_request():
            self.request_queue.append(request)
            return False
        
        request.status = RequestStatus.PROCESSING
        request.node_id = self.node_id
        self.active_requests[request.request_id] = request
        self._update_resource_usage(increase=True)
        return True
    
    def process_requests(self, num_requests: int = 1) -> List[ServiceRequest]:
        """Process pending requests"""
        processed = []
        requests_to_complete = list(self.active_requests.values())[:num_requests]
        
        for request in requests_to_complete:
            processing_time = self._calculate_processing_time(request.request_type)
            time.sleep(processing_time)
            
            success = self._execute_request(request)
            
            if success:
                request.status = RequestStatus.COMPLETED
                request.completed_at = time.time()
                request.processing_time = request.completed_at - request.created_at
                self.completed_requests[request.request_id] = request
                self.total_requests_processed += 1
                self.total_processing_time += request.processing_time
            else:
                request.status = RequestStatus.FAILED
                self.failed_requests += 1
            
            del self.active_requests[request.request_id]
            self._update_resource_usage(increase=False)
            processed.append(request)
        
        while self.request_queue and self.can_accept_request():
            queued_request = self.request_queue.pop(0)
            self.submit_request(queued_request)
        
        return processed
    
    def _execute_request(self, request: ServiceRequest) -> bool:
        """Execute service-specific request logic"""
        try:
            if self.service_type == ServiceType.USER_SERVICE:
                return self._execute_user_service(request)
            elif self.service_type == ServiceType.PROJECT_SERVICE:
                return self._execute_project_service(request)
            elif self.service_type == ServiceType.CHAT_SERVICE:
                return self._execute_chat_service(request)
            elif self.service_type == ServiceType.PAYMENT_SERVICE:
                return self._execute_payment_service(request)
            elif self.service_type == ServiceType.FILE_SERVICE:
                return self._execute_file_service(request)
            return True
        except Exception:
            return False
    
    def _execute_user_service(self, request: ServiceRequest) -> bool:
        """Handle user service operations"""
        if request.request_type == RequestType.REGISTER_USER:
            user_id = str(uuid.uuid4())
            self.data_store[user_id] = {
                'email': request.payload.get('email'),
                'name': request.payload.get('name'),
                'role': request.payload.get('role', 'freelancer'),
                'created_at': time.time()
            }
            request.payload['user_id'] = user_id
            return True
        elif request.request_type == RequestType.AUTHENTICATE:
            user_id = request.payload.get('user_id')
            token = hashlib.sha256(f"{user_id}-{time.time()}".encode()).hexdigest()
            self.cache[token] = user_id
            request.payload['token'] = token
            return True
        elif request.request_type == RequestType.UPDATE_PROFILE:
            user_id = request.payload.get('user_id')
            if user_id in self.data_store:
                self.data_store[user_id].update(request.payload.get('updates', {}))
                return True
        return False
    
    def _execute_project_service(self, request: ServiceRequest) -> bool:
        """Handle project service operations"""
        if request.request_type == RequestType.CREATE_PROJECT:
            project_id = str(uuid.uuid4())
            self.data_store[project_id] = {
                'title': request.payload.get('title'),
                'client_id': request.payload.get('client_id'),
                'team': [],
                'tasks': [],
                'status': 'active',
                'created_at': time.time()
            }
            request.payload['project_id'] = project_id
            return True
        elif request.request_type == RequestType.ASSIGN_TASK:
            project_id = request.payload.get('project_id')
            if project_id in self.data_store:
                task = {
                    'task_id': str(uuid.uuid4()),
                    'assignee': request.payload.get('freelancer_id'),
                    'description': request.payload.get('description'),
                    'status': 'pending'
                }
                self.data_store[project_id]['tasks'].append(task)
                return True
        elif request.request_type == RequestType.UPDATE_TASK:
            project_id = request.payload.get('project_id')
            task_id = request.payload.get('task_id')
            if project_id in self.data_store:
                for task in self.data_store[project_id]['tasks']:
                    if task['task_id'] == task_id:
                        task['status'] = request.payload.get('status', task['status'])
                        return True
        return False
    
    def _execute_chat_service(self, request: ServiceRequest) -> bool:
        """Handle chat service operations (WebSocket simulation)"""
        if request.request_type == RequestType.SEND_MESSAGE:
            message_id = str(uuid.uuid4())
            channel_id = request.payload.get('channel_id')
            
            if channel_id not in self.data_store:
                self.data_store[channel_id] = {'messages': []}
            
            message = {
                'message_id': message_id,
                'sender_id': request.payload.get('sender_id'),
                'content': request.payload.get('content'),
                'timestamp': time.time()
            }
            self.data_store[channel_id]['messages'].append(message)
            self.cache[f"recent_{channel_id}"] = self.data_store[channel_id]['messages'][-50:]
            return True
        elif request.request_type == RequestType.CREATE_CHANNEL:
            channel_id = str(uuid.uuid4())
            self.data_store[channel_id] = {
                'members': request.payload.get('members', []),
                'messages': [],
                'created_at': time.time()
            }
            request.payload['channel_id'] = channel_id
            return True
        return False
    
    def _execute_payment_service(self, request: ServiceRequest) -> bool:
        """Handle payment service operations with blockchain validation"""
        if request.request_type == RequestType.PROCESS_PAYMENT:
            payment_id = str(uuid.uuid4())
            self.data_store[payment_id] = {
                'client_id': request.payload.get('client_id'),
                'freelancer_id': request.payload.get('freelancer_id'),
                'amount': request.payload.get('amount'),
                'status': 'escrow',
                'created_at': time.time()
            }
            request.payload['payment_id'] = payment_id
            return True
        elif request.request_type == RequestType.VALIDATE_TASK:
            validation = TaskValidation(
                validation_id=str(uuid.uuid4()),
                task_id=request.payload.get('task_id'),
                freelancer_id=request.payload.get('freelancer_id'),
                client_id=request.payload.get('client_id'),
                proof_hash=hashlib.sha256(
                    f"{request.payload.get('task_id')}-{time.time()}".encode()
                ).hexdigest(),
                timestamp=time.time(),
                validated=True
            )
            self.task_validations.append(validation)
            request.payload['validation_id'] = validation.validation_id
            return True
        elif request.request_type == RequestType.RELEASE_ESCROW:
            payment_id = request.payload.get('payment_id')
            if payment_id in self.data_store:
                self.data_store[payment_id]['status'] = 'released'
                self.data_store[payment_id]['released_at'] = time.time()
                return True
        return False
    
    def _execute_file_service(self, request: ServiceRequest) -> bool:
        """Handle file service operations (uploads, downloads, storage)"""
        if request.request_type == RequestType.UPLOAD_FILE:
            file_id = str(uuid.uuid4())
            self.data_store[file_id] = {
                'filename': request.payload.get('filename'),
                'file_size': request.payload.get('file_size', 0),
                'file_type': request.payload.get('file_type', 'unknown'),
                'uploader_id': request.payload.get('uploader_id'),
                'uploaded_at': time.time(),
                'status': 'stored'
            }
            request.payload['file_id'] = file_id
            return True
        elif request.request_type == RequestType.DOWNLOAD_FILE:
            file_id = request.payload.get('file_id')
            if file_id in self.data_store:
                request.payload['file_data'] = self.data_store[file_id]
                return True
        elif request.request_type == RequestType.DELETE_FILE:
            file_id = request.payload.get('file_id')
            if file_id in self.data_store:
                del self.data_store[file_id]
                return True
        elif request.request_type == RequestType.LIST_FILES:
            request.payload['files'] = list(self.data_store.keys())
            return True
        return False
    
    def _update_resource_usage(self, increase: bool):
        """Update CPU and memory usage based on active requests"""
        load = len(self.active_requests) / self.max_requests_per_sec
        self.cpu_usage = min(load * 100, 100)
        self.memory_usage = min(load * 80, 100)
        if increase:
            self.current_requests_per_sec = len(self.active_requests)
    
    def simulate_failure(self):
        """Simulate node failure for fault tolerance testing"""
        self.is_healthy = False
        print(f"[FAULT] {self.node_id} ({self.service_type.name}) has failed!")
    
    def recover(self):
        """Recover from failure"""
        self.is_healthy = True
        print(f"[RECOVERY] {self.node_id} ({self.service_type.name}) has recovered!")
    
    def get_health_status(self) -> Dict[str, Union[bool, float, int, str]]:
        """Get current health status of the node"""
        return {
            'node_id': self.node_id,
            'service_type': self.service_type.name,
            'is_healthy': self.is_healthy,
            'cpu_usage_percent': round(self.cpu_usage, 2),
            'memory_usage_percent': round(self.memory_usage, 2),
            'active_requests': len(self.active_requests),
            'queued_requests': len(self.request_queue),
            'can_accept_requests': self.can_accept_request()
        }
    
    def get_performance_metrics(self) -> Dict[str, Union[int, float, str]]:
        """Get comprehensive performance metrics"""
        uptime = time.time() - self.uptime_start
        avg_processing_time = (
            self.total_processing_time / self.total_requests_processed
            if self.total_requests_processed > 0 else 0
        )
        
        return {
            'node_id': self.node_id,
            'service_type': self.service_type.name,
            'total_requests_processed': self.total_requests_processed,
            'failed_requests': self.failed_requests,
            'success_rate_percent': (
                (self.total_requests_processed / 
                 (self.total_requests_processed + self.failed_requests) * 100)
                if (self.total_requests_processed + self.failed_requests) > 0 else 0
            ),
            'average_processing_time_sec': round(avg_processing_time, 4),
            'uptime_sec': round(uptime, 2),
            'requests_per_sec': round(
                self.total_requests_processed / uptime if uptime > 0 else 0, 2
            ),
            'data_store_entries': len(self.data_store),
            'cache_entries': len(self.cache),
            'task_validations': len(self.task_validations)
        }