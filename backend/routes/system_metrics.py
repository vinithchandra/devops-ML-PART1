from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import random
import json
import os
from datetime import datetime, timedelta

# Import ML models
from ..ml.anomaly_detector import AnomalyDetector

# Create router
router = APIRouter(
    prefix="/api/system-metrics",
    tags=["system-metrics"],
    responses={404: {"description": "Not found"}},
)

# Models
class SystemMetricsResponse(BaseModel):
    cpu: List[Dict[str, Any]]
    memory: List[Dict[str, Any]]
    disk: List[Dict[str, Any]]
    network: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]

class AnomalyDetectionRequest(BaseModel):
    metricType: str
    timeRange: str
    threshold: Optional[float] = None

class AnomalyDetectionResponse(BaseModel):
    anomalies: List[Dict[str, Any]]

# Initialize anomaly detectors for each metric type
cpu_anomaly_detector = AnomalyDetector(metric_name="cpu")
memory_anomaly_detector = AnomalyDetector(metric_name="memory")
disk_anomaly_detector = AnomalyDetector(metric_name="disk")
network_anomaly_detector = AnomalyDetector(metric_name="network")

# Routes
@router.get("", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """
    Get system metrics data
    """
    # Mock implementation - in a real app, this would fetch from a monitoring system
    now = datetime.now()
    
    # Generate 30 data points for each metric (last 30 minutes)
    metrics = {}
    anomalies = []
    
    # Generate data for each metric type
    for metric_type in ["cpu", "memory", "disk", "network"]:
        # Base value and variance for each metric type
        if metric_type == "cpu":
            base_value = 40
            variance = 20
            threshold = 80
        elif metric_type == "memory":
            base_value = 60
            variance = 15
            threshold = 85
        elif metric_type == "disk":
            base_value = 50
            variance = 10
            threshold = 90
        else:  # network
            base_value = 30
            variance = 25
            threshold = 75
        
        # Generate time series data
        data_points = []
        
        for i in range(30):
            # Add some randomness and a slight trend
            value = base_value + random.uniform(-variance, variance)
            
            # Add occasional spikes
            if random.random() < 0.1:  # 10% chance of spike
                value += variance * 1.5
            
            # Add timestamp
            timestamp = (now - timedelta(minutes=29-i)).replace(microsecond=0).isoformat()
            
            # Add data point
            data_points.append({
                "timestamp": timestamp,
                "value": max(0, min(100, value))  # Ensure value is between 0-100
            })
            
            # Check for anomalies
            if value > threshold:
                anomalies.append({
                    "metric": metric_type.capitalize(),
                    "value": value,
                    "threshold": threshold,
                    "severity": "high" if value > threshold + 10 else "medium",
                    "timestamp": timestamp
                })
        
        metrics[metric_type] = data_points
    
    return SystemMetricsResponse(
        cpu=metrics["cpu"],
        memory=metrics["memory"],
        disk=metrics["disk"],
        network=metrics["network"],
        anomalies=anomalies
    )

@router.post("/detect-anomalies", response_model=AnomalyDetectionResponse)
async def detect_anomalies(request: AnomalyDetectionRequest):
    """
    Detect anomalies in system metrics
    """
    # Get the appropriate anomaly detector
    if request.metricType == "cpu":
        detector = cpu_anomaly_detector
    elif request.metricType == "memory":
        detector = memory_anomaly_detector
    elif request.metricType == "disk":
        detector = disk_anomaly_detector
    elif request.metricType == "network":
        detector = network_anomaly_detector
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported metric type: {request.metricType}")
    
    try:
        # In a real implementation, we would:
        # 1. Fetch the actual metric data for the requested time range
        # 2. Use the detector to find anomalies
        # 3. Return the results
        
        # For now, generate mock data
        now = datetime.now()
        
        # Parse time range
        if request.timeRange == "1h":
            start_time = now - timedelta(hours=1)
            data_points = 60  # 1 per minute
        elif request.timeRange == "6h":
            start_time = now - timedelta(hours=6)
            data_points = 72  # 1 per 5 minutes
        elif request.timeRange == "24h":
            start_time = now - timedelta(hours=24)
            data_points = 96  # 1 per 15 minutes
        elif request.timeRange == "7d":
            start_time = now - timedelta(days=7)
            data_points = 168  # 1 per hour
        else:
            start_time = now - timedelta(hours=1)
            data_points = 60
        
        # Generate mock metric data
        if request.metricType == "cpu":
            base_value = 40
            variance = 20
            threshold = 80 if request.threshold is None else request.threshold
        elif request.metricType == "memory":
            base_value = 60
            variance = 15
            threshold = 85 if request.threshold is None else request.threshold
        elif request.metricType == "disk":
            base_value = 50
            variance = 10
            threshold = 90 if request.threshold is None else request.threshold
        else:  # network
            base_value = 30
            variance = 25
            threshold = 75 if request.threshold is None else request.threshold
        
        # Generate mock data
        mock_data = []
        for i in range(data_points):
            # Add some randomness and a slight trend
            value = base_value + random.uniform(-variance, variance)
            
            # Add occasional spikes
            if random.random() < 0.1:  # 10% chance of spike
                value += variance * 1.5
            
            # Calculate timestamp
            if request.timeRange == "1h":
                timestamp = start_time + timedelta(minutes=i)
            elif request.timeRange == "6h":
                timestamp = start_time + timedelta(minutes=i*5)
            elif request.timeRange == "24h":
                timestamp = start_time + timedelta(minutes=i*15)
            else:  # 7d
                timestamp = start_time + timedelta(hours=i)
            
            mock_data.append({
                "timestamp": timestamp.replace(microsecond=0).isoformat(),
                "value": max(0, min(100, value))
            })
        
        # Convert to DataFrame for the detector
        import pandas as pd
        df = pd.DataFrame(mock_data)
        
        # Detect anomalies
        # In a real implementation, we would use the detector here
        # For now, just identify values above threshold
        anomalies = []
        for point in mock_data:
            value = point["value"]
            if value > threshold:
                severity = "high" if value > threshold + 10 else "medium"
                if value > threshold + 5 or random.random() < 0.3:  # Only report some anomalies
                    anomalies.append({
                        "metric": request.metricType,
                        "value": value,
                        "threshold": threshold,
                        "severity": severity,
                        "timestamp": point["timestamp"]
                    })
        
        return AnomalyDetectionResponse(anomalies=anomalies)
    
    except Exception as e:
        # Log the error
        print(f"Error detecting anomalies: {str(e)}")
        
        # Return empty result
        return AnomalyDetectionResponse(anomalies=[])

@router.get("/anomalies", response_model=List[Dict[str, Any]])
async def get_recent_anomalies():
    """
    Get recent system metric anomalies
    """
    # Mock implementation - in a real app, this would fetch from a database
    now = datetime.now()
    
    # Randomly decide if we should generate anomalies
    if random.random() < 0.7:  # 70% chance of no anomalies
        return []
    
    # Generate 1-3 random anomalies
    num_anomalies = random.randint(1, 3)
    metrics = ["CPU Usage", "Memory Usage", "Disk I/O", "Network Traffic"]
    severities = ["low", "medium", "high"]
    
    anomalies = []
    for _ in range(num_anomalies):
        metric = random.choice(metrics)
        value = random.uniform(80, 100)
        threshold = 80 if metric in ["CPU Usage", "Memory Usage"] else 70
        severity = random.choice(severities)
        
        anomalies.append({
            "id": f"anomaly_{random.randint(1000, 9999)}",
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "severity": severity,
            "timestamp": (now - timedelta(minutes=random.randint(0, 60))).replace(microsecond=0).isoformat()
        })
    
    return anomalies
