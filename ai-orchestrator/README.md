# AI Orchestrator

A production-grade, deterministic multi-agent AI coordination engine.

## Philosophy

AI Orchestrator is **infrastructure**, not a chatbot wrapper. It coordinates multiple AI models through a structured state machine to accomplish complex tasks with:

- **Deterministic execution** — State machine driven, not vibes
- **Model-agnostic design** — Swap models via config, not code
- **Local-first operation** — No cloud dependency required (Ollama support)
- **Full inspectability** — Complete audit trail of every decision
- **Constitutional governance** — Ma'aT enforcement layer
- **Production quality** — Built to ship as a developer tool

## Core Concept: Conductor + Compilation + Specialists

```
USER INPUT (task + context)
    ↓
ORCHESTRATOR (deterministic state machine)
    ↓
CONDUCTOR AGENT (creates execution plan)
    ↓
PROMPT COMPILER (template selection, context pruning, model adaptation)
    ↓
5 SPECIALIST AGENTS (parallel execution with optimized prompts)
    ├─ Architect:    System design, constraints
    ├─ Researcher:   Documentation, prior art
    ├─ Implementer:  Concrete code/content
    ├─ Reviewer:     Critique, edge cases
    └─ Integrator:   Synthesize outputs
    ↓
SCHEMA VALIDATOR (output format enforcement + auto-repair)
    ↓
GOVERNANCE LAYER (Ma'aT constitutional checks)
    ↓
RUN LEDGER (complete audit trail)
```

The orchestrator decides when to stop via **deterministic rules** (phase limits, confidence thresholds, risk flags) — never the LLM.

## Installation

```bash
# Clone and install
cd ai-orchestrator
pip install -e .

# Or install with specific model support
pip install -e ".[anthropic]"    # Claude support
pip install -e ".[openai]"      # GPT support
pip install -e ".[ollama]"      # Local model support
pip install -e ".[all]"         # Everything
```

### Requirements

- Python >= 3.9
- PyYAML >= 6.0
- python-dotenv >= 1.0.0

Optional (install as needed):
- `openai` — For OpenAI/GPT models
- `anthropic` — For Anthropic/Claude models
- `requests` — For Ollama local models

## Usage

### Quick Test (No API Keys)

```bash
python example.py
```

This runs the full orchestration architecture with mock models.

### Initialize a Project

```bash
python orchestrator.py init
```

Creates `.orchestrator/` directory with:
- `agents.yaml` — Agent configuration
- `.env` — API key placeholders
- `runs/` — Run history storage
- `logs/` — Log files

### Configure API Keys

Edit `.orchestrator/.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### Run an Orchestration

```bash
python orchestrator.py run "Design a REST API for user management"
```

Options:
- `--project <path>` — Project root (default: current dir)
- `--file <path>` — Include a specific file in context
- `--dry-run` — Show plan without executing
- `--no-compile` — Disable prompt compiler and schema validator
- `-v, --verbose` — Detailed output with decision chain and compiler/validator stats

### Check Status

```bash
python orchestrator.py status
```

### View History

```bash
python orchestrator.py history
python orchestrator.py history --detailed --limit 5
```

## Architecture Overview

### State Machine

```
INIT → PLAN → EXECUTE_PHASE → SYNTHESIZE → VALIDATE → TERMINATE
         ↑                                      ↓
         └──────────────────────────────────────┘
                    (loop with hard limits)
```

### Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Orchestrator | `core/orchestrator.py` | State machine engine |
| Prompt Compiler | `core/prompt_compiler.py` | Token-optimized prompt compilation |
| Schema Validator | `core/schema_validator.py` | Output format enforcement + auto-repair |
| Governance | `core/governance.py` | Ma'aT constitutional checks |
| Model Layer | `models/client.py` | Unified model abstraction |
| Agent System | `agents/agent.py` | Agent execution + registry |
| Context | `context/providers.py` | Project context collection |
| CLI | `orchestrator.py` | Command-line interface |
| Config | `config/agents.yaml` | Agent configurations |
| Templates | `config/prompt_templates.yaml` | Prompt compilation templates |

### Prompt Compilation Pipeline

The Prompt Compiler transforms high-level Conductor instructions into model-optimized prompts:

1. **Template Selection** — Match agent role to YAML-defined prompt template
2. **Context Pruning** — Remove irrelevant context (up to 40% token reduction)
3. **Model Adaptation** — Claude gets XML wrapping, GPT gets JSON schemas, Ollama gets instruction tags
4. **Token Budget Enforcement** — Hard limits prevent runaway prompt sizes
5. **Schema Injection** — Append output format requirements for structured responses

Disable with `--no-compile` flag.

### Schema Validation

The Schema Validator sits between agent output and synthesis:

- Validates outputs against declared JSON/Markdown/XML schemas
- Auto-repairs common issues (missing braces, trailing commas, single quotes)
- Logs all validation decisions for audit trail
- Reduces retry loops by 50%+

### Termination Logic

The orchestrator uses deterministic termination — never LLM judgment:

1. **Hard phase limit** — `max_phases` config (default: 10)
2. **Confidence threshold** — Average agent confidence must meet threshold (default: 0.85)
3. **Critical flags** — Any `CRITICAL_*` risk flag forces re-evaluation

## Configuration

### agents.yaml

```yaml
agents:
  - name: architect
    role: System Architect
    model_provider: anthropic    # or: openai, ollama, mock
    model_config:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    temperature: 0.7
    max_tokens: 2000
    system_prompt: |
      You are the System Architect agent...
    constraints:
      focus: "Architecture and design"

system:
  max_phases: 10
  confidence_threshold: 0.85
  enable_parallel_execution: true
```

### Swap Models

Change `model_provider` in agents.yaml to switch models without changing code:

| Provider | Value | Requires |
|----------|-------|----------|
| Anthropic (Claude) | `anthropic` | `ANTHROPIC_API_KEY` |
| OpenAI (GPT) | `openai` | `OPENAI_API_KEY` |
| Ollama (local) | `ollama` | Ollama running locally |
| Mock (testing) | `mock` | Nothing |

## Roadmap

### Phase 1: Foundation + Compilation (Current)
- State machine orchestration
- 5 specialist agents + conductor
- Prompt compiler with model adaptation
- Schema validator with auto-repair
- Mock and real model support
- CLI interface

### Phase 2: Intelligence
- Agent memory across runs
- Dynamic phase planning
- Tool use (file write, code execution)
- Streaming output

### Phase 3: Platform
- Web UI dashboard
- Run comparison and analytics
- Team collaboration
- Custom agent marketplace

### Phase 4: Sovereignty
- Full Ma'aT governance integration
- On-premise deployment
- Federated agent networks
- Compliance and audit reporting

## FAQ

**Q: Does this require API keys?**
A: No. Run `python example.py` to test the full architecture with mock models. Add API keys when ready for real model execution.

**Q: Can I use local models only?**
A: Yes. Set `model_provider: ollama` in agents.yaml and run Ollama locally. No cloud dependency needed.

**Q: How is this different from LangChain/CrewAI?**
A: AI Orchestrator uses a deterministic state machine with hard termination limits, not chain-of-thought. The LLM never decides when to stop — rules do. Full audit trail of every decision.

**Q: Can I add custom agents?**
A: Yes. Add a new entry to agents.yaml with a name, role, system prompt, and model provider. The agent will be automatically loaded.

**Q: Can I add custom model providers?**
A: Yes. Subclass `ModelClient` and register with `ModelFactory.register("name", YourClass)`.
