"""
Jenkins integration module for the CI/CD quality gate system.
"""
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import jenkins
from loguru import logger


class JenkinsClient:
    """Client for interacting with Jenkins CI server."""
    
    def __init__(self, url: str, username: str, password: str) -> None:
        """
        Initialize Jenkins client.
        
        Args:
            url: Jenkins server URL
            username: Jenkins username
            password: Jenkins API token or password
        """
        try:
            self.server = jenkins.Jenkins(url, username=username, password=password)
            self.server.get_whoami()
            logger.info("Successfully connected to Jenkins server")
        except Exception as e:
            logger.error(f"Failed to connect to Jenkins server: {str(e)}")
            raise
            
    def get_build_history(self, 
                         job_name: str, 
                         max_builds: int = 100) -> List[Dict[str, Any]]:
        """
        Get build history for a specific job.
        
        Args:
            job_name: Name of the Jenkins job
            max_builds: Maximum number of builds to retrieve
            
        Returns:
            List of build information dictionaries
        """
        try:
            job_info = self.server.get_job_info(job_name)
            builds = []
            
            for build_info in job_info['builds'][:max_builds]:
                build_number = build_info['number']
                build_details = self.server.get_build_info(job_name, build_number)
                
                builds.append({
                    'number': build_number,
                    'result': build_details['result'],
                    'timestamp': datetime.fromtimestamp(
                        build_details['timestamp'] / 1000
                    ).isoformat(),
                    'duration': build_details['duration'],
                    'url': build_details['url'],
                    'parameters': self._extract_parameters(build_details),
                    'test_results': self._get_test_results(job_name, build_number)
                })
                
            return builds
        except Exception as e:
            logger.error(f"Failed to get build history for {job_name}: {str(e)}")
            raise
            
    def _extract_parameters(self, 
                          build_details: Dict[str, Any]) -> Dict[str, Any]:
        """Extract build parameters from build details."""
        parameters = {}
        actions = build_details.get('actions', [])
        
        for action in actions:
            if action.get('_class') == 'hudson.model.ParametersAction':
                for param in action.get('parameters', []):
                    parameters[param['name']] = param.get('value')
                    
        return parameters
    
    def _get_test_results(self, 
                         job_name: str, 
                         build_number: int) -> Optional[Dict[str, Any]]:
        """Get test results for a specific build."""
        try:
            test_report = self.server.get_build_test_report(job_name, build_number)
            return {
                'total': test_report['totalCount'],
                'failed': test_report['failCount'],
                'skipped': test_report['skipCount'],
                'passed': test_report['passCount'],
                'duration': test_report.get('duration', 0)
            }
        except Exception:
            logger.warning(
                f"No test results found for {job_name} build #{build_number}"
            )
            return None
            
    def get_job_config(self, job_name: str) -> Dict[str, Any]:
        """
        Get job configuration details.
        
        Args:
            job_name: Name of the Jenkins job
            
        Returns:
            Dictionary containing job configuration
        """
        try:
            config_xml = self.server.get_job_config(job_name)
            return {
                'name': job_name,
                'config': config_xml,
                'url': f"{self.server.server}/job/{job_name}"
            }
        except Exception as e:
            logger.error(f"Failed to get config for {job_name}: {str(e)}")
            raise
            
    def analyze_build_stability(self, 
                              job_name: str, 
                              window_size: int = 10) -> Dict[str, Any]:
        """
        Analyze build stability over recent builds.
        
        Args:
            job_name: Name of the Jenkins job
            window_size: Number of recent builds to analyze
            
        Returns:
            Dictionary containing stability metrics
        """
        builds = self.get_build_history(job_name, window_size)
        
        if not builds:
            return {
                'success_rate': 0.0,
                'avg_duration': 0.0,
                'failure_count': 0,
                'total_builds': 0
            }
            
        success_count = sum(1 for b in builds if b['result'] == 'SUCCESS')
        durations = [b['duration'] for b in builds]
        
        return {
            'success_rate': success_count / len(builds),
            'avg_duration': sum(durations) / len(durations),
            'failure_count': len(builds) - success_count,
            'total_builds': len(builds)
        }
