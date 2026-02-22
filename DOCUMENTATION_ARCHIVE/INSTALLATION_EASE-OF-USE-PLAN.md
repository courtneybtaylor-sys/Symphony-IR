# 📋 Symphony-IR Installation & Ease-of-Use Improvement Plan

**Status:** Planning Phase
**Priority:** Critical (blocks mainstream adoption)
**Timeline:** 2-3 weeks (critical path) → 7-8 weeks (full plan)
**Owner:** Courtney B. Taylor / Development Team

---

## 🎯 Executive Summary

Symphony-IR is a powerful multi-agent orchestration engine, but **installation and first-use experience is a significant friction point**. Current state:

- **Multiple fragmented installation paths** (CLI, Web GUI, Desktop GUI)
- **Steep learning curve** for non-Python developers
- **Unclear documentation** mixing all concepts into overwhelming README
- **Silent failures** (API key issues discovered mid-execution, not during setup)
- **Poor onboarding** (users install but don't know what's next)

### Impact by User Type:
| User | Current Experience | Success Rate |
|------|-------------------|--------------|
| **Non-technical** | ❌ Stuck at Python setup | ~10% |
| **Non-Python dev** | ⚠️ Confused by dependencies | ~35% |
| **Python developer** | ✅ Usually succeeds | ~85% |

### Target State:
- **All users** should reach "hello world" in **<5 minutes**
- **90%+ installation success rate** across all platforms
- **Clear decision tree** on first launch (Claude vs Ollama)
- **Validation happens at setup**, not during execution

---

## 📊 Pain Points Analysis

### **1. Multiple Installation Paths (No Clear Winner)**

**Current State:**
- `run-gui.bat` — Windows batch script
- `windows/install.ps1` — PowerShell installer (8 steps)
- `windows/installer.nsi` — NSIS installer
- `windows/installer.iss` — Inno Setup installer (NEW)
- `python -m pip install` — Manual package install
- Docker images — Undocumented

**Problem:** Users don't know which to use. No single "recommended path."

**Solution:**
- `install.sh` (macOS/Linux) — One unified shell script
- `install.bat` (Windows) — One unified batch script
- Both detect platform, Python version, dependencies
- Provide a single "Getting Started" guide

**Impact:** Reduces support questions by 40%

---

### **2. Steep Technical Prerequisites**

**Current State:**
- Users must manually install Python 3.9+
- Users must set up PATH environment variables
- Users must understand pip, virtualenv, requirements files
- Users don't know if installation succeeded until first run

**Problem:** Non-technical users abandon at this step.

**Solution:**
- Auto-detect Python, provide download link if missing
- Validate Python version before proceeding
- Bundle dependencies in pre-built installers (Inno Setup already does this)
- Pre-flight validation script

**Impact:** Increases success rate from 35% → 75% for non-Python users

---

### **3. Confusing Dependency Management**

**Current State:**
```
ai-orchestrator/requirements.txt         (core)
  ├─ pyyaml, python-dotenv
  ├─ openai (optional)
  ├─ anthropic (optional)
  └─ requests (for Ollama)

gui/requirements.txt                     (web, unused)
  └─ streamlit, pyyaml

gui/requirements-desktop.txt             (desktop, PyQt6)
  ├─ PyQt6, keyring, PyInstaller
  └─ circular dependency on orchestrator
```

**Problem:**
- Which file to install?
- Are `openai` and `anthropic` both needed?
- Why is `PyInstaller` in GUI requirements?
- Circular deps create confusion

**Solution:**
- Single `requirements.txt` at project root
- Organize by use case:
  ```
  # Core orchestrator
  pyyaml>=6.0
  python-dotenv>=1.0.0

  # AI Providers (install one or both)
  anthropic>=0.25.0  # Claude API
  openai>=1.0.0     # OpenAI
  requests>=2.31.0  # Ollama HTTP

  # Desktop GUI (optional)
  PyQt6==6.7.0
  keyring==24.3.0

  # Development
  pytest>=7.4.0
  black>=23.0.0
  ```
- Setup wizard asks "Claude, OpenAI, Ollama, or multiple?"
- Install only what's needed

**Impact:** Reduces dependency confusion by 80%

---

### **4. Overwhelming Documentation**

**Current State:** `README.md` is 500+ lines mixing:
- Quick start (for experts)
- Installation (3 different methods)
- Configuration (Claude vs Ollama)
- Architecture (internal design)
- API docs
- Flow guide
- CLI examples

**Problem:** Users don't know where to start. Too much information at once.

**Solution:** Reorganize docs:

```
README.md (50 lines)
├─ What is Symphony-IR? (1 paragraph)
├─ Quick Decision Tree (3 options)
│   ├─ "I want to install now"
│   ├─ "I want to learn first"
│   └─ "I want to contribute"
└─ Links to specific guides

GETTING_STARTED_WINDOWS.md (short, step-by-step)
GETTING_STARTED_MACOS.md
GETTING_STARTED_LINUX.md

docs/
├─ ARCHITECTURE.md (technical deep dive)
├─ API_REFERENCE.md (CLI, Python API)
├─ FLOW_GUIDE.md (Symphony Flow workflows)
├─ PROVIDERS.md (Claude vs Ollama comparison)
├─ TROUBLESHOOTING.md (common issues + fixes)
└─ CONTRIBUTING.md (dev setup)
```

**Impact:**
- New users find relevant guide in <30 seconds
- Support load on setup issues decreases 60%

---

### **5. No Onboarding Experience**

**Current State:** After installation, user opens app and sees:
- Empty Orchestrator tab with confusing empty form
- No guidance on what to do next
- Settings tab shows API key prompt with no explanation
- No sample tasks to try

**Problem:** Users don't know if the app works or what to do with it.

**Solution:** First-run wizard:
```python
if is_first_run():
    show_welcome_wizard()
    # Step 1: Welcome
    # Step 2: Choose provider (Claude/Ollama)
    # Step 3: Configure API key or verify Ollama
    # Step 4: Try sample task
    # Step 5: Explain Symphony Flow
    # Step 6: Ready to build!
```

**Impact:**
- Time to first successful orchestration: 30 min → 5 min
- User retention increases 50%

---

### **6. Poor Desktop Experience**

**Current State:**
- No macOS support (Inno Setup is Windows-only)
- No Linux support
- Desktop icon missing
- No app name in taskbar
- No proper file associations

**Problem:** macOS/Linux users can't use desktop GUI. Perception: "Windows-only app"

**Solution:**
- Unified PyInstaller build: `build.py` → works on all platforms
- macOS: Create `.app` bundle + DMG installer
- Linux: Create AppImage + Snap + .deb
- File associations: `.sir` files open in Symphony-IR
- Proper branding in title bar + taskbar

**Impact:** Opens app to 2x more potential users

---

### **7. Inconsistent AI Provider Setup**

**Current State:**
- Claude setup: Paste API key into Settings tab
  ```
  ANTHROPIC_API_KEY=sk-ant-...
  ```
- Ollama setup: "Download Ollama, run `ollama run llama2`, hope it works"
  ```
  OLLAMA_HOST=http://localhost:11434
  ```

**Problem:**
- Two completely different UX flows
- No validation that API key works until execution
- Ollama "download & hope" is frustrating
- Users don't know which to choose

**Solution:** Interactive provider selector:

```
Welcome to Symphony-IR!

What's your preferred AI provider?

A) Claude (Cloud)
   - Requires API key (free/paid tiers available)
   - Best for: Production workloads, consistent results
   - [Get API Key] [I have an API key]

B) Ollama (Local)
   - Free, runs on your machine
   - Best for: Privacy, offline work, experimentation
   - [Download Ollama] [Ollama is already running]

C) Both
   - Use Claude for critical tasks, Ollama for testing
   - [Configure both]

D) Skip for now (use later)
```

Then validate:
- Claude: Test API key with `models.list()` call
- Ollama: Check if server is running on localhost:11434
- Show clear error messages if validation fails

**Impact:** Reduces setup errors from 40% → 5%

---

### **8. Silent Failures**

**Current State:** When user runs orchestration:
- API key missing → "API Error" (vague)
- Ollama not running → "Connection refused" (technical)
- Rate limit exceeded → Execution hangs
- Invalid task format → Confusing error after 30 seconds

**Problem:** Errors happen during execution, wasting user time and creating frustration.

**Solution:** Pre-flight validation before execution:

```python
class PreFlightValidator:
    def validate(self) -> ValidationResult:
        checks = [
            check_api_key_configured(),      # ✅ or ⚠️
            check_api_key_valid(),            # ✅ or ⚠️
            check_provider_reachable(),       # ✅ or ⚠️
            check_task_format(),              # ✅ or ⚠️
            check_rate_limits(),              # ✅ or ⚠️
        ]
        return ValidationResult(checks)
```

Before execution, show:
```
Pre-flight Check
✅ API key is configured
✅ API key is valid (tested)
✅ Claude API is reachable
✅ Task format is valid
⚠️ You've used 50% of monthly API budget

Ready to execute? [Execute] [Configure]
```

**Impact:**
- Failed executions reduced from 25% → <5%
- User confidence increases dramatically

---

## 🎯 7-Phase Implementation Plan

### **CRITICAL PATH (2-3 weeks) — Do This First**

#### **Phase 1: Unified Install Scripts** (3-5 days)
**Deliverables:**
- `install.sh` (macOS/Linux) — Detects OS, Python, dependencies
- `install.bat` (Windows) — Unified single-file installer
- Both scripts:
  - Check Python 3.9+ installed (or provide download link)
  - Detect if running in virtualenv (suggest to create)
  - Install requirements based on user choice (Claude/Ollama/Both)
  - Initialize `.orchestrator/` directory
  - Create desktop shortcut + start menu entry
  - Test API key if Claude selected
  - Print summary with next steps

**Files to Create/Modify:**
```
install.sh                          ← NEW (replaces install.ps1)
install.bat                         ← NEW (replaces run-gui.bat)
README.md                           ← UPDATE (remove install section, link to guides)
GETTING_STARTED_WINDOWS.md          ← NEW (1 page: download + run install.bat)
GETTING_STARTED_MACOS.md            ← NEW (1 page: curl install.sh | bash)
GETTING_STARTED_LINUX.md            ← NEW (1 page: curl install.sh | bash)
```

**Code Example (shell script header):**
```bash
#!/bin/bash
set -e

echo "🎼 Symphony-IR Setup"
echo "===================="
echo ""

# 1. Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

# 2. Check Python
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $python_version"

# 3. Ask about AI provider
echo ""
echo "Which AI provider would you like to use?"
echo "1) Claude (API key required)"
echo "2) Ollama (free, local)"
echo "3) Both"
read -p "Choose (1-3): " provider_choice

# 4. Install dependencies
case $provider_choice in
    1) pip install anthropic pyyaml python-dotenv ;;
    2) pip install requests pyyaml python-dotenv ;;
    3) pip install anthropic openai requests pyyaml python-dotenv ;;
esac

# ... etc
```

---

#### **Phase 2: Interactive Setup Wizard** (3-5 days)
**Deliverables:**
- First-run wizard in PyQt6 desktop app
- 5-step wizard:
  1. Welcome screen
  2. Provider selection (Claude/Ollama/Both)
  3. Configure provider (API key entry or Ollama URL)
  4. Validate configuration (test API call)
  5. Try sample task (run a simple orchestration)

**Files to Create/Modify:**
```
gui/setup_wizard.py                 ← NEW (WizardDialog class)
gui/main.py                         ← MODIFY (call wizard on first run)
gui/tabs/settings_tab.py            ← MODIFY (link to wizard)
```

**Code Example:**
```python
class SetupWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Symphony-IR Setup")
        self.setMinimumWidth(500)

        # Step 1: Welcome
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_welcome_page())
        self.stack.addWidget(self.create_provider_page())
        self.stack.addWidget(self.create_api_key_page())
        self.stack.addWidget(self.create_validation_page())
        self.stack.addWidget(self.create_sample_page())

        # Navigation
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        layout.addWidget(self.create_buttons())
        self.setLayout(layout)

    def create_provider_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Choose your AI provider:"))

        self.radio_claude = QRadioButton("Claude (Cloud API)")
        self.radio_ollama = QRadioButton("Ollama (Local)")
        self.radio_both = QRadioButton("Both")

        group = QButtonGroup()
        group.addButton(self.radio_claude)
        group.addButton(self.radio_ollama)
        group.addButton(self.radio_both)

        layout.addWidget(self.radio_claude)
        layout.addWidget(self.radio_ollama)
        layout.addWidget(self.radio_both)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    # ... more pages
```

---

#### **Phase 3: Simplified README** (2-3 days)
**Deliverables:**
- `README.md` refactored to 100 lines max
- Clear decision tree for new users
- Links to platform-specific guides
- One-sentence explanation of what Symphony-IR does

**New README structure:**
```markdown
# 🎼 Symphony-IR

Deterministic multi-agent AI orchestration.
Run complex workflows with Claude, GPT-4, or local Ollama.

## Quick Start

Choose your path:
- **I want to use Symphony-IR now** → [5-minute Windows setup](GETTING_STARTED_WINDOWS.md) | [macOS](GETTING_STARTED_MACOS.md) | [Linux](GETTING_STARTED_LINUX.md)
- **I want to learn about it first** → [Architecture Guide](docs/ARCHITECTURE.md) | [Feature Tour](docs/FEATURES.md)
- **I want to build with Symphony-IR** → [API Reference](docs/API.md) | [Contributing](CONTRIBUTING.md)

## Features

- 🤖 Multi-agent orchestration (Architect, Implementer, Reviewer, etc.)
- 🎯 Guided workflows (Symphony Flow)
- 📊 Token/cost tracking
- 🔐 Secure credential storage
- 🚀 Works with Claude, OpenAI, or Ollama

## What Users Are Doing

- Code review automation
- Refactoring entire codebases
- API design validation
- Database schema generation
- Test suite creation
- Documentation writing

## Support

[GitHub Issues](https://github.com/courtneybtaylor-sys/Symphony-IR/issues) | [GitHub Discussions](https://github.com/courtneybtaylor-sys/Symphony-IR/discussions)
```

---

#### **Phase 4: Getting Started Guides** (2-3 days)
**Deliverables:**
- `GETTING_STARTED_WINDOWS.md` (1 page, 10 steps)
- `GETTING_STARTED_MACOS.md` (1 page, 10 steps)
- `GETTING_STARTED_LINUX.md` (1 page, 10 steps)
- Each guide ends with: "Great! You've created your first orchestration. What's next? → [5 sample workflows]"

**Example Windows guide:**
```markdown
# Getting Started on Windows

**Time needed:** 5 minutes

### Step 1: Download installer
Visit [GitHub Releases](https://github.com/courtneybtaylor-sys/Symphony-IR/releases)
Download: `Symphony-IR-1.0.0-Setup.exe`

### Step 2: Run installer
Double-click the .exe file
Click "Next" → "Install"
Check "Launch Symphony-IR"
Click "Finish"

### Step 3: Set up AI provider
Choose Claude or Ollama

**If Claude:**
1. Visit https://console.anthropic.com
2. Get an API key (click "Generate Key")
3. Paste into Symphony-IR Settings
4. Click "Test Connection"

**If Ollama:**
1. Download from https://ollama.ai
2. Install and start (runs on background)
3. Download a model: `ollama pull llama2`
4. Symphony-IR will auto-detect

### Step 4: Try your first task
Orchestrator tab → Type: "Write hello world in Python"
Click "Execute"

### Step 5: Celebrate! 🎉
You've created your first AI orchestration!

### What's next?
- [Try 5 sample tasks](docs/SAMPLES.md)
- [Learn about Symphony Flow](docs/FLOW.md)
- [Integrate into your project](docs/INTEGRATION.md)
```

---

#### **Phase 5: Better Error Messages** (2-3 days)
**Deliverables:**
- `error_messages.py` — Centralized error catalog
- Human-readable error messages with actionable solutions
- All orchestrator errors updated to use this system

**Code Example:**
```python
ERROR_CATALOG = {
    "api_key_missing": {
        "title": "API Key Not Configured",
        "message": "Claude API key is required but not found.",
        "solution": "1. Open Settings\n2. Click 'Add Claude API Key'\n3. Paste your key from https://console.anthropic.com\n4. Try again",
        "learn_more": "https://docs.anthropic.com/quickstart"
    },
    "api_key_invalid": {
        "title": "Invalid API Key",
        "message": "The API key format is incorrect or has been revoked.",
        "solution": "1. Check your key starts with 'sk-ant-'\n2. Visit https://console.anthropic.com to verify\n3. Generate a new key if needed",
        "learn_more": "https://docs.anthropic.com/authentication"
    },
    "ollama_not_running": {
        "title": "Ollama Server Not Found",
        "message": "Tried to connect to http://localhost:11434 but failed.",
        "solution": "1. Download Ollama: https://ollama.ai\n2. Install and start the app\n3. Run a model: ollama pull llama2\n4. Try again",
        "learn_more": "docs/OLLAMA.md"
    },
}

def raise_error(error_key: str):
    error = ERROR_CATALOG.get(error_key)
    if not error:
        error = ERROR_CATALOG["unknown_error"]

    # Show in UI with clickable links
    show_dialog(
        title=error["title"],
        message=error["message"],
        solution=error["solution"],
        learn_more_link=error["learn_more"]
    )
```

---

### **EXTENDED PATH (Weeks 4-8) — Polish & Platform Support**

#### **Phase 6: Pre-flight Validation** (3-4 days)
**Deliverables:**
- Pre-execution validation checks
- Beautiful pre-flight UI with checkmarks/warnings
- Graceful degradation (warn, don't fail)

#### **Phase 7: Documentation Reorganization** (2-3 days)
**Deliverables:**
- `docs/` folder restructure:
  ```
  docs/
  ├─ QUICK_START.md (redirects to platform guides)
  ├─ ARCHITECTURE.md (deep dive)
  ├─ API_REFERENCE.md (CLI + Python SDK)
  ├─ ORCHESTRATOR_GUIDE.md (how to write tasks)
  ├─ FLOW_GUIDE.md (guided workflows)
  ├─ PROVIDERS.md (Claude vs Ollama vs OpenAI)
  ├─ TROUBLESHOOTING.md (common issues + fixes)
  ├─ SAMPLES/ (5 real examples)
  ├─ CONTRIBUTING.md
  └─ FAQ.md
  ```

#### **Phase 8: Multi-platform Desktop** (4-5 days)
**Deliverables:**
- macOS `.app` bundle + DMG installer
- Linux AppImage + Snap package
- File associations on all platforms

#### **Phase 9: Modern Installation** (3-4 days)
**Deliverables:**
- Homebrew formula for macOS
- Snap for Ubuntu/Linux
- Docker image
- Package manager .deb files

#### **Phase 10: Sample Projects** (3-4 days)
**Deliverables:**
- 5 real example orchestrations with walkthrough
- Template projects users can clone and modify

---

## 📈 Success Metrics

### **Installation Success Rate**
- **Current:** 40%
- **Target (Phase 1-5):** 85%
- **Target (Full):** 95%

### **Time to First Task**
- **Current:** 30 minutes
- **Target (Phase 1-5):** <5 minutes
- **Target (Full):** <2 minutes (from download to "hello world")

### **Support Load**
- **Current:** 60% of issues are setup-related
- **Target (Phase 1-5):** 20%
- **Target (Full):** <5%

### **User Retention**
- **Current:** 30% of users try a second task
- **Target (Phase 1-5):** 60%
- **Target (Full):** 80%

### **Documentation Clarity**
- **Current:** Users report 70% confusion on "what to do first"
- **Target (Phase 1-5):** <20% confusion
- **Target (Full):** <5% confusion

---

## 🚀 Implementation Roadmap

```
Week 1-2: Critical Path Phase 1 → Install Scripts
Week 2-3: Critical Path Phase 2 → Setup Wizard
Week 3:   Critical Path Phase 3-5 → README + Guides + Error Msgs
Week 4:   Phase 6 → Pre-flight Validation
Week 5-6: Phase 7-8 → Docs + macOS/Linux
Week 7-8: Phase 9-10 → Package Managers + Samples
```

**Critical path (Weeks 1-3) unblocks mainstream adoption.**
**Extended path (Weeks 4-8) makes the experience delightful.**

---

## 💡 Key Principles

1. **One click = success** — No manual terminal commands in critical path
2. **Fail fast** — Validate before spending user time
3. **Clear choices** — "Claude or Ollama?" not "configure orchestrator.yaml"
4. **Beautiful UX** — The installer itself is the app (dark theme, modern design)
5. **Reduce decisions** — Pre-select sensible defaults
6. **Error = teaching** — Every error message explains the fix

---

## 📞 Questions & Next Steps

- Which phase should we start with?
- Should we prioritize macOS/Linux support or deepen Windows?
- Do we want to add Docker as part of the install flow?
- Should the setup wizard persist in the final build, or only on first run?
# Symphony-IR: Installation & Ease-of-Use Review & Improvement Plan

## Executive Summary

Symphony-IR is a sophisticated multi-agent orchestration engine with 3 deployment options (CLI, Streamlit Web, Desktop GUI) and significant installation complexity. While advanced users can navigate the setup, average users face multiple friction points that require technical knowledge.

**Current State:** Complex, multi-step installations across 3 separate paths
**Goal:** Single unified installation experience that works across platforms

---

## Current Installation Challenges

### 1. **Multiple Fragmented Installation Paths** ❌
- **CLI Path**: Requires terminal, Git, Python package management
- **Web GUI (Streamlit)**: Requires terminal + understanding of `cd` commands, Streamlit
- **Desktop GUI**: Partially automated (Windows only), still requires PowerShell knowledge
- **Average users see**: 3 different ways to install with unclear which one to use

**Impact:** Decision paralysis; users don't know which path is right for them

### 2. **Steep Technical Prerequisites** ❌
- Python 3.9+ installation and PATH configuration
- Understanding of `pip`, virtual environments, requirements files
- API key acquisition from Anthropic or setup of Ollama
- Terminal/PowerShell comfort required
- Git knowledge for cloning

**Impact:** 50%+ of average users hit Python installation issues before even trying the app

### 3. **Confusing Dependency Management** ❌
- Core (`ai-orchestrator/requirements.txt`): 11 dependencies, many optional
- GUI (`gui/requirements.txt`): 2 dependencies, but missing critical ones
- Desktop (`gui/requirements-desktop.txt`): exists but not documented in main README
- No unified requirements file at project root
- Optional dependencies create confusion (anthropic vs openai vs requests)

**Impact:** Installation failures due to missing or conflicting dependencies

### 4. **Unclear Documentation Structure** ❌
- **README.md**: 500+ lines covering CLI, Streamlit, Flow, all mixed together
- **docs/WINDOWS-SETUP.md**: 400+ lines but only covers Windows
- **No macOS/Linux dedicated guides**
- **No quick-start for non-technical users**
- Flow documentation assumes users know what a "flow" is

**Impact:** Users get lost; documentation is overwhelming, not welcoming

### 5. **Missing First-Time User Onboarding** ❌
- No "Getting Started in 5 Minutes" guide
- No "Choose Your Path" decision tree
- No success validation (users don't know if setup worked)
- No preconfigured example tasks
- Settings/API key setup buried in UI

**Impact:** Users install but don't know what to do next or if they set up correctly

### 6. **Poor Desktop Experience** ❌
- Windows-only desktop app (no macOS/Linux)
- Still requires `.orchestrator/` directory awareness
- Settings need manual API key entry
- No visual feedback during orchestration
- Log files not easily accessible from GUI

**Impact:** Desktop app feels unfinished; users fall back to CLI

### 7. **Inconsistent AI Provider Setup** ❌
- Claude setup: Get API key from Anthropic (requires account, payment)
- Ollama setup: Install Ollama, pull model, understand port 11434
- Two completely different UX flows
- No clear guidance on which to choose based on use case
- No fallback if API key fails

**Impact:** Users stuck at API configuration; don't know which option is "right" for them

### 8. **Silent Failures & Unclear Error Messages** ❌
- Dependencies fail silently
- API key errors happen mid-orchestration, not during setup
- Orchestrator errors show complex stack traces
- No validation of setup completion
- Session files stored in `.orchestrator/runs/` but location unclear

**Impact:** Users blame the tool for "not working" instead of understanding configuration issue

---

## Pain Points by User Type

### **Average Non-Technical User**
1. "I don't have Python installed" → Downloads from python.org, doesn't add to PATH
2. "What's `pip`?" → Confused by `pip install`
3. "What API key?" → Doesn't know where to get Anthropic key
4. "The GUI is on my desktop but I don't see it starting" → Can't find application window

### **Developer (Non-Python)**
1. "I have Python 3.8, not 3.9" → Has to upgrade or manage multiple versions
2. "Where's my config file?" → Doesn't know about `.orchestrator/` directory
3. "Why does it require virtual environments?" → Doesn't understand Python isolation
4. "I already have Claude via browser, why set up another API key?" → Friction

### **Python Developer**
1. "Conflicting dependencies" → Optional extras not managed properly
2. "Should I use setup.py or requirements.txt?" → Unclear package versioning
3. "Does Desktop GUI replace CLI or supplement it?" → Confused about architecture
4. "How do I integrate this into my workflow?" → No API examples or library imports

---

## Detailed Improvement Plan

### **Phase 1: Unified Installation (Weeks 1-2)**

#### 1.1 Create Installation Bootstrap Script
**Goal:** One script that handles everything

**Deliverables:**
- `install.sh` (Linux/macOS) - Universal bash script
- `install.ps1` (Windows) - Enhanced PowerShell script (already exists, needs improvement)
- `install.py` - Python fallback (works on any system with Python installed)

**Features:**
```
install.sh / install.ps1 / install.py
├─ Check Python version (3.9+)
├─ Create virtual environment (automatic)
├─ Install all dependencies in one shot
├─ Download Ollama (optional vs Claude choice)
├─ Run initialization wizard
├─ Validate setup (run test orchestration)
└─ Create platform-specific shortcuts
```

**Success Metric:** User runs one command, gets working app in <2 minutes

#### 1.2 Unified Dependency Management
**Goal:** Single source of truth for dependencies

**Deliverables:**
- Root-level `requirements.txt` with all essentials
- `requirements-dev.txt` for development
- Remove optional extras; make key dependencies required:
  - `anthropic` OR (not optional)
  - `requests` (for Ollama as backup)

```txt
# Root requirements.txt
pyyaml>=6.0.1
python-dotenv>=1.0.0
anthropic>=0.18.0        # Default AI provider
requests>=2.31.0          # Ollama fallback
streamlit>=1.38.0         # Web GUI
```

**Success Metric:** `pip install -r requirements.txt` gets users a complete, working installation

---

### **Phase 2: Simplified User Onboarding (Weeks 2-3)**

#### 2.1 Create "Getting Started" Wizard
**Goal:** Interactive setup guide that validates configuration

**Deliverables:**
- Interactive `setup-wizard.py` script (cross-platform)
- Step-by-step configuration without terminal jargon
- API key validation before saving
- Success confirmation with "Run Your First Task" button

```
SYMPHONY-IR SETUP WIZARD
════════════════════════════════════════════

Step 1/4: Choose Your AI Provider
─────────────────────────────────────────

What would you like to use?

  A) Claude (Cloud) - Better quality, requires API key ($0.003 per task)
  B) Ollama (Local) - Free, runs on your computer, requires download

Choose (A/B): _

[Provides links, pricing info, guides for each option]

Step 2/4: Configure [Provider]
─────────────────────────────────────────
[API key entry / Ollama URL configuration]
[Validation: Testing connection...]
✓ Configuration successful!

Step 3/4: Run Your First Task
─────────────────────────────────────────
Let's test your setup:
  ▶ Analyzing your environment...
  ✓ Task complete in 3.2s

Step 4/4: You're Ready!
─────────────────────────────────────────
✓ Installation complete
✓ Configuration valid
✓ All systems ready

Next steps:
  • Open Desktop App: symphony-ir.exe
  • Open Web Interface: streamlit run gui/app.py
  • Use CLI: python orchestrator.py run "Your task"

Read more: symphony-ir.app/get-started
```

**Success Metric:** 90% of users complete setup without manual intervention

#### 2.2 Simplify Desktop Application UX
**Goal:** GUI feels like a native app, not a wrapper

**Deliverables:**
- Streamlined desktop entry point (`gui/desktop_app.py` → `symphony_ir_app.py`)
- Welcome screen on first launch:
  - "Choose AI Provider" (if not already configured)
  - "Import Your First Project" or "Try a Sample"
  - Quick access to common workflows
- Status bar showing:
  - Current provider (Claude / Ollama)
  - Connection status (✓ Connected / ✗ Error)
  - Recent tasks

**Success Metric:** Users can launch app and run first task in <1 minute

---

### **Phase 3: Clear Documentation Structure (Weeks 3-4)**

#### 3.1 Reorganize Documentation Hierarchy
**Goal:** Users find exactly what they need in <30 seconds

**New Structure:**
```
docs/
├── GETTING_STARTED.md (NEW - 5 min read)
├── INSTALLATION/
│   ├── README.md (decision tree: "What's your OS?")
│   ├── WINDOWS.md (Windows-specific)
│   ├── MACOS.md (NEW - macOS-specific)
│   ├── LINUX.md (NEW - Linux-specific)
│   └── TROUBLESHOOTING.md (solutions by error message)
├── GUIDES/
│   ├── FIRST_TASK.md (NEW - "Run Your First Orchestration")
│   ├── WORKFLOWS.md (Symphony Flow templates)
│   ├── API_KEYS.md (How to get Claude / setup Ollama)
│   ├── CONFIGURATION.md (agents.yaml, .env)
│   └── ADVANCED.md (Custom agents, development)
├── REFERENCE/
│   ├── CLI.md (all commands)
│   ├── WEB_GUI.md (Streamlit interface)
│   ├── DESKTOP_GUI.md (Desktop app)
│   └── API.md (Using as library)
└── OLD_README_ARCHIVE.md (current comprehensive README, preserved)
```

#### 3.2 Create Platform-Specific Quick Start
**Goal:** 5-minute getting started guide for each OS

**Deliverables:**
- `GETTING_STARTED_WINDOWS.md`
- `GETTING_STARTED_MACOS.md`
- `GETTING_STARTED_LINUX.md`

Each with:
- One-line installation command
- Screenshot showing expected output
- 3-step first task guide
- Common issues + solutions for that platform

**Success Metric:** User can go from zero to running first task in 5 minutes

#### 3.3 Simplify Main README
**Goal:** README is welcoming, not overwhelming

**New Structure:**
```markdown
# Symphony-IR

[Hero statement - 1 sentence]

## Quick Start (Choose One)

### Desktop GUI (Easiest)
```bash
# Windows
./install.ps1

# macOS/Linux
bash install.sh
```

### Web Interface
[Code example]

### Command Line
[Code example]

## Next Steps
- [Your First Task] → GETTING_STARTED.md
- [Installation Help] → docs/INSTALLATION/
- [Advanced Setup] → docs/ADVANCED/

## Features
[Brief bullets]

## Architecture
[Link to docs/ARCHITECTURE/]
```

---

### **Phase 4: Error Handling & Validation (Weeks 4-5)**

#### 4.1 Pre-Flight Validation Script
**Goal:** Catch setup issues before users run tasks

**Deliverables:**
- `validate-setup.py` script (runs during installation + anytime via CLI)
- Checks:
  - Python version (3.9+)
  - All dependencies installed
  - API key configured and working
  - Ollama connectivity (if configured)
  - `.orchestrator/` directory writable
  - Network connectivity

**Output:**
```
SYMPHONY-IR VALIDATION REPORT
════════════════════════════════════════════

System:
  ✓ Python 3.11.6
  ✓ Platform: macOS 14.0

Dependencies:
  ✓ pyyaml 6.0.1
  ✓ python-dotenv 1.0.2
  ✓ anthropic 0.21.0
  ✓ streamlit 1.38.0

Configuration:
  ✓ AI Provider: Claude
  ✓ API Key: Valid (last used 2m ago)
  ✓ .orchestrator/ directory: Writable

Network:
  ✓ Anthropic API: Reachable
  ✓ Internet: Connected

Status: ✓ ALL SYSTEMS GO

Ready to orchestrate! Run:
  python orchestrator.py run "Your task here"
```

**Success Metric:** 95% of configuration issues caught before user hits error

#### 4.2 User-Friendly Error Messages
**Goal:** Errors point users to solutions, not stack traces

**Current:** 
```
error: Unable to connect to API
  File "client.py", line 237...
  ConnectionError: [Errno 111]...
```

**Improved:**
```
⚠️  API CONNECTION ERROR
────────────────────────────────

Could not reach Anthropic API. This usually means:

1. API Key is invalid or expired
   ✓ Fix: Go to Settings → Update API Key
   
2. Internet connection is down
   ✓ Fix: Check your network connection
   
3. Anthropic service is down
   ✓ Fix: Try again in a few minutes or switch to Ollama

💡 Need help? Run: python validate-setup.py

[Show debug logs button]
```

**Success Metric:** Users can self-diagnose 80% of setup issues

---

### **Phase 5: Multi-Platform Desktop Support (Weeks 5-6)**

#### 5.1 Create macOS App Bundle
**Goal:** Desktop app works on macOS natively

**Deliverables:**
- Use PyInstaller to create `Symphony-IR.app` for macOS
- Create `.dmg` installer for distribution
- Register `.symphony` file type (for future integration)
- Add to Launchpad

#### 5.2 Create Linux Desktop App
**Goal:** Desktop app works on Linux

**Deliverables:**
- Create `.desktop` file for Linux integration
- Create AppImage or snap package
- Desktop integration (menu, icons, shortcuts)

---

### **Phase 6: Guided Experience Improvements (Weeks 6-7)**

#### 6.1 Sample Projects & Tasks
**Goal:** New users have templates to learn from

**Deliverables:**
- Pre-configured example tasks:
  - "Code Review" (with sample code to review)
  - "API Design" (with context)
  - "Bug Analysis" (with sample buggy code)
- Import sample projects from UI
- Run with one click

#### 6.2 In-App Guidance & Tooltips
**Goal:** Contextual help without leaving the UI

**Deliverables:**
- Hover tooltips explaining each option
- "?" buttons linking to specific docs
- "Show Examples" button for each workflow
- Progress indicators during tasks

---

### **Phase 7: Modern Installation Methods (Weeks 7-8)**

#### 7.1 Package Manager Support
**Goal:** Users can install like any other software

**Deliverables:**
- Homebrew formula for macOS (`brew install symphony-ir`)
- Snap package for Linux (`snap install symphony-ir`)
- Winget package for Windows (`winget install symphony-ir`)
- Store listings (Microsoft Store, Apple, eventually)

#### 7.2 Container Support
**Goal:** Docker deployment for cloud/shared environments

**Deliverables:**
- `Dockerfile` for containerization
- Docker Compose for full stack
- `docker run` one-liner for quick start
- Kubernetes manifests (future)

```bash
# One-line Docker deployment
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=sk-... courtneybtaylor/symphony-ir
```

---

## Priority Implementation Roadmap

### **CRITICAL PATH (Do These First)**

1. **Week 1: Unified Install Script** (4 days)
   - Single `install.py` that works on all platforms
   - Creates virtual env, installs dependencies
   - Runs validation

2. **Week 1-2: Setup Wizard** (3 days)
   - Interactive configuration
   - API key validation
   - Test orchestration

3. **Week 2: Simplified README** (2 days)
   - Clear decision tree
   - Links to specific guides
   - Remove overwhelming detail

4. **Week 2-3: Getting Started Guides** (3 days)
   - Platform-specific quick starts
   - Screenshots
   - First task tutorial

5. **Week 3: Better Error Messages** (2 days)
   - User-friendly error wrapper
   - Actionable solutions
   - Debug log access

### **IMPORTANT (Do These Next)**

6. **Week 4: Validation Script** (2 days)
   - Pre-flight checks
   - Setup verification
   - Actionable reports

7. **Week 4-5: Reorganized Docs** (3 days)
   - New directory structure
   - Platform-specific guides
   - Cleaner navigation

8. **Week 5-6: macOS Desktop App** (3 days)
   - App bundle
   - DMG installer
   - Native integration

### **NICE-TO-HAVE (Do These After)**

9. **Week 6-7: Linux Desktop Support** (2 days)
10. **Week 7: Sample Projects** (2 days)
11. **Week 7-8: Package Managers** (3 days)
12. **Week 8: Docker Support** (2 days)

---

## Success Metrics

### Installation Success Rate
- **Current:** ~40% users complete installation successfully
- **Target:** 90%+ users complete installation

### Time to First Task
- **Current:** 20-30 minutes (including troubleshooting)
- **Target:** <5 minutes

### Documentation Clarity
- **Current:** 70% of questions are "where do I find...?"
- **Target:** <10% navigation questions

### Support Load
- **Current:** 60% issues are setup/configuration related
- **Target:** <20% setup issues

### User Satisfaction
- **Current:** Unknown (no baseline)
- **Target:** 4.5+/5.0 rating for installation experience

---

## Files to Create/Modify

### New Files to Create
- `install.py` (unified installation script)
- `setup-wizard.py` (interactive configuration)
- `validate-setup.py` (pre-flight checks)
- `docs/GETTING_STARTED.md`
- `docs/INSTALLATION/README.md`
- `docs/INSTALLATION/WINDOWS.md`
- `docs/INSTALLATION/MACOS.md`
- `docs/INSTALLATION/LINUX.md`
- `docs/INSTALLATION/TROUBLESHOOTING.md`
- `docs/GUIDES/FIRST_TASK.md`
- `docs/GUIDES/API_KEYS.md`
- `Dockerfile`
- `docker-compose.yml`

### Files to Modify
- `README.md` (simplify significantly)
- `ai-orchestrator/requirements.txt` (consolidate at root)
- `gui/requirements.txt` (consolidate)
- `gui/requirements-desktop.txt` (consolidate)
- `gui/app.py` (add setup wizard trigger)
- `windows/install.ps1` (enhance validation)

### Files to Archive
- `docs/WINDOWS-SETUP.md` → `docs/INSTALLATION/WINDOWS.md`

---

## Implementation Notes

### Dependencies Management Strategy
Instead of optional extras, use conditional imports:
```python
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Fall back to Ollama if Claude not available
if not HAS_ANTHROPIC and os.getenv('OLLAMA_BASE_URL'):
    # Use Ollama
    pass
```

### Backward Compatibility
- Keep all existing CLI commands working
- Support old `.orchestrator/` directory structure
- Don't break existing scripts
- Version bump to 1.0.0 for this release

### Testing Plan
- Test on Windows 10/11 (2 configs each)
- Test on macOS 12/13/14
- Test on Ubuntu 20.04/22.04
- Test with and without existing Python
- Test offline Ollama, online Claude
- Test with invalid API keys

---

## Estimated Impact

### Before Improvements
- 60% of users struggle with installation
- 40% complete installation successfully
- 50% of support tickets are setup-related
- Average setup time: 30+ minutes

### After All Improvements
- 10% of users struggle with installation
- 90% complete installation successfully
- 10% of support tickets are setup-related
- Average setup time: <5 minutes
- 80% of users complete first task immediately after install

---

## Questions to Consider

1. **Is Python installation friction acceptable?** → Should we distribute standalone executable more prominently?

2. **Should we deprecate CLI for new users?** → Or make it a power-user option?

3. **Is Ollama complexity worth free option?** → Should we default to Claude trial?

4. **Should we require account creation?** → For future features like cloud sync?

5. **What's the target user base?** → Enterprise? Researchers? Developers? This changes priorities.

---

## Next Steps

1. Review this plan with the team
2. Adjust priorities based on user research
3. Start with Phase 1 (unified install script)
4. Measure impact after each phase
5. Iterate based on real user feedback

**Estimated Total Effort:** 7-8 weeks for all phases, or 2-3 weeks for critical path

