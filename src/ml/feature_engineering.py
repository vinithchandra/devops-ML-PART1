"""
Feature engineering pipeline for the ML-based CI/CD quality gate system.
"""
from typing import Dict, List, Any
import numpy as np
import pandas as pd
from datetime import datetime


class FeatureEngineer:
    """Transforms raw data into features for ML models."""
    
    def __init__(self) -> None:
        """Initialize the feature engineer."""
        self.feature_names: List[str] = []
        
    def extract_git_features(self, commit_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from Git commit data.
        
        Args:
            commit_data: Dictionary containing commit information
            
        Returns:
            Feature vector for the commit
        """
        features = {
            'files_changed': commit_data['files_changed'],
            'insertions': commit_data['insertions'],
            'deletions': commit_data['deletions'],
            'total_changes': commit_data['total_changes'],
            'has_tests': self._has_test_changes(commit_data['files']),
            'has_docs': self._has_doc_changes(commit_data['files']),
            'file_type_complexity': self._calculate_file_complexity(commit_data['files']),
            'commit_message_length': len(commit_data['message']),
            'time_of_day': self._extract_time_feature(commit_data['timestamp'])
        }
        
        self.feature_names = list(features.keys())
        return np.array([features[name] for name in self.feature_names])
    
    def extract_system_features(self, system_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from system metrics.
        
        Args:
            system_data: Dictionary containing system metrics
            
        Returns:
            Feature vector for system metrics
        """
        features = {
            'cpu_usage': system_data['cpu']['total_usage_percent'],
            'memory_usage': system_data['memory']['virtual']['percent'],
            'swap_usage': system_data['memory']['swap']['percent'],
            'disk_usage': system_data['disk']['usage']['percent'],
            'disk_io_rate': (
                system_data['disk']['io']['read_bytes'] + 
                system_data['disk']['io']['write_bytes']
            ) / 1e6  # Convert to MB
        }
        
        self.feature_names.extend(list(features.keys()))
        return np.array([features[name] for name in features.keys()])
    
    def _has_test_changes(self, files: List[Dict[str, Any]]) -> float:
        """Check if any test files were modified."""
        test_files = sum(
            1 for f in files 
            if 'test' in f['path'].lower() or 
            f['path'].endswith('_test.py') or 
            f['path'].endswith('test_.py')
        )
        return test_files / len(files) if files else 0.0
    
    def _has_doc_changes(self, files: List[Dict[str, Any]]) -> float:
        """Check if any documentation files were modified."""
        doc_files = sum(
            1 for f in files 
            if f['path'].endswith(('.md', '.rst', '.txt')) or 
            'doc' in f['path'].lower()
        )
        return doc_files / len(files) if files else 0.0
    
    def _calculate_file_complexity(self, files: List[Dict[str, Any]]) -> float:
        """Calculate complexity score based on file types and changes."""
        type_weights = {
            'python': 1.0,
            'java': 1.2,
            'cpp': 1.3,
            'javascript': 0.9,
            'yaml': 0.5,
            'json': 0.3,
            'markdown': 0.1,
            'other': 0.7
        }
        
        complexity = 0.0
        for file in files:
            weight = type_weights.get(file['type'], type_weights['other'])
            changes = file['insertions'] + file['deletions']
            complexity += changes * weight
            
        return complexity / len(files) if files else 0.0
    
    def _extract_time_feature(self, timestamp: str) -> float:
        """Convert timestamp to time of day feature (0-24 scale)."""
        dt = datetime.fromisoformat(timestamp)
        return dt.hour + dt.minute / 60.0
    
    def combine_features(self, 
                        git_features: np.ndarray, 
                        system_features: np.ndarray) -> np.ndarray:
        """
        Combine different feature sets into a single feature vector.
        
        Args:
            git_features: Features extracted from Git data
            system_features: Features extracted from system metrics
            
        Returns:
            Combined feature vector
        """
        return np.concatenate([git_features, system_features])
    
    def get_feature_names(self) -> List[str]:
        """Get the names of the features in order."""
        return self.feature_names
