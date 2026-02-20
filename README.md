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

### Experimental: Symphony Flow v0
- **Guided workflows**: Bounded decision trees (2-4 options per step)
- **Template-based**: Pre-built workflows for common tasks
- **Flow tracking**: Persistent state across decisions
- **Direct PromptIR mapping**: Each node maps to orchestrator execution

## Installation

### Prerequisites
- Python 3.9+
- API key for Claude (Anthropic)

### Quick Start

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

### Via Symphony Flow (Experimental)

```bash
# Enable experimental feature
export SYMPHONY_EXPERIMENTAL_FLOW=1

# Run guided workflow
python orchestrator.py flow --template code_review --var component=auth.py
python orchestrator.py flow --template refactor_code --var component=main.py
python orchestrator.py flow --template new_feature --var feature="API endpoint"
```

**Available Templates:**
- `code_review`: Guided code review with focused paths (bugs, style, performance)
- `refactor_code`: Structured refactoring guide (design improvements, quick fixes, dependency review)
- `new_feature`: Feature implementation planning (architecture, checklist, risk analysis)

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

## Development

### Adding a New Flow Template

1. Create `flow/templates/my_template.yaml`
2. Define template_id, nodes, and options
3. Enable feature flag: `export SYMPHONY_EXPERIMENTAL_FLOW=1`
4. Run: `python orchestrator.py flow --template my_template --var key=value`

### Running Tests

```bash
# Test CLI
python orchestrator.py status
python orchestrator.py history

# Test GUI
cd gui
streamlit run app.py

# Test Flow (with feature flag)
export SYMPHONY_EXPERIMENTAL_FLOW=1
python orchestrator.py flow --template code_review --var component=test.py
```

## Troubleshooting

### "orchestrator.py not found"
Ensure you're in the `ai-orchestrator` directory or use full path.

### API key errors
```bash
export ANTHROPIC_API_KEY=sk-...
# Or set in .orchestrator/.env
```

### Flow command not found
Enable experimental feature:
```bash
export SYMPHONY_EXPERIMENTAL_FLOW=1
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
- ✅ Streamlit GUI: Beta (v0.1)
- ⚠️ Symphony Flow: Experimental (feature-flagged)

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
