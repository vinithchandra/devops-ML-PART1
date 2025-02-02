"""
Configuration settings for the ML-based CI/CD quality gate system.
"""
from typing import Dict, Any
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
MODEL_DIR = BASE_DIR / 'models'
LOG_DIR = BASE_DIR / 'logs'

# Create directories if they don't exist
for directory in [DATA_DIR, MODEL_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# Jenkins configuration
JENKINS_CONFIG = {
    'url': os.getenv('JENKINS_URL', 'http://localhost:8080'),
    'username': os.getenv('JENKINS_USER', ''),
    'password': os.getenv('JENKINS_TOKEN', '')
}

# ML model configuration
MODEL_CONFIG = {
    'build_predictor': {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    },
    'time_estimator': {
        'n_estimators': 100,
        'max_depth': 5,
        'random_state': 42
    },
    'anomaly_detector': {
        'threshold': 2.0
    }
}

# Feature engineering configuration
FEATURE_CONFIG = {
    'git': {
        'max_commits': 100,
        'file_types': {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'cpp': ['.cpp', '.hpp', '.cc', '.h'],
            'config': ['.yml', '.yaml', '.json', '.xml'],
            'docs': ['.md', '.rst', '.txt']
        }
    },
    'system': {
        'metrics_window': 3600,  # 1 hour in seconds
        'collection_interval': 60  # 1 minute in seconds
    }
}

# API configuration
API_CONFIG = {
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', '8000')),
    'debug': os.getenv('DEBUG', 'False').lower() == 'true'
}

# Logging configuration
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '{time} | {level} | {message}',
    'rotation': '1 day',
    'retention': '1 month'
}

def get_config() -> Dict[str, Any]:
    """Get the complete configuration dictionary."""
    return {
        'base_dir': str(BASE_DIR),
        'data_dir': str(DATA_DIR),
        'model_dir': str(MODEL_DIR),
        'log_dir': str(LOG_DIR),
        'jenkins': JENKINS_CONFIG,
        'model': MODEL_CONFIG,
        'feature': FEATURE_CONFIG,
        'api': API_CONFIG,
        'logging': LOGGING_CONFIG
    }
