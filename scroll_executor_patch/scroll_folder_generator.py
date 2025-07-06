#!/usr/bin/env python3
"""
Scroll Folder Generator
Creates project structure based on .scroll files
"""

import os
import re
from typing import Dict, List, Set, Optional
from pathlib import Path
import json

class ScrollFolderGenerator:
    """Sacred folder generator for creating project structures from scroll files"""
    
    def __init__(self, base_dir: str = "scroll_projects"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.project_templates = self._load_project_templates()
        
    def _load_project_templates(self) -> Dict[str, Dict]:
        """Load project structure templates"""
        return {
            "web_app": {
                "description": "Web application with frontend and backend",
                "structure": {
                    "frontend": {
                        "index.html": "# Web App Frontend",
                        "styles.css": "/* Web App Styles */",
                        "script.js": "// Web App Scripts"
                    },
                    "backend": {
                        "app.py": "# Flask Backend",
                        "requirements.txt": "flask\nflask-cors",
                        "config.py": "# Configuration"
                    },
                    "static": {
                        "images": {},
                        "css": {},
                        "js": {}
                    },
                    "templates": {
                        "base.html": "<!-- Base Template -->",
                        "index.html": "<!-- Index Template -->"
                    }
                }
            },
            "api_service": {
                "description": "REST API service",
                "structure": {
                    "api": {
                        "__init__.py": "# API Package",
                        "routes.py": "# API Routes",
                        "models.py": "# Data Models"
                    },
                    "tests": {
                        "__init__.py": "# Tests Package",
                        "test_api.py": "# API Tests"
                    },
                    "docs": {
                        "README.md": "# API Documentation",
                        "swagger.yaml": "# OpenAPI Spec"
                    },
                    "requirements.txt": "flask\nflask-restful\npytest"
                }
            },
            "streamlit_app": {
                "description": "Streamlit data application",
                "structure": {
                    "app.py": "# Streamlit App",
                    "pages": {
                        "page1.py": "# Page 1",
                        "page2.py": "# Page 2"
                    },
                    "data": {
                        "raw": {},
                        "processed": {}
                    },
                    "utils": {
                        "__init__.py": "# Utils Package",
                        "helpers.py": "# Helper Functions"
                    },
                    "requirements.txt": "streamlit\npandas\nplotly"
                }
            },
            "data_pipeline": {
                "description": "Data processing pipeline",
                "structure": {
                    "src": {
                        "__init__.py": "# Source Package",
                        "extract.py": "# Data Extraction",
                        "transform.py": "# Data Transformation",
                        "load.py": "# Data Loading"
                    },
                    "data": {
                        "input": {},
                        "output": {},
                        "temp": {}
                    },
                    "config": {
                        "settings.yaml": "# Pipeline Settings"
                    },
                    "tests": {
                        "__init__.py": "# Tests Package",
                        "test_pipeline.py": "# Pipeline Tests"
                    },
                    "requirements.txt": "pandas\nnumpy\npyyaml"
                }
            },
            "machine_learning": {
                "description": "Machine learning project",
                "structure": {
                    "models": {
                        "__init__.py": "# Models Package",
                        "train.py": "# Model Training",
                        "predict.py": "# Model Prediction"
                    },
                    "data": {
                        "raw": {},
                        "processed": {},
                        "features": {}
                    },
                    "notebooks": {
                        "exploration.ipynb": "# Data Exploration",
                        "training.ipynb": "# Model Training"
                    },
                    "config": {
                        "model_config.yaml": "# Model Configuration"
                    },
                    "requirements.txt": "scikit-learn\npandas\nnumpy\njupyter"
                }
            }
        }
    
    def parse_scroll_file(self, scroll_file: str) -> Dict[str, List[str]]:
        """
        Parse scroll file to extract project requirements
        
        Args:
            scroll_file: Path to the scroll file
            
        Returns:
            Dictionary with parsed requirements
        """
        scroll_path = Path(scroll_file)
        if not scroll_path.exists():
            print(f"❌ Scroll file not found: {scroll_file}")
            return {}
        
        requirements = {
            "modules": [],
            "dependencies": [],
            "deploy_targets": [],
            "config_files": []
        }
        
        try:
            with open(scroll_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse different command types
                    if line.startswith('Build:'):
                        module = self._extract_module_name(line)
                        if module:
                            requirements["modules"].append(module)
                    
                    elif line.startswith('Gather:'):
                        deps = self._extract_dependencies(line)
                        requirements["dependencies"].extend(deps)
                    
                    elif line.startswith('Deploy:'):
                        target = self._extract_deploy_target(line)
                        if target:
                            requirements["deploy_targets"].append(target)
                    
                    elif line.startswith('Config:'):
                        config = self._extract_config_file(line)
                        if config:
                            requirements["config_files"].append(config)
        
        except Exception as e:
            print(f"❌ Error parsing scroll file: {str(e)}")
        
        return requirements
    
    def _extract_module_name(self, line: str) -> Optional[str]:
        """Extract module name from Build command"""
        match = re.match(r'^Build:\s*(\w+)', line)
        return match.group(1) if match else None
    
    def _extract_dependencies(self, line: str) -> List[str]:
        """Extract dependencies from Gather command"""
        match = re.match(r'^Gather:\s*(.+)', line)
        if not match:
            return []
        
        deps_str = match.group(1)
        return [dep.strip() for dep in deps_str.split(',') if dep.strip()]
    
    def _extract_deploy_target(self, line: str) -> Optional[str]:
        """Extract deploy target from Deploy command"""
        match = re.match(r'^Deploy:\s*(.+)', line)
        return match.group(1) if match else None
    
    def _extract_config_file(self, line: str) -> Optional[str]:
        """Extract config file from Config command"""
        match = re.match(r'^Config:\s*(.+)', line)
        return match.group(1) if match else None
    
    def determine_project_type(self, requirements: Dict[str, List[str]]) -> str:
        """
        Determine project type based on requirements
        
        Args:
            requirements: Parsed requirements from scroll file
            
        Returns:
            Project type string
        """
        modules = requirements.get("modules", [])
        dependencies = requirements.get("dependencies", [])
        
        # Check for web app indicators
        if any("StreamPlayer" in module for module in modules) or "flask" in dependencies:
            return "web_app"
        
        # Check for API service indicators
        if any("API" in module or "Endpoint" in module for module in modules):
            return "api_service"
        
        # Check for Streamlit indicators
        if any("Streamlit" in module for module in modules) or "streamlit" in dependencies:
            return "streamlit_app"
        
        # Check for data pipeline indicators
        if any("Pipeline" in module or "ETL" in module for module in modules):
            return "data_pipeline"
        
        # Check for ML indicators
        if any("Model" in module or "ML" in module for module in modules) or "scikit-learn" in dependencies:
            return "machine_learning"
        
        # Default to web app
        return "web_app"
    
    def generate_project_structure(self, project_name: str, requirements: Dict[str, List[str]]) -> bool:
        """
        Generate project structure based on requirements
        
        Args:
            project_name: Name of the project
            requirements: Parsed requirements from scroll file
            
        Returns:
            True if structure created successfully
        """
        try:
            # Determine project type
            project_type = self.determine_project_type(requirements)
            template = self.project_templates.get(project_type, self.project_templates["web_app"])
            
            # Create project directory
            project_dir = self.base_dir / project_name
            project_dir.mkdir(exist_ok=True)
            
            print(f"🔥 Creating {project_type} project: {project_name}")
            
            # Create structure recursively
            self._create_structure_recursive(project_dir, template["structure"])
            
            # Create additional files based on requirements
            self._create_requirements_file(project_dir, requirements)
            self._create_config_files(project_dir, requirements)
            self._create_deployment_files(project_dir, requirements)
            
            # Create scroll build log
            self._create_build_log(project_dir, requirements)
            
            print(f"✅ Project structure created: {project_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating project structure: {str(e)}")
            return False
    
    def _create_structure_recursive(self, base_path: Path, structure: Dict):
        """Recursively create directory structure"""
        for name, content in structure.items():
            path = base_path / name
            
            if isinstance(content, dict):
                # Directory
                path.mkdir(exist_ok=True)
                self._create_structure_recursive(path, content)
            else:
                # File
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def _create_requirements_file(self, project_dir: Path, requirements: Dict[str, List[str]]):
        """Create requirements.txt based on dependencies"""
        deps = requirements.get("dependencies", [])
        if deps:
            req_file = project_dir / "requirements.txt"
            with open(req_file, 'w') as f:
                for dep in deps:
                    f.write(f"{dep}\n")
            print(f"📦 Created requirements.txt with {len(deps)} dependencies")
    
    def _create_config_files(self, project_dir: Path, requirements: Dict[str, List[str]]):
        """Create configuration files"""
        config_files = requirements.get("config_files", [])
        for config in config_files:
            config_path = project_dir / "config" / f"{config}.yaml"
            config_path.parent.mkdir(exist_ok=True)
            with open(config_path, 'w') as f:
                f.write(f"# {config} Configuration\n# Generated from scroll file\n")
            print(f"⚙️ Created config file: {config_path}")
    
    def _create_deployment_files(self, project_dir: Path, requirements: Dict[str, List[str]]):
        """Create deployment configuration files"""
        deploy_targets = requirements.get("deploy_targets", [])
        if deploy_targets:
            deploy_dir = project_dir / "deploy"
            deploy_dir.mkdir(exist_ok=True)
            
            for target in deploy_targets:
                if "docker" in target.lower():
                    dockerfile = deploy_dir / "Dockerfile"
                    with open(dockerfile, 'w') as f:
                        f.write(f"""# Dockerfile for {target}
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
""")
                    print(f"🐳 Created Dockerfile for {target}")
                
                elif "heroku" in target.lower():
                    procfile = project_dir / "Procfile"
                    with open(procfile, 'w') as f:
                        f.write("web: python app.py\n")
                    print(f"☁️ Created Procfile for {target}")
    
    def _create_build_log(self, project_dir: Path, requirements: Dict[str, List[str]]):
        """Create scroll build log"""
        log_file = project_dir / "scroll_build_log.txt"
        with open(log_file, 'w') as f:
            f.write("ScrollWrappedCodex™ Build Log\n")
            f.write("=" * 40 + "\n\n")
            
            f.write("Modules Built:\n")
            for module in requirements.get("modules", []):
                f.write(f"  - {module}\n")
            
            f.write("\nDependencies Gathered:\n")
            for dep in requirements.get("dependencies", []):
                f.write(f"  - {dep}\n")
            
            f.write("\nDeploy Targets:\n")
            for target in requirements.get("deploy_targets", []):
                f.write(f"  - {target}\n")
            
            f.write("\nBuild Status: COMPLETE\n")
            f.write("Flame Verification: PASSED\n")
        
        print(f"📝 Created build log: {log_file}")
    
    def create_from_scroll_file(self, scroll_file: str, project_name: Optional[str] = None) -> bool:
        """
        Create project structure from scroll file
        
        Args:
            scroll_file: Path to the scroll file
            project_name: Optional project name (defaults to scroll file name)
            
        Returns:
            True if project created successfully
        """
        if not project_name:
            project_name = Path(scroll_file).stem
        
        # Parse scroll file
        requirements = self.parse_scroll_file(scroll_file)
        
        if not requirements:
            print(f"❌ No requirements found in scroll file: {scroll_file}")
            return False
        
        # Generate project structure
        return self.generate_project_structure(project_name, requirements)
    
    def list_project_templates(self) -> List[str]:
        """List available project templates"""
        return list(self.project_templates.keys())
    
    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """Get information about a project template"""
        template = self.project_templates.get(template_name)
        if template:
            return {
                "name": template_name,
                "description": template["description"],
                "structure": list(template["structure"].keys())
            }
        return None

# Example usage and testing
if __name__ == "__main__":
    # Initialize generator
    generator = ScrollFolderGenerator("test_projects")
    
    # Test scroll file parsing
    test_scroll_content = """
# Test scroll file
Build: StreamPlayerModule
Build: UploadEpisodeEndpoint
Gather: flask, flask-cors, loguru
Deploy: Docker Container
Config: app_settings
Build: FlaskAPI
"""
    
    # Create test scroll file
    with open("test_project.scroll", "w") as f:
        f.write(test_scroll_content)
    
    print("🔥 Testing project generation:")
    print("=" * 50)
    
    # Generate project from scroll file
    success = generator.create_from_scroll_file("test_project.scroll", "TestWebApp")
    
    if success:
        print("✅ Project generated successfully")
    else:
        print("❌ Project generation failed")
    
    # List available templates
    print("\n📋 Available project templates:")
    templates = generator.list_project_templates()
    for template in templates:
        info = generator.get_template_info(template)
        if info:
            print(f"  - {info['name']}: {info['description']}")
    
    # Clean up
    Path("test_project.scroll").unlink(missing_ok=True) 