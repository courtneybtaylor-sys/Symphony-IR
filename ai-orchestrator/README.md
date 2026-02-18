# Symphony-IR

**A compiler-grade runtime for multi-model AI orchestration.**

Deterministic state machine. Prompt intermediate representation. Governance before tokens.

![Status: Alpha](https://img.shields.io/badge/status-alpha-orange)
![Python >= 3.9](https://img.shields.io/badge/python-%3E%3D%203.9-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

---

## What is Symphony-IR?

Symphony-IR is an infrastructure-layer runtime that coordinates multiple AI models through a deterministic state machine and a prompt compilation pipeline based on Intermediate Representation (IR). It treats prompts the way compilers treat source code: parsing intent into a structured IR, running optimization and governance passes over that IR, then compiling model-specific output. The result is a **55.7% measured token reduction**, full auditability, and governance enforcement that happens *before* a single token is spent. Symphony-IR is model-agnostic, shipping with support for Claude, GPT, Ollama, and mock providers out of the box.

---

## Architecture

```
USER INPUT (task + context)
    |
    v
+-------------------------------------------+
|        ORCHESTRATOR (State Machine)        |
|  INIT -> PLAN -> EXECUTE -> SYNTH -> DONE  |
+-------------------------------------------+
    |
    v
CONDUCTOR AGENT (execution plan)
    |
    v
+-------------------------------------------+
|          PROMPT IR CONSTRUCTION            |
|  role | intent | context refs | budget     |
+-------------------------------------------+
    |
    v
+-------------------------------------------+
|            IR PIPELINE                     |
|  [GovernanceCheck] -> [PluginTransforms]   |
|   - Policy enforcement (pre-token)         |
|   - ContextDigestPlugin (compression)      |
|   - BudgetOptimizerPlugin (phase-aware)    |
+-------------------------------------------+
    |
    v
+-------------------------------------------+
|          PROMPT COMPILER                   |
|  Template -> Prune -> Adapt -> Budget      |
+-------------------------------------------+
    |
    v
+-------------------------------------------+
|         5 SPECIALIST AGENTS                |
|  Architect | Researcher | Implementer      |
|  Reviewer  | Integrator                     |
+-------------------------------------------+
    |
    v
+-------------------------------------------+
|  SCHEMA VALIDATOR (enforce + auto-repair)  |
+-------------------------------------------+
    |
    v
+-------------------------------------------+
|  GOVERNANCE LAYER (constitutional checks)  |
+-------------------------------------------+
    |
    v
+-------------------------------------------+
|  A/B EFFICIENCY STATS (token/cost/latency) |
+-------------------------------------------+
    |
    v
RUN LEDGER (complete audit trail)
```

---

## Quick Start

### Install

```bash
pip install symphony-ir
```

### Run Your First Orchestration

```python
from symphony_ir import Orchestrator, Config

config = Config.from_yaml("agents.yaml")
orch = Orchestrator(config)

result = orch.run("Design a REST API for user management")

print(f"Status: {result.status}")
print(f"Phases: {result.phases_executed}")
print(f"Tokens used: {result.token_usage.total}")
print(f"Token reduction: {result.efficiency.token_reduction_pct}%")
print(result.output)
```

### Run Without API Keys (Mock Mode)

```bash
symphony run "Design a REST API" --provider mock
```

This exercises the full pipeline -- state machine, IR, compilation, validation -- with no external calls.

---

## CLI Usage

```bash
# Initialize a project
symphony init

# Run an orchestration
symphony run "Design a REST API for user management"

# Run with options
symphony run "Refactor auth module" --project ./myapp --dry-run
symphony run "Build a CLI tool" --provider ollama --verbose

# Check project status
symphony status

# View run history
symphony history
symphony history --detailed --limit 10

# A/B efficiency report
symphony efficiency
symphony efficiency --json
symphony efficiency --export report.json
```

| Command | Description |
|---------|-------------|
| `symphony init` | Initialize `.symphony/` project directory with config templates |
| `symphony run <task>` | Execute a full orchestration run |
| `symphony status` | Show current project and agent configuration |
| `symphony history` | List past runs with summary statistics |
| `symphony efficiency` | Generate A/B efficiency comparison report |

### Run Options

| Flag | Effect |
|------|--------|
| `--project <path>` | Set project root (default: current directory) |
| `--file <path>` | Include a specific file in context |
| `--provider <name>` | Override model provider for all agents |
| `--dry-run` | Show execution plan without running agents |
| `--no-compile` | Disable prompt compiler, schema validator, and IR pipeline |
| `--no-ir` | Disable IR pipeline only (use direct compilation) |
| `-v, --verbose` | Show decision chain, compiler stats, and IR transformations |

---

## Key Features

| Feature | Description |
|---------|-------------|
| Deterministic State Machine | Rules-based phase transitions with hard limits. The LLM never decides when to stop. |
| Prompt IR | Structured intermediate representation -- the AST for prompts. Inspectable, transformable, auditable. |
| IR Governance | Policy enforcement *before* tokens are spent. Reject or modify runs at the IR level. |
| Prompt Compiler | Template selection, context pruning (up to 40% reduction), model-specific adaptation. |
| Schema Validator | Output format enforcement with auto-repair for common issues (missing braces, trailing commas). |
| 5 Specialist Agents | Architect, Researcher, Implementer, Reviewer, Integrator -- each with a constrained role. |
| Model-Agnostic | Swap between Claude, GPT, Ollama, or Mock via config. No code changes. |
| A/B Efficiency | Built-in measurement of token, cost, and latency differences between compiled and raw runs. |
| Plugin System | Extensible IR transformation pipeline. Write custom plugins for domain-specific optimization. |
| Full Audit Trail | Every decision, every phase, every token count recorded in the run ledger. |

---

## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Orchestrator | `core/orchestrator.py` | Deterministic state machine engine |
| Prompt IR | `core/prompt_ir.py` | Intermediate representation construction and pipeline |
| Prompt Compiler | `core/prompt_compiler.py` | Token-optimized prompt compilation with model adaptation |
| Schema Validator | `core/schema_validator.py` | Output format enforcement with auto-repair |
| Efficiency Stats | `core/efficiency_stats.py` | A/B measurement and ROI calculation |
| Governance | `core/governance.py` | Constitutional policy enforcement |
| Model Layer | `models/client.py` | Unified abstraction across providers |
| Agent System | `agents/agent.py` | Agent execution, registry, and lifecycle |
| Context | `context/providers.py` | Project context collection and injection |
| CLI | `cli.py` | Command-line interface (`symphony` command) |
| Config | `config/agents.yaml` | Agent and system configuration |
| Templates | `config/prompt_templates.yaml` | Prompt compilation templates |

---

## IR Pipeline

The Prompt IR (Intermediate Representation) is the core abstraction that separates *intent* from *execution*. It serves the same role for prompts that an AST serves for source code: a structured, inspectable, transformable representation that sits between what you want and what gets sent to the model.

```
Conductor Intent --> PromptIR --> IR Pipeline --> Compiled Prompt --> Model
```

1. **IR Construction** -- `PromptIRBuilder` creates a structured node with role, intent, context references, constraints, and token budget.
2. **IR Governance** -- `IRGovernanceChecker` enforces policies at the IR level. Violations are caught before any tokens are spent, saving 20-30% on rejected or modified runs.
3. **Plugin Transforms** -- `ContextDigestPlugin` compresses large context blocks. `BudgetOptimizerPlugin` adjusts token budgets based on phase and priority. Custom plugins implement the `IRPlugin` interface.
4. **Compilation** -- `compile_from_ir()` resolves context references and feeds the optimized IR into the prompt compiler.

Disable with `--no-ir` to fall back to direct compilation.

---

## Prompt Compilation Pipeline

The Prompt Compiler transforms high-level instructions into model-optimized prompts through five stages:

1. **Template Selection** -- Match agent role to a YAML-defined prompt template.
2. **Context Pruning** -- Remove irrelevant context, reducing token count by up to 40%.
3. **Model Adaptation** -- Claude receives XML wrapping, GPT receives JSON schemas, Ollama receives instruction tags.
4. **Token Budget Enforcement** -- Hard limits prevent runaway prompt sizes.
5. **Schema Injection** -- Append output format requirements for structured, parseable responses.

Disable with `--no-compile` to send raw prompts.

---

## Configuration

### agents.yaml

```yaml
agents:
  - name: architect
    role: System Architect
    model_provider: anthropic
    model_config:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    temperature: 0.7
    max_tokens: 2000
    system_prompt: |
      You are the System Architect agent. You analyze requirements,
      define system boundaries, and produce architecture decisions
      with explicit trade-off reasoning.
    constraints:
      focus: "Architecture and system design"

  - name: researcher
    role: Researcher
    model_provider: openai
    model_config:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
    temperature: 0.5
    max_tokens: 1500
    system_prompt: |
      You are the Researcher agent. You investigate prior art,
      documentation, and technical references relevant to the task.
    constraints:
      focus: "Research and documentation"

  - name: implementer
    role: Implementer
    model_provider: ollama
    model_config:
      model: llama3
      endpoint: http://localhost:11434
    temperature: 0.3
    max_tokens: 3000
    system_prompt: |
      You are the Implementer agent. You produce concrete code,
      configurations, and implementation artifacts.
    constraints:
      focus: "Code and implementation"

system:
  max_phases: 10
  confidence_threshold: 0.85
  enable_parallel_execution: true
```

### Environment Variables

Create `.symphony/.env` in your project root:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

---

## Model Providers

| Provider | Config Value | Requirements | Notes |
|----------|-------------|--------------|-------|
| Anthropic (Claude) | `anthropic` | `ANTHROPIC_API_KEY` | XML-adapted prompts, tool use support |
| OpenAI (GPT) | `openai` | `OPENAI_API_KEY` | JSON schema adaptation |
| Ollama (local) | `ollama` | Ollama running on `localhost:11434` | No cloud dependency, instruction-tag format |
| Mock (testing) | `mock` | Nothing | Full pipeline exercised with synthetic responses |

Switch providers per-agent in `agents.yaml` or globally with `--provider` on the CLI. No code changes required.

---

## A/B Efficiency Measurement

Symphony-IR includes a built-in `EfficiencyCalculator` that compares compiled runs against raw (uncompiled) baselines. Every run records token counts, latency, and cost, enabling precise measurement of the IR pipeline's impact.

**Measured results: 55.7% token reduction via IR pipeline.**

Metrics tracked per run:

| Metric | Description |
|--------|-------------|
| Token Reduction | Input and output token savings vs. raw prompts |
| Latency Reduction | Wall-clock time improvement from smaller prompts |
| Retry/Repair Reduction | Fewer validation failures due to schema injection |
| Cost Reduction | USD savings calculated from model-specific pricing |
| Annual Projection | Extrapolated savings at your current run volume |

```bash
# Generate a text report
symphony efficiency

# Export as JSON for dashboards
symphony efficiency --json

# Save to file
symphony efficiency --export report.json
```

---

## FAQ

**Q: Does Symphony-IR require API keys to evaluate?**
A: No. Run `symphony run "your task" --provider mock` to exercise the full pipeline -- state machine, IR, compilation, validation, all five agents -- with no external API calls.

**Q: How is this different from LangChain, CrewAI, or AutoGen?**
A: Symphony-IR uses a deterministic state machine with hard termination limits. The LLM never decides when to stop -- rules do. Prompts pass through a compiler-grade IR pipeline with governance enforcement before tokens are spent. There is no chain-of-thought loop, no unbounded agent recursion, and a complete audit trail for every decision.

**Q: Can I run entirely on local models?**
A: Yes. Set `model_provider: ollama` for all agents in `agents.yaml` and run Ollama locally. Symphony-IR has zero cloud dependency in this configuration.

**Q: Can I add custom agents beyond the five specialists?**
A: Yes. Add a new entry to `agents.yaml` with a name, role, system prompt, and model provider. The agent registry loads it automatically. Custom agents participate in the same state machine and receive compiled prompts.

**Q: Can I write custom IR plugins?**
A: Yes. Implement the `IRPlugin` interface with a `transform(ir_node) -> ir_node` method and register it with the IR pipeline. Plugins execute in order between governance checking and prompt compilation.

---

## Roadmap

### Phase 1: Foundation (Current)
- Deterministic state machine orchestration
- 5 specialist agents with conductor coordination
- Prompt IR pipeline with governance and plugin system
- Prompt compiler with model-specific adaptation
- Schema validator with auto-repair
- A/B efficiency measurement
- CLI interface and mock provider
- 55.7% token reduction achieved

### Phase 2: Intelligence
- Agent memory and context persistence across runs
- Dynamic phase planning based on task complexity
- Tool use integration (file I/O, code execution, HTTP)
- Streaming output for long-running orchestrations

### Phase 3: Platform
- Web dashboard for run inspection and comparison
- Team collaboration with shared agent configurations
- Run analytics and trend visualization
- Custom agent and plugin marketplace

### Phase 4: Sovereignty
- Full constitutional governance framework
- On-premise and air-gapped deployment
- Federated agent networks across organizations
- Compliance reporting and audit export

---

## Contributing

Contributions are welcome. Symphony-IR is in alpha and moving fast.

```bash
# Clone the repository
git clone https://github.com/kheper-company/symphony-ir.git
cd symphony-ir

# Install in development mode
pip install -e ".[dev]"

# Run the test suite
pytest

# Run with mock provider to validate changes
symphony run "Test task" --provider mock --verbose
```

Please open an issue before starting work on a large change. All contributions must pass the existing test suite and include tests for new functionality.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

Built by [Kheper Company](https://github.com/kheper-company).
