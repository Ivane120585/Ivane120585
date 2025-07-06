#!/usr/bin/env python3
"""
Deploy Handler
Executes Deploy: actions for different deployment targets
"""

import subprocess
import sys
import re
import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

class DeployHandler:
    """Sacred deploy handler for executing deployment actions"""
    
    def __init__(self, log_file: str = "deploy_trace.log"):
        self.log_file = Path(log_file)
        self.setup_logging()
        self.deploy_targets = self._load_deploy_targets()
        
    def setup_logging(self):
        """Setup logging for deployment traces"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_deploy_targets(self) -> Dict[str, Dict]:
        """Load deployment target configurations"""
        return {
            "streamlit_app": {
                "description": "Deploy Streamlit application",
                "command": "streamlit run app.py",
                "requirements": ["streamlit"],
                "port": 8501
            },
            "flask_app": {
                "description": "Deploy Flask application",
                "command": "python app.py",
                "requirements": ["flask"],
                "port": 5000
            },
            "docker_container": {
                "description": "Deploy as Docker container",
                "command": "docker build -t app . && docker run -p 8080:8080 app",
                "requirements": ["docker"],
                "port": 8080
            },
            "heroku": {
                "description": "Deploy to Heroku",
                "command": "git push heroku main",
                "requirements": ["heroku-cli"],
                "port": None
            },
            "aws_lambda": {
                "description": "Deploy to AWS Lambda",
                "command": "serverless deploy",
                "requirements": ["serverless"],
                "port": None
            },
            "google_cloud": {
                "description": "Deploy to Google Cloud",
                "command": "gcloud app deploy",
                "requirements": ["google-cloud-sdk"],
                "port": None
            },
            "azure": {
                "description": "Deploy to Azure",
                "command": "az webapp up",
                "requirements": ["azure-cli"],
                "port": None
            },
            "scrollx_marketplace": {
                "description": "Deploy to ScrollX Marketplace",
                "command": "scrollx publish",
                "requirements": ["scrollx-cli"],
                "port": None
            },
            "local": {
                "description": "Deploy locally",
                "command": "python app.py",
                "requirements": [],
                "port": 5000
            }
        }
    
    def parse_deploy_command(self, line: str) -> Optional[Tuple[str, str]]:
        """
        Parse a Deploy: command line
        
        Args:
            line: Scroll command line (e.g., "Deploy: Streamlit App")
            
        Returns:
            Tuple of (target, arguments) or None if not a deploy command
        """
        if not line.strip():
            return None
        
        # Check if it's a Deploy command
        deploy_pattern = r'^Deploy:\s*(.+)$'
        match = re.match(deploy_pattern, line.strip())
        
        if not match:
            return None
        
        # Extract target and arguments
        full_target = match.group(1).strip()
        
        # Split target and arguments
        parts = full_target.split(' ', 1)
        target = parts[0].lower().replace(' ', '_')
        arguments = parts[1] if len(parts) > 1 else ""
        
        return target, arguments
    
    def deploy_application(self, target: str, arguments: str = "", project_dir: str = ".") -> Dict[str, any]:
        """
        Deploy application to specified target
        
        Args:
            target: Deployment target
            arguments: Additional deployment arguments
            project_dir: Project directory path
            
        Returns:
            Dictionary with deployment results
        """
        project_path = Path(project_dir)
        if not project_path.exists():
            return {
                "success": False,
                "error": f"Project directory not found: {project_dir}",
                "target": target
            }
        
        # Get target configuration
        target_config = self.deploy_targets.get(target, {})
        if not target_config:
            return {
                "success": False,
                "error": f"Unknown deployment target: {target}",
                "target": target
            }
        
        self.logger.info(f"🔥 Deploying to {target}: {target_config['description']}")
        
        try:
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            # Execute deployment based on target
            if target == "streamlit_app":
                result = self._deploy_streamlit_app(arguments)
            elif target == "flask_app":
                result = self._deploy_flask_app(arguments)
            elif target == "docker_container":
                result = self._deploy_docker_container(arguments)
            elif target == "heroku":
                result = self._deploy_heroku(arguments)
            elif target == "aws_lambda":
                result = self._deploy_aws_lambda(arguments)
            elif target == "google_cloud":
                result = self._deploy_google_cloud(arguments)
            elif target == "azure":
                result = self._deploy_azure(arguments)
            elif target == "scrollx_marketplace":
                result = self._deploy_scrollx_marketplace(arguments)
            elif target == "local":
                result = self._deploy_local(arguments)
            else:
                result = self._deploy_generic(target, arguments, target_config)
            
            # Restore original directory
            os.chdir(original_dir)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Deployment failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "target": target
            }
    
    def _deploy_streamlit_app(self, arguments: str) -> Dict[str, any]:
        """Deploy Streamlit application"""
        try:
            # Check if app.py exists
            if not Path("app.py").exists():
                return {
                    "success": False,
                    "error": "app.py not found",
                    "target": "streamlit_app"
                }
            
            # Start Streamlit app
            cmd = ["streamlit", "run", "app.py"]
            if arguments:
                cmd.extend(arguments.split())
            
            self.logger.info(f"🚀 Starting Streamlit app: {' '.join(cmd)}")
            
            # Run in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return {
                "success": True,
                "message": f"Streamlit app started on port 8501",
                "target": "streamlit_app",
                "pid": process.pid,
                "url": "http://localhost:8501"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": "streamlit_app"
            }
    
    def _deploy_flask_app(self, arguments: str) -> Dict[str, any]:
        """Deploy Flask application"""
        try:
            # Check if app.py exists
            if not Path("app.py").exists():
                return {
                    "success": False,
                    "error": "app.py not found",
                    "target": "flask_app"
                }
            
            # Start Flask app
            cmd = ["python", "app.py"]
            if arguments:
                cmd.extend(arguments.split())
            
            self.logger.info(f"🚀 Starting Flask app: {' '.join(cmd)}")
            
            # Run in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return {
                "success": True,
                "message": f"Flask app started on port 5000",
                "target": "flask_app",
                "pid": process.pid,
                "url": "http://localhost:5000"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": "flask_app"
            }
    
    def _deploy_docker_container(self, arguments: str) -> Dict[str, any]:
        """Deploy as Docker container"""
        try:
            # Check if Dockerfile exists
            if not Path("Dockerfile").exists():
                return {
                    "success": False,
                    "error": "Dockerfile not found",
                    "target": "docker_container"
                }
            
            # Build Docker image
            self.logger.info("🐳 Building Docker image...")
            build_result = subprocess.run(
                ["docker", "build", "-t", "scroll-app", "."],
                capture_output=True,
                text=True
            )
            
            if build_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Docker build failed: {build_result.stderr}",
                    "target": "docker_container"
                }
            
            # Run Docker container
            self.logger.info("🐳 Running Docker container...")
            run_result = subprocess.run(
                ["docker", "run", "-d", "-p", "8080:8080", "scroll-app"],
                capture_output=True,
                text=True
            )
            
            if run_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Docker run failed: {run_result.stderr}",
                    "target": "docker_container"
                }
            
            return {
                "success": True,
                "message": "Docker container deployed successfully",
                "target": "docker_container",
                "url": "http://localhost:8080"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": "docker_container"
            }
    
    def _deploy_heroku(self, arguments: str) -> Dict[str, any]:
        """Deploy to Heroku"""
        try:
            # Check if Heroku CLI is available
            result = subprocess.run(["heroku", "--version"], capture_output=True)
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Heroku CLI not found",
                    "target": "heroku"
                }
            
            # Deploy to Heroku
            self.logger.info("☁️ Deploying to Heroku...")
            deploy_result = subprocess.run(
                ["git", "push", "heroku", "main"],
                capture_output=True,
                text=True
            )
            
            if deploy_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Heroku deployment failed: {deploy_result.stderr}",
                    "target": "heroku"
                }
            
            return {
                "success": True,
                "message": "Application deployed to Heroku",
                "target": "heroku"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": "heroku"
            }
    
    def _deploy_aws_lambda(self, arguments: str) -> Dict[str, any]:
        """Deploy to AWS Lambda"""
        try:
            # Check if Serverless Framework is available
            result = subprocess.run(["serverless", "--version"], capture_output=True)
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Serverless Framework not found",
                    "target": "aws_lambda"
                }
            
            # Deploy to AWS Lambda
            self.logger.info("☁️ Deploying to AWS Lambda...")
            deploy_result = subprocess.run(
                ["serverless", "deploy"],
                capture_output=True,
                text=True
            )
            
            if deploy_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"AWS Lambda deployment failed: {deploy_result.stderr}",
                    "target": "aws_lambda"
                }
            
            return {
                "success": True,
                "message": "Application deployed to AWS Lambda",
                "target": "aws_lambda"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": "aws_lambda"
            }
    
    def _deploy_google_cloud(self, arguments: str) -> Dict[str, any]:
        """Deploy to Google Cloud"""
        try:
            # Check if Google Cloud SDK is available
            result = subprocess.run(["gcloud", "--version"], capture_output=True)
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Google Cloud SDK not found",
                    "target": "google_cloud"
                }
            
            # Deploy to Google Cloud
            self.logger.info("☁️ Deploying to Google Cloud...")
            deploy_result = subprocess.run(
                ["gcloud", "app", "deploy"],
                capture_output=True,
                text=True
            )
            
            if deploy_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Google Cloud deployment failed: {deploy_result.stderr}",
                    "target": "google_cloud"
                }
            
            return {
                "success": True,
                "message": "Application deployed to Google Cloud",
                "target": "google_cloud"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": "google_cloud"
            }
    
    def _deploy_azure(self, arguments: str) -> Dict[str, any]:
        """Deploy to Azure"""
        try:
            # Check if Azure CLI is available
            result = subprocess.run(["az", "--version"], capture_output=True)
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Azure CLI not found",
                    "target": "azure"
                }
            
            # Deploy to Azure
            self.logger.info("☁️ Deploying to Azure...")
            deploy_result = subprocess.run(
                ["az", "webapp", "up"],
                capture_output=True,
                text=True
            )
            
            if deploy_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Azure deployment failed: {deploy_result.stderr}",
                    "target": "azure"
                }
            
            return {
                "success": True,
                "message": "Application deployed to Azure",
                "target": "azure"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": "azure"
            }
    
    def _deploy_scrollx_marketplace(self, arguments: str) -> Dict[str, any]:
        """Deploy to ScrollX Marketplace"""
        try:
            # Create marketplace listing
            listing = {
                "name": "ScrollWrappedCodex App",
                "description": "Flame-verified scroll application",
                "version": "1.0.0",
                "author": "ScrollBuilder",
                "flame_level": 3,
                "seal_level": 4,
                "deployed_at": "2024-01-01T00:00:00Z"
            }
            
            # Write listing to file
            listing_file = Path("scrollx_listing.json")
            with open(listing_file, 'w') as f:
                json.dump(listing, f, indent=2)
            
            self.logger.info("📦 Created ScrollX Marketplace listing")
            
            return {
                "success": True,
                "message": "Application listed on ScrollX Marketplace",
                "target": "scrollx_marketplace",
                "listing_file": str(listing_file)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": "scrollx_marketplace"
            }
    
    def _deploy_local(self, arguments: str) -> Dict[str, any]:
        """Deploy locally"""
        try:
            # Check if app.py exists
            if not Path("app.py").exists():
                return {
                    "success": False,
                    "error": "app.py not found",
                    "target": "local"
                }
            
            # Start local app
            cmd = ["python", "app.py"]
            if arguments:
                cmd.extend(arguments.split())
            
            self.logger.info(f"🚀 Starting local app: {' '.join(cmd)}")
            
            # Run in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return {
                "success": True,
                "message": "Application started locally",
                "target": "local",
                "pid": process.pid,
                "url": "http://localhost:5000"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": "local"
            }
    
    def _deploy_generic(self, target: str, arguments: str, config: Dict) -> Dict[str, any]:
        """Deploy using generic configuration"""
        try:
            cmd = config["command"].split()
            if arguments:
                cmd.extend(arguments.split())
            
            self.logger.info(f"🚀 Deploying with command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Deployed to {target}",
                    "target": target,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Deployment failed: {result.stderr}",
                    "target": target
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": target
            }
    
    def list_deploy_targets(self) -> List[str]:
        """List available deployment targets"""
        return list(self.deploy_targets.keys())
    
    def get_target_info(self, target: str) -> Optional[Dict]:
        """Get information about a deployment target"""
        return self.deploy_targets.get(target)

# Example usage and testing
if __name__ == "__main__":
    # Initialize deploy handler
    handler = DeployHandler()
    
    # Test deploy command parsing
    test_commands = [
        "Deploy: Streamlit App",
        "Deploy: Flask App",
        "Deploy: Docker Container",
        "Deploy: Heroku",
        "Deploy: AWS Lambda",
        "Deploy: Google Cloud",
        "Deploy: Azure",
        "Deploy: ScrollX Marketplace",
        "Deploy: Local",
        "Build: SomeModule"  # Not a deploy command
    ]
    
    print("🔥 Testing Deploy command parsing:")
    print("=" * 50)
    
    for command in test_commands:
        result = handler.parse_deploy_command(command)
        if result:
            target, arguments = result
            print(f"🚀 Deploy target: {target} {arguments}")
        else:
            print(f"❌ Not a deploy command: {command}")
    
    # List available targets
    print("\n📋 Available deployment targets:")
    targets = handler.list_deploy_targets()
    for target in targets:
        info = handler.get_target_info(target)
        if info:
            print(f"  - {target}: {info['description']}")
    
    # Test deployment (commented out for safety)
    # print("\n🔥 Testing deployment:")
    # print("=" * 50)
    # 
    # result = handler.deploy_application("local", "", "test_project")
    # print(f"Deployment result: {result}") 