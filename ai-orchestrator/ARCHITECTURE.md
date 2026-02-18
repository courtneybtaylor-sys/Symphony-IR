# Symphony-IR — Technical Architecture

## System Overview

```
+------------------------------------------------------------+
|                      CLI Interface                          |
|                    (symphony / orchestrator.py)              |
+------------------------------------------------------------+
|                                                             |
|  +--------------+  +-------------+  +------------------+   |
|  |  Orchestrator |  |   Agent     |  |    Context        |  |
|  |  State Machine|  |   Registry  |  |    Manager        |  |
|  |  (core/)      |  |  (agents/)  |  |   (context/)      |  |
|  +------+-------+  +------+------+  +--------+---------+   |
|         |                 |                   |             |
|  +------+-------+  +------+------+  +--------+---------+   |
|  |  Prompt IR    |  |  Schema     |  |   Providers       |  |
|  |  Pipeline     |  |  Validator  |  |  FS / Git / File  |  |
|  +------+-------+  +------+------+  +------------------+   |
|         |                 |                                 |
|  +------+-------+  +------+------+  +------------------+   |
|  |  Prompt       |  |   Model     |  |  Efficiency      |  |
|  |  Compiler     |  |   Factory   |  |  Stats (A/B)     |  |
|  +------+-------+  +------+------+  +------------------+   |
|         |                 |                                 |
|  +------+-------+                                           |
|  |  Governance   |                                           |
|  | (Ma'aT + IR) |                                           |
|  +--------------+                                           |
|                           |                                 |
|  +-----------------------------------------------------+   |
|  |              Model Abstraction Layer                  |  |
|  |   OpenAI  |  Anthropic  |  Ollama  |  Ma'aT  | Mock  |  |
|  +-----------------------------------------------------+   |
+------------------------------------------------------------+
```

## IR Schema Version

Symphony-IR uses a **frozen IR schema** (currently v1.0) with stability guarantees:

- All PromptIR fields in v1.0 remain present in future 1.x releases
- New optional fields may be added (with defaults) in minor releases
- Serialization format (`to_dict`/`from_dict`) is stable and backwards-compatible
- Plugin `transform()` signature is stable: `(PromptIR) -> PromptIR`
- Pipeline `process()` signature is stable: `(PromptIR) -> (PromptIR, bool, List[str])`

See `IR_SPEC.md` for the full schema specification.

## Core Components

### 1. State Machine Engine (`core/orchestrator.py`)

The orchestrator implements a finite state machine with these states:

| State | Description | Transitions To |
|-------|-------------|----------------|
| `INIT` | Run initialization | `PLAN` |
| `PLAN` | Conductor creates phases | `EXECUTE_PHASE` |
| `EXECUTE_PHASE` | Agents execute in parallel | `SYNTHESIZE` |
| `SYNTHESIZE` | Combine agent outputs | `VALIDATE` |
| `VALIDATE` | Deterministic checks | `EXECUTE_PHASE` or `TERMINATE` |
| `TERMINATE` | Run complete | (end) |
| `ERROR` | Exception handling | (end) |

**Key data structures:**

- `Phase` — Name, agent list, brief, termination condition, confidence threshold
- `AgentResponse` — Agent name, role, output, confidence (0-1), risk flags, metadata
- `RunLedger` — Complete audit trail: run_id, task, phases, responses, decisions, final output
- `Decision` — Timestamped record of every orchestrator decision

**Termination logic (deterministic):**

```python
# Hard limit
if phase_count >= max_phases:
    force_terminate()

# Confidence + risk
avg_confidence = sum(r.confidence) / len(responses)
critical_flags = [f for f in flags if f.startswith("CRITICAL")]
should_continue = avg_confidence < threshold or len(critical_flags) > 0
```

### 2. Model Abstraction Layer (`models/client.py`)

All model interaction goes through a unified interface:

```python
class ModelClient(ABC):
    def call(messages, temperature, max_tokens, tools) -> ModelResponse
    def get_provider() -> ModelProvider
    def get_model_name() -> str
```

**Adapters:**

| Adapter | Backend | Notes |
|---------|---------|-------|
| `OpenAIClient` | OpenAI API | GPT-4o, GPT-4, etc. |
| `AnthropicClient` | Anthropic API | Claude Sonnet, Opus, etc. |
| `OllamaClient` | HTTP to localhost:11434 | Llama, Mistral, etc. |
| `MaaTClient` | Governance engine | Placeholder for future integration |
| `MockModelClient` | In-memory | Role-aware mock responses for testing |

**ModelFactory** creates clients from config:

```python
client = ModelFactory.create("anthropic", api_key="...", model="claude-sonnet-4-20250514")
```

Agents never know which model they use. Swap via config alone.

### 3. Agent System (`agents/agent.py`)

**AgentConfig** dataclass holds:
- name, role, system_prompt
- model_provider, model_config
- temperature, max_tokens, constraints

**Agent.execute()** flow:
1. Build messages (system prompt + constraints + context + brief)
2. Call model via ModelClient
3. Parse structured response
4. Return: output, confidence, risk_flags, reasoning

**Structured output format (required):**

```
OUTPUT: [main content]
CONFIDENCE: [0.0-1.0]
RISK_FLAGS: [comma-separated, CRITICAL_ prefix for showstoppers]
REASONING: [explanation]
```

**AgentRegistry** loads from YAML:
- Creates ModelClient for each agent via ModelFactory
- `get_agent(name)`, `list_agents()`, `has_agent(name)`
- Supports `${VAR_NAME}` environment variable substitution

### 4. Context Providers (`context/providers.py`)

**Base interface:**

```python
class ContextProvider(ABC):
    def collect() -> Dict[str, Any]
    def is_available() -> bool
    def get_name() -> str
```

**Providers:**

| Provider | Data Collected |
|----------|---------------|
| `FileSystemContext` | File tree (max_depth=3), key files (README, package.json, etc.) |
| `GitContext` | Branch, status, recent commits, diff summary |
| `ActiveFileContext` | File content, metadata (path, extension, line count, size) |

**ContextManager** aggregates all providers:
- `add_provider(provider)`
- `collect_all()` — Returns `{provider_name: data}` dict
- `get_summary()` — Text status of all providers

### 5. Ma'aT Governance Engine (`core/governance.py`)

Constitutional principles enforced:

1. **Harm Prevention** — Blocks destructive commands (rm -rf, drop database, etc.)
2. **Privacy Protection** — Detects exposed API keys, passwords, secrets
3. **Transparency** — High-risk actions must have descriptions
4. **Human Sovereignty** — Low-trust actions require human review
5. **Fairness** — Equitable treatment
6. **Accountability** — Full audit trail

**Trust thresholds:**

| Trust Score | Behavior |
|-------------|----------|
| >= 0.95 | Auto-approve |
| 0.5 - 0.95 | Review for risky actions |
| < 0.5 | Strict evaluation required |

**Decisions:** `APPROVE`, `DENY`, `FLAG`, `REQUIRE_REVIEW`

**Audit trail:** Every evaluation is logged with timestamp, action details, decision, and reason.

### 6. Prompt Compiler (`core/prompt_compiler.py`)

Deterministic prompt compilation layer that transforms high-level intent into
model-optimized, token-efficient instruction packets.

**Compilation pipeline:**

```
Template Selection -> Context Pruning -> Model Adaptation -> Token Budget -> Schema Injection
```

| Step | Purpose | Savings |
|------|---------|---------|
| Template selection | Match role to YAML template with goal + constraints | - |
| Context pruning | Remove irrelevant files, truncate large content | 30-50% |
| Model adaptation | Claude->XML, GPT->JSON schema, Ollama->instruction tags | 5-10% |
| Token budget | Hard limits prevent runaway prompt sizes | variable |
| Schema injection | Append output format requirements | -5% (adds schema) |

**Key types:**
- `PromptTemplate` — Role, goal, constraints, output schema, model preferences
- `CompiledPrompt` — Final content, estimated tokens, schema, compilation metadata
- `TokenBudget` — max_input_tokens, max_output_tokens, max_total_tokens
- `OutputSchema` — format_type (JSON/MD/XML), required_fields, schema_definition, example

**Configuration:** `config/prompt_templates.yaml`

**Audit:** Every compilation is logged with timestamp, role, token estimates, adapter used.

### 7. Schema Validator (`core/schema_validator.py`)

Output format enforcement layer that validates agent outputs against their
declared schemas before synthesis.

**Validation flow:**

1. Detect format (JSON, Markdown, XML, text)
2. Parse output (extract JSON from markdown code blocks if needed)
3. Validate against schema (check required fields, types)
4. Auto-repair if invalid (fix quotes, commas, braces)
5. Log result to audit trail

**Auto-repair capabilities:**
- Extract JSON from markdown code blocks
- Fix single quotes to double quotes
- Remove trailing commas
- Balance unmatched braces/brackets

**Key types:**
- `ValidationReport` — result (VALID/INVALID/NEEDS_REPAIR), errors, warnings, repaired_output
- `SchemaValidator` — validate(), validate_batch(), get_validation_stats()

**Impact:** Reduces synthesis failures by 50%+ and retry loops by 67%.

### 8. Prompt IR Pipeline (`core/prompt_ir.py`)

The Prompt IR (Intermediate Representation) is the AST for prompts. It transforms
the system from "string plumbing" into a real compiler pipeline with structured,
inspectable IR between high-level intent and compiled prompts.

**Key types:**

- `PromptIR` — Structured representation: role, intent, phase, context_refs, constraints, token_budget, priority, model_hint, metadata
- `PromptIRBuilder` — Fluent builder for clean IR construction
- `PromptIRPlugin` — Base class for safe IR transformations
- `ContextDigestPlugin` — Compresses large context sets into digests (15 files to 1 summary)
- `BudgetOptimizerPlugin` — Phase/priority-aware budget adjustment (planning gets +20%, review gets -20%)
- `IRGovernanceChecker` — Policy enforcement before token spend (protected paths, destructive actions, sensitive constraints)
- `PromptIRPipeline` — Orchestrates governance check, plugin transforms, and audit logging

**Pipeline flow:**

```
PromptIRBuilder.build()
    |
PromptIR { role, intent, context_refs, constraints, budget }
    |
IRGovernanceChecker.check()  <- Free! No tokens spent
    |- DENY -> Block before compile  (saves 100% of rejected tokens)
    +- APPROVE -> Continue
    |
ContextDigestPlugin.transform()  <- Compress if needed
    |
BudgetOptimizerPlugin.transform()  <- Adjust budget
    |
PromptCompiler.compile_from_ir()  <- Standard compilation
    |
CompiledPrompt
```

**Governance policies (default):**

| Policy | Type | Action | Example |
|--------|------|--------|---------|
| Protected paths | context_ref | DENY | `/sys/`, `/etc/`, `C:\Windows\` |
| Destructive actions | intent | FLAG | "delete all", "drop database", "rm -rf" |
| Sensitive constraints | constraint | DENY | "ignore policy", "bypass", "override" |

**Budget optimization multipliers:**

| Phase | Multiplier | Rationale |
|-------|------------|-----------|
| Planning | 1.2x | Needs more exploration |
| Research | 1.3x | Needs most context |
| Implementation | 1.0x | Baseline |
| Review | 0.8x | Can be concise |
| Synthesis | 1.1x | Moderate needs |

Priority bonus: `(priority - 5) * 0.1` (-0.4 to +0.5)

See `PLUGIN_GUIDE.md` for writing custom IR plugins.

### 9. A/B Efficiency Statistics (`core/efficiency_stats.py`)

Quantifiable ROI measurement for the compiler pipeline.

**Key types:**

- `EfficiencyCalculator` — Computes cost, summarizes runs, compares A/B groups
- `RunStats` — Aggregated statistics (avg tokens, duration, retries, repairs, cost)
- `ABComparison` — Full comparison with improvement percentages and efficiency score
- `RunLedgerParser` — Extracts standardized stats from run ledgers

**Metrics tracked:**

| Metric | Weight | Measurement |
|--------|--------|-------------|
| Token reduction | 30% | Input + output tokens |
| Latency reduction | 20% | Execution duration |
| Retry reduction | 20% | Failed retry count |
| Cost reduction | 30% | USD based on model pricing |

**Model pricing:** Built-in pricing tables for Claude (Opus/Sonnet/Haiku), GPT (4/4-turbo/3.5), with configurable defaults.

**Statistical significance levels:**
- < 20 samples: insufficient_data
- 20-50 samples: low_confidence
- 50-100 samples: moderate_confidence
- 100+ samples: high_confidence

**CLI:** `symphony efficiency` generates an ROI report from saved run ledgers.

## Data Flow: Typical Execution

```
1.  CLI receives task: "Design auth system"
2.  ContextManager collects filesystem + git data
3.  Orchestrator transitions: INIT -> PLAN
4.  Conductor agent creates phase plan:
    Phase 1: Analysis (architect, researcher)
    Phase 2: Implementation (implementer)
    Phase 3: Review (reviewer, integrator)
5.  Orchestrator transitions: PLAN -> EXECUTE_PHASE
6.  For each agent, IR pipeline constructs + processes PromptIR:
    a. PromptIRBuilder creates IR: role=architect, intent="Analyze: Design auth...",
       context_refs=[file:README.md, file:requirements.txt, diff:main]
    b. IRGovernanceChecker validates policies -> APPROVED (no violations)
    c. ContextDigestPlugin: 3 refs <= 10 limit -> pass through
    d. BudgetOptimizerPlugin: planning phase x priority 5 -> 3000 x 1.2 x 1.0 = 3600
7.  Prompt Compiler compiles from IR:
    - compile_from_ir() resolves context refs to actual data
    - Template selection (architect template)
    - Context pruning (2 key files, git branch)
    - Model adaptation (mock -> default)
    - Token budget check (750 tokens, within 3600 adjusted limit)
    - Schema injection (JSON schema for system_design output)
8.  Phase 1 agents execute in parallel with compiled prompts:
    - Architect: system design -> confidence 0.88
    - Researcher: prior art -> confidence 0.92
9.  Schema Validator checks outputs against declared schemas
10. EXECUTE_PHASE -> SYNTHESIZE: Combine outputs
11. SYNTHESIZE -> VALIDATE: Check thresholds
    avg_confidence = 0.90 >= 0.85
    critical_flags = []
    -> Validation passes
12. Repeat for Phase 2, Phase 3
13. Compiler + validator + IR pipeline stats recorded in ledger
14. Governance checks final output
15. VALIDATE -> TERMINATE
16. RunLedger saved to .symphony/runs/
17. Compilation + validation logs saved to .symphony/logs/
18. Run `symphony efficiency` to measure A/B ROI across runs
```

## Extension Points

### Adding a New Model Provider

```python
from models.client import ModelClient, ModelResponse, ModelProvider

class CustomClient(ModelClient):
    def call(self, messages, temperature=0.7, max_tokens=2000, tools=None):
        # Your implementation
        return ModelResponse(content="...", provider=ModelProvider.MOCK, model="custom")

    def get_provider(self):
        return ModelProvider.MOCK

    def get_model_name(self):
        return "custom-v1"

# Register
from models.client import ModelFactory
ModelFactory.register("custom", CustomClient)
```

### Adding a New Context Provider

```python
from context.providers import ContextProvider

class DockerContext(ContextProvider):
    def collect(self):
        return {"containers": [...], "images": [...]}

    def is_available(self):
        return shutil.which("docker") is not None

    def get_name(self):
        return "docker"
```

### Adding a New Agent

Add to `.symphony/agents.yaml`:

```yaml
agents:
  - name: security_auditor
    role: Security Auditor
    model_provider: anthropic
    system_prompt: |
      You are the Security Auditor agent...
```

### Adding an IR Plugin

```python
from core.prompt_ir import PromptIRPlugin, PromptIR

class SecurityScanPlugin(PromptIRPlugin):
    """Scan for security anti-patterns in IR."""

    def transform(self, ir: PromptIR) -> PromptIR:
        ir_new = ir.clone()
        if "password" in ir.intent.lower():
            ir_new.constraints.append("Never log or display passwords")
        self._record_transformation(ir, ir_new, "security", "Added password safety")
        return ir_new
```

See `PLUGIN_GUIDE.md` for the full plugin development guide.

### Adding IR Governance Policies

```python
from core.prompt_ir import IRGovernanceChecker

checker = IRGovernanceChecker(policies=[
    {
        "name": "budget_limit",
        "type": "intent",
        "forbidden_keywords": ["unlimited tokens"],
        "action": "deny"
    }
])
```

### Adding Governance Rules

Extend `MaaTGovernanceEngine`:
- Add patterns to `DANGEROUS_PATTERNS` or `SECRET_PATTERNS`
- Override `evaluate_action()` for custom logic

## Performance Characteristics

- **Parallel execution:** Agents within a phase run concurrently (ThreadPoolExecutor)
- **Max workers:** Configurable, default 5
- **Timeouts:** Model calls have provider-specific timeouts
- **Memory:** RunLedger grows linearly with phases and agent responses
- **Disk:** Each run saves a JSON ledger (typically 5-50KB)

## Security Considerations

- API keys loaded from `.env` files, never hardcoded
- `${VAR_NAME}` substitution resolves from environment at runtime
- Governance engine blocks known dangerous patterns
- Secret detection prevents credential exposure in outputs
- `.symphony/.env` should be in `.gitignore`
- Trust-based authorization for high-risk actions

## Future Architecture

### Planned Enhancements

- **Agent memory:** Persistent memory across runs (vector store)
- **Tool use:** File write, code execution, network requests (governed)
- **Streaming:** Real-time output as agents produce results
- **Web UI:** Dashboard for run monitoring and comparison
- **Plugins:** Custom agent marketplace and shared configurations
- **Federation:** Distributed agent networks across machines
