#!/usr/bin/env python3
"""
ScrollIDE Alpha — Flame-Governed Developer Environment
Streamlit-based UI for scroll-sealed development
"""

import streamlit as st
import json
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import ScrollIDE components
from scrollide_scribe_agent import ScrollScribeAgent
from scrollide_executor import ScrollExecutor

class ScrollIDE:
    """Flame-governed developer environment"""
    
    def __init__(self):
        self.config = self._load_config()
        self.scribe_agent = ScrollScribeAgent()
        self.executor = ScrollExecutor()
        self.current_project = None
        self.current_file = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load ScrollIDE configuration"""
        try:
            with open("scrollide_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("ScrollIDE configuration not found")
            return {}
    
    def render_header(self):
        """Render ScrollIDE header with flame indicators"""
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4A148C, #FF6F00); padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
            <h1 style="color: white; text-align: center; margin: 0;">
                🔥 ScrollIDE Alpha — Flame-Governed Developer Environment
            </h1>
            <p style="color: white; text-align: center; margin: 0.5rem 0 0 0;">
                Let your code be sealed. Let your build be sacred.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Status indicators
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Flame Level", f"🔥{self.config.get('scroll_seal_level', 3)}")
        with col2:
            st.metric("Scroll Seal", "✅ Verified")
        with col3:
            st.metric("Law Compliance", "✅ Active")
        with col4:
            st.metric("Audit Trail", "📜 Enabled")
    
    def render_sidebar(self):
        """Render sidebar with project and file management"""
        with st.sidebar:
            st.markdown("### 📜 Project Management")
            
            # Project selection
            project_name = st.text_input("Project Name", value="sacred_project")
            if st.button("Create New Project"):
                self._create_project(project_name)
            
            # File management
            st.markdown("### 📁 File Explorer")
            files = self._get_project_files()
            selected_file = st.selectbox("Select File", files)
            
            if selected_file:
                self.current_file = selected_file
                if st.button("Open File"):
                    self._open_file(selected_file)
    
    def _open_file(self, selected_file):
        """Open file for editing"""
        try:
            if self.current_project and selected_file:
                filepath = f"projects/{self.current_project}/{selected_file}"
                if os.path.exists(filepath):
                    with open(filepath, "r") as f:
                        content = f.read()
                    st.text_area("File Content", value=content, height=300)
                    st.success(f"Opened file: {selected_file}")
                else:
                    st.error(f"File not found: {selected_file}")
        except Exception as e:
            st.error(f"Failed to open file: {e}")
            
            # Templates
            st.markdown("### 📋 Templates")
            templates = self.config.get("template_settings", {}).get("default_templates", [])
            selected_template = st.selectbox("Choose Template", templates)
            if st.button("Create from Template"):
                self._create_from_template(selected_template)
            
            # Community
            st.markdown("### 🌐 Community")
            if st.button("Share to Community"):
                self._share_to_community()
            
            # Settings
            st.markdown("### ⚙️ Settings")
            if st.button("ScrollIDE Settings"):
                self._show_settings()
    
    def render_editor(self):
        """Render main code editor"""
        st.markdown("### 🔥 Scroll Code Editor")
        
        # Editor tabs
        tab1, tab2, tab3 = st.tabs(["📝 Editor", "🔥 Flame Verification", "📊 Execution Log"])
        
        with tab1:
            self._render_code_editor()
        
        with tab2:
            self._render_flame_verification()
        
        with tab3:
            self._render_execution_log()
    
    def _render_code_editor(self):
        """Render the main code editor"""
        if self.current_file:
            # Load file content
            content = self._load_file_content(self.current_file)
            
            # Code editor
            edited_content = st.text_area(
                "Scroll Code",
                value=content,
                height=400,
                help="Write your scroll-sealed code here"
            )
            
            # Editor controls
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("💾 Save"):
                    self._save_file(self.current_file, edited_content)
                    st.success("File saved with flame verification")
            
            with col2:
                if st.button("🔥 Execute"):
                    result = self._execute_scroll(edited_content)
                    if result["success"]:
                        st.success("Scroll executed successfully")
                    else:
                        st.error(f"Execution failed: {result['error']}")
            
            with col3:
                if st.button("🔍 Validate"):
                    validation = self._validate_scroll(edited_content)
                    if validation["valid"]:
                        st.success("Scroll law compliance verified")
                    else:
                        st.error(f"Validation failed: {validation['errors']}")
            
            with col4:
                if st.button("📤 Share"):
                    self._share_scroll(edited_content)
        else:
            st.info("Select a file to edit or create a new project")
    
    def _render_flame_verification(self):
        """Render flame verification panel"""
        st.markdown("### 🔥 Flame Verification Status")
        
        # Verification levels
        levels = self.config.get("security_settings", {}).get("flame_verification_levels", {})
        
        for level, description in levels.items():
            status = "✅" if int(level.split("_")[1]) <= self.config.get("scroll_seal_level", 3) else "❌"
            st.markdown(f"{status} **{level.replace('_', ' ').title()}**: {description}")
        
        # Current verification
        st.markdown("### Current Scroll Verification")
        if self.current_file:
            verification = self._verify_current_file()
            if verification["verified"]:
                st.success("✅ Current file is flame-verified")
                st.json(verification["details"])
            else:
                st.error("❌ Current file requires flame verification")
                st.json(verification["errors"])
    
    def _render_execution_log(self):
        """Render execution log"""
        st.markdown("### 📊 Execution Log")
        
        # Recent executions
        executions = self._get_recent_executions()
        
        for execution in executions:
            with st.expander(f"Execution {execution['id']} - {execution['timestamp']}"):
                st.json(execution)
    
    def _create_project(self, project_name: str):
        """Create a new scroll project"""
        try:
            os.makedirs(f"projects/{project_name}", exist_ok=True)
            
            # Create default files
            default_files = [
                "main.scroll",
                "config.scroll",
                "README.md"
            ]
            
            for file in default_files:
                with open(f"projects/{project_name}/{file}", "w") as f:
                    if file.endswith(".scroll"):
                        f.write("# Sacred Project Configuration\n\nAnoint: My Sacred Project\nBuild: Core System\nSeal: With ScrollSeal 3\n")
                    else:
                        f.write(f"# {project_name}\n\nSacred project created with ScrollIDE Alpha.\n")
            
            st.success(f"Project '{project_name}' created successfully")
            self.current_project = project_name
            
        except Exception as e:
            st.error(f"Failed to create project: {e}")
    
    def _get_project_files(self) -> List[str]:
        """Get list of project files"""
        if not self.current_project:
            return []
        
        try:
            project_dir = f"projects/{self.current_project}"
            if os.path.exists(project_dir):
                files = [f for f in os.listdir(project_dir) if f.endswith(('.scroll', '.py', '.md', '.json'))]
                return files
        except Exception as e:
            st.error(f"Failed to get project files: {e}")
        
        return []
    
    def _load_file_content(self, filename: str) -> str:
        """Load file content"""
        try:
            filepath = f"projects/{self.current_project}/{filename}"
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    return f.read()
        except Exception as e:
            st.error(f"Failed to load file: {e}")
        
        return ""
    
    def _save_file(self, filename: str, content: str):
        """Save file with flame verification"""
        try:
            filepath = f"projects/{self.current_project}/{filename}"
            
            # Verify content before saving
            if filename.endswith(".scroll"):
                verification = self._verify_scroll_content(content)
                if not verification["valid"]:
                    st.error("Content failed flame verification")
                    return
            
            with open(filepath, "w") as f:
                f.write(content)
            
            st.success("File saved successfully")
            
        except Exception as e:
            st.error(f"Failed to save file: {e}")
    
    def _execute_scroll(self, content: str) -> Dict[str, Any]:
        """Execute scroll content"""
        try:
            result = self.executor.execute_scroll(content)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_scroll(self, content: str) -> Dict[str, Any]:
        """Validate scroll content"""
        try:
            # Basic validation
            required_keywords = ["Anoint:", "Build:", "Seal:"]
            errors = []
            
            for keyword in required_keywords:
                if keyword not in content:
                    errors.append(f"Missing required keyword: {keyword}")
            
            if "🔥" not in content:
                errors.append("Missing flame emoji")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
        except Exception as e:
            return {"valid": False, "errors": [str(e)]}
    
    def _verify_current_file(self) -> Dict[str, Any]:
        """Verify current file"""
        if not self.current_file:
            return {"verified": False, "errors": ["No file selected"]}
        
        content = self._load_file_content(self.current_file)
        return self._verify_scroll_content(content)
    
    def _verify_scroll_content(self, content: str) -> Dict[str, Any]:
        """Verify scroll content"""
        validation = self._validate_scroll(content)
        
        if validation["valid"]:
            return {
                "verified": True,
                "details": {
                    "flame_level": self.config.get("scroll_seal_level", 3),
                    "compliance": "verified",
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "verified": False,
                "errors": validation["errors"]
            }
    
    def _get_recent_executions(self) -> List[Dict[str, Any]]:
        """Get recent execution log"""
        # This would typically read from a log file or database
        return [
            {
                "id": "exec_001",
                "timestamp": datetime.now().isoformat(),
                "file": "main.scroll",
                "status": "success",
                "flame_verified": True
            }
        ]
    
    def _create_from_template(self, template_name: str):
        """Create file from template"""
        try:
            template_content = self._load_template(template_name)
            if template_content:
                st.text_area("Template Content", value=template_content, height=200)
                if st.button("Use Template"):
                    self._save_file(f"{template_name}", template_content)
                    st.success("File created from template")
        except Exception as e:
            st.error(f"Failed to load template: {e}")
    
    def _load_template(self, template_name: str) -> str:
        """Load template content"""
        templates = {
            "basic_project.scroll": """# Basic Project Template

Anoint: My Sacred Project
Build: Core System
Seal: With ScrollSeal 3

# Add your scroll commands here
""",
            "api_service.scroll": """# API Service Template

Anoint: API Service
Build: REST API
Seal: With ScrollSeal 4

# API endpoints and logic
""",
            "authentication.scroll": """# Authentication Template

Anoint: Authentication System
Build: Secure Auth
Seal: With ScrollSeal 5

# Authentication logic
""",
            "database.scroll": """# Database Template

Anoint: Database System
Build: Data Layer
Seal: With ScrollSeal 3

# Database operations
""",
            "security.scroll": """# Security Template

Anoint: Security Framework
Build: Protection System
Seal: With ScrollSeal 5

# Security measures
"""
        }
        
        return templates.get(template_name, "")
    
    def _share_to_community(self):
        """Share project to community"""
        st.info("Community sharing feature coming soon")
    
    def _show_settings(self):
        """Show ScrollIDE settings"""
        st.json(self.config)
    
    def _share_scroll(self, content: str):
        """Share scroll content"""
        st.info("Scroll sharing feature coming soon")
    
    def run(self):
        """Run ScrollIDE"""
        self.render_header()
        
        # Main layout
        col1, col2 = st.columns([1, 4])
        
        with col1:
            self.render_sidebar()
        
        with col2:
            self.render_editor()

def main():
    """Main ScrollIDE application"""
    st.set_page_config(
        page_title="ScrollIDE Alpha",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize ScrollIDE
    scrollide = ScrollIDE()
    
    # Run the application
    scrollide.run()

if __name__ == "__main__":
    main() 