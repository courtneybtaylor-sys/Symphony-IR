# AI Orchestrator — Quick Start Guide

Get running in 5 minutes.

## 1. Test Without API Keys

```bash
cd ai-orchestrator
pip install pyyaml
python example.py
```

This runs the full orchestration architecture with mock models. You'll see:
- State machine execution
- Multi-agent coordination (5 specialists)
- Prompt compilation (token optimization + model adaptation)
- Schema validation (output format enforcement)
- Governance checks
- Complete audit trail

## 2. Initialize Your Project

```bash
python orchestrator.py init
```

This creates `.orchestrator/` with:
```
.orchestrator/
├── agents.yaml      # Agent configurations
├── .env             # API key placeholders
├── .env.template    # Reference template
├── runs/            # Saved run ledgers
└── logs/            # Log files
```

## 3. Add API Keys

Edit `.orchestrator/.env`:

```bash
# Pick one (or multiple):
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

For **local-only** operation with Ollama:
```bash
# Install Ollama: https://ollama.ai
ollama pull llama3.2

# Edit .orchestrator/agents.yaml — change model_provider to "ollama"
```

## 4. Run Your First Task

```bash
python orchestrator.py run "Design a REST API for user authentication"
```

With verbose output:
```bash
python orchestrator.py run "Refactor the payment module" -v
```

Dry run (see plan without executing):
```bash
python orchestrator.py run "Add caching layer" --dry-run
```

Without prompt compilation (raw prompts only):
```bash
python orchestrator.py run "Simple task" --no-compile
```

## 5. Common Commands

```bash
# Check what context is available
python orchestrator.py status

# View recent runs
python orchestrator.py history

# View detailed run history
python orchestrator.py history --detailed --limit 5

# Include a specific file in context
python orchestrator.py run "Review this code" --file src/main.py

# Point to a different project
python orchestrator.py run "Analyze architecture" --project /path/to/project
```

## Troubleshooting

**"No agents.yaml found"**
Run `python orchestrator.py init` first.

**"openai package required"**
Install the model provider you need:
```bash
pip install openai        # For GPT models
pip install anthropic     # For Claude models
pip install requests      # For Ollama
```

**"Connection refused" (Ollama)**
Make sure Ollama is running: `ollama serve`

**Mock mode keeps activating**
Check that your API keys are set in `.orchestrator/.env` and the model_provider in agents.yaml matches your keys.

**Low confidence scores**
Adjust `confidence_threshold` in the `system:` section of agents.yaml (default: 0.85).
