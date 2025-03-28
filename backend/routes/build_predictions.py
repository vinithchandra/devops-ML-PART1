from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import random
import json
import os
from datetime import datetime

# Import ML models
from ..ml.build_success_predictor import BuildSuccessPredictor
from ..ml.build_time_estimator import BuildTimeEstimator
from ..ml.feature_engineering import FeatureEngineering

# Create router
router = APIRouter(
    prefix="/api/build-predictions",
    tags=["build-predictions"],
    responses={404: {"description": "Not found"}},
)

# Models
class BuildPredictionRequest(BaseModel):
    repositoryUrl: str
    branch: str
    commitHash: str
    codeChanges: Optional[Dict[str, Any]] = None
    buildHistory: Optional[List[Dict[str, Any]]] = None

class BuildPredictionResponse(BaseModel):
    buildId: str
    successProbability: float
    estimatedBuildTime: float  # in seconds
    riskFactors: List[Dict[str, Any]]
    recommendations: List[str]

# Initialize models
success_predictor = BuildSuccessPredictor()
time_estimator = BuildTimeEstimator()
feature_engineering = FeatureEngineering()

# Mock data for development
def get_mock_data(repo_url: str, branch: str, commit_hash: str):
    """Generate mock data for development purposes"""
    # Mock commit data
    commit_data = {
        "hash": commit_hash,
        "message": f"Update feature for {branch}",
        "author_experience": random.randint(1, 100),
        "files_changed": random.randint(1, 20),
        "lines_added": random.randint(10, 500),
        "lines_deleted": random.randint(5, 200),
        "changed_files": [
            f"src/main/java/com/example/file{i}.java" for i in range(random.randint(1, 10))
        ],
        "branch": branch,
        "branch_age_days": random.randint(1, 30),
        "is_merge": random.random() > 0.7,
        "has_conflicts": random.random() > 0.8,
        "parents_count": 1 if random.random() > 0.7 else 2
    }
    
    # Mock build history
    build_history = []
    for i in range(10):
        build_history.append({
            "id": f"build_{random.randint(1000, 9999)}",
            "status": "success" if random.random() > 0.3 else "failure",
            "duration": f"{random.randint(1, 15)}m {random.randint(0, 59)}s",
            "timestamp": (datetime.now().replace(microsecond=0) - 
                          datetime.timedelta(days=i)).isoformat()
        })
    
    # Mock code quality data
    code_quality_data = {
        "cyclomatic_complexity": random.randint(5, 30),
        "cognitive_complexity": random.randint(10, 40),
        "test_coverage": random.uniform(50, 95),
        "test_count": random.randint(10, 200),
        "test_failures": random.randint(0, 5),
        "code_smells": random.randint(0, 30),
        "duplicated_lines": random.randint(0, 20),
        "technical_debt": random.randint(60, 480),
        "blocker_violations": random.randint(0, 3),
        "critical_violations": random.randint(0, 10),
        "major_violations": random.randint(0, 20)
    }
    
    # Mock system metrics
    system_metrics = {
        "cpu": [random.uniform(10, 90) for _ in range(30)],
        "memory": [random.uniform(20, 85) for _ in range(30)],
        "disk": [random.uniform(30, 70) for _ in range(30)],
        "network": [random.uniform(5, 60) for _ in range(30)]
    }
    
    # Mock dependencies data
    dependencies = []
    for i in range(random.randint(5, 20)):
        dependencies.append({
            "name": f"dependency-{i}",
            "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "is_outdated": random.random() > 0.7,
            "has_vulnerabilities": random.random() > 0.9,
            "version_diff": random.randint(0, 3)
        })
    
    dependencies_data = {
        "dependencies": dependencies
    }
    
    return {
        "commit_data": commit_data,
        "build_history": build_history,
        "code_quality_data": code_quality_data,
        "system_metrics": system_metrics,
        "dependencies_data": dependencies_data
    }

# Routes
@router.post("", response_model=BuildPredictionResponse)
async def predict_build(request: BuildPredictionRequest):
    """
    Predict build success probability and estimated build time
    """
    # Get mock data for development
    mock_data = get_mock_data(
        request.repositoryUrl,
        request.branch,
        request.commitHash
    )
    
    try:
        # Extract features
        features = feature_engineering.extract_all_features(
            mock_data["commit_data"],
            mock_data["build_history"],
            mock_data["code_quality_data"],
            mock_data["system_metrics"],
            mock_data["dependencies_data"]
        )
        
        # Make predictions
        success_result = success_predictor.predict(features)
        time_result = time_estimator.predict(features)
        
        # Generate risk factors
        risk_factors = success_predictor.get_risk_factors(features)
        
        # Generate recommendations
        recommendations = success_predictor.generate_recommendations(risk_factors)
        
        # Create response
        build_id = f"build_{random.randint(1000, 9999)}"
        
        return BuildPredictionResponse(
            buildId=build_id,
            successProbability=success_result["success_probability"],
            estimatedBuildTime=time_result["estimated_time"],
            riskFactors=risk_factors,
            recommendations=recommendations
        )
    except Exception as e:
        # Log the error
        print(f"Error predicting build: {str(e)}")
        
        # Return mock data for now
        success_probability = random.uniform(50, 100)
        
        # Generate risk factors based on success probability
        risk_factors = []
        if success_probability < 80:
            risk_factors.append({
                "name": "Code Complexity",
                "value": random.uniform(15, 30),
                "importance": 0.3
            })
        if success_probability < 70:
            risk_factors.append({
                "name": "Test Coverage",
                "value": random.uniform(50, 70),
                "importance": 0.25
            })
        if success_probability < 60:
            risk_factors.append({
                "name": "Integration Issues",
                "value": random.uniform(20, 40),
                "importance": 0.2
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
            buildId=f"build_{random.randint(1000, 9999)}",
            successProbability=success_probability,
            estimatedBuildTime=random.uniform(120, 600),
            riskFactors=risk_factors,
            recommendations=recommendations
        )

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_build_history():
    """
    Get build prediction history
    """
    # Mock implementation - in a real app, this would fetch from a database
    history = []
    now = datetime.now()
    
    for i in range(10):
        success_probability = random.uniform(50, 100)
        status = "success" if success_probability > 75 else "failure"
        
        history.append({
            "id": f"build_{random.randint(1000, 9999)}",
            "timestamp": (now.replace(microsecond=0) - 
                         datetime.timedelta(hours=i*2)).isoformat(),
            "repositoryUrl": "https://github.com/example/repo",
            "branch": random.choice(["main", "develop", "feature/new-ui"]),
            "commitHash": f"{random.randint(1000, 9999)}abcdef",
            "successProbability": success_probability,
            "estimatedBuildTime": random.uniform(120, 600),
            "actualBuildTime": random.uniform(100, 700) if status != "in_progress" else None,
            "status": status,
            "riskFactors": [
                {
                    "name": "Code Complexity",
                    "value": random.uniform(10, 30)
                }
            ] if success_probability < 80 else []
        })
    
    return history
