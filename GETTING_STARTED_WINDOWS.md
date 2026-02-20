# 🚀 Getting Started on Windows

**Time needed:** 5 minutes
**Prerequisites:** Windows 10 or later, Python 3.9+

---

## Step 1: Install Python (if needed)

**Check if Python is installed:**
```cmd
python --version
```

**If Python is not installed:**
1. Visit https://www.python.org/downloads/
2. Download Python 3.11 (latest stable)
3. **Important:** Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Close the installer

---

## Step 2: Run the Symphony-IR Installer

**Option A: From GitHub (Easiest)**
1. Visit https://github.com/courtneybtaylor-sys/Symphony-IR/releases
2. Download `Symphony-IR-1.0.0-Setup.exe`
3. Double-click the file
4. Click "Next" → "Install" → "Finish"
5. Symphony-IR will launch automatically

**Option B: From Source (If you cloned the repo)**
1. Open Command Prompt
2. Navigate to the Symphony-IR folder:
   ```cmd
   cd C:\path\to\Symphony-IR
   ```
3. Run the installer:
   ```cmd
   install.bat
   ```
4. Follow the prompts to choose Claude or Ollama

---

## Step 3: Set Up Your AI Provider

The installer will ask: **"Which AI provider would you like to use?"**

### Option 1: Claude (Cloud API) — Recommended for Production
**Setup (2 minutes):**
1. Visit https://console.anthropic.com
2. Sign up (free account)
3. Click "Generate API Key" in the top right
4. Copy the key (starts with `sk-ant-`)
5. Paste into Symphony-IR when prompted
6. Done! ✅

**Cost:** Pay as you go (~$0.0008 per 1K tokens)
**Best for:** Production workloads, consistent results

### Option 2: Ollama (Local, Free) — Recommended for Learning
**Setup (5-10 minutes):**
1. Download Ollama from https://ollama.ai
2. Install and launch the app
3. Open Command Prompt and run:
   ```cmd
   ollama pull llama2
   ```
   (First download takes 5-10 minutes, ~4GB)
4. Done! Ollama runs in the background ✅

**Cost:** Free
**Best for:** Privacy, offline work, experimentation

### Option 3: Both (Maximum Flexibility)
Install both Claude and Ollama to use whichever fits your task.

---

## Step 4: Launch Symphony-IR

**Method 1: Click the Shortcut**
- Look for "Symphony-IR" on your Desktop or Start Menu
- Double-click it

**Method 2: Command Prompt**
```cmd
python gui\main.py
```

**Method 3: Windows Run Dialog**
- Press `Win + R`
- Type: `python gui\main.py`

---

## Step 5: Try Your First Orchestration

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
3. Follow the wizard — each step asks a question and Claude helps decide

### Explore More Examples
```cmd
# Try these tasks in the Orchestrator tab:

1. "Write unit tests for a Python function"
2. "Design a REST API for a blog application"
3. "Create a database schema for an e-commerce site"
4. "Write documentation for a Python library"
5. "Review this code for security issues" (then paste code)
```

### View Your History
- **"Sessions"** tab shows all past orchestrations
- Click any session to view the full output
- Download sessions as JSON files

### Check Metrics
- **"Metrics"** tab shows:
  - Tokens used (cost tracking)
  - Execution phases
  - Confidence scores

---

## ❓ Troubleshooting

### "Python not found"
**Solution:**
1. Install Python 3.9+ from https://www.python.org
2. **Important:** Check "Add Python to PATH"
3. Restart your computer
4. Try again

### "API key rejected"
**Solution:**
1. Visit https://console.anthropic.com
2. Check your API key (should start with `sk-ant-`)
3. Make sure it hasn't been revoked
4. Generate a new key if needed

### "Ollama not found"
**Solution:**
1. Download Ollama from https://ollama.ai
2. Install and launch the app
3. Run: `ollama pull llama2`
4. Wait for the model to download (~4GB)

### App won't launch
**Solution:**
1. Open Command Prompt
2. Navigate to the project folder
3. Run: `python gui\main.py`
4. Check the error message and refer to [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

### Dependencies failed to install
**Solution:**
1. Open Command Prompt
2. Run:
   ```cmd
   python -m pip install --upgrade pip
   python -m pip install -r gui\requirements-desktop.txt
   ```
3. Try launching again

---

## 📚 Learn More

- **README.md** — Overview of Symphony-IR
- **docs/ARCHITECTURE.md** — How it works under the hood
- **docs/FLOW.md** — Deep dive into Symphony Flow
- **docs/TROUBLESHOOTING.md** — Common issues and fixes

---

## 💬 Need Help?

- **GitHub Issues:** https://github.com/courtneybtaylor-sys/Symphony-IR/issues
- **GitHub Discussions:** https://github.com/courtneybtaylor-sys/Symphony-IR/discussions

---

**Congratulations!** 🎉 You've set up Symphony-IR. Now go build something amazing!
