from sqlalchemy.orm import Session
from sqlalchemy import desc
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from . import models

# Settings CRUD operations
def get_setting(db: Session, key: str):
    """Get a setting by key"""
    return db.query(models.Settings).filter(models.Settings.key == key).first()

def get_settings(db: Session, skip: int = 0, limit: int = 100):
    """Get all settings"""
    return db.query(models.Settings).offset(skip).limit(limit).all()

def create_setting(db: Session, key: str, value: Any):
    """Create a new setting"""
    # Convert value to JSON string if it's a dict or list
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    
    db_setting = models.Settings(key=key, value=str(value))
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting

def update_setting(db: Session, key: str, value: Any):
    """Update an existing setting"""
    db_setting = get_setting(db, key)
    
    # Convert value to JSON string if it's a dict or list
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    
    if db_setting:
        db_setting.value = str(value)
        db_setting.updated_at = datetime.now()
        db.commit()
        db.refresh(db_setting)
        return db_setting
    
    # Create if it doesn't exist
    return create_setting(db, key, value)

def delete_setting(db: Session, key: str):
    """Delete a setting"""
    db_setting = get_setting(db, key)
    if db_setting:
        db.delete(db_setting)
        db.commit()
        return True
    return False

# Build Prediction CRUD operations
def get_build_prediction(db: Session, build_id: str):
    """Get a build prediction by build_id"""
    return db.query(models.BuildPrediction).filter(models.BuildPrediction.build_id == build_id).first()

def get_build_predictions(db: Session, skip: int = 0, limit: int = 100):
    """Get all build predictions, ordered by creation date (newest first)"""
    return db.query(models.BuildPrediction).order_by(desc(models.BuildPrediction.created_at)).offset(skip).limit(limit).all()

def create_build_prediction(db: Session, build_data: Dict[str, Any]):
    """Create a new build prediction"""
    # Convert risk_factors and recommendations to JSON
    if "risk_factors" in build_data and isinstance(build_data["risk_factors"], list):
        build_data["risk_factors"] = build_data["risk_factors"]
    
    if "recommendations" in build_data and isinstance(build_data["recommendations"], list):
        build_data["recommendations"] = build_data["recommendations"]
    
    # Map dict keys to model field names
    field_mapping = {
        "buildId": "build_id",
        "repositoryUrl": "repository_url",
        "commitHash": "commit_hash",
        "successProbability": "success_probability",
        "estimatedBuildTime": "estimated_build_time",
        "actualBuildTime": "actual_build_time",
        "riskFactors": "risk_factors",
        "recommendations": "recommendations"
    }
    
    # Create model data
    model_data = {}
    for key, value in build_data.items():
        model_key = field_mapping.get(key, key)
        model_data[model_key] = value
    
    db_prediction = models.BuildPrediction(**model_data)
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def update_build_prediction(db: Session, build_id: str, build_data: Dict[str, Any]):
    """Update an existing build prediction"""
    db_prediction = get_build_prediction(db, build_id)
    
    if db_prediction:
        # Map dict keys to model field names
        field_mapping = {
            "repositoryUrl": "repository_url",
            "commitHash": "commit_hash",
            "successProbability": "success_probability",
            "estimatedBuildTime": "estimated_build_time",
            "actualBuildTime": "actual_build_time",
            "status": "status",
            "riskFactors": "risk_factors",
            "recommendations": "recommendations"
        }
        
        # Update fields
        for key, value in build_data.items():
            model_key = field_mapping.get(key, key)
            if hasattr(db_prediction, model_key):
                setattr(db_prediction, model_key, value)
        
        db_prediction.updated_at = datetime.now()
        db.commit()
        db.refresh(db_prediction)
        return db_prediction
    
    return None

def delete_build_prediction(db: Session, build_id: str):
    """Delete a build prediction"""
    db_prediction = get_build_prediction(db, build_id)
    if db_prediction:
        db.delete(db_prediction)
        db.commit()
        return True
    return False

# System Metric CRUD operations
def create_system_metric(db: Session, metric_type: str, value: float, timestamp: Optional[datetime] = None):
    """Create a new system metric"""
    if timestamp is None:
        timestamp = datetime.now()
    
    db_metric = models.SystemMetric(
        metric_type=metric_type,
        value=value,
        timestamp=timestamp
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

def get_system_metrics(db: Session, metric_type: str, start_time: datetime, end_time: datetime):
    """Get system metrics for a specific type and time range"""
    return db.query(models.SystemMetric).filter(
        models.SystemMetric.metric_type == metric_type,
        models.SystemMetric.timestamp >= start_time,
        models.SystemMetric.timestamp <= end_time
    ).order_by(models.SystemMetric.timestamp).all()

def get_latest_system_metrics(db: Session, metric_type: str, limit: int = 30):
    """Get the latest system metrics for a specific type"""
    return db.query(models.SystemMetric).filter(
        models.SystemMetric.metric_type == metric_type
    ).order_by(desc(models.SystemMetric.timestamp)).limit(limit).all()

# Anomaly CRUD operations
def create_anomaly(db: Session, anomaly_data: Dict[str, Any]):
    """Create a new anomaly"""
    # Map dict keys to model field names
    field_mapping = {
        "metricType": "metric_type",
        "isResolved": "is_resolved",
        "resolvedAt": "resolved_at"
    }
    
    # Create model data
    model_data = {}
    for key, value in anomaly_data.items():
        model_key = field_mapping.get(key, key)
        model_data[model_key] = value
    
    db_anomaly = models.Anomaly(**model_data)
    db.add(db_anomaly)
    db.commit()
    db.refresh(db_anomaly)
    return db_anomaly

def get_anomalies(db: Session, skip: int = 0, limit: int = 100, include_resolved: bool = False):
    """Get all anomalies, ordered by timestamp (newest first)"""
    query = db.query(models.Anomaly)
    
    if not include_resolved:
        query = query.filter(models.Anomaly.is_resolved == False)
    
    return query.order_by(desc(models.Anomaly.timestamp)).offset(skip).limit(limit).all()

def get_anomalies_by_metric(db: Session, metric_type: str, skip: int = 0, limit: int = 100):
    """Get anomalies for a specific metric type"""
    return db.query(models.Anomaly).filter(
        models.Anomaly.metric_type == metric_type,
        models.Anomaly.is_resolved == False
    ).order_by(desc(models.Anomaly.timestamp)).offset(skip).limit(limit).all()

def resolve_anomaly(db: Session, anomaly_id: int):
    """Mark an anomaly as resolved"""
    db_anomaly = db.query(models.Anomaly).filter(models.Anomaly.id == anomaly_id).first()
    
    if db_anomaly:
        db_anomaly.is_resolved = True
        db_anomaly.resolved_at = datetime.now()
        db.commit()
        db.refresh(db_anomaly)
        return db_anomaly
    
    return None

# User CRUD operations
def get_user(db: Session, user_id: int):
    """Get a user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """Get a user by username"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Get a user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get all users"""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, username: str, email: str, hashed_password: str, is_admin: bool = False):
    """Create a new user"""
    db_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_data: Dict[str, Any]):
    """Update an existing user"""
    db_user = get_user(db, user_id)
    
    if db_user:
        for key, value in user_data.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
        
        db_user.updated_at = datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    
    return None

def delete_user(db: Session, user_id: int):
    """Delete a user"""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
