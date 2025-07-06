#!/usr/bin/env python3
"""
Scroll Executor Hook
Integrates all executor patch components into ScribeCodex.execute()
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .gather_installer import GatherInstaller
from .scroll_file_writer import ScrollFileWriter
from .scroll_folder_generator import ScrollFolderGenerator
from .deploy_handler import DeployHandler

class ScrollExecutorHook:
    """Sacred hook for integrating executor patch components into ScribeCodex"""
    
    def __init__(self, scribe_codex=None):
        self.scribe = scribe_codex
        self.gather_installer = GatherInstaller()
        self.file_writer = ScrollFileWriter()
        self.folder_generator = ScrollFolderGenerator()
        self.deploy_handler = DeployHandler()
        
        # Command patterns
        self.build_pattern = re.compile(r'^Build:\s*(\w+)(?:\s+(.+))?$')
        self.gather_pattern = re.compile(r'^Gather:\s*(.+)$')
        self.deploy_pattern = re.compile(r'^Deploy:\s*(.+)$')
        
    def set_scribe_codex(self, scribe_codex):
        """Set the ScribeCodex instance"""
        self.scribe = scribe_codex
    
    def hook_into_execute(self, original_execute_method):
        """
        Hook into the original ScribeCodex.execute() method
        
        Args:
            original_execute_method: The original execute method to wrap
            
        Returns:
            Wrapped execute method with patch functionality
        """
        def wrapped_execute(scroll_content: str) -> str:
            """Wrapped execute method with patch functionality"""
            
            # First run the original Codex execution
            original_result = original_execute_method(scroll_content)
            
            # Parse scroll content for patch commands
            lines = scroll_content.split('\n')
            patch_results = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Check for Gather commands
                if self.gather_pattern.match(line):
                    result = self._handle_gather_command(line)
                    if result:
                        patch_results.append(result)
                
                # Check for Build commands
                elif self.build_pattern.match(line):
                    result = self._handle_build_command(line)
                    if result:
                        patch_results.append(result)
                
                # Check for Deploy commands
                elif self.deploy_pattern.match(line):
                    result = self._handle_deploy_command(line)
                    if result:
                        patch_results.append(result)
            
            # Combine original result with patch results
            if patch_results:
                patch_summary = "\n\n🔥 PATCH EXECUTION RESULTS:\n" + "=" * 50 + "\n"
                for result in patch_results:
                    patch_summary += f"{result}\n"
                
                return original_result + patch_summary
            else:
                return original_result
        
        return wrapped_execute
    
    def _handle_gather_command(self, line: str) -> Optional[str]:
        """Handle Gather: command execution"""
        try:
            packages = self.gather_installer.parse_gather_command(line)
            if packages:
                print(f"📦 Installing packages: {packages}")
                results = self.gather_installer.install_packages(packages)
                
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                return f"📦 GATHER: Installed {success_count}/{total_count} packages"
            
        except Exception as e:
            return f"❌ GATHER ERROR: {str(e)}"
        
        return None
    
    def _handle_build_command(self, line: str) -> Optional[str]:
        """Handle Build: command execution"""
        try:
            result = self.file_writer.parse_build_command(line)
            if result:
                module_name, arguments = result
                print(f"🔨 Building module: {module_name}")
                
                success = self.file_writer.write_file(module_name, arguments)
                
                if success:
                    return f"🔨 BUILD: Created {module_name} successfully"
                else:
                    return f"❌ BUILD ERROR: Failed to create {module_name}"
            
        except Exception as e:
            return f"❌ BUILD ERROR: {str(e)}"
        
        return None
    
    def _handle_deploy_command(self, line: str) -> Optional[str]:
        """Handle Deploy: command execution"""
        try:
            result = self.deploy_handler.parse_deploy_command(line)
            if result:
                target, arguments = result
                print(f"🚀 Deploying to: {target}")
                
                deploy_result = self.deploy_handler.deploy_application(target, arguments)
                
                if deploy_result["success"]:
                    return f"🚀 DEPLOY: Successfully deployed to {target}"
                else:
                    return f"❌ DEPLOY ERROR: {deploy_result.get('error', 'Unknown error')}"
            
        except Exception as e:
            return f"❌ DEPLOY ERROR: {str(e)}"
        
        return None
    
    def create_project_from_scroll(self, scroll_file: str, project_name: Optional[str] = None) -> bool:
        """
        Create complete project from scroll file
        
        Args:
            scroll_file: Path to the scroll file
            project_name: Optional project name
            
        Returns:
            True if project created successfully
        """
        try:
            # Parse scroll file for requirements
            requirements = self.folder_generator.parse_scroll_file(scroll_file)
            
            if not requirements:
                print(f"❌ No requirements found in scroll file: {scroll_file}")
                return False
            
            # Generate project structure
            if not project_name:
                project_name = Path(scroll_file).stem
            
            success = self.folder_generator.generate_project_structure(project_name, requirements)
            
            if success:
                print(f"✅ Project created: {project_name}")
                
                # Install dependencies if any
                dependencies = requirements.get("dependencies", [])
                if dependencies:
                    print(f"📦 Installing {len(dependencies)} dependencies...")
                    self.gather_installer.install_packages(dependencies)
                
                return True
            else:
                print(f"❌ Failed to create project: {project_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating project: {str(e)}")
            return False
    
    def execute_scroll_with_patches(self, scroll_file: str) -> Dict[str, any]:
        """
        Execute scroll file with all patch functionality
        
        Args:
            scroll_file: Path to the scroll file
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Read scroll file
            with open(scroll_file, 'r', encoding='utf-8') as f:
                scroll_content = f.read()
            
            # Create project structure
            project_created = self.create_project_from_scroll(scroll_file)
            
            # Execute with ScribeCodex if available
            scribe_result = None
            if self.scribe:
                scribe_result = self.scribe.execute(scroll_content)
            
            # Parse for patch commands
            lines = scroll_content.split('\n')
            patch_results = {
                "gather": [],
                "build": [],
                "deploy": []
            }
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Gather commands
                if self.gather_pattern.match(line):
                    result = self._handle_gather_command(line)
                    if result:
                        patch_results["gather"].append(result)
                
                # Build commands
                elif self.build_pattern.match(line):
                    result = self._handle_build_command(line)
                    if result:
                        patch_results["build"].append(result)
                
                # Deploy commands
                elif self.deploy_pattern.match(line):
                    result = self._handle_deploy_command(line)
                    if result:
                        patch_results["deploy"].append(result)
            
            return {
                "success": True,
                "project_created": project_created,
                "scribe_result": scribe_result,
                "patch_results": patch_results,
                "scroll_file": scroll_file
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "scroll_file": scroll_file
            }
    
    def get_patch_status(self) -> Dict[str, any]:
        """Get status of all patch components"""
        return {
            "gather_installer": {
                "status": "active",
                "log_file": str(self.gather_installer.log_file)
            },
            "file_writer": {
                "status": "active",
                "output_dir": str(self.file_writer.output_dir)
            },
            "folder_generator": {
                "status": "active",
                "base_dir": str(self.folder_generator.base_dir)
            },
            "deploy_handler": {
                "status": "active",
                "log_file": str(self.deploy_handler.log_file)
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize hook
    hook = ScrollExecutorHook()
    
    # Test scroll file
    test_scroll_content = """
# Test scroll with patch commands
Gather: flask, flask-cors, loguru
Build: StreamPlayerModule
Build: UploadEpisodeEndpoint
Deploy: Streamlit App
Build: FlaskAPI
Gather: streamlit, plotly
Deploy: Local
"""
    
    # Create test scroll file
    with open("test_patch.scroll", "w") as f:
        f.write(test_scroll_content)
    
    print("🔥 Testing scroll executor patch:")
    print("=" * 50)
    
    # Execute scroll with patches
    result = hook.execute_scroll_with_patches("test_patch.scroll")
    
    if result["success"]:
        print("✅ Scroll executed with patches successfully")
        print(f"📁 Project created: {result['project_created']}")
        
        if result["patch_results"]:
            print("\n📋 Patch Results:")
            for category, results in result["patch_results"].items():
                if results:
                    print(f"  {category.upper()}:")
                    for res in results:
                        print(f"    {res}")
    else:
        print(f"❌ Scroll execution failed: {result.get('error', 'Unknown error')}")
    
    # Get patch status
    status = hook.get_patch_status()
    print(f"\n📊 Patch Status:")
    for component, info in status.items():
        print(f"  {component}: {info['status']}")
    
    # Clean up
    Path("test_patch.scroll").unlink(missing_ok=True) 