# Symphony-IR — Quick Start Guide

Get running in 5 minutes.

## 1. Install

```bash
pip install symphony-ir
```

Or from source:

```bash
cd ai-orchestrator
pip install -e .
```

## 2. Test Without API Keys

```bash
python example.py
```

This runs the full compiler-grade orchestration architecture with mock models. You'll see:
- State machine execution
- Multi-agent coordination (5 specialists)
- Prompt IR pipeline (governance + plugin transforms)
- Prompt compilation (token optimization + model adaptation)
- Schema validation (output format enforcement)
- A/B efficiency statistics
- Complete audit trail

## 3. Initialize Your Project

```bash
symphony init
```

This creates `.symphony/` with:
```
.symphony/
├── agents.yaml      # Agent configurations
├── .env             # API key placeholders
├── .env.template    # Reference template
├── runs/            # Saved run ledgers
└── logs/            # Log files
```

## 4. Add API Keys

Edit `.symphony/.env`:

```bash
# Pick one (or multiple):
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

For **local-only** operation with Ollama:
```bash
# Install Ollama: https://ollama.ai
ollama pull llama3.2

# Edit .symphony/agents.yaml — change model_provider to "ollama"
```

## 5. Run Your First Task

```bash
symphony run "Design a REST API for user authentication"
```

With verbose output:
```bash
symphony run "Refactor the payment module" -v
```

Dry run (see plan without executing):
```bash
symphony run "Add caching layer" --dry-run
```

Without IR pipeline (direct compilation only):
```bash
symphony run "Simple task" --no-ir
```

Without any compilation (raw prompts):
```bash
symphony run "Simple task" --no-compile
```

## 6. Common Commands

```bash
# Check what context is available
symphony status

# View recent runs
symphony history

# View detailed run history
symphony history --detailed --limit 5

# Include a specific file in context
symphony run "Review this code" --file src/main.py

# Point to a different project
symphony run "Analyze architecture" --project /path/to/project

# Generate A/B efficiency report
symphony efficiency

# Export efficiency report as JSON
symphony efficiency --json --export report.json
```

## 7. Try the Workflow Examples

```bash
# Code refactoring workflow
python examples/workflow_code_refactor.py

# Multi-file analysis with context compression
python examples/workflow_multifile_analysis.py

# Research and synthesis pipeline
python examples/workflow_research_synthesis.py
```

## Troubleshooting

**"No agents.yaml found"**
Run `symphony init` first.

**"openai package required"**
Install the model provider you need:
```bash
pip install symphony-ir[anthropic]   # For Claude models
pip install symphony-ir[openai]      # For GPT models
pip install symphony-ir[ollama]      # For Ollama
pip install symphony-ir[all]         # Everything
```

**"Connection refused" (Ollama)**
Make sure Ollama is running: `ollama serve`

**Mock mode keeps activating**
Check that your API keys are set in `.symphony/.env` and the model_provider in agents.yaml matches your keys.

**Low confidence scores**
Adjust `confidence_threshold` in the `system:` section of agents.yaml (default: 0.85).
