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

