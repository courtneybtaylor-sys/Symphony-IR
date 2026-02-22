# CLI (Command-Line Interface) Guide

The Symphony-IR CLI provides a powerful command-line interface for orchestrating multi-agent workflows. This guide covers all available commands and usage patterns.

## Quick Start

```bash
# Initialize Symphony-IR
python orchestrator.py init

# Run a simple task
python orchestrator.py run "Write a Python function that checks if a number is prime"

# See available workflows
python orchestrator.py flow-list

# Run a specific workflow
python orchestrator.py flow security_audit --variables=target=api-server

# View execution history
python orchestrator.py history

# Show system status
python orchestrator.py status
```

## Available Commands

### `init`
Initialize Symphony-IR with configuration and setup wizard.

```bash
python orchestrator.py init
```

**What it does:**
1. Creates `.orchestrator/` directory
2. Launches interactive setup wizard
3. Prompts for provider selection (Claude/Ollama/Both)
4. Validates API keys or Ollama connection
5. Saves configuration to `~/.symphonyir/config.json`

### `run`
Execute a task through the orchestrator.

```bash
python orchestrator.py run "Your task description here"
```

**Options:**
- `--provider` — Force provider (claude, ollama, openai)
- `--verbose` — Show detailed output
- `--output` — Save results to file

**Example:**
```bash
python orchestrator.py run "Analyze this code for bugs" --provider claude --verbose
```

### `flow`
Execute a symphony flow (workflow template).

```bash
python orchestrator.py flow TEMPLATE_NAME [--variables KEY=VALUE ...]
```

**Available Templates:**
- `code_review` — Review code quality
- `security_audit` — Audit for security issues
- `cloud_architecture` — Design cloud solutions
- `data_pipeline` — Plan data flows
- `ml_model` — Design ML solutions
- `incident_response` — Handle incidents
- `compliance_audit` — Check compliance
- `performance_optimization` — Optimize performance

**Example:**
```bash
python orchestrator.py flow code_review --variables component=auth.py provider=claude
```

### `flow-list`
List available workflow templates.

```bash
python orchestrator.py flow-list
python orchestrator.py flow-list --domain security
python orchestrator.py flow-list --search "audit"
```

### `history`
View past orchestration runs.

```bash
python orchestrator.py history
python orchestrator.py history --limit 10
python orchestrator.py history --template code_review
```

### `status`
Check system status and provider availability.

```bash
python orchestrator.py status
```

Shows:
- Python version
- Available providers
- Provider connectivity (Claude API, Ollama, OpenAI)
- Configuration status

### `help`
Show help for any command.

```bash
python orchestrator.py --help
python orchestrator.py run --help
python orchestrator.py flow --help
```

## Configuration

Symphony-IR stores configuration in `~/.symphonyir/config.json`:

```json
{
  "providers": {
    "claude": {
      "api_key": "sk-ant-...",
      "model": "claude-opus"
    },
    "ollama": {
      "url": "http://localhost:11434",
      "model": "mistral"
    }
  },
  "default_provider": "claude"
}
```

**To change configuration:**
1. Run `python orchestrator.py init` to re-run setup wizard
2. Or edit `~/.symphonyir/config.json` directly
3. Or set environment variables:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   export OLLAMA_URL="http://localhost:11434"
   ```

## Advanced Usage

### Scripting

Use Symphony-IR in bash scripts:

```bash
#!/bin/bash

# Run a task and capture output
result=$(python orchestrator.py run "Analyze the README" --output json)

# Extract JSON results
echo $result | jq '.orchestration.result'
```

### CI/CD Integration

Use in GitHub Actions or CI/CD pipelines:

```yaml
# .github/workflows/review.yml
- name: Code Review
  run: |
    python orchestrator.py flow code_review \
      --variables component=src/main.py \
      --output results.json
```

### Custom Workflows

Create custom workflow files:

```yaml
# my_workflow.yaml
name: "Custom Analysis"
agents:
  architect:
    prompt: "You are an architect..."
  reviewer:
    prompt: "You are a reviewer..."
workflow:
  - step: 1
    agent: architect
    task: "Analyze the problem..."
```

Run custom workflow:

```bash
python orchestrator.py flow custom_analysis --template my_workflow.yaml
```

## Troubleshooting

### Issue: `Command not found: orchestrator.py`

**Solution**: Run from the project directory:
```bash
python orchestrator.py  # if in ai-orchestrator/ directory
python ai-orchestrator/orchestrator.py  # if in project root
```

### Issue: `API key not found`

**Solution**: Run setup:
```bash
python orchestrator.py init
# Or set environment variable:
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Issue: `Ollama connection refused`

**Solution**: Ensure Ollama is running:
```bash
ollama serve
# In another terminal:
python orchestrator.py status
```

## See Also

- [Python API](PYTHON_API.md) — Use as a library
- [GUI Guide](GUI.md) — Desktop application
- [Architecture](../ARCHITECTURE.md) — How it works
- [Contributing](../../CONTRIBUTING.md) — Help develop

## References

For complete command reference, see:
- `ai-orchestrator/orchestrator.py` — Command implementation
- `ai-orchestrator/README.md` — Technical details
