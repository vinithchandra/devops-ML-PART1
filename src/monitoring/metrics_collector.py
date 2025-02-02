"""
System metrics collection and monitoring service.
"""
import time
from typing import Dict, Any, List
import threading
from datetime import datetime
import queue
from pathlib import Path
import json
import psutil
from loguru import logger

from ..ml.models import AnomalyDetector
from ..config.settings import FEATURE_CONFIG, LOG_DIR


class MetricsCollector:
    """Collects and stores system metrics with anomaly detection."""
    
    def __init__(self, 
                 metrics_window: int = FEATURE_CONFIG['system']['metrics_window'],
                 collection_interval: int = FEATURE_CONFIG['system']['collection_interval']) -> None:
        """
        Initialize the metrics collector.
        
        Args:
            metrics_window: Time window for keeping metrics in memory (seconds)
            collection_interval: Interval between metric collections (seconds)
        """
        self.metrics_window = metrics_window
        self.collection_interval = collection_interval
        self.metrics_queue: queue.Queue = queue.Queue()
        self.metrics_history: List[Dict[str, Any]] = []
        self.anomaly_detector = AnomalyDetector()
        self.stop_event = threading.Event()
        
        # Set up logging
        log_file = LOG_DIR / 'system_metrics.log'
        logger.add(
            log_file,
            rotation="1 day",
            retention="1 month",
            level="INFO"
        )
        
    def start(self) -> None:
        """Start the metrics collection service."""
        self.stop_event.clear()
        collection_thread = threading.Thread(
            target=self._collect_metrics,
            daemon=True
        )
        processing_thread = threading.Thread(
            target=self._process_metrics,
            daemon=True
        )
        
        collection_thread.start()
        processing_thread.start()
        logger.info("Metrics collection service started")
        
    def stop(self) -> None:
        """Stop the metrics collection service."""
        self.stop_event.set()
        logger.info("Metrics collection service stopped")
        
    def _collect_metrics(self) -> None:
        """Continuously collect system metrics."""
        while not self.stop_event.is_set():
            try:
                metrics = self._get_current_metrics()
                self.metrics_queue.put(metrics)
                time.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error collecting metrics: {str(e)}")
                
    def _process_metrics(self) -> None:
        """Process collected metrics and detect anomalies."""
        while not self.stop_event.is_set():
            try:
                metrics = self.metrics_queue.get(timeout=1)
                self._update_history(metrics)
                self._detect_anomalies()
                self._save_metrics(metrics)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing metrics: {str(e)}")
                
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        cpu_times = psutil.cpu_times()
        virtual_memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'times': {
                    'user': cpu_times.user,
                    'system': cpu_times.system,
                    'idle': cpu_times.idle
                }
            },
            'memory': {
                'total': virtual_memory.total,
                'available': virtual_memory.available,
                'percent': virtual_memory.percent,
                'used': virtual_memory.used,
                'free': virtual_memory.free
            },
            'disk': {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': disk_usage.percent
            },
            'network': self._get_network_metrics()
        }
        
    def _get_network_metrics(self) -> Dict[str, int]:
        """Get network I/O metrics."""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
        
    def _update_history(self, metrics: Dict[str, Any]) -> None:
        """Update metrics history within the specified window."""
        current_time = datetime.now().timestamp()
        cutoff_time = current_time - self.metrics_window
        
        # Remove old metrics
        self.metrics_history = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m['timestamp']).timestamp() > cutoff_time
        ]
        
        # Add new metrics
        self.metrics_history.append(metrics)
        
    def _detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in recent metrics."""
        if len(self.metrics_history) < 2:
            return []
            
        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements
        
        # Extract features for anomaly detection
        features = []
        for m in recent_metrics:
            features.append([
                m['cpu']['percent'],
                m['memory']['percent'],
                m['disk']['percent']
            ])
            
        # Detect anomalies
        result = self.anomaly_detector.detect(features[-1])
        
        if result['is_anomaly']:
            anomaly = {
                'timestamp': datetime.now().isoformat(),
                'metrics': recent_metrics[-1],
                'scores': result['z_scores']
            }
            self._log_anomaly(anomaly)
            return [anomaly]
            
        return []
        
    def _log_anomaly(self, anomaly: Dict[str, Any]) -> None:
        """Log detected anomalies."""
        logger.warning(f"Anomaly detected: {json.dumps(anomaly, indent=2)}")
        
    def _save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to disk."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        metrics_file = LOG_DIR / f'metrics_{date_str}.json'
        
        try:
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    daily_metrics = json.load(f)
            else:
                daily_metrics = []
                
            daily_metrics.append(metrics)
            
            with open(metrics_file, 'w') as f:
                json.dump(daily_metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")
            
    def get_recent_metrics(self) -> List[Dict[str, Any]]:
        """Get recent metrics within the window."""
        return self.metrics_history
        
    def get_anomalies(self) -> List[Dict[str, Any]]:
        """Get detected anomalies."""
        return self._detect_anomalies()
