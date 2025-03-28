import os
import joblib
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseModel(ABC):
    """Base class for all ML models in the system."""
    
    def __init__(self, model_name: str, model_dir: str = "models"):
        """
        Initialize the base model.
        
        Args:
            model_name: Name of the model
            model_dir: Directory where models are stored
        """
        self.model_name = model_name
        self.model_dir = model_dir
        self.model = None
        self.logger = logging.getLogger(f"ml.{model_name}")
        
        # Create model directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), model_dir), exist_ok=True)
    
    def get_model_path(self) -> str:
        """Get the full path to the model file."""
        return os.path.join(os.path.dirname(__file__), self.model_dir, f"{self.model_name}.joblib")
    
    def save_model(self) -> None:
        """Save the model to disk."""
        if self.model is None:
            self.logger.warning("No model to save")
            return
        
        model_path = self.get_model_path()
        self.logger.info(f"Saving model to {model_path}")
        joblib.dump(self.model, model_path)
        self.logger.info(f"Model saved successfully")
    
    def load_model(self) -> bool:
        """
        Load the model from disk.
        
        Returns:
            bool: True if model was loaded successfully, False otherwise
        """
        model_path = self.get_model_path()
        if not os.path.exists(model_path):
            self.logger.warning(f"Model file not found at {model_path}")
            return False
        
        try:
            self.logger.info(f"Loading model from {model_path}")
            self.model = joblib.load(model_path)
            self.logger.info(f"Model loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return False
    
    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Train the model.
        
        Args:
            X: Features
            y: Target variable
        """
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> Any:
        """
        Make predictions using the model.
        
        Args:
            X: Features
            
        Returns:
            Predictions
        """
        pass
    
    @abstractmethod
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Evaluate the model.
        
        Args:
            X: Features
            y: Target variable
            
        Returns:
            Dictionary of evaluation metrics
        """
        pass
    
    def feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Get feature importance if the model supports it.
        
        Returns:
            Dictionary mapping feature names to importance scores, or None if not supported
        """
        return None
