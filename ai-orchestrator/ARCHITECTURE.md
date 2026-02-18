# AI Orchestrator — Technical Architecture

## System Overview

```
┌────────────────────────────────────────────────────────────┐
│                     CLI Interface                          │
│                   (orchestrator.py)                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │  Orchestrator │  │   Agent     │  │    Context        │  │
│  │  State Machine│  │   Registry  │  │    Manager        │  │
│  │  (core/)      │  │  (agents/)  │  │   (context/)      │  │
│  └──────┬───────┘  └──────┬──────┘  └────────┬─────────┘  │
│         │                 │                   │            │
│  ┌──────┴───────┐  ┌──────┴──────┐  ┌────────┴─────────┐  │
│  │  Governance   │  │   Model     │  │   Providers       │  │
│  │  (Ma'aT)      │  │   Factory   │  │  FS / Git / File  │  │
│  └──────────────┘  └──────┬──────┘  └──────────────────┘  │
│                           │                                │
│  ┌────────────────────────┴────────────────────────────┐   │
│  │              Model Abstraction Layer                 │   │
│  │   OpenAI  │  Anthropic  │  Ollama  │  Ma'aT  │ Mock │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

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

## Data Flow: Typical Execution

```
1. CLI receives task → "Design auth system"
2. ContextManager collects filesystem + git data
3. Orchestrator transitions: INIT → PLAN
4. Conductor agent creates phase plan:
   Phase 1: Analysis (architect, researcher)
   Phase 2: Implementation (implementer)
   Phase 3: Review (reviewer, integrator)
5. Orchestrator transitions: PLAN → EXECUTE_PHASE
6. Phase 1 agents execute in parallel:
   - Architect: system design → confidence 0.88
   - Researcher: prior art → confidence 0.92
7. EXECUTE_PHASE → SYNTHESIZE: Combine outputs
8. SYNTHESIZE → VALIDATE: Check thresholds
   avg_confidence = 0.90 >= 0.85 ✓
   critical_flags = [] ✓
   → Validation passes
9. Repeat for Phase 2, Phase 3
10. Governance checks final output
11. VALIDATE → TERMINATE
12. RunLedger saved to .orchestrator/runs/
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

Add to `agents.yaml`:

```yaml
agents:
  - name: security_auditor
    role: Security Auditor
    model_provider: anthropic
    system_prompt: |
      You are the Security Auditor agent...
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
- `.orchestrator/.env` should be in `.gitignore`
- Trust-based authorization for high-risk actions

## Future Architecture

### Planned Enhancements

- **Agent memory:** Persistent memory across runs (vector store)
- **Tool use:** File write, code execution, network requests (governed)
- **Streaming:** Real-time output as agents produce results
- **Web UI:** Dashboard for run monitoring and comparison
- **Plugins:** Custom agent marketplace and shared configurations
- **Federation:** Distributed agent networks across machines
