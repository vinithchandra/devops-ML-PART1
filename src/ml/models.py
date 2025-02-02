"""
Core machine learning models for the CI/CD quality gate system.
"""
from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.base import BaseEstimator
from sklearn.exceptions import NotFittedError


class BuildSuccessPredictor:
    """Predicts the probability of a successful build using Random Forest."""
    
    def __init__(self) -> None:
        self.model: RandomForestClassifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.feature_names: Optional[List[str]] = None
        
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> None:
        """
        Train the model with the provided data.
        
        Args:
            X: Training features
            y: Target labels (0 for failed, 1 for success)
            feature_names: Names of the features
        """
        self.feature_names = feature_names
        self.model.fit(X, y)
        
    def predict_proba(self, X: np.ndarray) -> float:
        """
        Predict the probability of build success.
        
        Args:
            X: Feature vector
            
        Returns:
            Probability of build success
        """
        if not self.feature_names:
            raise NotFittedError("Model needs to be fitted before prediction")
        
        return self.model.predict_proba(X)[0][1]


class BuildTimeEstimator:
    """Estimates build time using Gradient Boosting."""
    
    def __init__(self) -> None:
        self.model: GradientBoostingRegressor = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.feature_names: Optional[List[str]] = None
        
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> None:
        """
        Train the model with the provided data.
        
        Args:
            X: Training features
            y: Build times in seconds
            feature_names: Names of the features
        """
        self.feature_names = feature_names
        self.model.fit(X, y)
        
    def predict(self, X: np.ndarray) -> float:
        """
        Predict build time in seconds.
        
        Args:
            X: Feature vector
            
        Returns:
            Estimated build time in seconds
        """
        if not self.feature_names:
            raise NotFittedError("Model needs to be fitted before prediction")
        
        return self.model.predict(X)[0]


class AnomalyDetector:
    """Detects anomalies in system metrics using statistical methods."""
    
    def __init__(self, threshold: float = 2.0) -> None:
        self.threshold = threshold
        self.mean: Optional[np.ndarray] = None
        self.std: Optional[np.ndarray] = None
        
    def fit(self, X: np.ndarray) -> None:
        """
        Calculate baseline statistics from normal operation data.
        
        Args:
            X: Training data of system metrics
        """
        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0)
        
    def detect(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Detect anomalies in new data.
        
        Args:
            X: New system metrics data
            
        Returns:
            Dictionary containing anomaly scores and flags
        """
        if self.mean is None or self.std is None:
            raise NotFittedError("Detector needs to be fitted before detection")
        
        z_scores = np.abs((X - self.mean) / self.std)
        is_anomaly = np.any(z_scores > self.threshold)
        
        return {
            "is_anomaly": bool(is_anomaly),
            "z_scores": z_scores.tolist(),
            "threshold": self.threshold
        }
