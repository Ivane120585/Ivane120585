#!/usr/bin/env python3
"""
ScrollVerse Execution Engine
Wraps ScribeCodex and handles package installation and folder creation
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import logging
from datetime import datetime

class ScrollExecutionEngine:
    """Sacred scroll execution engine"""
    
    def __init__(self):
        self.base_path = Path.cwd()
        self.log_file = "scroll_execution_log.txt"
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for execution engine"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def execute_scroll(self, scroll_code: str, user_id: int = None) -> Dict:
        """Execute a scroll and return results"""
        self.logger.info(f"🔥 Starting scroll execution for user {user_id}")
        
        results = {
            "success": True,
            "output": [],
            "errors": [],
            "files_created": [],
            "packages_installed": [],
            "execution_time": None
        }
        
        start_time = datetime.now()
        
        try:
            lines = scroll_code.strip().split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                self.logger.info(f"Processing line {line_num}: {line}")
                
                if line.startswith("Anoint:"):
                    result = self._handle_anoint(line, line_num)
                    results["output"].append(result)
                    
                elif line.startswith("Build:"):
                    result = self._handle_build(line, line_num)
                    results["output"].append(result)
                    if result.get("file_created"):
                        results["files_created"].append(result["file_created"])
                    
                elif line.startswith("Gather:"):
                    result = self._handle_gather(line, line_num)
                    results["output"].append(result)
                    if result.get("packages_installed"):
                        results["packages_installed"].extend(result["packages_installed"])
                    
                elif line.startswith("Deploy:"):
                    result = self._handle_deploy(line, line_num)
                    results["output"].append(result)
                    
                else:
                    result = self._handle_unknown(line, line_num)
                    results["output"].append(result)
                    results["errors"].append(f"Unknown command on line {line_num}")
        
        except Exception as e:
            self.logger.error(f"❌ Scroll execution failed: {str(e)}")
            results["success"] = False
            results["errors"].append(str(e))
        
        finally:
            end_time = datetime.now()
            results["execution_time"] = (end_time - start_time).total_seconds()
            self.logger.info(f"🔥 Scroll execution completed in {results['execution_time']:.2f}s")
        
        return results
    
    def _handle_anoint(self, line: str, line_num: int) -> Dict:
        """Handle Anoint command - create project structure"""
        try:
            project_name = line.split(":", 1)[1].strip()
            project_path = self.base_path / project_name
            
            if project_path.exists():
                return {
                    "type": "anoint",
                    "status": "warning",
                    "message": f"Project {project_name} already exists",
                    "line": line_num
                }
            
            # Create project structure
            project_path.mkdir(exist_ok=True)
            (project_path / "backend").mkdir(exist_ok=True)
            (project_path / "frontend").mkdir(exist_ok=True)
            (project_path / "docs").mkdir(exist_ok=True)
            
            # Create basic files
            self._create_file(project_path / "README.md", f"# {project_name}\n\nSacred flame-verified project.")
            self._create_file(project_path / "requirements.txt", "# Project dependencies\n")
            self._create_file(project_path / ".gitignore", "# Git ignore file\n__pycache__/\n*.pyc\n")
            
            self.logger.info(f"✅ Anointed project: {project_name}")
            
            return {
                "type": "anoint",
                "status": "success",
                "message": f"🔥 Anointed: {project_name}",
                "project_name": project_name,
                "line": line_num
            }
        
        except Exception as e:
            self.logger.error(f"❌ Anoint failed: {str(e)}")
            return {
                "type": "anoint",
                "status": "error",
                "message": f"Anoint failed: {str(e)}",
                "line": line_num
            }
    
    def _handle_build(self, line: str, line_num: int) -> Dict:
        """Handle Build command - create files"""
        try:
            file_path = line.split(":", 1)[1].strip()
            full_path = self.base_path / file_path
            
            # Create directory if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file with basic template
            content = self._get_file_template(file_path)
            self._create_file(full_path, content)
            
            self.logger.info(f"✅ Built file: {file_path}")
            
            return {
                "type": "build",
                "status": "success",
                "message": f"📝 Building: {file_path}",
                "file_created": file_path,
                "line": line_num
            }
        
        except Exception as e:
            self.logger.error(f"❌ Build failed: {str(e)}")
            return {
                "type": "build",
                "status": "error",
                "message": f"Build failed: {str(e)}",
                "line": line_num
            }
    
    def _handle_gather(self, line: str, line_num: int) -> Dict:
        """Handle Gather command - install packages"""
        try:
            packages = line.split(":", 1)[1].strip()
            package_list = [pkg.strip() for pkg in packages.split()]
            
            # Update requirements.txt
            requirements_path = self.base_path / "requirements.txt"
            if requirements_path.exists():
                with open(requirements_path, "a") as f:
                    f.write(f"\n# Added by scroll execution\n")
                    for pkg in package_list:
                        f.write(f"{pkg}\n")
            else:
                with open(requirements_path, "w") as f:
                    f.write("# Project dependencies\n")
                    for pkg in package_list:
                        f.write(f"{pkg}\n")
            
            # Install packages
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + package_list,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    self.logger.info(f"✅ Gathered packages: {packages}")
                    return {
                        "type": "gather",
                        "status": "success",
                        "message": f"📦 Gathering: {packages}",
                        "packages_installed": package_list,
                        "line": line_num
                    }
                else:
                    self.logger.warning(f"⚠️ Package installation had issues: {result.stderr}")
                    return {
                        "type": "gather",
                        "status": "warning",
                        "message": f"📦 Gathering: {packages} (with warnings)",
                        "packages_installed": package_list,
                        "line": line_num
                    }
            
            except subprocess.TimeoutExpired:
                return {
                    "type": "gather",
                    "status": "error",
                    "message": f"Package installation timed out",
                    "line": line_num
                }
        
        except Exception as e:
            self.logger.error(f"❌ Gather failed: {str(e)}")
            return {
                "type": "gather",
                "status": "error",
                "message": f"Gather failed: {str(e)}",
                "line": line_num
            }
    
    def _handle_deploy(self, line: str, line_num: int) -> Dict:
        """Handle Deploy command - deployment logic"""
        try:
            deployment_target = line.split(":", 1)[1].strip()
            
            # Simple deployment simulation
            self.logger.info(f"🚀 Deploying to: {deployment_target}")
            
            return {
                "type": "deploy",
                "status": "success",
                "message": f"🚀 Deploying to: {deployment_target}",
                "deployment_target": deployment_target,
                "line": line_num
            }
        
        except Exception as e:
            self.logger.error(f"❌ Deploy failed: {str(e)}")
            return {
                "type": "deploy",
                "status": "error",
                "message": f"Deploy failed: {str(e)}",
                "line": line_num
            }
    
    def _handle_unknown(self, line: str, line_num: int) -> Dict:
        """Handle unknown commands"""
        return {
            "type": "unknown",
            "status": "error",
            "message": f"❓ Unknown command: {line}",
            "line": line_num
        }
    
    def _create_file(self, file_path: Path, content: str):
        """Create a file with content"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _get_file_template(self, file_path: str) -> str:
        """Get template content based on file type"""
        file_ext = Path(file_path).suffix.lower()
        
        templates = {
            ".py": """#!/usr/bin/env python3
\"\"\"
Generated by ScrollVerse Execution Engine
\"\"\"

def main():
    print("🔥 Sacred flame-verified code")
    
if __name__ == "__main__":
    main()
""",
            ".js": """// Generated by ScrollVerse Execution Engine
console.log("🔥 Sacred flame-verified JavaScript");
""",
            ".html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ScrollVerse Generated</title>
</head>
<body>
    <h1>🔥 Sacred Flame-Verified HTML</h1>
</body>
</html>
""",
            ".css": """/* Generated by ScrollVerse Execution Engine */
body {
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #ff6b35, #f7931e);
    color: white;
}
""",
            ".json": """{
    "generated_by": "ScrollVerse Execution Engine",
    "timestamp": "2024-01-30T00:00:00Z",
    "sacred": true
}
""",
            ".md": """# Generated by ScrollVerse Execution Engine

🔥 Sacred flame-verified documentation
"""
        }
        
        return templates.get(file_ext, f"# Generated file: {file_path}\n# Created by ScrollVerse Execution Engine\n")
    
    def get_execution_summary(self, results: Dict) -> str:
        """Get a formatted execution summary"""
        summary_lines = []
        
        if results["success"]:
            summary_lines.append("🔥 Scroll execution completed successfully!")
        else:
            summary_lines.append("❌ Scroll execution failed!")
        
        summary_lines.append(f"⏱️ Execution time: {results['execution_time']:.2f}s")
        
        if results["files_created"]:
            summary_lines.append(f"📁 Files created: {len(results['files_created'])}")
            for file in results["files_created"]:
                summary_lines.append(f"  - {file}")
        
        if results["packages_installed"]:
            summary_lines.append(f"📦 Packages installed: {len(results['packages_installed'])}")
            for pkg in results["packages_installed"]:
                summary_lines.append(f"  - {pkg}")
        
        if results["errors"]:
            summary_lines.append(f"❌ Errors: {len(results['errors'])}")
            for error in results["errors"]:
                summary_lines.append(f"  - {error}")
        
        return "\n".join(summary_lines)

# Example usage
if __name__ == "__main__":
    engine = ScrollExecutionEngine()
    
    # Test scroll
    test_scroll = """
Anoint: ScrollRadio
Build: backend/app.py
Build: frontend/index.html
Gather: flask requests
Deploy: localhost:5000
"""
    
    results = engine.execute_scroll(test_scroll)
    print(engine.get_execution_summary(results)) 