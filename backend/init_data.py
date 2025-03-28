import os
import sys
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database and auth modules
from backend.database import init_db, SessionLocal, crud, Base, engine
from backend.auth.utils import get_password_hash

def init_users(db: Session):
    """Initialize users"""
    # Check if admin user exists
    admin_user = crud.get_user_by_username(db, "admin")
    if not admin_user:
        # Create admin user
        hashed_password = get_password_hash("admin123")
        admin_user = crud.create_user(
            db=db,
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            is_admin=True
        )
        print(f"Created admin user: {admin_user.username}")
    
    # Create a regular user
    regular_user = crud.get_user_by_username(db, "user")
    if not regular_user:
        hashed_password = get_password_hash("user123")
        regular_user = crud.create_user(
            db=db,
            username="user",
            email="user@example.com",
            hashed_password=hashed_password,
            is_admin=False
        )
        print(f"Created regular user: {regular_user.username}")

def init_settings(db: Session):
    """Initialize settings"""
    # Default settings
    default_settings = {
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
    
    # Create or update settings
    for key, value in default_settings.items():
        setting = crud.get_setting(db, key)
        if not setting:
            crud.create_setting(db, key, value)
            print(f"Created setting: {key}")
        else:
            print(f"Setting already exists: {key}")

def init_build_predictions(db: Session):
    """Initialize build predictions"""
    # Create sample build predictions
    repositories = [
        "https://github.com/example/repo1",
        "https://github.com/example/repo2",
        "https://github.com/example/repo3"
    ]
    
    branches = ["main", "develop", "feature/new-feature"]
    
    statuses = ["success", "failure", "in_progress"]
    
    # Create 10 sample build predictions
    for i in range(10):
        build_id = f"build-{i+1}"
        
        # Check if build prediction already exists
        existing_build = crud.get_build_prediction(db, build_id)
        if existing_build:
            print(f"Build prediction already exists: {build_id}")
            continue
        
        # Create random build prediction
        success_probability = random.uniform(0, 100)
        estimated_build_time = random.uniform(30, 600)
        actual_build_time = estimated_build_time * random.uniform(0.8, 1.2) if random.random() > 0.3 else None
        
        build_data = {
            "build_id": build_id,
            "repository_url": random.choice(repositories),
            "branch": random.choice(branches),
            "commit_hash": "".join(random.choices("0123456789abcdef", k=40)),
            "success_probability": success_probability,
            "estimated_build_time": estimated_build_time,
            "actual_build_time": actual_build_time,
            "status": random.choice(statuses) if actual_build_time is not None else "in_progress",
            "risk_factors": [
                {"name": "Code complexity", "value": random.uniform(0, 100)},
                {"name": "Test coverage", "value": random.uniform(0, 100)},
                {"name": "Code churn", "value": random.uniform(0, 100)}
            ],
            "recommendations": [
                "Improve test coverage",
                "Reduce code complexity",
                "Add more unit tests"
            ]
        }
        
        crud.create_build_prediction(db, build_data)
        print(f"Created build prediction: {build_id}")

def init_system_metrics(db: Session):
    """Initialize system metrics"""
    # Create sample system metrics
    metric_types = ["cpu", "memory", "disk", "network"]
    
    # Create metrics for the last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    # Create a data point every 5 minutes
    current_time = start_time
    while current_time <= end_time:
        for metric_type in metric_types:
            # Base value for each metric type
            if metric_type == "cpu":
                base_value = 30
                variation = 20
            elif metric_type == "memory":
                base_value = 50
                variation = 15
            elif metric_type == "disk":
                base_value = 60
                variation = 10
            else:  # network
                base_value = 40
                variation = 30
            
            # Add some randomness
            value = base_value + random.uniform(-variation, variation)
            
            # Create the metric
            crud.create_system_metric(db, metric_type, value, current_time)
        
        # Move to next time point
        current_time += timedelta(minutes=5)
    
    print(f"Created system metrics from {start_time} to {end_time}")

def init_anomalies(db: Session):
    """Initialize anomalies"""
    # Create sample anomalies
    metric_types = ["cpu", "memory", "disk", "network"]
    severities = ["low", "medium", "high"]
    
    # Create 5 sample anomalies
    for i in range(5):
        metric_type = random.choice(metric_types)
        
        # Create anomaly data
        anomaly_data = {
            "metric_type": metric_type,
            "value": random.uniform(80, 100),
            "threshold": 80.0,
            "severity": random.choice(severities),
            "is_resolved": random.random() > 0.7,
            "timestamp": datetime.now() - timedelta(hours=random.randint(0, 24))
        }
        
        # Add resolved_at if resolved
        if anomaly_data["is_resolved"]:
            anomaly_data["resolved_at"] = anomaly_data["timestamp"] + timedelta(minutes=random.randint(5, 60))
        
        crud.create_anomaly(db, anomaly_data)
    
    print(f"Created 5 sample anomalies")

def main():
    """Main function to initialize the database with sample data"""
    print("Initializing database...")
    
    # Create database tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Initialize users
        print("Initializing users...")
        init_users(db)
        
        # Initialize settings
        print("Initializing settings...")
        init_settings(db)
        
        # Initialize build predictions
        print("Initializing build predictions...")
        init_build_predictions(db)
        
        # Initialize system metrics
        print("Initializing system metrics...")
        init_system_metrics(db)
        
        # Initialize anomalies
        print("Initializing anomalies...")
        init_anomalies(db)
        
        print("Database initialization completed successfully!")
    
    except Exception as e:
        print(f"Error initializing database: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
