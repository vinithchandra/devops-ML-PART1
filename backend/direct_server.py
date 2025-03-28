import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import random
import json

# Create FastAPI app
app = FastAPI(
    title="ML-Based CI/CD Quality Gate System API",
    description="API for the ML-Based CI/CD Quality Gate System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    modelUpdateInterval: Optional[int] = 24
    metricsCollectionInterval: Optional[int] = 5
    theme: Optional[str] = "light"
    notifications: Optional[Dict[str, bool]] = None

@app.get("/", response_class=HTMLResponse)
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
            <span class="method post">POST</span> <code>/api/metrics/detect-anomalies</code> - Detect anomalies
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/dashboard</code> - Get dashboard data
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/settings</code> - Get settings
        </div>
        
        <h2>Version</h2>
        <p>API Version: 1.0.0</p>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

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

@app.get("/api/dashboard")
async def get_dashboard_data():
    # Mock implementation - in a real app, this would fetch data from database
    
    # Generate build predictions
    build_predictions = []
    for i in range(10):
        status = random.choice(["success", "failure", "in_progress"])
        build_predictions.append({
            "buildId": f"build_{random.randint(1000, 9999)}",
            "repositoryUrl": "https://github.com/example/repo",
            "branch": random.choice(["main", "develop", "feature/new-feature"]),
            "commitHash": "".join(random.choices("0123456789abcdef", k=40)),
            "successProbability": random.uniform(0, 100),
            "estimatedBuildTime": random.uniform(30, 600),
            "actualBuildTime": random.uniform(30, 600) if status != "in_progress" else None,
            "status": status,
            "createdAt": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "updatedAt": datetime.now().isoformat()
        })
    
    # Generate system metrics
    system_metrics = {
        "cpu": [random.uniform(10, 90) for _ in range(30)],
        "memory": [random.uniform(20, 85) for _ in range(30)],
        "disk": [random.uniform(30, 70) for _ in range(30)],
        "network": [random.uniform(5, 60) for _ in range(30)]
    }
    
    # Generate anomalies
    anomalies = []
    for i in range(random.randint(0, 5)):
        metric_type = random.choice(["cpu", "memory", "disk", "network"])
        anomalies.append({
            "id": i + 1,
            "metricType": metric_type,
            "value": random.uniform(80, 100),
            "threshold": 80,
            "severity": random.choice(["low", "medium", "high"]),
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "isResolved": random.choice([True, False])
        })
    
    # Generate summary stats
    summary = {
        "totalBuilds": len(build_predictions),
        "successfulBuilds": len([b for b in build_predictions if b["status"] == "success"]),
        "failedBuilds": len([b for b in build_predictions if b["status"] == "failure"]),
        "inProgressBuilds": len([b for b in build_predictions if b["status"] == "in_progress"]),
        "averageBuildTime": sum([b["actualBuildTime"] for b in build_predictions if b["actualBuildTime"] is not None]) / len([b for b in build_predictions if b["actualBuildTime"] is not None]) if len([b for b in build_predictions if b["actualBuildTime"] is not None]) > 0 else 0,
        "totalAnomalies": len(anomalies),
        "unresolvedAnomalies": len([a for a in anomalies if not a["isResolved"]])
    }
    
    return {
        "buildPredictions": build_predictions,
        "systemMetrics": system_metrics,
        "anomalies": anomalies,
        "summary": summary
    }

@app.get("/api/settings")
async def get_settings():
    # Mock implementation - in a real app, this would fetch from database
    return {
        "jenkinsUrl": "https://jenkins.example.com",
        "modelUpdateInterval": 24,
        "metricsCollectionInterval": 5,
        "theme": "light",
        "notifications": {
            "email": True,
            "slack": False,
            "inApp": True
        },
        "thresholds": {
            "cpu": 80,
            "memory": 80,
            "disk": 90,
            "network": 70
        }
    }

@app.put("/api/settings")
async def update_settings(settings: Settings):
    # Mock implementation - in a real app, this would update database
    return settings

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9001)
