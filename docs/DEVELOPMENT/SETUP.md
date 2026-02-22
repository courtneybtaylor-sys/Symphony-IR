# Development Setup Guide

This guide walks through setting up a development environment for Symphony-IR.

## Prerequisites

- **Python 3.10+** — Check with `python --version`
- **Git** — For version control
- **pip** — Python package manager (included with Python)
- **Virtual environment** — Python's `venv` module

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/courtneybtaylor-sys/Symphony-IR.git
cd Symphony-IR

# Add upstream remote (if you forked)
git remote add upstream https://github.com/courtneybtaylor-sys/Symphony-IR.git
```

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify activation (should show venv in prompt)
```

## Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install AI orchestrator dependencies
pip install -r ai-orchestrator/requirements.txt

# Install GUI dependencies
pip install -r gui/requirements.txt

# Install development tools
pip install pytest pytest-cov black isort flake8 mypy
```

## Step 4: Verify Installation

```bash
# Check imports
python -c "from ai_orchestrator import orchestrator; print('✓ CLI OK')"
python -c "from gui import main; print('✓ GUI OK')"

# Check tools
black --version
pytest --version
mypy --version
```

## Step 5: Configure for Development

### Set Up API Keys

```bash
# Create config file
mkdir -p ~/.symphonyir
cat > ~/.symphonyir/config.json << 'EOF'
{
  "providers": {
    "claude": {
      "api_key": "sk-ant-YOUR-KEY-HERE"
    }
  },
  "default_provider": "claude"
}
EOF

# Or set environment variable
export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"
```

### Or Use Ollama (Local)

```bash
# Install Ollama from https://ollama.ai

# Run Ollama in background
ollama serve

# In another terminal, pull a model
ollama pull mistral

# Set config
export OLLAMA_URL="http://localhost:11434"
export SYMPHONY_PROVIDER="ollama"
```

## Step 6: Test the Setup

```bash
# Test CLI
python ai-orchestrator/orchestrator.py --help

# Test system status
python ai-orchestrator/orchestrator.py status

# Test GUI (if you have a display)
python gui/main.py

# Run tests
pytest tests/ -v
```

## Directory Structure

```
Symphony-IR/
├── ai-orchestrator/          # CLI & core engine
│   ├── orchestrator.py       # Main entry point
│   ├── agents/               # Agent implementations
│   ├── core/                 # Core orchestration logic
│   ├── flow/                 # Workflow/template system
│   ├── models/               # Data models
│   ├── config.py             # Configuration
│   └── requirements.txt
│
├── gui/                       # Desktop GUI
│   ├── main.py               # PyQt6 entry point
│   ├── streamlit_app.py      # Streamlit web UI
│   ├── design_tokens.py      # Design system tokens
│   └── requirements.txt
│
├── windows/                   # Build & installation
│   ├── build.py              # PyInstaller wrapper
│   ├── build_dmg.py          # macOS DMG builder
│   ├── build_appimage.py     # Linux AppImage builder
│   └── sign_*.py             # Code signing scripts
│
├── docs/                     # Documentation (this directory)
├── tests/                    # Test suite
├── .github/                  # GitHub Actions workflows
├── README.md                 # Project overview
├── CONTRIBUTING.md           # Contribution guidelines
└── LICENSE.txt               # Apache 2.0 license
```

## Common Tasks

### Run the Application

```bash
# CLI
python ai-orchestrator/orchestrator.py run "Your task here"

# GUI
python gui/main.py

# Streamlit
streamlit run gui/streamlit_app.py
```

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=ai_orchestrator --cov=gui --cov-report=html

# Specific test file
pytest tests/test_agents.py -v

# Specific test
pytest tests/test_agents.py::test_architect_agent -v
```

### Run Linting

```bash
# Format code
black ai-orchestrator/ gui/ windows/

# Sort imports
isort ai-orchestrator/ gui/

# Check style
flake8 ai-orchestrator/ gui/

# Type check
mypy ai-orchestrator/
```

### Build Executables

```bash
# Auto-detect platform
python windows/build.py

# Windows
python windows/build.py --platform win

# macOS
python windows/build.py --platform mac

# Linux
python windows/build.py --platform linux
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Edit files, add features, fix bugs
vim ai-orchestrator/orchestrator.py

# Test changes
pytest tests/ -v

# Check code quality
black ai-orchestrator/
flake8 ai-orchestrator/
mypy ai-orchestrator/
```

### 3. Commit Changes

```bash
git add ai-orchestrator/orchestrator.py
git commit -m "feat: add new orchestration feature"
```

### 4. Push and Create PR

```bash
git push origin feature/my-feature
# Open PR on GitHub
```

### 5. Address Review Feedback

```bash
# Make changes based on review
vim ai-orchestrator/orchestrator.py
git add .
git commit -m "refactor: address code review feedback"
git push origin feature/my-feature
```

## Debugging

### Enable Debug Logging

```bash
# Python
export PYTHONVERBOSE=1
python ai-orchestrator/orchestrator.py run "task"

# CLI with verbose flag
python ai-orchestrator/orchestrator.py run "task" --verbose

# GUI with debug
python gui/main.py --debug
```

### Use a Debugger

```bash
# pdb (built-in)
python -m pdb ai-orchestrator/orchestrator.py run "task"

# VS Code debugger
# Add breakpoints and press F5

# PyCharm debugger
# Right-click and "Debug"
```

### Check Dependencies

```bash
# List installed packages
pip list

# Check for outdated packages
pip list --outdated

# Check for security issues
pip-audit
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'anthropic'`

**Solution**: Install dependencies
```bash
pip install -r ai-orchestrator/requirements.txt
```

### Issue: `Permission denied` on macOS/Linux

**Solution**: Fix file permissions
```bash
chmod +x ai-orchestrator/orchestrator.py
python ai-orchestrator/orchestrator.py
```

### Issue: Tests fail with `import error`

**Solution**: Ensure venv is activated
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install pytest
pytest tests/
```

### Issue: `API key not found`

**Solution**: Set configuration
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python ai-orchestrator/orchestrator.py status
```

### Issue: Port 11434 (Ollama) already in use

**Solution**: Change Ollama port
```bash
# Change OLLAMA_NUM_GPU or port
OLLAMA_NUM_GPU=0 ollama serve
```

## IDE Setup

### VS Code

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true
  }
}
```

### PyCharm

1. Open project
2. File → Settings → Project → Python Interpreter
3. Click gear icon → Add
4. Select `venv/bin/python`
5. Apply

### Vim/Neovim

```bash
# Install language server
pip install pylsp-mypy pylsp-black pylsp-isort

# Configure in your init.vim or init.lua
```

## Performance Development

### Profile Code

```bash
python -m cProfile -o stats.prof ai-orchestrator/orchestrator.py run "task"
python -m pstats stats.prof
```

### Memory Profiling

```bash
pip install memory-profiler
python -m memory_profiler ai-orchestrator/orchestrator.py run "task"
```

## Contributing

Before committing:

1. **Run tests**: `pytest tests/ -v`
2. **Format code**: `black ai-orchestrator/ gui/`
3. **Check style**: `flake8 ai-orchestrator/`
4. **Type check**: `mypy ai-orchestrator/`
5. **Add Apache headers** to new Python files

See [Contributing Guide](../../CONTRIBUTING.md) for full details.

## Getting Help

- **Questions**: [GitHub Discussions](https://github.com/courtneybtaylor-sys/Symphony-IR/discussions)
- **Bugs**: [GitHub Issues](https://github.com/courtneybtaylor-sys/Symphony-IR/issues)
- **Security**: [Security Policy](../../SECURITY.md)

## Next Steps

- Read [Architecture](../ARCHITECTURE.md) to understand the system
- Check [Contributing Guide](../../CONTRIBUTING.md) before submitting PRs
- Review [CI/CD Guide](CI.md) to understand automated testing
