# Symphony-IR Windows Installation Guide

Complete guide to installing Symphony-IR on Windows 10/11 as a desktop application with GUI.

## Installation Methods

### Method 1: Automatic PowerShell Installer (Recommended)

The easiest way to install Symphony-IR with one command.

**Prerequisites:**
- Windows 10 or later
- Python 3.9+ installed and in PATH

**Steps:**

1. **Download** the installer or clone the repository:
   ```bash
   git clone https://github.com/courtneybtaylor-sys/Symphony-IR.git
   cd Symphony-IR
   ```

2. **Right-click PowerShell** and select "Run as Administrator"

3. **Run the installer:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
   .\windows\install.ps1
   ```

4. **Follow the prompts** - the installer will:
   - Check Python installation
   - Create installation directory
   - Download dependencies
   - Create Start Menu and Desktop shortcuts
   - Optionally save your API key

5. **Launch Symphony-IR** from Start Menu or Desktop shortcut

### Method 2: Standalone Windows Executable

Use the pre-built executable (no Python installation needed).

**Prerequisites:**
- Windows 10 or later
- ~500MB disk space

**Steps:**

1. **Download** `Symphony-IR-1.0.0-Installer.exe` from releases

2. **Double-click** the installer

3. **Follow the installation wizard** (standard Windows installer)

4. **Launch** from Start Menu or Desktop

### Method 3: Manual Installation

For developers or custom setups.

**Prerequisites:**
- Windows 10 or later
- Python 3.9+ (https://www.python.org/)
- Git (optional)

**Steps:**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/courtneybtaylor-sys/Symphony-IR.git
   cd Symphony-IR
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r gui\requirements-desktop.txt
   ```

4. **Initialize orchestrator:**
   ```bash
   cd ai-orchestrator
   python orchestrator.py init --project ..
   cd ..
   ```

5. **Run the application:**
   ```bash
   python gui\desktop_app.py
   ```

## First Time Setup

### Step 1: Start the Application

**Desktop Shortcut:** Double-click "Symphony-IR" on your desktop

**Start Menu:** Click Windows key, search "Symphony-IR"

**Command Line:** `python gui\desktop_app.py`

### Step 2: Configure API Provider

1. Go to **Settings** tab
2. Choose your AI provider:
   - **Claude (Cloud)** - Recommended for best quality
   - **Ollama (Local)** - Free, no API key needed

### Step 3: Add API Key (if using Claude)

1. Get key from https://console.anthropic.com
2. Paste in Settings → API Key field
3. Click "Save Settings"

### Step 4: Start Using

**Option A: Quick Task**
1. Go to **Orchestrator** tab
2. Enter task description
3. Click "Run Orchestrator"

**Option B: Guided Workflow**
1. Go to **Symphony Flow** tab
2. Choose a template (Code Review, API Design, etc.)
3. Add variables if needed
4. Click "Start Workflow"

## Desktop Shortcuts

### What You Get

After installation, you'll have:

```
📁 Start Menu
  └─ 📁 Symphony-IR
      ├─ 🚀 Symphony-IR.exe (main app)
      └─ ⏹️ Uninstall

📁 Desktop
  └─ 🚀 Symphony-IR (shortcut)

📁 C:\Program Files\Symphony-IR\
  └─ (installation directory)
```

### Custom Shortcuts

Create a custom shortcut:

1. **Right-click** on Desktop → **New** → **Shortcut**
2. **Target:** `python.exe C:\Program Files\Symphony-IR\gui\desktop_app.py`
3. **Start in:** `C:\Program Files\Symphony-IR`
4. **Name:** Symphony-IR

## Building from Source

### Build Standalone Executable

Create a standalone `Symphony-IR.exe` without Python dependency.

**Prerequisites:**
- Python 3.9+
- All requirements installed

**Steps:**

1. **Navigate to project:**
   ```bash
   cd Symphony-IR
   ```

2. **Install build tools:**
   ```bash
   pip install PyInstaller
   ```

3. **Build executable:**
   ```bash
   python windows\build.py
   ```

4. **Find output:**
   ```
   dist\Symphony-IR.exe          (portable executable)
   dist\Symphony-IR\             (application directory)
   ```

### Create Installer

Create a professional Windows installer with NSIS.

**Prerequisites:**
- NSIS installed (https://nsis.sourceforge.io/)
- Standalone executable built (see above)

**Steps:**

1. **Install NSIS**

2. **Right-click** `windows\installer.nsi` → **Compile NSIS Script**

3. **Installer created:**
   ```
   dist\Symphony-IR-1.0.0-Installer.exe
   ```

## Troubleshooting

### Application Won't Start

**Error:** "Python not found"

**Solution:**
```bash
# Ensure Python is installed and in PATH
python --version

# Add to PATH if needed:
# 1. Search "Edit environment variables"
# 2. Add Python directory to PATH
```

### Dependencies Won't Install

**Error:** "pip install failed"

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements manually
pip install PyQt6 PyQt6-Charts streamlit anthropic pyyaml requests
```

### API Key Not Saving

**Solution:**
1. Go to **Settings**
2. Enter API key
3. Click **Save Settings**
4. Check that Anthropic provider is selected

### Ollama Connection Failed

**Solution:**
1. Ensure Ollama is running: `ollama serve`
2. Check Ollama URL in Settings: `http://localhost:11434`
3. Test connection: `curl http://localhost:11434/api/tags`

### GUI Looks Blurry

**Solution (for high-DPI displays):**
1. Create `run.bat`:
   ```batch
   @echo off
   set QT_QPA_PLATFORM_PLUGIN_PATH=
   python gui\desktop_app.py
   ```
2. Double-click `run.bat`

## Uninstalling

### Using Windows Settings

1. **Settings** → **Apps** → **Apps & Features**
2. Find **Symphony-IR**
3. Click **Uninstall**
4. Follow prompts

### Using Start Menu

1. **Start Menu** → **Symphony-IR** → **Uninstall**

### Manual Uninstall

1. **Delete folder:** `C:\Program Files\Symphony-IR\`
2. **Remove shortcuts:** Delete from Start Menu and Desktop
3. **Remove from PATH:** Edit environment variables

## Advanced Configuration

### Custom Installation Directory

```powershell
# Use custom directory
.\windows\install.ps1 -InstallPath "C:\MyApps\Symphony-IR"
```

### Configure via Settings File

Edit `.orchestrator\agents.yaml` for:
- AI model selection
- Temperature and token limits
- Agent configurations
- Governance settings

### Environment Variables

Set these for automatic configuration:

```batch
# Set API key
setx ANTHROPIC_API_KEY sk-your-key-here

# Set Ollama URL
setx OLLAMA_BASE_URL http://localhost:11434

# Set project directory
setx SYMPHONY_HOME C:\MyProjects\Symphony-IR
```

## System Requirements

### Minimum

- **OS:** Windows 10 or later
- **RAM:** 4GB
- **Storage:** 1GB free
- **CPU:** Intel/AMD x64

### Recommended

- **OS:** Windows 10/11
- **RAM:** 8GB+
- **Storage:** 5GB+ (for Ollama models)
- **GPU:** NVIDIA/AMD for faster Ollama

### Cloud AI (Claude)

- **Internet:** Required
- **Connection:** 10+ Mbps
- **Latency:** ~1-2s per request

### Local AI (Ollama)

- **Internet:** Not required (after setup)
- **GPU Memory:** 4-24GB (depending on model)
- **Latency:** ~2-5s per request

## Windows Defender SmartScreen

**If you see a warning:**

1. Click **More info**
2. Click **Run anyway**
3. Application will start normally

This is normal for unsigned executables. You can also:
- Download from Microsoft Store (future)
- Use Python version (no warning)

## Getting Help

### In-Application Help

- **Settings** → Help section for API key links
- **File** → **Documentation** for online guides
- Hover over buttons for tooltips

### Documentation

- **README.md** - Main documentation
- **docs/FLOW.md** - Workflow templates guide
- **docs/OLLAMA.md** - Local AI setup
- **docs/WINDOWS-SETUP.md** - This file

### Issue Reporting

Report issues on GitHub:
https://github.com/courtneybtaylor-sys/Symphony-IR/issues

Include:
- Windows version
- Python version
- Error message
- Steps to reproduce

## Next Steps

1. **Choose AI Provider:**
   - Claude for best quality
   - Ollama for free/local

2. **Run Your First Workflow:**
   - Code Review
   - API Design
   - Feature Planning

3. **Explore Templates:**
   - Database Schema
   - Testing Strategy
   - Documentation

4. **Customize:**
   - Settings → Model selection
   - Create custom templates
   - Configure governance

## Tips & Tricks

### Performance

- Use **mistral** Ollama model for best speed/quality
- Enable **parallel execution** in Settings
- Close other applications for faster inference

### Productivity

- **Keyboard shortcuts:**
  - `Ctrl+T` → Task input (in future versions)
  - `Ctrl+Enter` → Run task
  - `Ctrl+S` → Save session

- **Workflows:**
  - Code Review before commits
  - Design review before implementation
  - Test strategy before coding

### Integrations

- **with Version Control:**
  - Run before commits
  - Save results in git history

- **with IDEs:**
  - Copy code from IDE
  - Paste into Symphony-IR
  - Use recommendations

- **with Documentation:**
  - Generate docs with Documentation template
  - Save to project wiki
  - Update README

## System Monitoring

**Check resource usage:**

1. Open **Task Manager** (`Ctrl+Shift+Esc`)
2. Look for **Python** or **Symphony-IR**
3. Monitor CPU/Memory/Disk usage

**For Ollama:**

1. Open **Task Manager**
2. Look for Ollama process
3. Monitor GPU usage

## Uninstall & Reinstall

**Complete cleanup:**

```batch
# Remove environment variables
setx ANTHROPIC_API_KEY ""
setx OLLAMA_BASE_URL ""

# Remove installation directory
rmdir /s /q "C:\Program Files\Symphony-IR"

# Remove application data (optional)
rmdir /s /q "%APPDATA%\Symphony-IR"

# Reinstall
# Run installer again
```

## Contact & Support

- **GitHub:** https://github.com/courtneybtaylor-sys/Symphony-IR
- **Documentation:** https://github.com/courtneybtaylor-sys/Symphony-IR#readme
- **Issues:** https://github.com/courtneybtaylor-sys/Symphony-IR/issues

---

**Happy orchestrating!** 🎼
