"""
Animation and Visualization Engine for TalentSync Network Simulation

Provides real-time visualization of network events, request flows,
node status, and performance metrics with ANSI animations.
"""

import time
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
from datetime import datetime


class AnimationStyle(Enum):
    """ANSI color and style codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    # Background colors
    BG_RED = "\033[101m"
    BG_GREEN = "\033[102m"
    BG_YELLOW = "\033[103m"
    BG_BLUE = "\033[104m"
    BG_MAGENTA = "\033[105m"
    BG_CYAN = "\033[106m"
    
    # Effects
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"


class EventType(Enum):
    """Types of events to animate"""
    REQUEST_ROUTED = auto()
    REQUEST_PROCESSING = auto()
    REQUEST_COMPLETED = auto()
    REQUEST_FAILED = auto()
    NODE_FAILURE = auto()
    NODE_RECOVERY = auto()
    LOAD_INCREASE = auto()
    LOAD_DECREASE = auto()
    FILE_UPLOAD_STARTED = auto()
    FILE_DOWNLOAD_STARTED = auto()
    FILE_TRANSFER_PROGRESS = auto()
    FILE_TRANSFER_COMPLETED = auto()
    FILE_TRANSFER_FAILED = auto()


class NetworkAnimator:
    """
    Animates network events and system state
    Creates visual representations of network activity
    """
    
    def __init__(self, width: int = 70, height: int = 30):
        self.width = width
        self.height = height
        self.event_history: List[Tuple[float, str]] = []
        self.active_flows: Dict[str, Dict] = {}  # request_id -> flow_info
        self.node_statuses: Dict[str, Dict] = {}
        self.start_time = time.time()
        self.event_log: List[str] = []
    
    def animate_request_routed(self, 
                              request_id: str,
                              from_node: str,
                              to_node: str,
                              request_type: str):
        """Animate a request being routed to a node"""
        timestamp = self._get_timestamp()
        message = (f"{AnimationStyle.CYAN.value}[{timestamp}]{AnimationStyle.RESET.value} "
                  f"{AnimationStyle.BOLD.value}→{AnimationStyle.RESET.value} "
                  f"{request_type} routed to {to_node}")
        self._print_animated(message)
        self.event_history.append((time.time(), message))
        self.event_log.append(message)
    
    def animate_request_processing(self, 
                                  request_id: str,
                                  node_id: str,
                                  request_type: str,
                                  progress: int = 0):
        """Animate request processing with progress indicator"""
        timestamp = self._get_timestamp()
        progress_bar = self._create_progress_bar(progress)
        
        message = (f"{AnimationStyle.BLUE.value}[{timestamp}]{AnimationStyle.RESET.value} "
                  f"{AnimationStyle.BOLD.value}⚙{AnimationStyle.RESET.value}  "
                  f"Processing {request_type} on {node_id} {progress_bar}")
        self._print_animated(message, clear_previous=True)
    
    def animate_request_completed(self, 
                                 request_id: str,
                                 node_id: str,
                                 processing_time: float):
        """Animate successful request completion"""
        timestamp = self._get_timestamp()
        message = (f"{AnimationStyle.GREEN.value}[{timestamp}]{AnimationStyle.RESET.value} "
                  f"{AnimationStyle.BOLD.value}✓{AnimationStyle.RESET.value}  "
                  f"Request completed on {node_id} ({processing_time*1000:.1f}ms)")
        self._print_animated(message)
        self.event_history.append((time.time(), message))
        self.event_log.append(message)
    
    def animate_request_failed(self, 
                              request_id: str,
                              node_id: str,
                              reason: str = "Unknown"):
        """Animate request failure"""
        timestamp = self._get_timestamp()
        message = (f"{AnimationStyle.RED.value}[{timestamp}]{AnimationStyle.RESET.value} "
                  f"{AnimationStyle.BOLD.value}✗{AnimationStyle.RESET.value}  "
                  f"Request failed on {node_id}: {reason}")
        self._print_animated(message)
        self.event_history.append((time.time(), message))
        self.event_log.append(message)
    
    def animate_node_failure(self, node_id: str, service_type: str):
        """Animate node failure event"""
        timestamp = self._get_timestamp()
        message = (f"{AnimationStyle.BG_RED.value}{AnimationStyle.WHITE.value}[{timestamp}]"
                  f"{AnimationStyle.RESET.value} "
                  f"{AnimationStyle.RED.value}{AnimationStyle.BOLD.value}⚡ FAILURE{AnimationStyle.RESET.value} "
                  f"{node_id} ({service_type}) is DOWN")
        self._print_animated(message)
        self.event_history.append((time.time(), message))
        self.event_log.append(message)
    
    def animate_node_recovery(self, node_id: str, service_type: str):
        """Animate node recovery event"""
        timestamp = self._get_timestamp()
        message = (f"{AnimationStyle.BG_GREEN.value}{AnimationStyle.WHITE.value}[{timestamp}]"
                  f"{AnimationStyle.RESET.value} "
                  f"{AnimationStyle.GREEN.value}{AnimationStyle.BOLD.value}↻ RECOVERY{AnimationStyle.RESET.value} "
                  f"{node_id} ({service_type}) is UP")
        self._print_animated(message)
        self.event_history.append((time.time(), message))
        self.event_log.append(message)
    
    def animate_load_change(self, node_id: str, cpu_usage: float, memory_usage: float):
        """Animate load indicator for a node"""
        cpu_bar = self._create_load_bar(cpu_usage, max_width=15)
        mem_bar = self._create_load_bar(memory_usage, max_width=15)
        
        timestamp = self._get_timestamp()
        message = (f"{AnimationStyle.YELLOW.value}[{timestamp}]{AnimationStyle.RESET.value} "
                  f"📊 {node_id:20s} "
                  f"CPU:{cpu_bar} {cpu_usage:5.1f}%  "
                  f"MEM:{mem_bar} {memory_usage:5.1f}%")
        return message
    
    def create_network_visualization(self, nodes_status: Dict[str, Dict]) -> str:
        """Create ASCII visualization of network topology"""
        viz = []
        viz.append("\n" + "="*70)
        viz.append(" "*20 + "LIVE NETWORK VISUALIZATION")
        viz.append("="*70)
        
        # Group nodes by service type
        services = {}
        for node_id, status in nodes_status.items():
            service = status.get('service_type', 'unknown')
            if service not in services:
                services[service] = []
            services[service].append((node_id, status))
        
        # Visualize each service
        for service, nodes in services.items():
            viz.append(f"\n{AnimationStyle.BOLD.value}{service}{AnimationStyle.RESET.value}")
            viz.append("─" * 70)
            
            for node_id, status in nodes:
                is_healthy = status.get('is_healthy', False)
                cpu = status.get('cpu_usage_percent', 0)
                memory = status.get('memory_usage_percent', 0)
                
                health_icon = f"{AnimationStyle.GREEN.value}●{AnimationStyle.RESET.value}" if is_healthy else f"{AnimationStyle.RED.value}●{AnimationStyle.RESET.value}"
                cpu_bar = self._create_load_bar(cpu, max_width=20)
                mem_bar = self._create_load_bar(memory, max_width=20)
                
                viz.append(
                    f"  {health_icon} {node_id:20s} "
                    f"CPU:{cpu_bar} {cpu:5.1f}%  "
                    f"MEM:{mem_bar} {memory:5.1f}%"
                )
        
        viz.append("\n" + "="*70 + "\n")
        return "\n".join(viz)
    
    def create_traffic_flow_visualization(self, 
                                        from_node: str, 
                                        to_node: str,
                                        progress: int = 50) -> str:
        """Create ASCII visualization of data flow between nodes"""
        arrow_width = 50
        filled = int((progress / 100) * arrow_width)
        empty = arrow_width - filled
        
        flow = f"{from_node}" + "─" * filled + f"{AnimationStyle.CYAN.value}●{AnimationStyle.RESET.value}" + "─" * empty + f"→ {to_node}"
        return flow
    
    def create_metrics_dashboard(self, 
                                total_requests: int,
                                success_count: int,
                                failed_count: int,
                                avg_latency: float,
                                nodes_healthy: int,
                                nodes_total: int) -> str:
        """Create a metrics dashboard display"""
        dashboard = []
        dashboard.append("\n" + "="*70)
        dashboard.append(" "*18 + "REAL-TIME METRICS DASHBOARD")
        dashboard.append("="*70)
        
        success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
        success_bar = self._create_percentage_bar(success_rate)
        
        dashboard.append(f"\n{AnimationStyle.BOLD.value}Performance Metrics:{AnimationStyle.RESET.value}")
        dashboard.append(f"  Total Requests:    {total_requests:8d}")
        dashboard.append(f"  Successful:        {success_count:8d}  {AnimationStyle.GREEN.value}✓{AnimationStyle.RESET.value}")
        dashboard.append(f"  Failed:            {failed_count:8d}  {AnimationStyle.RED.value}✗{AnimationStyle.RESET.value}")
        dashboard.append(f"  Success Rate:      {success_bar} {success_rate:6.2f}%")
        dashboard.append(f"  Avg Latency:       {avg_latency*1000:8.2f}ms")
        
        dashboard.append(f"\n{AnimationStyle.BOLD.value}System Health:{AnimationStyle.RESET.value}")
        dashboard.append(f"  Healthy Nodes:     {nodes_healthy:8d}/{nodes_total}")
        health_bar = self._create_percentage_bar((nodes_healthy/nodes_total*100) if nodes_total > 0 else 0)
        dashboard.append(f"  Availability:      {health_bar} {(nodes_healthy/nodes_total*100):.1f}%")
        
        dashboard.append("\n" + "="*70 + "\n")
        return "\n".join(dashboard)
    
    def animate_node_grid(self, nodes_info: Dict[str, Dict]):
        """Display nodes as an animated grid"""
        grid = []
        grid.append("\n┌" + "─"*68 + "┐")
        grid.append("│" + " "*20 + "NETWORK NODE GRID" + " "*31 + "│")
        grid.append("├" + "─"*68 + "┤")
        
        for node_id, info in nodes_info.items():
            is_healthy = info.get('is_healthy', False)
            cpu = info.get('cpu_usage_percent', 0)
            requests = info.get('active_requests', 0)
            
            health_symbol = f"{AnimationStyle.GREEN.value}▓▓{AnimationStyle.RESET.value}" if is_healthy else f"{AnimationStyle.RED.value}░░{AnimationStyle.RESET.value}"
            node_display = f"│ {health_symbol} {node_id:25s} CPU:{cpu:5.1f}% REQ:{requests:3d}"
            node_display += " " * (68 - len(node_display) + 1) + "│"
            grid.append(node_display)
        
        grid.append("└" + "─"*68 + "┘\n")
        return "\n".join(grid)
    
    def animate_file_upload(self, 
                           transfer_id: str,
                           filename: str,
                           source_node: str,
                           dest_node: str,
                           file_size_mb: float):
        """Animate file upload start"""
        timestamp = self._get_timestamp()
        message = (f"{AnimationStyle.MAGENTA.value}[{timestamp}]{AnimationStyle.RESET.value} "
                  f"{AnimationStyle.BOLD.value}⬆{AnimationStyle.RESET.value}  "
                  f"UPLOAD: {filename} ({file_size_mb:.1f}MB) "
                  f"{source_node} → {dest_node}")
        self._print_animated(message)
        self.event_log.append(message)
    
    def animate_file_download(self, 
                             transfer_id: str,
                             filename: str,
                             source_node: str,
                             dest_node: str,
                             file_size_mb: float):
        """Animate file download start"""
        timestamp = self._get_timestamp()
        message = (f"{AnimationStyle.CYAN.value}[{timestamp}]{AnimationStyle.RESET.value} "
                  f"{AnimationStyle.BOLD.value}⬇{AnimationStyle.RESET.value}  "
                  f"DOWNLOAD: {filename} ({file_size_mb:.1f}MB) "
                  f"{source_node} → {dest_node}")
        self._print_animated(message)
        self.event_log.append(message)
    
    def animate_transfer_progress(self, 
                                 filename: str,
                                 progress: float,
                                 throughput_mbps: float,
                                 eta_seconds: float):
        """Animate file transfer progress"""
        progress_bar = self._create_progress_bar(int(progress), width=40)
        eta_min = int(eta_seconds // 60)
        eta_sec = int(eta_seconds % 60)
        
        message = (f"  {progress_bar} {progress:5.1f}% | "
                  f"Speed: {throughput_mbps:6.1f} MB/s | "
                  f"ETA: {eta_min:02d}:{eta_sec:02d}")
        return message
    
    def animate_transfer_completed(self, 
                                  filename: str,
                                  file_size_mb: float,
                                  transfer_time_sec: float,
                                  throughput_mbps: float):
        """Animate transfer completion"""
        timestamp = self._get_timestamp()
        message = (f"{AnimationStyle.GREEN.value}[{timestamp}]{AnimationStyle.RESET.value} "
                  f"{AnimationStyle.BOLD.value}✓ TRANSFER COMPLETE{AnimationStyle.RESET.value}  "
                  f"{filename} - {file_size_mb:.1f}MB in {transfer_time_sec:.2f}s "
                  f"({throughput_mbps:.1f} MB/s)")
        self._print_animated(message)
        self.event_log.append(message)
    
    def animate_transfer_failed(self, 
                               filename: str,
                               reason: str = "Unknown"):
        """Animate transfer failure"""
        timestamp = self._get_timestamp()
        message = (f"{AnimationStyle.RED.value}[{timestamp}]{AnimationStyle.RESET.value} "
                  f"{AnimationStyle.BOLD.value}✗ TRANSFER FAILED{AnimationStyle.RESET.value}  "
                  f"{filename}: {reason}")
        self._print_animated(message)
        self.event_log.append(message)
    
    def create_file_transfer_dashboard(self, 
                                      active_transfers: int,
                                      completed_transfers: int,
                                      failed_transfers: int,
                                      total_data_transferred_mb: float,
                                      avg_throughput_mbps: float,
                                      avg_latency_ms: float,
                                      avg_packet_loss_percent: float) -> str:
        """Create file transfer metrics dashboard"""
        dashboard = []
        dashboard.append("\n" + "="*70)
        dashboard.append(" "*15 + "FILE TRANSFER METRICS DASHBOARD")
        dashboard.append("="*70)
        
        dashboard.append(f"\n{AnimationStyle.BOLD.value}Transfer Statistics:{AnimationStyle.RESET.value}")
        dashboard.append(f"  Active Transfers:       {active_transfers:8d}")
        dashboard.append(f"  Completed Transfers:    {completed_transfers:8d}  {AnimationStyle.GREEN.value}✓{AnimationStyle.RESET.value}")
        dashboard.append(f"  Failed Transfers:       {failed_transfers:8d}  {AnimationStyle.RED.value}✗{AnimationStyle.RESET.value}")
        dashboard.append(f"  Total Data Transferred: {total_data_transferred_mb:8.2f} MB")
        
        dashboard.append(f"\n{AnimationStyle.BOLD.value}Performance Metrics:{AnimationStyle.RESET.value}")
        throughput_bar = self._create_percentage_bar(min(avg_throughput_mbps / 200 * 100, 100))
        dashboard.append(f"  Avg Throughput:         {throughput_bar} {avg_throughput_mbps:6.2f} MB/s")
        dashboard.append(f"  Avg Latency:            {avg_latency_ms:8.2f} ms")
        loss_bar = self._create_percentage_bar(100 - min(avg_packet_loss_percent * 10, 100))
        dashboard.append(f"  Avg Packet Loss:        {loss_bar} {avg_packet_loss_percent:6.2f}%")
        
        dashboard.append("\n" + "="*70 + "\n")
        return "\n".join(dashboard)
    
    def _create_progress_bar(self, progress: int, width: int = 30) -> str:
        """Create an animated progress bar"""
        filled = int((progress / 100) * width)
        empty = width - filled
        
        return f"[{AnimationStyle.GREEN.value}{'█' * filled}{AnimationStyle.RESET.value}{'░' * empty}] {progress}%"
    
    def _create_load_bar(self, load: float, max_width: int = 20) -> str:
        """Create a load indicator bar"""
        filled = int((load / 100) * max_width)
        empty = max_width - filled
        
        if load > 80:
            color = AnimationStyle.RED.value
        elif load > 60:
            color = AnimationStyle.YELLOW.value
        else:
            color = AnimationStyle.GREEN.value
        
        return f"[{color}{'▓' * filled}{AnimationStyle.RESET.value}{'░' * empty}]"
    
    def _create_percentage_bar(self, percentage: float, width: int = 40) -> str:
        """Create a percentage bar"""
        filled = int((percentage / 100) * width)
        empty = width - filled
        
        if percentage >= 95:
            color = AnimationStyle.GREEN.value
        elif percentage >= 80:
            color = AnimationStyle.YELLOW.value
        else:
            color = AnimationStyle.RED.value
        
        return f"[{color}{'█' * filled}{AnimationStyle.RESET.value}{'░' * empty}]"
    
    def _print_animated(self, message: str, clear_previous: bool = False):
        """Print an animated message"""
        if clear_previous:
            print("\033[A\033[K", end="")  # Move up one line and clear
        print(message)
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        millis = int((elapsed % 1) * 1000)
        return f"{minutes:02d}:{seconds:02d}.{millis:03d}"
    
    def print_event_log(self):
        """Print summary of events"""
        print("\n" + "="*70)
        print(" "*22 + "EVENT LOG SUMMARY")
        print("="*70)
        
        for event in self.event_log[-20:]:  # Show last 20 events
            print(event)
        
        print("="*70 + "\n")


class SequenceDiagram:
    """Generate ASCII sequence diagrams for service interactions"""
    
    def __init__(self):
        self.interactions: List[Dict] = []
    
    def add_interaction(self, from_service: str, to_service: str, message: str):
        """Add an interaction to the sequence diagram"""
        self.interactions.append({
            'from': from_service,
            'to': to_service,
            'message': message
        })
    
    def render(self) -> str:
        """Render the sequence diagram as ASCII art"""
        if not self.interactions:
            return "No interactions recorded"
        
        # Get unique services
        services = []
        for interaction in self.interactions:
            if interaction['from'] not in services:
                services.append(interaction['from'])
            if interaction['to'] not in services:
                services.append(interaction['to'])
        
        # Calculate column widths
        col_width = max(len(service) for service in services) + 2
        diagram = []
        
        # Draw header
        header = "  "
        for service in services:
            header += f"{service:^{col_width}}"
        diagram.append(header)
        
        # Draw separators
        separator = "  " + "┬" + ("─" * col_width + "┬") * (len(services) - 1) + "─" * col_width + "┐"
        diagram.append(separator)
        
        # Draw interactions
        for interaction in self.interactions:
            from_idx = services.index(interaction['from'])
            to_idx = services.index(interaction['to'])
            
            line = "  "
            for i in range(len(services)):
                if i == min(from_idx, to_idx):
                    line += f"│{interaction['message']:<{col_width-1}}"
                elif i == max(from_idx, to_idx):
                    line += f"│{' ':{col_width-1}}"
                else:
                    line += f"│{' ':{col_width}}"
            line += "│"
            diagram.append(line)
        
        return "\n".join(diagram)
