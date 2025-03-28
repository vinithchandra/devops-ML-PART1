import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from .base_model import BaseModel

class BuildTimeEstimator(BaseModel):
    """
    Model to estimate build time using Gradient Boosting Regressor.
    """
    
    def __init__(self):
        """Initialize the build time estimator model."""
        super().__init__(model_name="build_time_estimator")
        self.feature_names = []
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Train the build time estimation model.
        
        Args:
            X: Features dataframe
            y: Target variable (build time in seconds)
            
        Returns:
            Dictionary of evaluation metrics
        """
        self.logger.info("Training build time estimation model")
        self.feature_names = X.columns.tolist()
        
        # Split data into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Initialize and train the model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
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
        Predict build time.
        
        Args:
            X: Features dataframe
            
        Returns:
            Dictionary with estimated build time and additional information
        """
        if self.model is None:
            if not self.load_model():
                self.logger.error("No model available for prediction")
                return {"estimated_time": 300, "confidence": 0.0}  # Default 5 minutes
        
        # Ensure X has the expected features
        missing_features = set(self.feature_names) - set(X.columns)
        if missing_features:
            self.logger.warning(f"Missing features in input data: {missing_features}")
            # Add missing features with default values
            for feature in missing_features:
                X[feature] = 0
        
        # Reorder columns to match training data
        X = X[self.feature_names]
        
        # Predict build time
        estimated_time = self.model.predict(X)[0]
        
        # Calculate confidence based on model's feature importance
        # Higher importance for the features that are present in this sample = higher confidence
        feature_importance = self.feature_importance()
        present_features_importance = sum(
            importance for feature, importance in feature_importance.items()
            if X[feature].iloc[0] != 0
        )
        confidence = min(1.0, present_features_importance * 2)  # Scale to 0-1
        
        return {
            "estimated_time": max(1, estimated_time),  # Ensure positive time
            "confidence": confidence
        }
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Evaluate the model on test data.
        
        Args:
            X: Features dataframe
            y: Target variable (build time in seconds)
            
        Returns:
            Dictionary of evaluation metrics
        """
        if self.model is None:
            self.logger.error("No model available for evaluation")
            return {
                "mse": 0.0,
                "rmse": 0.0,
                "mae": 0.0,
                "r2": 0.0
            }
        
        # Make predictions
        y_pred = self.model.predict(X)
        
        # Calculate metrics
        mse = mean_squared_error(y, y_pred)
        metrics = {
            "mse": mse,
            "rmse": np.sqrt(mse),
            "mae": mean_absolute_error(y, y_pred),
            "r2": r2_score(y, y_pred)
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
    
    def get_time_factors(self, X: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify factors that contribute most to the build time.
        
        Args:
            X: Features dataframe for a single prediction
            
        Returns:
            List of factors with their names and values
        """
        if self.model is None:
            return []
        
        # Get feature importances
        importances = self.feature_importance()
        
        # Get feature values for this prediction
        feature_values = X.iloc[0].to_dict()
        
        # Identify top factors
        time_factors = []
        
        # Sort features by importance
        sorted_features = sorted(
            importances.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Take top 5 important features
        for feature, importance in sorted_features[:5]:
            time_factors.append({
                "name": feature,
                "value": feature_values[feature],
                "importance": importance
            })
        
        return time_factors
