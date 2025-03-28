# ML-Based CI/CD Quality Gate System Backend

This is the backend API for the ML-Based CI/CD Quality Gate System, built with FastAPI, SQLAlchemy, and ML models for build prediction and anomaly detection.

## Features

- **Build Prediction API**: Predict build success probability and estimated build time
- **System Metrics API**: Monitor system metrics and detect anomalies
- **Dashboard API**: Retrieve dashboard data for visualization
- **Settings API**: Configure system settings
- **Authentication API**: User authentication and authorization

## Project Structure

```
backend/
├── auth/                  # Authentication module
│   ├── __init__.py
│   ├── routes.py          # Authentication routes
│   └── utils.py           # Authentication utilities
├── database/              # Database module
│   ├── __init__.py
│   ├── crud.py            # CRUD operations
│   ├── database.py        # Database connection
│   └── models.py          # SQLAlchemy models
├── ml/                    # Machine Learning module
│   ├── __init__.py
│   ├── anomaly_detector.py
│   ├── base_model.py
│   ├── build_success_predictor.py
│   ├── build_time_estimator.py
│   └── feature_engineering.py
├── routes/                # API routes
│   ├── __init__.py
│   ├── build_predictions.py
│   ├── dashboard.py
│   ├── settings.py
│   └── system_metrics.py
├── data/                  # Database and model storage (created at runtime)
├── init_data.py           # Initialize database with sample data
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
└── run.py                 # Run script
```

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository
2. Navigate to the project directory
3. Install the dependencies:

```bash
pip install -r backend/requirements.txt
```

### Running the Backend

1. Initialize the database with sample data:

```bash
python -m backend.init_data
```

2. Start the FastAPI server:

```bash
python -m backend.run
```

The API will be available at http://localhost:8000

### API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/auth/token` - Get access token
- `POST /api/auth/register` - Register a new user
- `GET /api/auth/users/me` - Get current user
- `GET /api/auth/users` - Get all users (admin only)

### Build Predictions

- `GET /api/build-predictions` - Get build predictions
- `POST /api/build-predictions/predict` - Predict build success
- `GET /api/build-predictions/history` - Get build history

### System Metrics

- `GET /api/system-metrics` - Get system metrics
- `GET /api/system-metrics/anomalies` - Get system anomalies
- `POST /api/system-metrics/analyze` - Analyze system metrics

### Dashboard

- `GET /api/dashboard` - Get dashboard data
- `GET /api/dashboard/summary` - Get dashboard summary
- `GET /api/dashboard/recent-builds` - Get recent builds

### Settings

- `GET /api/settings` - Get settings
- `POST /api/settings` - Update settings
- `POST /api/settings/reset` - Reset settings to defaults
- `GET /api/settings/jenkins-connection` - Test Jenkins connection
- `POST /api/settings/notification-test` - Send test notification

## Default Users

The system comes with two default users:

1. Admin User:
   - Username: `admin`
   - Password: `admin123`
   - Role: Administrator

2. Regular User:
   - Username: `user`
   - Password: `user123`
   - Role: User

## Environment Variables

The following environment variables can be set to configure the application:

- `PORT` - Port to run the server on (default: 8000)
- `SECRET_KEY` - Secret key for JWT token generation
- `DATABASE_URL` - Database URL (default: SQLite database in the data directory)

## License

This project is licensed under the MIT License.
