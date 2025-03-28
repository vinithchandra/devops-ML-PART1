import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from .base_model import BaseModel

class BuildSuccessPredictor(BaseModel):
    """
    Model to predict build success using Random Forest Classifier.
    """
    
    def __init__(self):
        """Initialize the build success predictor model."""
        super().__init__(model_name="build_success_predictor")
        self.feature_names = []
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Train the build success prediction model.
        
        Args:
            X: Features dataframe
            y: Target variable (1 for success, 0 for failure)
            
        Returns:
            Dictionary of evaluation metrics
        """
        self.logger.info("Training build success prediction model")
        self.feature_names = X.columns.tolist()
        
        # Split data into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Initialize and train the model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate on validation set
        metrics = self.evaluate(X_val, y_val)
        self.logger.info(f"Model training completed with metrics: {metrics}")
        
        # Save the trained model
        self.save_model()
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> Dict[str, Any]:
        """
        Predict build success probability.
        
        Args:
            X: Features dataframe
            
        Returns:
            Dictionary with success probability and additional information
        """
        if self.model is None:
            if not self.load_model():
                self.logger.error("No model available for prediction")
                return {"success_probability": 0.5, "risk_factors": [], "confidence": 0.0}
        
        # Ensure X has the expected features
        missing_features = set(self.feature_names) - set(X.columns)
        if missing_features:
            self.logger.warning(f"Missing features in input data: {missing_features}")
            # Add missing features with default values
            for feature in missing_features:
                X[feature] = 0
        
        # Reorder columns to match training data
        X = X[self.feature_names]
        
        # Get probability of success (class 1)
        probabilities = self.model.predict_proba(X)
        success_probability = probabilities[0][1] * 100  # Convert to percentage
        
        # Get feature importances for this prediction
        risk_factors = self.get_risk_factors(X)
        
        # Calculate confidence based on how far the probability is from 0.5
        confidence = abs(success_probability/100 - 0.5) * 2  # Scale to 0-1
        
        return {
            "success_probability": success_probability,
            "risk_factors": risk_factors,
            "confidence": confidence
        }
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Evaluate the model on test data.
        
        Args:
            X: Features dataframe
            y: Target variable (1 for success, 0 for failure)
            
        Returns:
            Dictionary of evaluation metrics
        """
        if self.model is None:
            self.logger.error("No model available for evaluation")
            return {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "auc": 0.0
            }
        
        # Make predictions
        y_pred = self.model.predict(X)
        y_prob = self.model.predict_proba(X)[:, 1]
        
        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y, y_pred),
            "precision": precision_score(y, y_pred, zero_division=0),
            "recall": recall_score(y, y_pred, zero_division=0),
            "f1": f1_score(y, y_pred, zero_division=0),
            "auc": roc_auc_score(y, y_prob)
        }
        
        return metrics
    
    def feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance from the model.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.model is None or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importances = self.model.feature_importances_
        feature_importance = {
            feature: importance 
            for feature, importance in zip(self.feature_names, importances)
        }
        
        # Sort by importance (descending)
        return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
    
    def get_risk_factors(self, X: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify risk factors for a specific prediction.
        
        Args:
            X: Features dataframe for a single prediction
            
        Returns:
            List of risk factors with their names and values
        """
        if self.model is None:
            return []
        
        # Get feature importances
        importances = self.feature_importance()
        
        # Get feature values for this prediction
        feature_values = X.iloc[0].to_dict()
        
        # Identify top risk factors
        risk_factors = []
        
        # Sort features by importance
        sorted_features = sorted(
            importances.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Take top 5 important features
        for feature, importance in sorted_features[:5]:
            risk_factors.append({
                "name": feature,
                "value": feature_values[feature],
                "importance": importance
            })
        
        return risk_factors
    
    def generate_recommendations(self, risk_factors: List[Dict[str, Any]]) -> List[str]:
        """
        Generate recommendations based on identified risk factors.
        
        Args:
            risk_factors: List of risk factors
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Map of risk factors to recommendations
        recommendation_map = {
            "code_complexity": "Refactor complex code modules to improve maintainability",
            "test_coverage": "Increase test coverage for critical components",
            "commit_frequency": "Consider smaller, more frequent commits",
            "lines_changed": "Break large changes into smaller, more manageable pull requests",
            "previous_failures": "Review and address patterns in previous build failures",
            "dependencies_count": "Audit and minimize external dependencies",
            "build_time": "Optimize build process to reduce build time",
            "merge_conflicts": "Improve team coordination to reduce merge conflicts",
            "branch_age": "Regularly merge from main branch to reduce integration issues",
            "code_churn": "Stabilize rapidly changing code areas with better tests"
        }
        
        # Generate recommendations based on risk factors
        for factor in risk_factors:
            factor_name = factor["name"].lower()
            
            # Find matching recommendations
            for key, recommendation in recommendation_map.items():
                if key in factor_name:
                    recommendations.append(recommendation)
                    break
        
        # Add generic recommendation if none found
        if not recommendations:
            recommendations.append("No specific recommendations - build looks good!")
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(recommendations))
