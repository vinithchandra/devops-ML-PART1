"""
Tests for ML models in the CI/CD quality gate system.
"""
import numpy as np
import pytest
from datetime import datetime

from src.ml.models import BuildSuccessPredictor, BuildTimeEstimator, AnomalyDetector
from src.ml.feature_engineering import FeatureEngineer


@pytest.fixture
def sample_commit_data():
    """Sample Git commit data for testing."""
    return {
        'hash': 'abc123',
        'author': 'Test User',
        'timestamp': datetime.now().isoformat(),
        'message': 'Test commit',
        'files_changed': 3,
        'insertions': 100,
        'deletions': 50,
        'total_changes': 150,
        'files': [
            {
                'path': 'test_file.py',
                'type': 'python',
                'insertions': 50,
                'deletions': 25,
                'lines': 75
            },
            {
                'path': 'README.md',
                'type': 'markdown',
                'insertions': 30,
                'deletions': 15,
                'lines': 45
            }
        ]
    }


@pytest.fixture
def sample_system_data():
    """Sample system metrics data for testing."""
    return {
        'cpu': {
            'total_usage_percent': 45.5,
            'per_cpu_percent': [40.0, 50.0, 46.0, 46.0]
        },
        'memory': {
            'virtual': {
                'total': 16000000000,
                'available': 8000000000,
                'used': 8000000000,
                'free': 8000000000,
                'percent': 50.0
            },
            'swap': {
                'total': 8000000000,
                'used': 1000000000,
                'free': 7000000000,
                'percent': 12.5
            }
        },
        'disk': {
            'usage': {
                'total': 500000000000,
                'used': 250000000000,
                'free': 250000000000,
                'percent': 50.0
            },
            'io': {
                'read_bytes': 1000000,
                'write_bytes': 500000,
                'read_count': 100,
                'write_count': 50
            }
        }
    }


def test_build_predictor():
    """Test BuildSuccessPredictor functionality."""
    predictor = BuildSuccessPredictor()
    X = np.random.rand(100, 10)
    y = np.random.randint(0, 2, 100)
    feature_names = [f'feature_{i}' for i in range(10)]
    
    # Test fitting
    predictor.fit(X, y, feature_names)
    assert predictor.feature_names == feature_names
    
    # Test prediction
    X_new = np.random.rand(1, 10)
    prob = predictor.predict_proba(X_new)
    assert 0 <= prob <= 1


def test_build_time_estimator():
    """Test BuildTimeEstimator functionality."""
    estimator = BuildTimeEstimator()
    X = np.random.rand(100, 10)
    y = np.random.randint(60, 3600, 100)  # Build times between 1-60 minutes
    feature_names = [f'feature_{i}' for i in range(10)]
    
    # Test fitting
    estimator.fit(X, y, feature_names)
    assert estimator.feature_names == feature_names
    
    # Test prediction
    X_new = np.random.rand(1, 10)
    time = estimator.predict(X_new)
    assert time > 0


def test_anomaly_detector():
    """Test AnomalyDetector functionality."""
    detector = AnomalyDetector(threshold=2.0)
    X = np.random.rand(100, 5)
    
    # Test fitting
    detector.fit(X)
    assert detector.mean is not None
    assert detector.std is not None
    
    # Test detection
    X_new = np.random.rand(1, 5)
    result = detector.detect(X_new)
    assert isinstance(result['is_anomaly'], bool)
    assert len(result['z_scores']) == 5
    assert result['threshold'] == 2.0


def test_feature_engineering(sample_commit_data, sample_system_data):
    """Test FeatureEngineer functionality."""
    engineer = FeatureEngineer()
    
    # Test Git feature extraction
    git_features = engineer.extract_git_features(sample_commit_data)
    assert isinstance(git_features, np.ndarray)
    assert len(git_features) > 0
    
    # Test system feature extraction
    system_features = engineer.extract_system_features(sample_system_data)
    assert isinstance(system_features, np.ndarray)
    assert len(system_features) > 0
    
    # Test feature combination
    combined = engineer.combine_features(git_features, system_features)
    assert len(combined) == len(git_features) + len(system_features)
