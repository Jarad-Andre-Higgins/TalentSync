"""
File Service Module for TalentSync

Implements file transfer simulation with bandwidth management,
progress tracking, and distributed storage across service nodes.
"""

import time
import uuid
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import math


class TransferType(Enum):
    """Types of file transfers"""
    UPLOAD = auto()
    DOWNLOAD = auto()
    REPLICATION = auto()
    BACKUP = auto()


class TransferStatus(Enum):
    """Status of a file transfer"""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    PAUSED = auto()


@dataclass
class FileMetadata:
    """Metadata for a file"""
    file_id: str
    filename: str
    file_size: int  # in bytes
    file_type: str  # e.g., 'document', 'image', 'video', 'archive'
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    checksum: str = ""  # SHA-256 hash
    owner_id: str = ""
    storage_nodes: List[str] = field(default_factory=list)  # Replicated nodes
    
    def calculate_checksum(self, data: bytes = None) -> str:
        """Calculate SHA-256 checksum of file"""
        if data:
            self.checksum = hashlib.sha256(data).hexdigest()
        else:
            self.checksum = hashlib.sha256(f"{self.file_id}{self.filename}".encode()).hexdigest()
        return self.checksum


@dataclass
class FileTransfer:
    """Represents a file transfer operation"""
    transfer_id: str
    file_id: str
    transfer_type: TransferType
    source_node: str
    dest_node: str
    file_size: int  # bytes
    bandwidth_limit: int = 10_000_000  # 10 MB/s default
    
    status: TransferStatus = TransferStatus.PENDING
    bytes_transferred: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # Performance metrics
    throughput_mbps: float = 0.0  # Current throughput in MB/s
    estimated_time_remaining: float = 0.0
    packet_loss_percent: float = 0.0
    latency_ms: float = 0.0
    
    def get_progress(self) -> float:
        """Get transfer progress as percentage (0-100)"""
        if self.file_size == 0:
            return 0.0
        return (self.bytes_transferred / self.file_size) * 100
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def calculate_throughput(self) -> float:
        """Calculate actual throughput in MB/s"""
        elapsed = self.get_elapsed_time()
        if elapsed == 0:
            return 0.0
        mb_transferred = self.bytes_transferred / (1024 * 1024)
        self.throughput_mbps = mb_transferred / elapsed
        return self.throughput_mbps
    
    def calculate_eta(self) -> float:
        """Calculate estimated time to completion in seconds"""
        if self.throughput_mbps == 0:
            return 0.0
        remaining_bytes = self.file_size - self.bytes_transferred
        remaining_mb = remaining_bytes / (1024 * 1024)
        self.estimated_time_remaining = remaining_mb / self.throughput_mbps if self.throughput_mbps > 0 else 0
        return self.estimated_time_remaining
    
    def __str__(self):
        return f"Transfer({self.transfer_id[:8]}... {self.transfer_type.name} {self.get_progress():.1f}%)"


@dataclass
class StorageNode:
    """Represents file storage on a service node"""
    node_id: str
    storage_capacity: int  # bytes
    storage_used: int = 0
    files: Dict[str, FileMetadata] = field(default_factory=dict)  # file_id -> metadata
    file_data: Dict[str, bytes] = field(default_factory=dict)  # file_id -> data
    
    def get_available_space(self) -> int:
        """Get available storage space in bytes"""
        return self.storage_capacity - self.storage_used
    
    def get_usage_percent(self) -> float:
        """Get storage usage as percentage"""
        if self.storage_capacity == 0:
            return 0.0
        return (self.storage_used / self.storage_capacity) * 100
    
    def can_store_file(self, file_size: int) -> bool:
        """Check if node has space for file"""
        return self.get_available_space() >= file_size
    
    def store_file(self, metadata: FileMetadata, data: bytes = None) -> bool:
        """Store file on this node"""
        if not self.can_store_file(metadata.file_size):
            return False
        
        self.files[metadata.file_id] = metadata
        self.storage_used += metadata.file_size
        
        if data:
            self.file_data[metadata.file_id] = data
        
        return True
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from this node"""
        if file_id not in self.files:
            return False
        
        file_size = self.files[file_id].file_size
        del self.files[file_id]
        self.storage_used -= file_size
        
        if file_id in self.file_data:
            del self.file_data[file_id]
        
        return True
    
    def get_file_data(self, file_id: str) -> Optional[bytes]:
        """Retrieve file data"""
        return self.file_data.get(file_id)


class FileTransferSimulator:
    """Simulates file transfer operations with bandwidth and latency"""
    
    def __init__(self, base_bandwidth_mbps: float = 100.0, latency_ms: float = 5.0):
        """
        Initialize file transfer simulator
        
        Args:
            base_bandwidth_mbps: Base bandwidth in MB/s
            latency_ms: Network latency in milliseconds
        """
        self.base_bandwidth_mbps = base_bandwidth_mbps
        self.latency_ms = latency_ms
        self.active_transfers: Dict[str, FileTransfer] = {}
        self.completed_transfers: Dict[str, FileTransfer] = {}
        self.failed_transfers: Dict[str, FileTransfer] = {}
    
    def start_transfer(self, 
                      file_id: str,
                      transfer_type: TransferType,
                      source_node: str,
                      dest_node: str,
                      file_size: int,
                      bandwidth_limit_mbps: float = None) -> FileTransfer:
        """Start a new file transfer"""
        transfer = FileTransfer(
            transfer_id=str(uuid.uuid4()),
            file_id=file_id,
            transfer_type=transfer_type,
            source_node=source_node,
            dest_node=dest_node,
            file_size=file_size,
            bandwidth_limit=int((bandwidth_limit_mbps or self.base_bandwidth_mbps) * 1024 * 1024)
        )
        transfer.status = TransferStatus.IN_PROGRESS
        transfer.latency_ms = self.latency_ms
        
        self.active_transfers[transfer.transfer_id] = transfer
        return transfer
    
    def simulate_transfer_progress(self, 
                                   transfer: FileTransfer,
                                   elapsed_time_ms: float,
                                   packet_loss_percent: float = 0.5) -> float:
        """
        Simulate transfer progress over elapsed time
        
        Args:
            transfer: The FileTransfer object
            elapsed_time_ms: Time elapsed in milliseconds
            packet_loss_percent: Packet loss percentage (0-100)
        
        Returns:
            Bytes transferred in this interval
        """
        # Calculate effective bandwidth with packet loss
        effective_bandwidth = transfer.bandwidth_limit * (1 - packet_loss_percent / 100)
        
        # Calculate bytes that should have been transferred
        bytes_per_ms = effective_bandwidth / 1000
        bytes_to_transfer = int(bytes_per_ms * elapsed_time_ms)
        
        # Ensure we don't exceed file size
        bytes_to_transfer = min(bytes_to_transfer, 
                               transfer.file_size - transfer.bytes_transferred)
        
        transfer.bytes_transferred += bytes_to_transfer
        transfer.packet_loss_percent = packet_loss_percent
        
        # Check if transfer completed
        if transfer.bytes_transferred >= transfer.file_size:
            transfer.status = TransferStatus.COMPLETED
            transfer.end_time = time.time()
            self.active_transfers.pop(transfer.transfer_id, None)
            self.completed_transfers[transfer.transfer_id] = transfer
        
        transfer.calculate_throughput()
        transfer.calculate_eta()
        
        return bytes_to_transfer
    
    def get_transfer_stats(self) -> Dict:
        """Get overall transfer statistics"""
        total_transfers = len(self.active_transfers) + len(self.completed_transfers) + len(self.failed_transfers)
        total_data_transferred = sum(t.bytes_transferred for t in self.completed_transfers.values())
        total_time = sum(t.get_elapsed_time() for t in self.completed_transfers.values())
        
        avg_throughput = 0.0
        if total_time > 0:
            total_mb = total_data_transferred / (1024 * 1024)
            avg_throughput = total_mb / total_time
        
        return {
            'total_transfers': total_transfers,
            'active_transfers': len(self.active_transfers),
            'completed_transfers': len(self.completed_transfers),
            'failed_transfers': len(self.failed_transfers),
            'total_data_transferred_mb': total_data_transferred / (1024 * 1024),
            'average_throughput_mbps': avg_throughput,
            'total_time_seconds': total_time
        }


class DistributedStorageManager:
    """Manages distributed file storage across multiple nodes"""
    
    def __init__(self):
        self.storage_nodes: Dict[str, StorageNode] = {}
        self.files: Dict[str, FileMetadata] = {}  # file_id -> metadata
        self.replication_factor = 2  # Default: store files on 2 nodes
    
    def register_storage_node(self, 
                            node_id: str,
                            storage_capacity_gb: float) -> StorageNode:
        """Register a storage node in the system"""
        storage_bytes = int(storage_capacity_gb * 1024 * 1024 * 1024)
        node = StorageNode(node_id=node_id, storage_capacity=storage_bytes)
        self.storage_nodes[node_id] = node
        print(f"[STORAGE] Registered node {node_id} with {storage_capacity_gb}GB capacity")
        return node
    
    def store_file(self, 
                  filename: str,
                  file_size: int,
                  file_type: str = "unknown",
                  owner_id: str = "system",
                  data: bytes = None) -> Optional[FileMetadata]:
        """Store a file across replicated nodes"""
        file_id = str(uuid.uuid4())
        metadata = FileMetadata(
            file_id=file_id,
            filename=filename,
            file_size=file_size,
            file_type=file_type,
            owner_id=owner_id
        )
        metadata.calculate_checksum(data)
        
        # Find suitable nodes for storage
        suitable_nodes = [
            node for node in self.storage_nodes.values()
            if node.can_store_file(file_size)
        ]
        
        if len(suitable_nodes) < self.replication_factor:
            print(f"[STORAGE] ERROR: Not enough nodes with space for file {filename}")
            return None
        
        # Sort by available space (prefer nodes with more space)
        suitable_nodes.sort(key=lambda n: n.get_available_space(), reverse=True)
        
        # Store on selected nodes
        replicated_count = 0
        for node in suitable_nodes[:self.replication_factor]:
            if node.store_file(metadata, data):
                metadata.storage_nodes.append(node.node_id)
                replicated_count += 1
        
        if replicated_count > 0:
            self.files[file_id] = metadata
            print(f"[STORAGE] Stored file '{filename}' ({file_size} bytes) on {replicated_count} nodes")
            return metadata
        
        return None
    
    def retrieve_file(self, file_id: str) -> Optional[Tuple[FileMetadata, bytes, str]]:
        """Retrieve file from storage"""
        if file_id not in self.files:
            return None
        
        metadata = self.files[file_id]
        
        # Try to retrieve from first available node
        for node_id in metadata.storage_nodes:
            if node_id in self.storage_nodes:
                node = self.storage_nodes[node_id]
                data = node.get_file_data(file_id)
                if data:
                    return metadata, data, node_id
        
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from all replicated nodes"""
        if file_id not in self.files:
            return False
        
        metadata = self.files[file_id]
        deleted_count = 0
        
        for node_id in metadata.storage_nodes:
            if node_id in self.storage_nodes:
                if self.storage_nodes[node_id].delete_file(file_id):
                    deleted_count += 1
        
        if deleted_count > 0:
            del self.files[file_id]
            return True
        
        return False
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics across all nodes"""
        total_capacity = sum(n.storage_capacity for n in self.storage_nodes.values())
        total_used = sum(n.storage_used for n in self.storage_nodes.values())
        total_available = sum(n.get_available_space() for n in self.storage_nodes.values())
        
        return {
            'total_nodes': len(self.storage_nodes),
            'total_capacity_gb': total_capacity / (1024 * 1024 * 1024),
            'total_used_gb': total_used / (1024 * 1024 * 1024),
            'total_available_gb': total_available / (1024 * 1024 * 1024),
            'usage_percent': (total_used / total_capacity * 100) if total_capacity > 0 else 0,
            'total_files': len(self.files),
            'replication_factor': self.replication_factor
        }
    
    def print_storage_info(self):
        """Print detailed storage information"""
        stats = self.get_storage_stats()
        
        print("\n" + "="*70)
        print(" "*15 + "DISTRIBUTED STORAGE INFORMATION")
        print("="*70)
        
        print(f"\n[OVERALL STATISTICS]")
        print(f"  Total Nodes:        {stats['total_nodes']}")
        print(f"  Total Capacity:     {stats['total_capacity_gb']:.2f} GB")
        print(f"  Total Used:         {stats['total_used_gb']:.2f} GB")
        print(f"  Total Available:    {stats['total_available_gb']:.2f} GB")
        print(f"  Usage:              {stats['usage_percent']:.1f}%")
        print(f"  Total Files:        {stats['total_files']}")
        print(f"  Replication Factor: {stats['replication_factor']}x")
        
        print(f"\n[NODE BREAKDOWN]")
        for node_id, node in self.storage_nodes.items():
            capacity_gb = node.storage_capacity / (1024 * 1024 * 1024)
            used_gb = node.storage_used / (1024 * 1024 * 1024)
            available_gb = node.get_available_space() / (1024 * 1024 * 1024)
            
            print(f"  {node_id:20s}")
            print(f"    Capacity:   {capacity_gb:8.2f} GB")
            print(f"    Used:       {used_gb:8.2f} GB ({node.get_usage_percent():5.1f}%)")
            print(f"    Available:  {available_gb:8.2f} GB")
            print(f"    Files:      {len(node.files)}")
        
        print(f"\n[STORED FILES]")
        for file_id, metadata in self.files.items():
            file_size_mb = metadata.file_size / (1024 * 1024)
            print(f"  {metadata.filename}")
            print(f"    ID:        {file_id[:8]}...")
            print(f"    Size:      {file_size_mb:.2f} MB")
            print(f"    Type:      {metadata.file_type}")
            print(f"    Owner:     {metadata.owner_id}")
            print(f"    Replicas:  {len(metadata.storage_nodes)}")
            print(f"    Nodes:     {', '.join(metadata.storage_nodes)}")
        
        print("="*70 + "\n")


class NetworkMetricsTracker:
    """Tracks network performance metrics for file transfers"""
    
    def __init__(self):
        self.transfers_completed = 0
        self.total_data_transferred = 0  # bytes
        self.total_transfer_time = 0.0  # seconds
        self.packet_loss_samples: List[float] = []
        self.latency_samples: List[float] = []
        self.throughput_samples: List[float] = []
    
    def record_transfer(self, 
                       transfer: FileTransfer,
                       packet_loss_percent: float,
                       latency_ms: float):
        """Record metrics from a completed transfer"""
        if transfer.status == TransferStatus.COMPLETED:
            self.transfers_completed += 1
            self.total_data_transferred += transfer.bytes_transferred
            self.total_transfer_time += transfer.get_elapsed_time()
            
            self.packet_loss_samples.append(packet_loss_percent)
            self.latency_samples.append(latency_ms)
            self.throughput_samples.append(transfer.calculate_throughput())
    
    def get_average_throughput(self) -> float:
        """Get average throughput in MB/s"""
        if not self.throughput_samples:
            return 0.0
        return sum(self.throughput_samples) / len(self.throughput_samples)
    
    def get_average_latency(self) -> float:
        """Get average latency in ms"""
        if not self.latency_samples:
            return 0.0
        return sum(self.latency_samples) / len(self.latency_samples)
    
    def get_average_packet_loss(self) -> float:
        """Get average packet loss percentage"""
        if not self.packet_loss_samples:
            return 0.0
        return sum(self.packet_loss_samples) / len(self.packet_loss_samples)
    
    def get_metrics_summary(self) -> Dict:
        """Get comprehensive metrics summary"""
        total_mb = self.total_data_transferred / (1024 * 1024)
        avg_throughput = total_mb / self.total_transfer_time if self.total_transfer_time > 0 else 0
        
        return {
            'transfers_completed': self.transfers_completed,
            'total_data_transferred_mb': total_mb,
            'total_time_seconds': self.total_transfer_time,
            'average_throughput_mbps': avg_throughput,
            'average_latency_ms': self.get_average_latency(),
            'average_packet_loss_percent': self.get_average_packet_loss(),
            'min_throughput_mbps': min(self.throughput_samples) if self.throughput_samples else 0,
            'max_throughput_mbps': max(self.throughput_samples) if self.throughput_samples else 0,
            'min_latency_ms': min(self.latency_samples) if self.latency_samples else 0,
            'max_latency_ms': max(self.latency_samples) if self.latency_samples else 0,
        }
    
    def print_metrics_report(self):
        """Print detailed metrics report"""
        metrics = self.get_metrics_summary()
        
        print("\n" + "="*70)
        print(" "*15 + "NETWORK METRICS & PERFORMANCE REPORT")
        print("="*70)
        
        print(f"\n[TRANSFER STATISTICS]")
        print(f"  Transfers Completed:    {metrics['transfers_completed']}")
        print(f"  Total Data Transferred: {metrics['total_data_transferred_mb']:.2f} MB")
        print(f"  Total Time:             {metrics['total_time_seconds']:.2f} seconds")
        
        print(f"\n[THROUGHPUT METRICS]")
        print(f"  Average Throughput:     {metrics['average_throughput_mbps']:.2f} MB/s")
        print(f"  Min Throughput:         {metrics['min_throughput_mbps']:.2f} MB/s")
        print(f"  Max Throughput:         {metrics['max_throughput_mbps']:.2f} MB/s")
        
        print(f"\n[LATENCY METRICS]")
        print(f"  Average Latency:        {metrics['average_latency_ms']:.2f} ms")
        print(f"  Min Latency:            {metrics['min_latency_ms']:.2f} ms")
        print(f"  Max Latency:            {metrics['max_latency_ms']:.2f} ms")
        
        print(f"\n[PACKET LOSS METRICS]")
        print(f"  Average Packet Loss:    {metrics['average_packet_loss_percent']:.2f}%")
        
        print("="*70 + "\n")
