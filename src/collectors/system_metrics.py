"""
System resource monitoring and metrics collection.
"""
from typing import Dict, Any
import psutil
from datetime import datetime


class SystemMetricsCollector:
    """Collects system resource metrics."""
    
    def __init__(self) -> None:
        """Initialize the system metrics collector."""
        self.previous_cpu_times = psutil.cpu_times()
        self.previous_disk_io = psutil.disk_io_counters()
        self.previous_net_io = psutil.net_io_counters()
        
    def get_metrics(self) -> Dict[str, Any]:
        """
        Collect current system metrics.
        
        Returns:
            Dictionary containing system metrics
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": self._get_cpu_metrics(),
            "memory": self._get_memory_metrics(),
            "disk": self._get_disk_metrics(),
            "network": self._get_network_metrics()
        }
    
    def _get_cpu_metrics(self) -> Dict[str, Any]:
        """
        Get CPU-related metrics.
        
        Returns:
            Dictionary containing CPU metrics
        """
        cpu_times = psutil.cpu_times()
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        
        return {
            "total_usage_percent": sum(cpu_percent) / len(cpu_percent),
            "per_cpu_percent": cpu_percent,
            "user_time": cpu_times.user,
            "system_time": cpu_times.system,
            "idle_time": cpu_times.idle,
            "core_count": psutil.cpu_count(),
            "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
    
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """
        Get memory-related metrics.
        
        Returns:
            Dictionary containing memory metrics
        """
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        
        return {
            "virtual": {
                "total": virtual_memory.total,
                "available": virtual_memory.available,
                "used": virtual_memory.used,
                "free": virtual_memory.free,
                "percent": virtual_memory.percent
            },
            "swap": {
                "total": swap_memory.total,
                "used": swap_memory.used,
                "free": swap_memory.free,
                "percent": swap_memory.percent
            }
        }
    
    def _get_disk_metrics(self) -> Dict[str, Any]:
        """
        Get disk-related metrics.
        
        Returns:
            Dictionary containing disk metrics
        """
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        return {
            "usage": {
                "total": disk_usage.total,
                "used": disk_usage.used,
                "free": disk_usage.free,
                "percent": disk_usage.percent
            },
            "io": {
                "read_bytes": disk_io.read_bytes,
                "write_bytes": disk_io.write_bytes,
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count
            }
        }
    
    def _get_network_metrics(self) -> Dict[str, Any]:
        """
        Get network-related metrics.
        
        Returns:
            Dictionary containing network metrics
        """
        net_io = psutil.net_io_counters()
        
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "error_in": net_io.errin,
            "error_out": net_io.errout,
            "drop_in": net_io.dropin,
            "drop_out": net_io.dropout
        }
