from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Settings(Base):
    """Settings model for storing application settings"""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class BuildPrediction(Base):
    """Build prediction model for storing build predictions"""
    __tablename__ = "build_predictions"

    id = Column(Integer, primary_key=True, index=True)
    build_id = Column(String, unique=True, index=True)
    repository_url = Column(String)
    branch = Column(String)
    commit_hash = Column(String)
    success_probability = Column(Float)
    estimated_build_time = Column(Float)
    actual_build_time = Column(Float, nullable=True)
    status = Column(String, nullable=True)  # success, failure, in_progress
    risk_factors = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class SystemMetric(Base):
    """System metric model for storing system metrics"""
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(String, index=True)  # cpu, memory, disk, network
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.now, index=True)

class Anomaly(Base):
    """Anomaly model for storing detected anomalies"""
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(String, index=True)
    value = Column(Float)
    threshold = Column(Float)
    severity = Column(String)  # low, medium, high
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
