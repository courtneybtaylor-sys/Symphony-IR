# Symphony-IR

Deterministic multi-agent orchestration engine with structured guidance and Web UI.

## Features

### Core Orchestration
- **Multi-agent coordination**: Architect, Implementer, Reviewer, Researcher, Integrator
- **Deterministic execution**: Hard termination limits and confidence thresholds
- **PromptIR**: Structured intermediate representation for prompts
- **Governance layer**: Cost-efficient policy checks before token spending
- **Token optimization**: Prompt compiler and schema validator for efficiency

### Web Interface (Streamlit GUI)
- **Task execution**: Run orchestration jobs from browser
- **Real-time output**: Color-coded execution results
- **Session management**: View and download execution results
- **Metrics dashboard**: Track tokens, costs, confidence scores
- **Session upload**: Import and analyze existing sessions

### Symphony Flow - Guided Decision-Tree Workflows
- **Guided workflows**: Bounded decision trees (2-4 options per step)
- **7 built-in templates**: Code review, refactoring, new features, API design, database schema, testing, documentation
- **Flow tracking**: Persistent state across decisions with full history
- **Direct PromptIR mapping**: Each node maps to orchestrator execution
- **Interactive CLI**: Make bounded choices, automatic execution, real-time feedback
- **Flow management**: List templates, view project status, browse sessions

## Installation

### Prerequisites

**Option A: Use Cloud Claude (Recommended for Quality)**
- Python 3.9+
- API key for Claude (Anthropic)

**Option B: Use Local Ollama (Free, No API Key Required)**
- Python 3.9+
- Ollama installed (https://ollama.ai)
- A local LLM model (llama2, mistral, etc.)

### Quick Start

**Windows Users: Desktop GUI (No Terminal!)**

```batch
REM Download or clone Symphony-IR
REM Then double-click: run-gui.bat

REM Or use PowerShell installer:
REM   Right-click PowerShell as Admin
REM   Run: .\windows\install.ps1
```

See [docs/WINDOWS-SETUP.md](docs/WINDOWS-SETUP.md) for complete Windows installation guide with:
- One-click installer
- Standalone executable
- Desktop shortcuts
- System tray integration

**Linux/macOS or Advanced Users:**

```bash
# Clone and install
git clone https://github.com/courtneybtaylor-sys/Symphony-IR.git
cd Symphony-IR

# Set up orchestrator
cd ai-orchestrator
python orchestrator.py init --project ..

# Add your API keys
export ANTHROPIC_API_KEY=sk-...
```

## Usage

### Via Desktop GUI (Windows - Easiest!)

**No terminal commands needed!**

```batch
REM Simply double-click:
run-gui.bat
```

Or use the installer:
```powershell
# Right-click PowerShell as Admin, then:
.\windows\install.ps1
```

The desktop app includes:
- 🎼 **Orchestrator Tab**: Run AI orchestration tasks with full control
- 🗺️ **Symphony Flow Tab**: Guided workflows (Code Review, API Design, Testing, etc.)
- 📋 **History Tab**: Browse all past executions
- ⚙️ **Settings Tab**: Configure API keys, models, preferences

**Features:**
- ✅ Point-and-click interface
- ✅ Real-time progress and output
- ✅ Session history and management
- ✅ Settings persistence
- ✅ Works with Claude (cloud) or Ollama (local)
- ✅ No terminal required

See [docs/WINDOWS-SETUP.md](docs/WINDOWS-SETUP.md) for detailed setup.

### Via CLI (Traditional)

```bash
# Initialize
python orchestrator.py init --project .

# Run a task
python orchestrator.py run "Design a user authentication system"

# View results
python orchestrator.py history --limit 10
```

### Via Streamlit GUI (Web Interface)

```bash
# From repository root
cd gui
pip install -r requirements.txt
streamlit run app.py
```

Then visit `http://localhost:8501` in your browser.

**Features:**
- Task description input with variable support
- Real-time execution output display
- Session file browsing and download
- Metrics and token analysis dashboard
- Session JSON upload and import

See [gui/README.md](gui/README.md) for full documentation.

### Via Symphony Flow - Guided Workflows

List available templates:

```bash
python orchestrator.py flow-list
```

Run a guided workflow:

```bash
python orchestrator.py flow --template code_review --var component=auth.py
python orchestrator.py flow --template refactor_code --var component=main.py
python orchestrator.py flow --template new_feature --var feature="API endpoint"
python orchestrator.py flow --template api_design --var api_name="user-service"
python orchestrator.py flow --template database_schema --var database_name="accounts"
python orchestrator.py flow --template testing_strategy --var component_name="payment"
python orchestrator.py flow --template documentation --var project_name="MyProject"
```

View flow project status:

```bash
python orchestrator.py flow-status
```

**Built-in Templates:**
- `code_review`: Guided code review (bugs, style, performance)
- `refactor_code`: Refactoring guide (design, quick fixes, dependencies)
- `new_feature`: Feature planning (architecture, checklist, risks)
- `api_design`: API design (REST, GraphQL, hybrid)
- `database_schema`: Database design (SQL, NoSQL, hybrid)
- `testing_strategy`: Testing plans (unit, integration, performance, security)
- `documentation`: Documentation planning (user, developer, architecture)

See [docs/FLOW.md](docs/FLOW.md) for comprehensive guide.

## Architecture

```
CLI/GUI Input
    ↓
Task → Conductor (planning)
    ↓
Phase Plans → Agents (parallel execution)
    ↓
PromptIR → Compiler → Claude API
    ↓
Responses → Synthesis → Ledger
```

### Key Components

- **PromptIR**: Structured prompt representation with governance hooks
- **Orchestrator**: State machine for multi-phase coordination
- **Compiler**: Token optimization and format enforcement
- **Agents**: Specialized roles (architect, implementer, reviewer, etc.)
- **Governance**: Policy layer for cost control and safety

## Configuration

### agents.yaml

Located in `.orchestrator/agents.yaml`. Customize:
- Agent roles and model providers
- Temperature, token limits, system prompts
- Custom constraints and output formats

### .env

Set environment variables:
```
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=...
```

## Flow Templates

### code_review.yaml
- **Start**: Choose focus (bugs, style, performance)
- **Bugs**: Identify logic errors with severity
- **Style**: Check conventions and consistency
- **Performance**: Find bottlenecks and optimizations

### refactor_code.yaml
- **Start**: Analyze structure
- **Design**: Propose improved architecture
- **Fixes**: Quick refactoring wins
- **Dependencies**: Optimize and upgrade

### new_feature.yaml
- **Start**: Define requirements
- **Design**: Create technical architecture
- **Checklist**: Implementation steps
- **Risks**: Identify and mitigate risks

## Examples

### Example 1: Code Review via Flow

```bash
export SYMPHONY_EXPERIMENTAL_FLOW=1
python orchestrator.py flow --template code_review --var component=src/auth.py
```

Output:
```
🎼 Symphony Flow: code_review
📋 Project: a1b2c3d4

✓ Starting code review

What's next?
  A) Focus on bugs
      Look for potential bugs and logic errors
  B) Focus on style
      Check code style and conventions
  C) Focus on performance
      Identify performance bottlenecks

Choice: A

⚙️  Executing via Symphony-IR...

✓ Execution complete
  Run ID: xyz789
  Confidence: 0.92
  Decisions: 1

🎉 Workflow complete!

💾 Session saved: .orchestrator/flows/a1b2c3d4.json
🗺️  Path: 1. Starting code review -> A
```

### Example 2: Using Streamlit GUI

1. Open browser to `http://localhost:8501`
2. Enter task: "Review authentication system for security vulnerabilities"
3. Add variable: `component=auth.py`
4. Click "▶ Run Orchestrator"
5. View results in Output tab
6. Browse previous sessions in Sessions tab
7. Analyze metrics in Metrics tab

### Example 3: Using Local Ollama Models (No API Key Needed)

```bash
# Install and start Ollama
brew install ollama        # or from https://ollama.ai
ollama pull llama2         # Download a model
ollama serve              # Start server (runs on localhost:11434)

# Use Ollama config
cp ai-orchestrator/config/agents-ollama.yaml .orchestrator/agents.yaml

# Run workflows with local models (completely free)
python orchestrator.py run "Your task here"
python orchestrator.py flow --template code_review --var component=src/main.py
```

See [docs/OLLAMA.md](docs/OLLAMA.md) for:
- Model selection guide (llama2, mistral, dolphin-mixtral)
- Performance tips and GPU acceleration
- Cost comparison (Ollama: free vs Claude: paid)
- Troubleshooting guide

**Available Local Models:**
- `llama2`: Fast, good quality (4GB) - default
- `mistral`: Faster & better (5GB) - recommended
- `neural-chat`: Great for conversations (5GB)
- `dolphin-mixtral`: Most capable (45GB, requires 24GB+ VRAM)

## Development

### Adding a New Flow Template

1. Create `ai-orchestrator/flow/templates/my_template.yaml`
2. Define template_id, nodes, and options (see [docs/FLOW.md](docs/FLOW.md))
3. Test it: `python orchestrator.py flow --template my_template --var key=value`
4. View it: `python orchestrator.py flow-list`

### Running Tests

```bash
# Test CLI
python orchestrator.py status
python orchestrator.py history

# Test GUI
cd gui
streamlit run app.py

# Test Flow
python orchestrator.py flow-list
python orchestrator.py flow --template code_review --var component=test.py

# Test with local Ollama
cp ai-orchestrator/config/agents-ollama.yaml .orchestrator/agents.yaml
ollama serve &
python orchestrator.py flow --template code_review --var component=test.py
```

## Troubleshooting

### "orchestrator.py not found"
Ensure you're in the `ai-orchestrator` directory or use full path.

### API key errors
**If using Claude:**
```bash
export ANTHROPIC_API_KEY=sk-...
# Or set in .orchestrator/.env
```

**If using local Ollama (no key needed):**
```bash
cp ai-orchestrator/config/agents-ollama.yaml .orchestrator/agents.yaml
ollama serve
```

### Ollama connection errors
```bash
# Ensure Ollama is running
ollama serve

# Check it's accessible
curl http://localhost:11434/api/tags

# If remote, set custom URL
export OLLAMA_BASE_URL=http://your-host:11434
```

### GUI timeout
Increase timeout in `gui/app.py` line ~180:
```python
timeout=600  # 10 minutes instead of 5
```

## Performance Notes

- Default token budget: 3000 per prompt
- Phase execution: Up to 10 phases max
- Confidence threshold: 0.85 (for termination)
- Parallel execution: Enabled by default (5 workers)

## Security

- Governance layer checks context refs and intent before execution
- Protected paths: `/sys/`, `/etc/`, `C:\Windows\System32\`
- Destructive keywords: `delete all`, `drop database`, `rm -rf`
- All executions logged to `.orchestrator/runs/`

## License

Part of Symphony-IR project

## Support

- Check logs in `.orchestrator/logs/`
- View ledgers in `.orchestrator/runs/`
- Review agent config in `.orchestrator/agents.yaml`
- Run with `--verbose` flag for debugging

## Status

- ✅ Core Orchestrator: Production ready
- ✅ Streamlit GUI: Production ready (v1.0)
- ✅ Symphony Flow: Production ready (7 templates)

---

**Ready to get started?**

```bash
# Initialize orchestrator
python ai-orchestrator/orchestrator.py init --project .

# Try the CLI
python ai-orchestrator/orchestrator.py run "your task here"

# Or launch the GUI
cd gui && streamlit run app.py
```
