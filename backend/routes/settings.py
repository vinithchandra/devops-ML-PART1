from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime

# Create router
router = APIRouter(
    prefix="/api/settings",
    tags=["settings"],
    responses={404: {"description": "Not found"}},
)

# Models
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

# Mock settings storage
# In a real app, this would be stored in a database
DEFAULT_SETTINGS = {
    "jenkinsUrl": "https://jenkins.example.com",
    "jenkinsUser": "admin",
    "jenkinsToken": "",
    "modelUpdateInterval": 24,
    "metricsCollectionInterval": 5,
    "theme": "light",
    "notifications": {
        "email": True,
        "slack": False,
        "inApp": True
    },
    "refreshInterval": 60,
    "apiEndpoints": {
        "backend": "http://localhost:8000",
        "mockApi": "http://localhost:3001"
    },
    "thresholds": {
        "buildSuccess": 80,
        "codeComplexity": 20,
        "testCoverage": 70,
        "memoryUsage": 80,
        "cpuUsage": 90
    }
}

# In-memory settings storage
current_settings = DEFAULT_SETTINGS.copy()

# Routes
@router.get("")
async def get_settings():
    """
    Get current settings
    """
    return current_settings

@router.post("")
async def update_settings(settings: Settings):
    """
    Update settings
    """
    global current_settings
    
    # Update only the provided settings
    settings_dict = settings.dict(exclude_unset=True)
    
    for key, value in settings_dict.items():
        if value is not None:
            if isinstance(value, dict) and key in current_settings and isinstance(current_settings[key], dict):
                # Merge dictionaries for nested settings
                current_settings[key].update(value)
            else:
                # Replace value for non-nested settings
                current_settings[key] = value
    
    # In a real app, we would save to a database here
    
    return {
        "message": "Settings updated successfully",
        "settings": current_settings
    }

@router.post("/reset")
async def reset_settings():
    """
    Reset settings to defaults
    """
    global current_settings
    current_settings = DEFAULT_SETTINGS.copy()
    
    return {
        "message": "Settings reset to defaults",
        "settings": current_settings
    }

@router.get("/jenkins-connection")
async def test_jenkins_connection():
    """
    Test Jenkins connection
    """
    # In a real app, we would actually test the connection
    # For now, just return success/failure randomly
    import random
    
    success = random.random() > 0.2  # 80% chance of success
    
    if success:
        return {
            "status": "success",
            "message": "Successfully connected to Jenkins"
        }
    else:
        return {
            "status": "error",
            "message": "Failed to connect to Jenkins. Please check your credentials."
        }

@router.post("/notification-test")
async def send_test_notification():
    """
    Send a test notification
    """
    # In a real app, we would actually send a notification
    # For now, just return success
    return {
        "status": "success",
        "message": "Test notification sent successfully"
    }
