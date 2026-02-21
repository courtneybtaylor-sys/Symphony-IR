# 🚀 Getting Started on Linux

**Time needed:** 5 minutes
**Prerequisites:** Ubuntu 20.04+ / Debian 11+ / Fedora 35+, Python 3.9+

---

## Step 1: Install Python and Dependencies

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install python3 python3-venv python3-dev python3-pip git
```

**Fedora / RHEL / CentOS:**
```bash
sudo dnf install python3 python3-devel python3-pip git
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip git
```

**Verify Python is installed:**
```bash
python3 --version
```

---

## Step 2: Clone the Repository

```bash
git clone https://github.com/courtneybtaylor-sys/Symphony-IR.git
cd Symphony-IR
```

---

## Step 3: Run the Installation Script

```bash
chmod +x install.sh  # Make script executable
./install.sh
```

**What it does:**
- ✅ Detects OS (Ubuntu, Fedora, etc.)
- ✅ Checks Python 3.9+
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Initializes orchestrator
- ✅ Configures AI provider (Claude/Ollama/Both)

---

## Step 4: Choose Your AI Provider

The installer will ask: **"Which AI provider would you like to use?"**

### Option 1: Claude (Cloud API) — Recommended for Production
**Setup (2 minutes):**
1. Visit https://console.anthropic.com
2. Sign up (free account)
3. Click "Generate API Key"
4. Copy the key (starts with `sk-ant-`)
5. Paste when the installer asks
6. Done! ✅

**Cost:** Pay as you go (~$0.0008 per 1K tokens)
**Best for:** Production workloads, consistent results

### Option 2: Ollama (Local, Free) — Recommended for Learning
**Setup (5-10 minutes):**
1. Download Ollama from https://ollama.ai
2. Extract and install:
   ```bash
   curl https://ollama.ai/install.sh | sh
   ```
3. Pull a model:
   ```bash
   ollama pull llama2
   ```
4. Done! ✅

**Cost:** Free
**Best for:** Privacy, offline work, experimentation

### Option 3: Both (Maximum Flexibility)
Install both to use whichever fits your task.

---

## Step 5: Launch Symphony-IR

**Method 1: Run directly**
```bash
python3 gui/main.py
```

**Method 2: From the virtual environment**
```bash
source venv/bin/activate
python3 gui/main.py
```

**Method 3: Create an alias** (optional)
```bash
# Add to ~/.bashrc or ~/.zshrc
echo "alias symphony='cd ~/Symphony-IR && python3 gui/main.py'" >> ~/.bashrc
source ~/.bashrc

# Now you can just type:
symphony
```

**Method 4: Create a desktop shortcut** (optional, GNOME/KDE)
```bash
cat > ~/.local/share/applications/symphony-ir.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Symphony-IR
Exec=python3 /home/USER/Symphony-IR/gui/main.py
Icon=application-x-python
Categories=Development;
Terminal=false
EOF

# Replace USER with your username
# Now Symphony-IR appears in your application menu
```

---

## Step 6: Try Your First Orchestration

1. Open Symphony-IR
2. Go to the **"Orchestrator"** tab
3. In the **Task Description** box, type:
   ```
   Write a Python function that checks if a number is prime
   ```
4. Click **"Execute Orchestration"**
5. Watch as Claude/Ollama generates code! 🎉

---

## 🎯 Next Steps

### Learn Symphony Flow (Guided Workflows)
1. Go to the **"Flow"** tab
2. Choose a workflow:
   - Code Review
   - Refactor Code
   - New Feature
   - API Design
3. Follow the wizard

### Try More Examples
```bash
# Open Symphony-IR and try these tasks:

1. "Write unit tests for a Python function"
2. "Design a REST API for a blog application"
3. "Create a database schema for an e-commerce site"
4. "Write documentation for a Python library"
5. "Review this code for security issues"
```

### Use from Command Line
You can also use the orchestrator from the terminal:
```bash
# Activate virtualenv
source venv/bin/activate

# Run a task
python3 ai-orchestrator/orchestrator.py run "Your task here"

# View history
python3 ai-orchestrator/orchestrator.py history

# List flows
python3 ai-orchestrator/orchestrator.py flow-list
```

---

## ❓ Troubleshooting

### "Python not found"
```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv

# Verify
python3 --version
```

### "Permission denied" on install.sh
```bash
chmod +x install.sh
```

### "pip: command not found"
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# Fedora
sudo dnf install python3-pip
```

### "Module not found: PyQt6"
```bash
# Run the install script again
./install.sh

# Or manually install:
python3 -m pip install PyQt6==6.6.1 PyQt6-Charts==6.6.0 keyring
```

### "API key rejected"
1. Visit https://console.anthropic.com
2. Check your API key (starts with `sk-ant-`)
3. Generate a new key if needed

### "Ollama connection failed"
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Start the service
ollama serve  # Run in another terminal

# In another terminal, pull a model
ollama pull llama2
```

### Display issues (missing icons, text rendering)
```bash
# Install additional fonts
sudo apt install fonts-dejavu fonts-liberation

# Try running again
python3 gui/main.py
```

---

## 📚 Learn More

- **README.md** — Overview
- **docs/ARCHITECTURE.md** — Deep dive
- **docs/FLOW.md** — Symphony Flow guide
- **docs/TROUBLESHOOTING.md** — Common issues

---

## 💬 Need Help?

- **GitHub Issues:** https://github.com/courtneybtaylor-sys/Symphony-IR/issues
- **GitHub Discussions:** https://github.com/courtneybtaylor-sys/Symphony-IR/discussions

---

**Congratulations!** 🎉 You've set up Symphony-IR. Start building!
