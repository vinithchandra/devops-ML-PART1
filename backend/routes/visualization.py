from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from ..database import get_db, crud
from ..visualization import (
    generate_build_success_chart,
    generate_build_time_chart,
    generate_system_metrics_chart,
    generate_anomaly_chart,
    generate_feature_importance_chart,
    generate_dashboard_summary_charts
)

# Create router
router = APIRouter(
    prefix="/api/visualization",
    tags=["visualization"],
    responses={404: {"description": "Not found"}},
)

@router.get("/build-success-chart")
async def get_build_success_chart(db: Session = Depends(get_db)):
    """
    Get build success rate chart
    """
    # Get build data from database
    build_data = crud.get_build_predictions(db, limit=100)
    
    # Convert SQLAlchemy objects to dictionaries
    build_data_dict = []
    for build in build_data:
        build_dict = {
            "build_id": build.build_id,
            "status": build.status,
            "created_at": build.created_at.isoformat()
        }
        build_data_dict.append(build_dict)
    
    # Generate chart
    chart_data = generate_build_success_chart(build_data_dict)
    
    return {
        "chart": chart_data,
        "chartType": "image",
        "title": "Build Success Rate Over Time"
    }

@router.get("/build-time-chart")
async def get_build_time_chart(db: Session = Depends(get_db)):
    """
    Get build time chart
    """
    # Get build data from database
    build_data = crud.get_build_predictions(db, limit=100)
    
    # Convert SQLAlchemy objects to dictionaries
    build_data_dict = []
    for build in build_data:
        if build.actual_build_time is not None:
            build_dict = {
                "build_id": build.build_id,
                "estimated_build_time": build.estimated_build_time,
                "actual_build_time": build.actual_build_time
            }
            build_data_dict.append(build_dict)
    
    # Generate chart
    chart_data = generate_build_time_chart(build_data_dict)
    
    return {
        "chart": chart_data,
        "chartType": "image",
        "title": "Estimated vs Actual Build Time"
    }

@router.get("/system-metrics-chart")
async def get_system_metrics_chart(
    metric_types: Optional[str] = None,
    days: int = 1,
    db: Session = Depends(get_db)
):
    """
    Get system metrics chart
    """
    # Parse metric types
    if metric_types:
        metric_type_list = metric_types.split(',')
    else:
        metric_type_list = ["cpu", "memory", "disk", "network"]
    
    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # Get metrics data from database
    metrics_data = {}
    for metric_type in metric_type_list:
        metrics = crud.get_system_metrics(db, metric_type, start_time, end_time)
        
        # Convert SQLAlchemy objects to dictionaries
        metrics_dict = []
        for metric in metrics:
            metric_dict = {
                "value": metric.value,
                "timestamp": metric.timestamp.isoformat()
            }
            metrics_dict.append(metric_dict)
        
        metrics_data[metric_type] = metrics_dict
    
    # Generate chart
    chart_data = generate_system_metrics_chart(metrics_data)
    
    return {
        "chart": chart_data,
        "chartType": "image",
        "title": "System Metrics Over Time"
    }

@router.get("/anomalies-chart")
async def get_anomalies_chart(db: Session = Depends(get_db)):
    """
    Get anomalies chart
    """
    # Get anomalies data from database
    anomalies = crud.get_anomalies(db, limit=100)
    
    # Convert SQLAlchemy objects to dictionaries
    anomalies_dict = []
    for anomaly in anomalies:
        anomaly_dict = {
            "metric_type": anomaly.metric_type,
            "value": anomaly.value,
            "severity": anomaly.severity,
            "timestamp": anomaly.timestamp.isoformat()
        }
        anomalies_dict.append(anomaly_dict)
    
    # Generate chart
    chart_data = generate_anomaly_chart(anomalies_dict)
    
    return {
        "chart": chart_data,
        "chartType": "image",
        "title": "Anomalies by Metric Type and Severity"
    }

@router.get("/feature-importance-chart")
async def get_feature_importance_chart():
    """
    Get feature importance chart
    """
    # Mock feature importance data
    # In a real app, this would come from the ML model
    feature_importance = {
        "Code Complexity": 0.25,
        "Test Coverage": 0.20,
        "Code Churn": 0.18,
        "Previous Build Status": 0.15,
        "Commit Size": 0.12,
        "Time Since Last Build": 0.10
    }
    
    # Generate chart
    chart_data = generate_feature_importance_chart(feature_importance)
    
    return {
        "chart": chart_data,
        "chartType": "image",
        "title": "Feature Importance for Build Success Prediction"
    }

@router.get("/dashboard-summary")
async def get_dashboard_summary_charts(db: Session = Depends(get_db)):
    """
    Get all dashboard summary charts
    """
    # Get build data
    build_data = crud.get_build_predictions(db, limit=100)
    build_data_dict = []
    for build in build_data:
        build_dict = {
            "build_id": build.build_id,
            "status": build.status,
            "created_at": build.created_at.isoformat(),
            "estimated_build_time": build.estimated_build_time,
            "actual_build_time": build.actual_build_time
        }
        build_data_dict.append(build_dict)
    
    # Get metrics data
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    metrics_data = {}
    for metric_type in ["cpu", "memory", "disk", "network"]:
        metrics = crud.get_system_metrics(db, metric_type, start_time, end_time)
        metrics_dict = []
        for metric in metrics:
            metric_dict = {
                "value": metric.value,
                "timestamp": metric.timestamp.isoformat()
            }
            metrics_dict.append(metric_dict)
        metrics_data[metric_type] = metrics_dict
    
    # Get anomalies data
    anomalies = crud.get_anomalies(db, limit=100)
    anomalies_dict = []
    for anomaly in anomalies:
        anomaly_dict = {
            "metric_type": anomaly.metric_type,
            "value": anomaly.value,
            "severity": anomaly.severity,
            "timestamp": anomaly.timestamp.isoformat()
        }
        anomalies_dict.append(anomaly_dict)
    
    # Generate charts
    charts = generate_dashboard_summary_charts(build_data_dict, metrics_data, anomalies_dict)
    
    # Add chart type and titles
    result = {}
    chart_titles = {
        "build_success": "Build Success Rate Over Time",
        "build_time": "Estimated vs Actual Build Time",
        "system_metrics": "System Metrics Over Time",
        "anomalies": "Anomalies by Metric Type and Severity"
    }
    
    for chart_name, chart_data in charts.items():
        result[chart_name] = {
            "chart": chart_data,
            "chartType": "image",
            "title": chart_titles.get(chart_name, chart_name.replace("_", " ").title())
        }
    
    return result
