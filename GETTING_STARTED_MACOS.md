# 🚀 Getting Started on macOS

**Time needed:** 5 minutes
**Prerequisites:** macOS 10.14+, Python 3.9+

---

## Step 1: Install Python (if needed)

**Check if Python is installed:**
```bash
python3 --version
```

**If Python is not installed:**

**Option A: Using Homebrew (Recommended)**
```bash
brew install python3
```

**Option B: Download from Python.org**
1. Visit https://www.python.org/downloads/macos/
2. Download Python 3.11 (latest stable)
3. Run the installer
4. Follow the setup wizard

---

## Step 2: Run the Symphony-IR Installer

**Option A: Direct Download (Easiest)**
1. Clone or download the repository:
   ```bash
   git clone https://github.com/courtneybtaylor-sys/Symphony-IR.git
   cd Symphony-IR
   ```

**Option B: Using curl**
```bash
curl -fsSL https://raw.githubusercontent.com/courtneybtaylor-sys/Symphony-IR/main/install.sh | bash
```

**Option C: Manual Download**
1. Visit the [GitHub repository](https://github.com/courtneybtaylor-sys/Symphony-IR)
2. Click **"Code"** → **"Download ZIP"**
3. Extract the folder
4. Open Terminal and navigate to it:
   ```bash
   cd /path/to/Symphony-IR
   ```

---

## Step 3: Run the Installation Script

```bash
chmod +x install.sh  # Make script executable
./install.sh
```

**What it does:**
- ✅ Detects macOS version
- ✅ Checks Python 3.9+
- ✅ Creates virtual environment (optional)
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
2. Install and launch
3. Open Terminal and run:
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

**Method 2: Create an alias** (optional, for future launches)
```bash
echo "alias symphony='python3 ~/path/to/Symphony-IR/gui/main.py'" >> ~/.zshrc
source ~/.zshrc
symphony  # Now you can just type 'symphony'
```

**Method 3: Create an App shortcut** (optional)
```bash
# Create a launcher script
cat > ~/Applications/Symphony-IR.command << 'EOF'
#!/bin/bash
cd /path/to/Symphony-IR
python3 gui/main.py
EOF

chmod +x ~/Applications/Symphony-IR.command
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

### View Your History
- **"Sessions"** tab shows all past orchestrations
- Download sessions as JSON files

### Check Metrics
- **"Metrics"** tab shows tokens used, execution phases, confidence scores

---

## ❓ Troubleshooting

### "Python not found"
```bash
# Install Python
brew install python3

# Verify
python3 --version
```

### "API key rejected"
1. Visit https://console.anthropic.com
2. Check your API key (starts with `sk-ant-`)
3. Generate a new key if needed
4. Try again

### "Ollama not found"
```bash
# Install Ollama
brew install ollama

# Or download from https://ollama.ai

# Pull a model
ollama pull llama2
```

### App won't launch
```bash
# Run directly to see the error
python3 gui/main.py

# Or check the log
tail -50 ~/.orchestrator/logs.txt
```

### Permission denied
```bash
# Make the script executable
chmod +x install.sh
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
