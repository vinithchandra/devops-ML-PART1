"""
Deployment script for the ML-based CI/CD quality gate system.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path
import shutil
from typing import List, Optional
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Deployer:
    """Handles deployment of the application."""
    
    def __init__(self, target_dir: str) -> None:
        """
        Initialize the deployer.
        
        Args:
            target_dir: Directory to deploy to
        """
        self.target_dir = Path(target_dir)
        self.source_dir = Path(__file__).parent.parent
        self.deployment_log = self.target_dir / 'deployment_log.json'
        
    def deploy(self, 
               components: Optional[List[str]] = None,
               build_frontend: bool = True) -> None:
        """
        Deploy the application.
        
        Args:
            components: List of components to deploy (backend, frontend, or both)
            build_frontend: Whether to build the frontend
        """
        if components is None:
            components = ['backend', 'frontend']
            
        try:
            # Create deployment directory
            self.target_dir.mkdir(exist_ok=True)
            
            # Deploy components
            if 'backend' in components:
                self._deploy_backend()
            if 'frontend' in components:
                self._deploy_frontend(build_frontend)
                
            # Log deployment
            self._log_deployment(components)
            
            logger.info(f"Deployment completed successfully to {self.target_dir}")
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            raise
            
    def _deploy_backend(self) -> None:
        """Deploy the backend components."""
        logger.info("Deploying backend components...")
        
        # Create necessary directories
        backend_dir = self.target_dir / 'backend'
        backend_dir.mkdir(exist_ok=True)
        
        # Copy source files
        src_dir = self.source_dir / 'src'
        if src_dir.exists():
            shutil.copytree(src_dir, backend_dir / 'src', dirs_exist_ok=True)
            
        # Copy requirements
        req_file = self.source_dir / 'requirements.txt'
        if req_file.exists():
            shutil.copy2(req_file, backend_dir)
            
        # Create virtual environment
        venv_dir = backend_dir / 'venv'
        if not venv_dir.exists():
            subprocess.run(
                [sys.executable, '-m', 'venv', str(venv_dir)],
                check=True
            )
            
        # Install dependencies
        pip = str(venv_dir / 'Scripts' / 'pip')
        subprocess.run(
            [pip, 'install', '-r', str(backend_dir / 'requirements.txt')],
            check=True
        )
        
    def _deploy_frontend(self, build: bool = True) -> None:
        """
        Deploy the frontend components.
        
        Args:
            build: Whether to build the frontend
        """
        logger.info("Deploying frontend components...")
        
        frontend_dir = self.target_dir / 'frontend'
        frontend_dir.mkdir(exist_ok=True)
        
        # Copy frontend files
        src_frontend = self.source_dir / 'frontend'
        if src_frontend.exists():
            # Copy everything except node_modules and build
            for item in src_frontend.glob('*'):
                if item.name not in ['node_modules', 'build']:
                    if item.is_file():
                        shutil.copy2(item, frontend_dir)
                    else:
                        shutil.copytree(item, frontend_dir / item.name, 
                                      dirs_exist_ok=True)
                        
        if build:
            # Install dependencies and build
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
            subprocess.run(['npm', 'run', 'build'], cwd=frontend_dir, check=True)
            
    def _log_deployment(self, components: List[str]) -> None:
        """Log deployment details."""
        deployment = {
            'timestamp': datetime.now().isoformat(),
            'components': components,
            'source_dir': str(self.source_dir),
            'target_dir': str(self.target_dir),
            'python_version': sys.version,
        }
        
        # Load existing log if it exists
        if self.deployment_log.exists():
            with open(self.deployment_log, 'r') as f:
                log = json.load(f)
        else:
            log = []
            
        # Add new deployment and save
        log.append(deployment)
        with open(self.deployment_log, 'w') as f:
            json.dump(log, f, indent=2)
            

def main():
    """Main deployment script."""
    parser = argparse.ArgumentParser(description='Deploy the CI/CD quality gate system')
    parser.add_argument(
        '--target-dir',
        required=True,
        help='Directory to deploy to'
    )
    parser.add_argument(
        '--components',
        nargs='+',
        choices=['backend', 'frontend'],
        default=['backend', 'frontend'],
        help='Components to deploy'
    )
    parser.add_argument(
        '--skip-frontend-build',
        action='store_true',
        help='Skip building the frontend'
    )
    
    args = parser.parse_args()
    
    try:
        deployer = Deployer(args.target_dir)
        deployer.deploy(
            components=args.components,
            build_frontend=not args.skip_frontend_build
        )
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        sys.exit(1)
        

if __name__ == '__main__':
    main()
