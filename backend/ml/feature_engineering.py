import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import re
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("ml.feature_engineering")

class FeatureEngineering:
    """
    Feature engineering for CI/CD build data.
    Extracts and transforms features from various data sources.
    """
    
    def __init__(self):
        """Initialize the feature engineering module."""
        self.logger = logger
    
    def extract_git_features(self, commit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from git commit data.
        
        Args:
            commit_data: Dictionary containing git commit information
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Basic commit info
        features["commit_hash"] = commit_data.get("hash", "")
        features["commit_message_length"] = len(commit_data.get("message", ""))
        features["commit_message_has_issue_ref"] = int(bool(re.search(r'#\d+', commit_data.get("message", ""))))
        
        # Author info
        features["author_experience"] = commit_data.get("author_experience", 0)  # Number of previous commits
        
        # Code changes
        features["files_changed"] = commit_data.get("files_changed", 0)
        features["lines_added"] = commit_data.get("lines_added", 0)
        features["lines_deleted"] = commit_data.get("lines_deleted", 0)
        features["lines_changed"] = features["lines_added"] + features["lines_deleted"]
        features["code_churn"] = abs(features["lines_added"] - features["lines_deleted"])
        
        # File types
        file_extensions = [f.split('.')[-1] if '.' in f else '' for f in commit_data.get("changed_files", [])]
        features["py_files_changed"] = sum(1 for ext in file_extensions if ext == 'py')
        features["js_files_changed"] = sum(1 for ext in file_extensions if ext == 'js')
        features["html_files_changed"] = sum(1 for ext in file_extensions if ext == 'html')
        features["css_files_changed"] = sum(1 for ext in file_extensions if ext == 'css')
        features["test_files_changed"] = sum(1 for f in commit_data.get("changed_files", []) if 'test' in f.lower())
        features["doc_files_changed"] = sum(1 for f in commit_data.get("changed_files", []) if f.endswith(('.md', '.rst', '.txt')))
        
        # Branch info
        features["is_main_branch"] = int(commit_data.get("branch", "") in ["main", "master"])
        features["branch_age_days"] = commit_data.get("branch_age_days", 0)
        
        # Merge info
        features["is_merge_commit"] = int(commit_data.get("is_merge", False))
        features["has_conflicts"] = int(commit_data.get("has_conflicts", False))
        features["parents_count"] = commit_data.get("parents_count", 1)
        
        return features
    
    def extract_build_history_features(self, build_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract features from build history.
        
        Args:
            build_history: List of previous builds
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        if not build_history:
            # Default values if no history
            return {
                "previous_builds_count": 0,
                "previous_success_rate": 0.5,
                "previous_failure_rate": 0.5,
                "days_since_last_build": 30,
                "days_since_last_failure": 30,
                "days_since_last_success": 30,
                "avg_build_duration": 300,
                "consecutive_failures": 0,
                "consecutive_successes": 0
            }
        
        # Count builds
        features["previous_builds_count"] = len(build_history)
        
        # Success/failure rates
        successes = sum(1 for build in build_history if build.get("status") == "success")
        failures = sum(1 for build in build_history if build.get("status") == "failure")
        
        features["previous_success_rate"] = successes / len(build_history) if build_history else 0
        features["previous_failure_rate"] = failures / len(build_history) if build_history else 0
        
        # Sort builds by timestamp (newest first)
        sorted_builds = sorted(build_history, key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Days since last build/failure/success
        now = datetime.now()
        
        if sorted_builds:
            last_build_time = datetime.fromisoformat(sorted_builds[0].get("timestamp", now.isoformat()))
            features["days_since_last_build"] = (now - last_build_time).days
        else:
            features["days_since_last_build"] = 30  # Default if no builds
        
        # Find last failure
        last_failure = next((build for build in sorted_builds if build.get("status") == "failure"), None)
        if last_failure:
            last_failure_time = datetime.fromisoformat(last_failure.get("timestamp", now.isoformat()))
            features["days_since_last_failure"] = (now - last_failure_time).days
        else:
            features["days_since_last_failure"] = 30  # Default if no failures
        
        # Find last success
        last_success = next((build for build in sorted_builds if build.get("status") == "success"), None)
        if last_success:
            last_success_time = datetime.fromisoformat(last_success.get("timestamp", now.isoformat()))
            features["days_since_last_success"] = (now - last_success_time).days
        else:
            features["days_since_last_success"] = 30  # Default if no successes
        
        # Average build duration
        durations = []
        for build in build_history:
            duration_str = build.get("duration", "0m 0s")
            minutes = int(re.search(r'(\d+)m', duration_str).group(1)) if re.search(r'(\d+)m', duration_str) else 0
            seconds = int(re.search(r'(\d+)s', duration_str).group(1)) if re.search(r'(\d+)s', duration_str) else 0
            durations.append(minutes * 60 + seconds)
        
        features["avg_build_duration"] = sum(durations) / len(durations) if durations else 300
        
        # Consecutive failures/successes
        consecutive_failures = 0
        consecutive_successes = 0
        
        for build in sorted_builds:
            if build.get("status") == "failure":
                consecutive_failures += 1
                consecutive_successes = 0
            elif build.get("status") == "success":
                consecutive_successes += 1
                consecutive_failures = 0
            else:
                break  # Stop at first non-success/failure status
        
        features["consecutive_failures"] = consecutive_failures
        features["consecutive_successes"] = consecutive_successes
        
        return features
    
    def extract_code_quality_features(self, code_quality_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from code quality metrics.
        
        Args:
            code_quality_data: Dictionary containing code quality metrics
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Code complexity
        features["cyclomatic_complexity"] = code_quality_data.get("cyclomatic_complexity", 10)
        features["cognitive_complexity"] = code_quality_data.get("cognitive_complexity", 15)
        
        # Test coverage
        features["test_coverage"] = code_quality_data.get("test_coverage", 70)
        features["test_count"] = code_quality_data.get("test_count", 50)
        features["test_failures"] = code_quality_data.get("test_failures", 0)
        
        # Code smells
        features["code_smells"] = code_quality_data.get("code_smells", 10)
        features["duplicated_lines"] = code_quality_data.get("duplicated_lines", 5)
        features["technical_debt"] = code_quality_data.get("technical_debt", 120)  # in minutes
        
        # Violations
        features["blocker_violations"] = code_quality_data.get("blocker_violations", 0)
        features["critical_violations"] = code_quality_data.get("critical_violations", 2)
        features["major_violations"] = code_quality_data.get("major_violations", 5)
        
        return features
    
    def extract_system_metrics_features(self, system_metrics: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Extract features from system metrics.
        
        Args:
            system_metrics: Dictionary containing system metric time series
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Process each metric type
        for metric_name, values in system_metrics.items():
            if not values:
                continue
                
            # Calculate statistics
            features[f"{metric_name}_mean"] = np.mean(values)
            features[f"{metric_name}_std"] = np.std(values)
            features[f"{metric_name}_min"] = np.min(values)
            features[f"{metric_name}_max"] = np.max(values)
            features[f"{metric_name}_range"] = np.max(values) - np.min(values)
            features[f"{metric_name}_last"] = values[-1]
            
            # Calculate trend (slope of linear regression)
            if len(values) >= 3:
                x = np.arange(len(values))
                A = np.vstack([x, np.ones(len(x))]).T
                slope, _ = np.linalg.lstsq(A, values, rcond=None)[0]
                features[f"{metric_name}_trend"] = slope
            else:
                features[f"{metric_name}_trend"] = 0
        
        return features
    
    def extract_dependencies_features(self, dependencies_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from dependencies information.
        
        Args:
            dependencies_data: Dictionary containing dependencies information
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Count dependencies
        features["dependencies_count"] = len(dependencies_data.get("dependencies", []))
        
        # Count outdated dependencies
        outdated = sum(1 for dep in dependencies_data.get("dependencies", []) 
                      if dep.get("is_outdated", False))
        features["outdated_dependencies"] = outdated
        
        # Count vulnerable dependencies
        vulnerable = sum(1 for dep in dependencies_data.get("dependencies", []) 
                        if dep.get("has_vulnerabilities", False))
        features["vulnerable_dependencies"] = vulnerable
        
        # Calculate outdated ratio
        if features["dependencies_count"] > 0:
            features["outdated_ratio"] = outdated / features["dependencies_count"]
            features["vulnerable_ratio"] = vulnerable / features["dependencies_count"]
        else:
            features["outdated_ratio"] = 0
            features["vulnerable_ratio"] = 0
        
        # Major version differences
        version_diffs = [dep.get("version_diff", 0) for dep in dependencies_data.get("dependencies", [])]
        features["max_version_diff"] = max(version_diffs) if version_diffs else 0
        features["avg_version_diff"] = sum(version_diffs) / len(version_diffs) if version_diffs else 0
        
        return features
    
    def combine_features(self, feature_sets: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Combine multiple feature sets into a single DataFrame.
        
        Args:
            feature_sets: List of feature dictionaries
            
        Returns:
            DataFrame with combined features
        """
        # Merge all feature dictionaries
        combined = {}
        for feature_set in feature_sets:
            combined.update(feature_set)
        
        # Convert to DataFrame
        return pd.DataFrame([combined])
    
    def preprocess_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess features for model input.
        
        Args:
            df: DataFrame with raw features
            
        Returns:
            DataFrame with preprocessed features
        """
        # Make a copy to avoid modifying the original
        processed = df.copy()
        
        # Handle missing values
        processed = processed.fillna(0)
        
        # Convert boolean columns to integers
        bool_cols = processed.select_dtypes(include=['bool']).columns
        for col in bool_cols:
            processed[col] = processed[col].astype(int)
        
        # Cap extreme values (winsorization)
        numeric_cols = processed.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            q1 = processed[col].quantile(0.01)
            q99 = processed[col].quantile(0.99)
            processed[col] = processed[col].clip(q1, q99)
        
        return processed
    
    def extract_all_features(self, 
                           commit_data: Dict[str, Any],
                           build_history: List[Dict[str, Any]],
                           code_quality_data: Dict[str, Any],
                           system_metrics: Dict[str, List[float]],
                           dependencies_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Extract all features from various data sources.
        
        Args:
            commit_data: Git commit information
            build_history: Previous build history
            code_quality_data: Code quality metrics
            system_metrics: System metrics time series
            dependencies_data: Dependencies information
            
        Returns:
            DataFrame with all features
        """
        self.logger.info("Extracting features from all data sources")
        
        # Extract features from each source
        git_features = self.extract_git_features(commit_data)
        history_features = self.extract_build_history_features(build_history)
        quality_features = self.extract_code_quality_features(code_quality_data)
        metrics_features = self.extract_system_metrics_features(system_metrics)
        deps_features = self.extract_dependencies_features(dependencies_data)
        
        # Combine all features
        all_features = self.combine_features([
            git_features,
            history_features,
            quality_features,
            metrics_features,
            deps_features
        ])
        
        # Preprocess features
        processed_features = self.preprocess_features(all_features)
        
        self.logger.info(f"Extracted {processed_features.shape[1]} features")
        
        return processed_features
