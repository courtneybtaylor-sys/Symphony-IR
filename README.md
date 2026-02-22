# 🎼 Symphony-IR

**Deterministic multi-agent AI orchestration.** Run complex workflows with Claude, GPT-4, or local Ollama.

---

## 🚀 Get Started in 5 Minutes

**Choose your path:**

### 👤 I want to use Symphony-IR now
- [Getting Started Guide](GETTING_STARTED.md) (Windows, macOS, Linux)

### 📚 I want to learn about it first
- [Architecture & Features](docs/ARCHITECTURE.md)
- [How Symphony Flow works](docs/FLOW.md)
- [Claude vs Ollama comparison](docs/PROVIDERS.md)

### 👨‍💻 I want to integrate it into my code
- [Python API Reference](docs/API.md)
- [CLI Guide](docs/CLI.md)
- [Contributing Guide](CONTRIBUTING.md)

---

## ✨ What Symphony-IR Does

**In 30 seconds:**
- 🤖 Coordinates multiple AI agents to solve complex problems
- 🎯 Tracks costs and token usage
- 🔐 Stores API keys securely (system Credential Manager)
- 📊 Provides a beautiful desktop GUI (Windows/Mac/Linux)
- 🎨 Includes guided workflows (Code Review, API Design, Testing, etc.)

**Real examples:**
- Analyze entire codebases for bugs or refactoring
- Design database schemas with expert guidance
- Create comprehensive test suites
- Write documentation automatically
- Validate API designs before implementation

---

## 🎯 Three Ways to Use It

### 1️⃣ Desktop App (Easiest)
```bash
# After installation, just run:
python gui/main.py
```
✨ Beautiful point-and-click interface
📊 Real-time progress tracking
🗂️ Session history and downloads
⚙️ Settings tab for API keys

### 2️⃣ Command Line
```bash
python orchestrator.py run "Write a Python function that checks if a number is prime"
python orchestrator.py flow --template code_review --var component=auth.py
python orchestrator.py history
```
💻 Powerful for automation
🔄 Perfect for scripts and CI/CD
📋 Full CLI documentation in [docs/CLI.md](docs/CLI.md)

### 3️⃣ Web Browser (Streamlit)
```bash
cd gui && streamlit run app.py
```
🌐 Access from any browser
📈 Advanced metrics dashboard
📤 Import/export sessions

---

## 🎯 Try It Now

```bash
# Step 1: Install (choose your platform above)
# Takes 5 minutes with the automated installer

# Step 2: Try your first task
# Launch Symphony-IR and type:
#   "Write a Python function that checks if a number is prime"

# Step 3: Explore Symphony Flow
# Go to "Symphony Flow" tab and pick a workflow template
```

---

## 📖 Documentation

All documentation is organized in the [`docs/`](docs/) directory. Here's where to find what you need:

| Want to... | Read... |
|------------|---------|
| **Get started** | [Getting Started](GETTING_STARTED.md) |
| **Learn the architecture** | [Architecture Overview](docs/ARCHITECTURE.md) |
| **Use the CLI** | [CLI Guide](docs/USAGE/CLI.md) |
| **Use the GUI** | [GUI Guide](docs/USAGE/GUI.md) |
| **Use as a Python library** | [Python API](docs/USAGE/PYTHON_API.md) |
| **Understand workflows** | [Templates Guide](docs/USAGE/TEMPLATES.md) |
| **Set up for development** | [Development Setup](docs/DEVELOPMENT/SETUP.md) |
| **Contribute code** | [Contributing Guide](CONTRIBUTING.md) |
| **View the roadmap** | [Project Roadmap](ROADMAP.md) |
| **Report security issues** | [Security Policy](SECURITY.md) |

**👉 [Full Documentation Hub →](docs/)**

---

## 💬 Need Help?

- **GitHub Issues:** [Report bugs](https://github.com/courtneybtaylor-sys/Symphony-IR/issues)
- **GitHub Discussions:** [Ask questions](https://github.com/courtneybtaylor-sys/Symphony-IR/discussions)
- **Troubleshooting:** [Common issues & solutions](docs/TROUBLESHOOTING.md)

---

## 🎁 Features at a Glance

✅ **Multi-agent orchestration** — Architect, Implementer, Reviewer roles working together
✅ **Beautiful desktop GUI** — Point-and-click interface with session history
✅ **Guided workflows** — 7 templates (Code Review, API Design, Testing, etc.)
✅ **Cost tracking** — See exactly what you're spending on API calls
✅ **Works with Claude & Ollama** — Cloud or local, your choice
✅ **Secure credentials** — API keys stored in system Credential Manager
✅ **Session management** — Save, download, and replay executions
✅ **Real-time progress** — Watch as AI agents work through your task

---

## 📝 License & Patent Protection

Symphony-IR is released under the **Apache License 2.0** to enable:

✅ **Wide adoption** — Use in commercial and non-commercial projects
✅ **Derivative works** — Modify and build upon Symphony-IR
✅ **Sublicensing** — Include in proprietary products
✅ **Patent protection** — Explicit patent grant protects you and contributors (critical for AI/ML products)

**What this means for you:**
- You can use Symphony-IR in closed-source products
- You must include the original license and copyright notice
- You receive an explicit patent grant for AI/ML use cases
- No warranties or liability (see [LICENSE.txt](LICENSE.txt) for details)

For enterprise licensing, partnerships, or support: contact the maintainers

---

**Ready?** [Get started now →](GETTING_STARTED.md)
