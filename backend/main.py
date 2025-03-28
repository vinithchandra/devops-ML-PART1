from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import uvicorn
import random
import os
from datetime import datetime, timedelta

# Import database
from .database import init_db, get_db
from sqlalchemy.orm import Session

# Import routes
from .routes import api_router
from .auth import auth_router

# Create FastAPI app
app = FastAPI(
    title="ML-Based CI/CD Quality Gate System API",
    description="API for the ML-Based CI/CD Quality Gate System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)
app.include_router(auth_router)

# Models
class BuildPredictionRequest(BaseModel):
    repositoryUrl: str
    branch: str
    commitHash: str

class BuildPredictionResponse(BaseModel):
    buildId: str
    successProbability: float
    estimatedBuildTime: float  # in seconds
    riskFactors: List[Dict[str, Any]]
    recommendations: List[str]

class SystemMetric(BaseModel):
    timestamp: datetime
    value: float

class AnomalyDetectionResponse(BaseModel):
    metric: str
    value: float
    threshold: float
    severity: str
    timestamp: datetime

class Settings(BaseModel):
    jenkinsUrl: Optional[str] = None
    jenkinsUser: Optional[str] = None
    jenkinsToken: Optional[str] = None
    modelUpdateInterval: Optional[int] = 24
    metricsCollectionInterval: Optional[int] = 5
    theme: Optional[str] = "light"
    notifications: Optional[Dict[str, bool]] = None
    refreshInterval: Optional[int] = 60
    apiEndpoints: Optional[Dict[str, str]] = None
    thresholds: Optional[Dict[str, float]] = None

# Root endpoint
@app.get("/")
async def root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ML-Based CI/CD Quality Gate System API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 {
                color: #2563eb;
                border-bottom: 2px solid #e5e7eb;
                padding-bottom: 10px;
            }
            h2 {
                color: #4b5563;
                margin-top: 30px;
            }
            .endpoint {
                background-color: #f9fafb;
                border-left: 4px solid #2563eb;
                padding: 10px 15px;
                margin: 10px 0;
                border-radius: 0 4px 4px 0;
            }
            .method {
                display: inline-block;
                padding: 3px 6px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get {
                background-color: #10b981;
                color: white;
            }
            .post {
                background-color: #3b82f6;
                color: white;
            }
            .put {
                background-color: #f59e0b;
                color: white;
            }
            .delete {
                background-color: #ef4444;
                color: white;
            }
            a {
                color: #2563eb;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>ML-Based CI/CD Quality Gate System API</h1>
        <p>Welcome to the ML-Based CI/CD Quality Gate System API. This API provides endpoints for predicting build success, monitoring system metrics, and managing CI/CD pipeline quality gates.</p>
        
        <h2>API Documentation</h2>
        <p>For detailed API documentation, visit the <a href="/docs">Swagger UI</a> or <a href="/redoc">ReDoc</a> interface.</p>
        
        <h2>Key Endpoints</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/health</code> - Health check endpoint
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/predict/build</code> - Predict build success
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/metrics/system</code> - Get system metrics
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/metrics/detect-anomalies</code> - Detect anomalies in system metrics
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/dashboard</code> - Get dashboard data
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/visualization/dashboard-summary</code> - Get visualization dashboard summary
        </div>
        
        <h2>Authentication</h2>
        <div class="endpoint">
            <span class="method post">POST</span> <code>/auth/token</code> - Get access token
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/auth/users/me</code> - Get current user
        </div>
        
        <h2>Version</h2>
        <p>API Version: 1.0.0</p>
    </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)

# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Try to make a simple database query
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }

# Build Predictions
@app.post("/api/predict/build", response_model=BuildPredictionResponse)
async def predict_build(request: BuildPredictionRequest):
    # Mock implementation - in a real app, this would use ML models
    build_id = f"build_{random.randint(1000, 9999)}"
    success_probability = random.uniform(50, 100)
    estimated_time = random.uniform(120, 600)  # 2-10 minutes
    
    # Generate risk factors based on success probability
    risk_factors = []
    if success_probability < 80:
        risk_factors.append({
            "name": "Code Complexity",
            "value": random.uniform(15, 30)
        })
    if success_probability < 70:
        risk_factors.append({
            "name": "Test Coverage",
            "value": random.uniform(50, 70)
        })
    if success_probability < 60:
        risk_factors.append({
            "name": "Integration Issues",
            "value": random.uniform(20, 40)
        })
    
    # Generate recommendations
    recommendations = []
    if "Code Complexity" in [rf["name"] for rf in risk_factors]:
        recommendations.append("Refactor complex code modules to improve maintainability")
    if "Test Coverage" in [rf["name"] for rf in risk_factors]:
        recommendations.append("Increase test coverage for critical components")
    if "Integration Issues" in [rf["name"] for rf in risk_factors]:
        recommendations.append("Review integration points and ensure proper error handling")
    
    if not recommendations:
        recommendations.append("No specific recommendations - build looks good!")
    
    return BuildPredictionResponse(
        buildId=build_id,
        successProbability=success_probability,
        estimatedBuildTime=estimated_time,
        riskFactors=risk_factors,
        recommendations=recommendations
    )

# System Metrics
@app.get("/api/metrics/system")
async def get_system_metrics():
    # Mock implementation - in a real app, this would fetch real metrics
    now = datetime.now()
    
    # Generate 30 data points for each metric (last 30 minutes)
    cpu_data = [random.uniform(10, 90) for _ in range(30)]
    memory_data = [random.uniform(20, 85) for _ in range(30)]
    disk_data = [random.uniform(30, 70) for _ in range(30)]
    network_data = [random.uniform(5, 60) for _ in range(30)]
    
    # Generate some anomalies
    anomalies = []
    if max(cpu_data) > 85:
        anomalies.append({
            "metric": "CPU Usage",
            "value": max(cpu_data),
            "threshold": 80,
            "severity": "high" if max(cpu_data) > 90 else "medium",
            "timestamp": (now - timedelta(minutes=cpu_data.index(max(cpu_data)))).isoformat()
        })
    
    if max(memory_data) > 80:
        anomalies.append({
            "metric": "Memory Usage",
            "value": max(memory_data),
            "threshold": 80,
            "severity": "high" if max(memory_data) > 90 else "medium",
            "timestamp": (now - timedelta(minutes=memory_data.index(max(memory_data)))).isoformat()
        })
    
    return {
        "cpu": cpu_data,
        "memory": memory_data,
        "disk": disk_data,
        "network": network_data,
        "anomalies": anomalies
    }

@app.post("/api/metrics/detect-anomalies")
async def detect_anomalies():
    # Mock implementation - in a real app, this would use ML models
    anomalies = []
    
    # Randomly decide if we should generate anomalies
    if random.random() < 0.7:  # 70% chance of no anomalies
        return {"anomalies": []}
    
    # Generate 1-3 random anomalies
    num_anomalies = random.randint(1, 3)
    metrics = ["CPU Usage", "Memory Usage", "Disk I/O", "Network Traffic"]
    severities = ["low", "medium", "high"]
    
    for _ in range(num_anomalies):
        metric = random.choice(metrics)
        value = random.uniform(80, 100)
        threshold = 80 if metric in ["CPU Usage", "Memory Usage"] else 70
        severity = random.choice(severities)
        
        anomalies.append({
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
    
    return {"anomalies": anomalies}

# Dashboard
@app.get("/api/dashboard")
async def get_dashboard_data():
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

# Settings
@app.get("/api/settings")
async def get_settings():
    # Mock implementation - in a real app, this would fetch from a database
    return Settings(
        jenkinsUrl="https://jenkins.example.com",
        jenkinsUser="admin",
        jenkinsToken="",
        modelUpdateInterval=24,
        metricsCollectionInterval=5,
        theme="light",
        notifications={
            "email": True,
            "slack": False,
            "inApp": True
        },
        refreshInterval=60,
        apiEndpoints={
            "backend": "http://localhost:8000",
            "mockApi": "http://localhost:3001"
        },
        thresholds={
            "buildSuccess": 80,
            "codeComplexity": 20,
            "testCoverage": 70,
            "memoryUsage": 80,
            "cpuUsage": 90
        }
    )

@app.post("/api/settings")
async def update_settings(settings: Settings):
    # Mock implementation - in a real app, this would update a database
    return {"message": "Settings updated successfully"}

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()

# Run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
