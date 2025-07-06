#!/usr/bin/env python3
"""
Gather Installer
Parses Gather: commands from .scroll files and installs Python packages
"""

import subprocess
import sys
import re
import logging
from typing import List, Dict, Optional
from pathlib import Path

class GatherInstaller:
    """Sacred installer for gathering Python packages from scroll commands"""
    
    def __init__(self, log_file: str = "flame_trace.log"):
        self.log_file = Path(log_file)
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for installation traces"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def parse_gather_command(self, line: str) -> Optional[List[str]]:
        """
        Parse a Gather: command line
        
        Args:
            line: Scroll command line (e.g., "Gather: flask, flask-cors, loguru")
            
        Returns:
            List of package names to install, or None if not a gather command
        """
        if not line.strip():
            return None
        
        # Check if it's a Gather command
        gather_pattern = r'^Gather:\s*(.+)$'
        match = re.match(gather_pattern, line.strip())
        
        if not match:
            return None
        
        # Extract package names
        packages_str = match.group(1).strip()
        
        # Split by comma and clean up
        packages = []
        for package in packages_str.split(','):
            package = package.strip()
            if package:
                packages.append(package)
        
        return packages if packages else None
    
    def install_packages(self, packages: List[str], upgrade: bool = False) -> Dict[str, bool]:
        """
        Install Python packages using pip
        
        Args:
            packages: List of package names to install
            upgrade: Whether to upgrade existing packages
            
        Returns:
            Dictionary mapping package names to installation success status
        """
        results = {}
        
        for package in packages:
            try:
                self.logger.info(f"🔥 Installing package: {package}")
                
                # Build pip command
                cmd = [sys.executable, "-m", "pip", "install"]
                if upgrade:
                    cmd.append("--upgrade")
                cmd.append(package)
                
                # Execute installation
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    self.logger.info(f"✅ Successfully installed: {package}")
                    results[package] = True
                else:
                    self.logger.error(f"❌ Failed to install {package}: {result.stderr}")
                    results[package] = False
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"⏰ Timeout installing: {package}")
                results[package] = False
            except Exception as e:
                self.logger.error(f"🔥 Error installing {package}: {str(e)}")
                results[package] = False
        
        return results
    
    def install_from_requirements(self, requirements_file: str) -> Dict[str, bool]:
        """
        Install packages from a requirements.txt file
        
        Args:
            requirements_file: Path to requirements.txt file
            
        Returns:
            Dictionary mapping package names to installation success status
        """
        req_file = Path(requirements_file)
        if not req_file.exists():
            self.logger.error(f"❌ Requirements file not found: {requirements_file}")
            return {}
        
        try:
            self.logger.info(f"🔥 Installing from requirements: {requirements_file}")
            
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for requirements
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ Successfully installed from requirements: {requirements_file}")
                return {"requirements_file": True}
            else:
                self.logger.error(f"❌ Failed to install from requirements: {result.stderr}")
                return {"requirements_file": False}
                
        except Exception as e:
            self.logger.error(f"🔥 Error installing from requirements: {str(e)}")
            return {"requirements_file": False}
    
    def parse_scroll_file(self, scroll_file: str) -> List[str]:
        """
        Parse a scroll file and extract all Gather commands
        
        Args:
            scroll_file: Path to the scroll file
            
        Returns:
            List of all packages found in Gather commands
        """
        scroll_path = Path(scroll_file)
        if not scroll_path.exists():
            self.logger.error(f"❌ Scroll file not found: {scroll_file}")
            return []
        
        all_packages = []
        
        try:
            with open(scroll_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    packages = self.parse_gather_command(line)
                    if packages:
                        self.logger.info(f"📜 Found Gather command at line {line_num}: {packages}")
                        all_packages.extend(packages)
        
        except Exception as e:
            self.logger.error(f"🔥 Error parsing scroll file: {str(e)}")
        
        return all_packages
    
    def install_from_scroll(self, scroll_file: str, upgrade: bool = False) -> Dict[str, bool]:
        """
        Parse scroll file and install all packages from Gather commands
        
        Args:
            scroll_file: Path to the scroll file
            upgrade: Whether to upgrade existing packages
            
        Returns:
            Dictionary mapping package names to installation success status
        """
        packages = self.parse_scroll_file(scroll_file)
        
        if not packages:
            self.logger.warning(f"⚠️ No Gather commands found in: {scroll_file}")
            return {}
        
        # Remove duplicates while preserving order
        unique_packages = []
        seen = set()
        for package in packages:
            if package not in seen:
                unique_packages.append(package)
                seen.add(package)
        
        self.logger.info(f"🔥 Installing {len(unique_packages)} packages from scroll file")
        return self.install_packages(unique_packages, upgrade)
    
    def create_requirements_file(self, packages: List[str], output_file: str = "requirements.txt") -> bool:
        """
        Create a requirements.txt file from package list
        
        Args:
            packages: List of package names
            output_file: Output file path
            
        Returns:
            True if file created successfully
        """
        try:
            with open(output_file, 'w') as f:
                for package in packages:
                    f.write(f"{package}\n")
            
            self.logger.info(f"📄 Created requirements file: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"🔥 Error creating requirements file: {str(e)}")
            return False
    
    def check_package_installed(self, package: str) -> bool:
        """
        Check if a package is already installed
        
        Args:
            package: Package name to check
            
        Returns:
            True if package is installed
        """
        try:
            cmd = [sys.executable, "-m", "pip", "show", package]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_installed_packages(self) -> List[str]:
        """
        Get list of currently installed packages
        
        Returns:
            List of installed package names
        """
        try:
            cmd = [sys.executable, "-m", "pip", "list", "--format=freeze"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                packages = []
                for line in result.stdout.split('\n'):
                    if line.strip():
                        package_name = line.split('==')[0]
                        packages.append(package_name)
                return packages
            else:
                self.logger.error(f"❌ Failed to get installed packages: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"🔥 Error getting installed packages: {str(e)}")
            return []

# Example usage and testing
if __name__ == "__main__":
    # Initialize installer
    installer = GatherInstaller()
    
    # Test parsing
    test_commands = [
        "Gather: flask, flask-cors, loguru",
        "Gather: requests",
        "Gather: numpy, pandas, matplotlib",
        "Build: SomeModule",  # Not a gather command
        "Gather: streamlit, plotly, altair"
    ]
    
    print("🔥 Testing Gather command parsing:")
    print("=" * 50)
    
    for command in test_commands:
        packages = installer.parse_gather_command(command)
        if packages:
            print(f"📦 Found packages: {packages}")
        else:
            print(f"❌ Not a gather command: {command}")
    
    # Test installation (commented out for safety)
    # print("\n🔥 Testing package installation:")
    # print("=" * 50)
    # 
    # test_packages = ["requests", "loguru"]
    # results = installer.install_packages(test_packages)
    # 
    # for package, success in results.items():
    #     status = "✅" if success else "❌"
    #     print(f"{status} {package}")
    
    # Test scroll file parsing
    print("\n🔥 Testing scroll file parsing:")
    print("=" * 50)
    
    # Create test scroll file
    test_scroll_content = """
# Test scroll file
Gather: flask, flask-cors, loguru
Build: SomeModule
Gather: requests, numpy
Deploy: Application
Gather: streamlit, plotly
"""
    
    with open("test_gather.scroll", "w") as f:
        f.write(test_scroll_content)
    
    packages = installer.parse_scroll_file("test_gather.scroll")
    print(f"📦 Packages found: {packages}")
    
    # Clean up
    Path("test_gather.scroll").unlink(missing_ok=True) 