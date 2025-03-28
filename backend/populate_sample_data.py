import os
import sys
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database modules
from backend.database.models import Base, User, Settings, BuildPrediction, SystemMetric, Anomaly
from backend.database.database import engine, SessionLocal

def populate_build_predictions(db: Session, num_builds=30):
    """Populate build predictions with sample data"""
    print("Populating build predictions...")
    
    # Repository and branch data
    repositories = [
        "https://github.com/example/repo1",
        "https://github.com/example/repo2",
        "https://github.com/example/repo3"
    ]
    
    branches = ["main", "develop", "feature/new-feature"]
    
    statuses = ["success", "failure", "in_progress"]
    
    # Create sample build predictions
    for i in range(num_builds):
        build_id = f"build-{i+1}"
        
        # Check if build prediction already exists
        existing_build = db.query(BuildPrediction).filter(BuildPrediction.build_id == build_id).first()
        if existing_build:
            print(f"Build prediction already exists: {build_id}")
            continue
        
        # Create random build data
        success_probability = random.uniform(0, 100)
        estimated_build_time = random.uniform(30, 600)
        actual_build_time = estimated_build_time * random.uniform(0.8, 1.2) if random.random() > 0.2 else None
        
        # Create build prediction
        build = BuildPrediction(
            build_id=build_id,
            repository_url=random.choice(repositories),
            branch=random.choice(branches),
            commit_hash="".join(random.choices("0123456789abcdef", k=40)),
            success_probability=success_probability,
            estimated_build_time=estimated_build_time,
            actual_build_time=actual_build_time,
            status=random.choice(statuses) if actual_build_time is not None else "in_progress",
            risk_factors=[
                {"name": "Code complexity", "value": random.uniform(0, 100)},
                {"name": "Test coverage", "value": random.uniform(0, 100)},
                {"name": "Code churn", "value": random.uniform(0, 100)}
            ],
            recommendations=[
                "Improve test coverage",
                "Reduce code complexity",
                "Add more unit tests"
            ],
            created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
            updated_at=datetime.now() - timedelta(days=random.randint(0, 5))
        )
        
        db.add(build)
    
    db.commit()
    print(f"Created {num_builds} build predictions")

def populate_system_metrics(db: Session, days=30):
    """Populate system metrics with sample data"""
    print("Populating system metrics...")
    
    # Metric types
    metric_types = ["cpu", "memory", "disk", "network"]
    
    # Create metrics for the specified number of days
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # Create a data point every 30 minutes
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
            
            # Add some randomness and a daily pattern
            hour_factor = 1.0 + 0.3 * abs(12 - current_time.hour) / 12.0
            value = base_value + random.uniform(-variation, variation) * hour_factor
            
            # Add occasional spikes
            if random.random() < 0.05:
                value += random.uniform(20, 40)
            
            # Create the metric
            metric = SystemMetric(
                metric_type=metric_type,
                value=value,
                timestamp=current_time
            )
            
            db.add(metric)
        
        # Move to next time point
        current_time += timedelta(minutes=30)
    
    db.commit()
    print(f"Created system metrics from {start_time} to {end_time}")

def populate_anomalies(db: Session, num_anomalies=20):
    """Populate anomalies with sample data"""
    print("Populating anomalies...")
    
    # Metric types and severities
    metric_types = ["cpu", "memory", "disk", "network"]
    severities = ["low", "medium", "high"]
    
    # Create sample anomalies
    for i in range(num_anomalies):
        metric_type = random.choice(metric_types)
        
        # Create timestamp within the last 30 days
        timestamp = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # Determine if resolved
        is_resolved = random.random() > 0.3
        resolved_at = timestamp + timedelta(hours=random.randint(1, 24)) if is_resolved else None
        
        # Create anomaly
        anomaly = Anomaly(
            metric_type=metric_type,
            value=random.uniform(80, 100),
            threshold=80.0,
            severity=random.choice(severities),
            is_resolved=is_resolved,
            resolved_at=resolved_at,
            timestamp=timestamp
        )
        
        db.add(anomaly)
    
    db.commit()
    print(f"Created {num_anomalies} anomalies")

def main():
    """Main function to populate the database with sample data"""
    print("Populating database with sample data...")
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Populate build predictions
        populate_build_predictions(db, num_builds=50)
        
        # Populate system metrics
        populate_system_metrics(db, days=30)
        
        # Populate anomalies
        populate_anomalies(db, num_anomalies=30)
        
        print("Database population completed successfully!")
    
    except Exception as e:
        print(f"Error populating database: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
