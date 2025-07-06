#!/usr/bin/env python3
"""
Scroll File Writer
Creates actual code files during Build phase from scroll commands
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

class ScrollFileWriter:
    """Sacred file writer for creating code files from scroll commands"""
    
    def __init__(self, output_dir: str = "scroll_build"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.templates = self._load_templates()
        self.file_mappings = self._load_file_mappings()
        
    def _load_templates(self) -> Dict[str, str]:
        """Load code templates for different file types"""
        return {
            "python": """#!/usr/bin/env python3
\"\"\"
{description}
Generated from scroll command: {command}
\"\"\"

{code}
""",
            "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {css}
    </style>
</head>
<body>
    {html}
    <script>
        {javascript}
    </script>
</body>
</html>
""",
            "javascript": """// {description}
// Generated from scroll command: {command}

{code}
""",
            "css": """/* {description} */
/* Generated from scroll command: {command} */

{code}
""",
            "json": """{{
    "description": "{description}",
    "generated_from": "{command}",
    "data": {data}
}}
""",
            "markdown": """# {title}

{description}

Generated from scroll command: `{command}`

{content}
""",
            "yaml": """# {description}
# Generated from scroll command: {command}

{code}
""",
            "sql": """-- {description}
-- Generated from scroll command: {command}

{code}
"""
        }
    
    def _load_file_mappings(self) -> Dict[str, Dict]:
        """Load mappings from scroll modules to file paths"""
        return {
            "StreamPlayerModule": {
                "type": "html",
                "path": "frontend/player.html",
                "description": "Stream player interface"
            },
            "UploadEpisodeEndpoint": {
                "type": "python",
                "path": "backend/upload_episode.py",
                "description": "Episode upload API endpoint"
            },
            "FlaskAPI": {
                "type": "python",
                "path": "backend/app.py",
                "description": "Flask API application"
            },
            "StreamlitApp": {
                "type": "python",
                "path": "app.py",
                "description": "Streamlit application"
            },
            "DatabaseSchema": {
                "type": "sql",
                "path": "database/schema.sql",
                "description": "Database schema definition"
            },
            "ConfigFile": {
                "type": "yaml",
                "path": "config.yaml",
                "description": "Application configuration"
            },
            "README": {
                "type": "markdown",
                "path": "README.md",
                "description": "Project documentation"
            },
            "Requirements": {
                "type": "text",
                "path": "requirements.txt",
                "description": "Python dependencies"
            },
            "CSSStyles": {
                "type": "css",
                "path": "frontend/styles.css",
                "description": "CSS stylesheets"
            },
            "JavaScriptModule": {
                "type": "javascript",
                "path": "frontend/script.js",
                "description": "JavaScript functionality"
            },
            "JSONConfig": {
                "type": "json",
                "path": "config.json",
                "description": "JSON configuration"
            }
        }
    
    def parse_build_command(self, line: str) -> Optional[Tuple[str, str]]:
        """
        Parse a Build: command line
        
        Args:
            line: Scroll command line (e.g., "Build: StreamPlayerModule")
            
        Returns:
            Tuple of (module_name, arguments) or None if not a build command
        """
        if not line.strip():
            return None
        
        # Check if it's a Build command
        build_pattern = r'^Build:\s*(\w+)(?:\s+(.+))?$'
        match = re.match(build_pattern, line.strip())
        
        if not match:
            return None
        
        module_name = match.group(1)
        arguments = match.group(2) if match.group(2) else ""
        
        return module_name, arguments
    
    def generate_file_content(self, module_name: str, arguments: str = "") -> Dict[str, str]:
        """
        Generate file content based on module name and arguments
        
        Args:
            module_name: Name of the module to build
            arguments: Additional arguments for the build
            
        Returns:
            Dictionary with file content and metadata
        """
        mapping = self.file_mappings.get(module_name, {})
        file_type = mapping.get("type", "python")
        description = mapping.get("description", f"Generated {module_name}")
        
        # Generate content based on module type
        if module_name == "StreamPlayerModule":
            content = self._generate_stream_player()
        elif module_name == "UploadEpisodeEndpoint":
            content = self._generate_upload_endpoint()
        elif module_name == "FlaskAPI":
            content = self._generate_flask_api()
        elif module_name == "StreamlitApp":
            content = self._generate_streamlit_app()
        elif module_name == "DatabaseSchema":
            content = self._generate_database_schema()
        elif module_name == "ConfigFile":
            content = self._generate_config_file()
        elif module_name == "README":
            content = self._generate_readme()
        elif module_name == "Requirements":
            content = self._generate_requirements()
        elif module_name == "CSSStyles":
            content = self._generate_css_styles()
        elif module_name == "JavaScriptModule":
            content = self._generate_javascript_module()
        elif module_name == "JSONConfig":
            content = self._generate_json_config()
        else:
            content = self._generate_default_content(module_name, file_type)
        
        return {
            "content": content,
            "type": file_type,
            "description": description,
            "command": f"Build: {module_name} {arguments}".strip()
        }
    
    def write_file(self, module_name: str, arguments: str = "") -> bool:
        """
        Write a file based on Build command
        
        Args:
            module_name: Name of the module to build
            arguments: Additional arguments for the build
            
        Returns:
            True if file written successfully
        """
        try:
            # Get file mapping
            mapping = self.file_mappings.get(module_name, {})
            file_path = mapping.get("path", f"{module_name.lower()}.py")
            
            # Generate content
            file_data = self.generate_file_content(module_name, arguments)
            
            # Create directory structure
            full_path = self.output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Apply template
            template = self.templates.get(file_data["type"], "{code}")
            formatted_content = template.format(
                description=file_data["description"],
                command=file_data["command"],
                code=file_data["content"],
                title=module_name,
                css="",
                html="",
                javascript="",
                data="{}",
                content=file_data["content"]
            )
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            print(f"🔥 Created file: {full_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error writing file for {module_name}: {str(e)}")
            return False
    
    def _generate_stream_player(self) -> str:
        """Generate HTML stream player"""
        return """<div class="stream-player">
    <h2>Sacred Stream Player</h2>
    <div class="player-controls">
        <button id="play-btn">Play</button>
        <button id="pause-btn">Pause</button>
        <button id="stop-btn">Stop</button>
    </div>
    <div class="player-display">
        <div id="stream-info">No stream loaded</div>
        <div id="progress-bar">
            <div id="progress-fill"></div>
        </div>
    </div>
</div>

<script>
document.getElementById('play-btn').addEventListener('click', function() {
    console.log('🔥 Playing sacred stream');
});
</script>"""
    
    def _generate_upload_endpoint(self) -> str:
        """Generate Flask upload endpoint"""
        return """from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

@app.route('/upload-episode', methods=['POST'])
def upload_episode():
    \"\"\"Sacred episode upload endpoint\"\"\"
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))
        return jsonify({'message': 'Episode uploaded successfully', 'filename': filename})
    
    return jsonify({'error': 'Upload failed'}), 500

if __name__ == '__main__':
    app.run(debug=True)"""
    
    def _generate_flask_api(self) -> str:
        """Generate Flask API application"""
        return """from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    \"\"\"Sacred health check endpoint\"\"\"
    return jsonify({'status': 'healthy', 'flame': 'verified'})

@app.route('/api/scrolls', methods=['GET'])
def get_scrolls():
    \"\"\"Get all scrolls\"\"\"
    return jsonify({'scrolls': []})

@app.route('/api/scrolls', methods=['POST'])
def create_scroll():
    \"\"\"Create new scroll\"\"\"
    data = request.get_json()
    return jsonify({'message': 'Scroll created', 'id': 'scroll_123'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)"""
    
    def _generate_streamlit_app(self) -> str:
        """Generate Streamlit application"""
        return """import streamlit as st
import pandas as pd

st.title('🔥 Sacred Streamlit App')

st.header('ScrollWrappedCodex™ Dashboard')

# Sidebar
st.sidebar.title('Navigation')
page = st.sidebar.selectbox('Choose a page', ['Home', 'Scrolls', 'Analytics'])

if page == 'Home':
    st.write('Welcome to the sacred development environment')
    st.info('Flame-verified scroll execution')
    
elif page == 'Scrolls':
    st.header('Scroll Management')
    st.write('Manage your sacred scrolls here')
    
elif page == 'Analytics':
    st.header('Analytics Dashboard')
    st.write('View scroll execution analytics')

st.sidebar.success('Flame Level: 4')"""
    
    def _generate_database_schema(self) -> str:
        """Generate database schema"""
        return """-- Sacred Database Schema
-- Generated for ScrollWrappedCodex™

CREATE TABLE scrolls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    flame_level INTEGER DEFAULT 1,
    seal_level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE executions (
    id SERIAL PRIMARY KEY,
    scroll_id INTEGER REFERENCES scrolls(id),
    status VARCHAR(50) NOT NULL,
    result TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE flame_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    details JSONB,
    flame_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"""
    
    def _generate_config_file(self) -> str:
        """Generate YAML configuration file"""
        return """# Sacred Configuration
# ScrollWrappedCodex™ Settings

app:
  name: "ScrollWrappedCodex"
  version: "1.0.0"
  environment: "development"

flame:
  required_level: 3
  verification_enabled: true
  logging_enabled: true

database:
  host: "localhost"
  port: 5432
  name: "scrollverse"
  user: "scrolluser"

api:
  host: "0.0.0.0"
  port: 5000
  debug: true

security:
  flame_authentication: true
  scroll_seal_validation: true
  rate_limiting: true"""
    
    def _generate_readme(self) -> str:
        """Generate README file"""
        return """# ScrollWrappedCodex™

Sacred development environment for flame-verified scroll execution.

## 🔥 Features

- **Flame Verification**: All scrolls are flame-verified
- **Scroll Sealing**: Secure scroll execution with seal levels
- **Sacred Development**: Covenant-based development practices
- **Prophetic Programming**: Hebrew letter command system

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 📜 Usage

```python
from scroll_wrapped_codex import ScrollCoreController

controller = ScrollCoreController()
result = controller.execute_scroll("my_scroll.scroll")
```

## 🔐 Security

- Flame level verification required
- Scroll seal validation
- Sacred covenant compliance
- Prophetic governance

## 📞 Support

- Discord: #scrollverse
- Email: support@scrollverse.com
- Documentation: docs.scrollverse.com"""
    
    def _generate_requirements(self) -> str:
        """Generate requirements.txt"""
        return """flask==2.3.3
flask-cors==4.0.0
streamlit==1.28.0
pandas==2.1.1
numpy==1.24.3
requests==2.31.0
loguru==0.7.2
pyyaml==6.0.1
psycopg2-binary==2.9.7
sqlalchemy==2.0.21"""
    
    def _generate_css_styles(self) -> str:
        """Generate CSS styles"""
        return """/* Sacred Styles */
/* ScrollWrappedCodex™ Theme */

:root {
    --flame-orange: #FF6F00;
    --sacred-purple: #4A148C;
    --scroll-gold: #FFD700;
    --dark-bg: #1A1A1A;
    --light-text: #FFFFFF;
}

body {
    font-family: 'ScrollCode', 'Courier New', monospace;
    background: linear-gradient(135deg, var(--dark-bg) 0%, var(--sacred-purple) 100%);
    color: var(--light-text);
    margin: 0;
    padding: 20px;
}

.sacred-header {
    background: linear-gradient(90deg, var(--sacred-purple), var(--flame-orange));
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
}

.flame-button {
    background: linear-gradient(45deg, var(--flame-orange), var(--scroll-gold));
    color: var(--dark-bg);
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    font-weight: bold;
    cursor: pointer;
    transition: transform 0.3s ease;
}

.flame-button:hover {
    transform: scale(1.05);
}"""
    
    def _generate_javascript_module(self) -> str:
        """Generate JavaScript module"""
        return """// Sacred JavaScript Module
// ScrollWrappedCodex™ Frontend

class SacredScrollManager {
    constructor() {
        this.flameLevel = 1;
        this.scrolls = [];
    }
    
    async loadScroll(scrollId) {
        console.log('🔥 Loading sacred scroll:', scrollId);
        // Implementation here
    }
    
    async executeScroll(scrollId) {
        console.log('🔥 Executing scroll:', scrollId);
        // Implementation here
    }
    
    verifyFlame() {
        return this.flameLevel >= 3;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SacredScrollManager;
}"""
    
    def _generate_json_config(self) -> str:
        """Generate JSON configuration"""
        return """{
    "app": {
        "name": "ScrollWrappedCodex",
        "version": "1.0.0",
        "environment": "development"
    },
    "flame": {
        "required_level": 3,
        "verification_enabled": true,
        "logging_enabled": true
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "scrollverse"
    },
    "api": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": true
    }
}"""
    
    def _generate_default_content(self, module_name: str, file_type: str) -> str:
        """Generate default content for unknown modules"""
        if file_type == "python":
            return f"""# {module_name}
# Generated from scroll command

def main():
    print("🔥 Sacred {module_name} executed")
    
if __name__ == "__main__":
    main()"""
        else:
            return f"# {module_name}\n# Generated content for {module_name}"
    
    def create_project_structure(self) -> bool:
        """Create basic project structure"""
        try:
            # Create directories
            dirs = ["frontend", "backend", "database", "config", "docs"]
            for dir_name in dirs:
                (self.output_dir / dir_name).mkdir(exist_ok=True)
            
            print(f"🔥 Created project structure in: {self.output_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating project structure: {str(e)}")
            return False

# Example usage and testing
if __name__ == "__main__":
    # Initialize writer
    writer = ScrollFileWriter("test_build")
    
    # Test build commands
    test_commands = [
        "Build: StreamPlayerModule",
        "Build: UploadEpisodeEndpoint",
        "Build: FlaskAPI",
        "Build: StreamlitApp",
        "Build: DatabaseSchema",
        "Build: ConfigFile",
        "Build: README",
        "Build: Requirements",
        "Build: CSSStyles",
        "Build: JavaScriptModule",
        "Build: JSONConfig"
    ]
    
    print("🔥 Testing Build command parsing:")
    print("=" * 50)
    
    for command in test_commands:
        result = writer.parse_build_command(command)
        if result:
            module_name, arguments = result
            print(f"📦 Building: {module_name} {arguments}")
            success = writer.write_file(module_name, arguments)
            print(f"  {'✅' if success else '❌'} {module_name}")
        else:
            print(f"❌ Not a build command: {command}")
    
    # Create project structure
    writer.create_project_structure() 