"""
Model serialization utilities for saving and loading trained models.
"""
import os
from typing import Any, Dict, Optional
import joblib
from datetime import datetime
import json
from pathlib import Path
from loguru import logger

from ..config.settings import MODEL_DIR


class ModelSerializer:
    """Handles model serialization and versioning."""
    
    def __init__(self) -> None:
        """Initialize the model serializer."""
        self.model_dir = MODEL_DIR
        self.model_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different model types
        self.build_predictor_dir = self.model_dir / 'build_predictor'
        self.time_estimator_dir = self.model_dir / 'time_estimator'
        self.anomaly_detector_dir = self.model_dir / 'anomaly_detector'
        
        for directory in [self.build_predictor_dir, 
                         self.time_estimator_dir,
                         self.anomaly_detector_dir]:
            directory.mkdir(exist_ok=True)
            
    def save_model(self,
                  model: Any,
                  model_type: str,
                  metrics: Optional[Dict[str, float]] = None) -> str:
        """
        Save a trained model with metadata.
        
        Args:
            model: The trained model to save
            model_type: Type of the model (build_predictor, time_estimator, or anomaly_detector)
            metrics: Optional dictionary of evaluation metrics
            
        Returns:
            Path to the saved model
        """
        # Create version string
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        version = f"v_{timestamp}"
        
        # Get appropriate directory
        if model_type == 'build_predictor':
            save_dir = self.build_predictor_dir
        elif model_type == 'time_estimator':
            save_dir = self.time_estimator_dir
        elif model_type == 'anomaly_detector':
            save_dir = self.anomaly_detector_dir
        else:
            raise ValueError(f"Unknown model type: {model_type}")
            
        # Create version directory
        version_dir = save_dir / version
        version_dir.mkdir(exist_ok=True)
        
        # Save model
        model_path = version_dir / 'model.joblib'
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata = {
            'version': version,
            'timestamp': timestamp,
            'model_type': model_type,
            'metrics': metrics or {},
            'python_version': os.sys.version,
        }
        
        metadata_path = version_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Saved {model_type} model version {version}")
        return str(model_path)
        
    def load_model(self,
                  model_type: str,
                  version: Optional[str] = None) -> tuple[Any, Dict[str, Any]]:
        """
        Load a model and its metadata.
        
        Args:
            model_type: Type of the model to load
            version: Specific version to load, or None for latest
            
        Returns:
            Tuple of (loaded model, metadata dictionary)
        """
        # Get appropriate directory
        if model_type == 'build_predictor':
            model_dir = self.build_predictor_dir
        elif model_type == 'time_estimator':
            model_dir = self.time_estimator_dir
        elif model_type == 'anomaly_detector':
            model_dir = self.anomaly_detector_dir
        else:
            raise ValueError(f"Unknown model type: {model_type}")
            
        # Find version directory
        if version is None:
            # Get latest version
            versions = sorted(model_dir.glob('v_*'))
            if not versions:
                raise FileNotFoundError(f"No saved models found for {model_type}")
            version_dir = versions[-1]
        else:
            version_dir = model_dir / version
            if not version_dir.exists():
                raise FileNotFoundError(f"Version {version} not found for {model_type}")
                
        # Load model
        model_path = version_dir / 'model.joblib'
        model = joblib.load(model_path)
        
        # Load metadata
        metadata_path = version_dir / 'metadata.json'
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        logger.info(f"Loaded {model_type} model version {metadata['version']}")
        return model, metadata
        
    def list_versions(self, model_type: str) -> list[Dict[str, Any]]:
        """
        List all available versions for a model type.
        
        Args:
            model_type: Type of model to list versions for
            
        Returns:
            List of metadata dictionaries for each version
        """
        # Get appropriate directory
        if model_type == 'build_predictor':
            model_dir = self.build_predictor_dir
        elif model_type == 'time_estimator':
            model_dir = self.time_estimator_dir
        elif model_type == 'anomaly_detector':
            model_dir = self.anomaly_detector_dir
        else:
            raise ValueError(f"Unknown model type: {model_type}")
            
        versions = []
        for version_dir in sorted(model_dir.glob('v_*')):
            metadata_path = version_dir / 'metadata.json'
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                versions.append(metadata)
                
        return versions
        
    def delete_version(self, model_type: str, version: str) -> None:
        """
        Delete a specific model version.
        
        Args:
            model_type: Type of the model
            version: Version to delete
        """
        # Get appropriate directory
        if model_type == 'build_predictor':
            model_dir = self.build_predictor_dir
        elif model_type == 'time_estimator':
            model_dir = self.time_estimator_dir
        elif model_type == 'anomaly_detector':
            model_dir = self.anomaly_detector_dir
        else:
            raise ValueError(f"Unknown model type: {model_type}")
            
        version_dir = model_dir / version
        if not version_dir.exists():
            raise FileNotFoundError(f"Version {version} not found for {model_type}")
            
        # Remove version directory and contents
        for file in version_dir.glob('*'):
            file.unlink()
        version_dir.rmdir()
        
        logger.info(f"Deleted {model_type} model version {version}")
