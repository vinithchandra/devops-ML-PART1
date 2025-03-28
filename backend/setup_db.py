import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create database directory if it doesn't exist
database_dir = Path(__file__).parent / "data"
os.makedirs(database_dir, exist_ok=True)

# Database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{database_dir}/app.db"

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Import models after engine is created
from backend.database.models import Base, User, Settings, BuildPrediction, SystemMetric, Anomaly
from backend.auth.utils import get_password_hash

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_database():
    """Set up the database and create initial data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # Create admin user
            hashed_password = get_password_hash("admin123")
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hashed_password,
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print(f"Created admin user: {admin_user.username}")
        
        # Create a regular user
        regular_user = db.query(User).filter(User.username == "user").first()
        if not regular_user:
            hashed_password = get_password_hash("user123")
            regular_user = User(
                username="user",
                email="user@example.com",
                hashed_password=hashed_password,
                is_active=True,
                is_admin=False
            )
            db.add(regular_user)
            db.commit()
            print(f"Created regular user: {regular_user.username}")
        
        print("Database setup completed successfully!")
    
    except Exception as e:
        print(f"Error setting up database: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()
