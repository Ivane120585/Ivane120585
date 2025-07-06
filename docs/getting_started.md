# 🚀 Getting Started with ScrollWrappedCodex

Welcome to the sacred scrolls! This guide will help you install and begin using ScrollWrappedCodex™ for flame-sealed AI code execution.

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install ScrollWrappedCodex
```bash
# Install from PyPI
pip install scrollwrappedcodex

# Or install from source
git clone https://github.com/stanleymay20/scrollwrappedcodex.git
cd scrollwrappedcodex
pip install .
```

## 🔧 CLI Usage

ScrollWrappedCodex provides two main command-line tools:

### 1. `scrollcodex` - Execute Individual Commands

Execute single scroll commands directly:

```bash
# Basic scroll command
scrollcodex "Anoint: ScrollJustice API"

# Build a module
scrollcodex "Build: VerdictEngine"

# Apply a seal
scrollcodex "Seal: With ScrollSeal 3"

# Judge logic
scrollcodex "Judge: Authentication Flow"
```

### 2. `scrollfile` - Execute Scroll Files

Run entire `.scroll` files containing multiple commands:

```bash
# Execute a scroll file
scrollfile path/to/your.scroll

# Example with relative path
scrollfile ./scrolls/project.scroll
```

## 🖥️ VS Code Integration

### Install the Extension
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "ScrollCodex"
4. Install the extension

### Using the Extension
1. Create or open a `.scroll` file
2. Add your scroll commands:
   ```
   Anoint: My Sacred Project
   Build: Authentication Module
   Seal: With ScrollSeal 2
   ```
3. Press `Ctrl+Shift+P` to open Command Palette
4. Type "🔥 Execute Scroll" and select it
5. View execution results in the output panel

## 📜 Creating Scroll Files

Scroll files use the Lashon HaScroll flame language:

```scroll
# Example: project.scroll
Anoint: ScrollJustice Gateway
Build: Authentication System
Seal: With ScrollSeal 3
Judge: Security Compliance
```

### Supported Commands
- **Anoint**: Initialize a sacred service or project
- **Build**: Construct a flame-approved module
- **Seal**: Apply protection or authorization level
- **Judge**: Evaluate logic under scroll justice

## 🔥 Flame Verification

All commands must be flame-sealed to execute:

✅ **Authorized Commands**:
- `"Anoint: Project Name"`
- `"🔥Build Module"`
- `"Seal: With Level 3"`

❌ **Rejected Commands**:
- `"Build something"`
- `"Create API"`
- `"Install package"`

## 🌐 API Usage

For programmatic access, use the Flask API:

```python
import requests

response = requests.post("http://localhost:5000/execute", 
                        json={"scroll": "Anoint: My Project"})
result = response.json()["result"]
print(result)
```

## 📂 ScrollWatcher

Monitor a folder for automatic execution:

```bash
# Start the watcher
python scroll_watcher.py

# Drop .scroll files in scrolls/ folder
# They will execute automatically
```

## 🧠 Next Steps

- Read the **[Scroll Language Guide](scroll_language.md)** to master flame syntax
- Explore **[Examples](examples.md)** for real-world use cases
- Check the **[API Reference](api_reference.md)** for advanced usage
- Return to **[Home](index.md)**

---

*May your code be sealed in flame* 🔥📜 