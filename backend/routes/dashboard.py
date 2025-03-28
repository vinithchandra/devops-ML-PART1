from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import random
from datetime import datetime, timedelta

# Create router
router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)

# Routes
@router.get("")
async def get_dashboard_data():
    """
    Get dashboard data including build history, performance trends, and recent anomalies
    """
    # Mock implementation - in a real app, this would fetch real data
    now = datetime.now()
    
    # Generate build history
    build_statuses = ["success", "failure", "in_progress"]
    build_history = []
    
    for i in range(10):
        status = random.choices(
            build_statuses, 
            weights=[0.7, 0.2, 0.1], 
            k=1
        )[0]
        
        duration = f"{random.randint(1, 15)}m {random.randint(0, 59)}s"
        
        build_history.append({
            "id": f"build_{random.randint(1000, 9999)}",
            "name": f"Build #{random.randint(100, 999)}",
            "status": status,
            "branch": random.choice(["main", "develop", "feature/new-ui"]),
            "duration": duration,
            "timestamp": (now - timedelta(hours=i*2 + random.randint(0, 3))).isoformat()
        })
    
    # Generate recent anomalies
    anomaly_severities = ["warning", "critical"]
    recent_anomalies = []
    
    # 50% chance of having anomalies
    if random.random() < 0.5:
        num_anomalies = random.randint(1, 3)
        for i in range(num_anomalies):
            severity = random.choice(anomaly_severities)
            metric = random.choice(["CPU", "Memory", "Disk", "Network"])
            value = random.uniform(80, 95)
            
            recent_anomalies.append({
                "id": f"anomaly_{random.randint(1000, 9999)}",
                "severity": severity,
                "message": f"Unusual {metric} usage detected: {value:.1f}%",
                "timestamp": (now - timedelta(hours=random.randint(0, 24))).isoformat()
            })
    
    # Generate performance trends
    dates = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    dates.reverse()  # Oldest first
    
    success_rates = []
    build_durations = []
    
    # Start with a base success rate and duration
    base_success_rate = random.uniform(70, 90)
    base_duration = random.uniform(5, 10)
    
    # Generate slightly varying data for each day
    for _ in dates:
        success_rates.append(min(100, max(0, base_success_rate + random.uniform(-5, 5))))
        build_durations.append(max(1, base_duration + random.uniform(-1, 1)))
    
    # Current metrics
    current_success_rate = success_rates[-1]
    success_rate_trend = success_rates[-1] - success_rates[-2] if len(success_rates) > 1 else 0
    
    return {
        "buildHistory": build_history,
        "recentAnomalies": recent_anomalies,
        "performanceTrends": {
            "dates": dates,
            "successRates": success_rates,
            "buildDurations": build_durations,
            "currentSuccessRate": round(current_success_rate, 1),
            "successRateTrend": round(success_rate_trend, 1),
            "averageDuration": round(sum(build_durations) / len(build_durations), 1),
            "totalBuilds": random.randint(10, 30),
            "activeBuilds": random.randint(0, 3)
        }
    }

@router.get("/summary")
async def get_dashboard_summary():
    """
    Get a summary of key metrics for the dashboard
    """
    return {
        "buildSuccessRate": random.uniform(70, 95),
        "averageBuildTime": random.uniform(3, 10),
        "totalBuilds": random.randint(100, 500),
        "activeBuilds": random.randint(0, 5),
        "pendingBuilds": random.randint(0, 10),
        "failedBuilds": random.randint(5, 20),
        "systemHealth": random.choice(["healthy", "warning", "critical"]),
        "lastUpdated": datetime.now().isoformat()
    }

@router.get("/recent-builds")
async def get_recent_builds():
    """
    Get recent builds for the dashboard
    """
    now = datetime.now()
    build_statuses = ["success", "failure", "in_progress"]
    builds = []
    
    for i in range(5):
        status = random.choices(
            build_statuses, 
            weights=[0.7, 0.2, 0.1], 
            k=1
        )[0]
        
        duration = f"{random.randint(1, 15)}m {random.randint(0, 59)}s"
        
        builds.append({
            "id": f"build_{random.randint(1000, 9999)}",
            "name": f"Build #{random.randint(100, 999)}",
            "status": status,
            "branch": random.choice(["main", "develop", "feature/new-ui"]),
            "duration": duration,
            "timestamp": (now - timedelta(hours=i*2 + random.randint(0, 3))).isoformat()
        })
    
    return builds
