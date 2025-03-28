import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from .base_model import BaseModel

class AnomalyDetector(BaseModel):
    """
    Model to detect anomalies in system metrics using Isolation Forest.
    """
    
    def __init__(self, metric_name: str = "generic"):
        """
        Initialize the anomaly detector model.
        
        Args:
            metric_name: Name of the metric this detector is for (e.g., 'cpu', 'memory')
        """
        super().__init__(model_name=f"anomaly_detector_{metric_name}")
        self.metric_name = metric_name
        self.scaler = StandardScaler()
        self.threshold = -0.5  # Default anomaly threshold
        self.feature_names = []
    
    def train(self, X: pd.DataFrame, y=None) -> Dict[str, float]:
        """
        Train the anomaly detection model.
        
        Args:
            X: Features dataframe with time series data
            y: Not used for unsupervised learning, but kept for API consistency
            
        Returns:
            Dictionary of evaluation metrics
        """
        self.logger.info(f"Training anomaly detection model for {self.metric_name}")
        self.feature_names = X.columns.tolist()
        
        # Scale the features
        X_scaled = self.scaler.fit_transform(X)
        
        # Initialize and train the model
        self.model = IsolationForest(
            n_estimators=100,
            max_samples='auto',
            contamination=0.05,  # Expected proportion of anomalies
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_scaled)
        
        # Calculate anomaly scores on training data to set threshold
        scores = self.model.decision_function(X_scaled)
        
        # Set threshold at 5th percentile of scores
        self.threshold = np.percentile(scores, 5)
        
        # Save the trained model
        self.save_model()
        
        return {"threshold": self.threshold}
    
    def predict(self, X: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect anomalies in the input data.
        
        Args:
            X: Features dataframe with time series data
            
        Returns:
            Dictionary with anomaly detection results
        """
        if self.model is None:
            if not self.load_model():
                self.logger.error("No model available for anomaly detection")
                return {"anomalies": [], "scores": []}
        
        # Ensure X has the expected features
        missing_features = set(self.feature_names) - set(X.columns)
        if missing_features:
            self.logger.warning(f"Missing features in input data: {missing_features}")
            # Add missing features with default values
            for feature in missing_features:
                X[feature] = 0
        
        # Reorder columns to match training data
        X = X[self.feature_names]
        
        # Scale the features
        X_scaled = self.scaler.transform(X)
        
        # Get anomaly scores (-1 for anomalies, 1 for normal)
        raw_predictions = self.model.predict(X_scaled)
        
        # Get decision scores (lower = more anomalous)
        scores = self.model.decision_function(X_scaled)
        
        # Identify anomalies based on threshold
        anomalies = []
        for i, (score, row) in enumerate(zip(scores, X.iterrows())):
            if score < self.threshold:
                timestamp = row[1].get('timestamp', datetime.now())
                value = row[1].get('value', 0)
                
                # Determine severity based on how far below threshold
                severity = self._determine_severity(score)
                
                anomalies.append({
                    "index": i,
                    "timestamp": timestamp,
                    "value": value,
                    "score": score,
                    "severity": severity,
                    "metric": self.metric_name
                })
        
        return {
            "anomalies": anomalies,
            "scores": scores.tolist()
        }
    
    def evaluate(self, X: pd.DataFrame, y=None) -> Dict[str, float]:
        """
        Evaluate the model on test data.
        
        Args:
            X: Features dataframe
            y: Not used for unsupervised learning, but kept for API consistency
            
        Returns:
            Dictionary of evaluation metrics
        """
        if self.model is None:
            self.logger.error("No model available for evaluation")
            return {"anomaly_rate": 0.0}
        
        # Scale the features
        X_scaled = self.scaler.transform(X)
        
        # Get anomaly scores
        scores = self.model.decision_function(X_scaled)
        
        # Calculate anomaly rate
        anomaly_rate = np.mean(scores < self.threshold)
        
        return {"anomaly_rate": anomaly_rate}
    
    def _determine_severity(self, score: float) -> str:
        """
        Determine the severity of an anomaly based on its score.
        
        Args:
            score: Anomaly score from the model
            
        Returns:
            Severity level as string ('low', 'medium', or 'high')
        """
        # The more negative the score, the more anomalous
        if score < self.threshold * 2:
            return "high"
        elif score < self.threshold * 1.5:
            return "medium"
        else:
            return "low"
    
    def detect_anomalies_with_context(self, 
                                     data: pd.DataFrame, 
                                     window_size: int = 10) -> List[Dict[str, Any]]:
        """
        Detect anomalies with contextual information.
        
        Args:
            data: DataFrame with timestamp and value columns
            window_size: Size of the sliding window for feature extraction
            
        Returns:
            List of detected anomalies with context
        """
        if len(data) < window_size:
            self.logger.warning(f"Not enough data points for anomaly detection (got {len(data)}, need {window_size})")
            return []
        
        # Extract features from time series data
        features = self._extract_features(data, window_size)
        
        # Detect anomalies
        result = self.predict(features)
        
        # Add more context to anomalies
        enriched_anomalies = []
        for anomaly in result["anomalies"]:
            # Get the window of data around the anomaly
            idx = anomaly["index"]
            start_idx = max(0, idx - window_size // 2)
            end_idx = min(len(data), idx + window_size // 2)
            context_window = data.iloc[start_idx:end_idx]
            
            # Calculate statistics for the context window
            context = {
                "mean": context_window["value"].mean(),
                "std": context_window["value"].std(),
                "min": context_window["value"].min(),
                "max": context_window["value"].max(),
                "current": anomaly["value"],
                "z_score": (anomaly["value"] - context_window["value"].mean()) / max(0.001, context_window["value"].std())
            }
            
            # Add context to anomaly
            enriched_anomaly = {**anomaly, "context": context}
            enriched_anomalies.append(enriched_anomaly)
        
        return enriched_anomalies
    
    def _extract_features(self, data: pd.DataFrame, window_size: int) -> pd.DataFrame:
        """
        Extract features from time series data using sliding windows.
        
        Args:
            data: DataFrame with timestamp and value columns
            window_size: Size of the sliding window
            
        Returns:
            DataFrame with extracted features
        """
        features = []
        
        for i in range(len(data) - window_size + 1):
            window = data.iloc[i:i+window_size]
            values = window["value"].values
            
            # Extract statistical features
            feature_dict = {
                "timestamp": window.iloc[-1]["timestamp"],
                "value": window.iloc[-1]["value"],
                "mean": np.mean(values),
                "std": np.std(values),
                "min": np.min(values),
                "max": np.max(values),
                "range": np.max(values) - np.min(values),
                "median": np.median(values)
            }
            
            # Add trend features
            if len(values) >= 3:
                # Simple linear regression slope
                x = np.arange(len(values))
                A = np.vstack([x, np.ones(len(x))]).T
                slope, _ = np.linalg.lstsq(A, values, rcond=None)[0]
                feature_dict["slope"] = slope
                
                # Rate of change
                feature_dict["rate_of_change"] = (values[-1] - values[0]) / window_size
            else:
                feature_dict["slope"] = 0
                feature_dict["rate_of_change"] = 0
            
            features.append(feature_dict)
        
        return pd.DataFrame(features)
