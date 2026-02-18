# Symphony-IR: Prompt IR Specification

**IR Schema Version:** 1.0 (FROZEN)
**Status:** Stable
**Module:** `core/prompt_ir.py`

---

## Table of Contents

1. [Overview](#overview)
2. [Design Rationale](#design-rationale)
3. [PromptIR Schema](#promptir-schema)
4. [Field Reference](#field-reference)
5. [PhaseType Enum](#phasetype-enum)
6. [Serialization Format](#serialization-format)
7. [Context Reference Format](#context-reference-format)
8. [Pipeline Flow](#pipeline-flow)
9. [Governance Policies](#governance-policies)
10. [Budget Optimization](#budget-optimization)
11. [Version Guarantees](#version-guarantees)
12. [IRTransformation Record](#irtransformation-record)
13. [Examples](#examples)

---

## Overview

The Prompt IR (Intermediate Representation) is the AST (Abstract Syntax Tree)
for prompts in the Symphony-IR system. It transforms the orchestration pipeline
from unstructured string plumbing into a compiler-grade pipeline with
inspectable, structured IR between high-level intent and compiled prompts.

```
Before:  Conductor -> (strings) -> Compiler -> (strings) -> Model
After:   Conductor -> PromptIR -> IR Pipeline -> Compiler -> CompiledPrompt -> Model
```

The IR enables:

- Governance inspection of intent before tokens are spent.
- Plugin-based mutation of structured fields with full audit trails.
- Deterministic token budgeting based on phase and priority.
- Meaningful per-field metrics and diagnostics.
- Versioned schemas with backwards-compatibility guarantees.
- Safe extensibility through the metadata field and plugin system.

---

## Design Rationale

Traditional prompt construction concatenates strings with no structure and no
inspection points. This means governance checks require parsing natural
language, budget enforcement is approximate, and debugging prompt issues requires
reading raw text dumps.

The PromptIR solves these problems by introducing a typed, structured
representation that sits between intent and compilation. Every field has a
defined type, a clear semantic purpose, and a stable serialization format.
Governance can inspect `intent` and `context_refs` as structured data.
Budget optimization can read `phase` and `priority` as typed values. Plugins
can add `constraints` without parsing strings.

---

## PromptIR Schema

```python
@dataclass
class PromptIR:
    # Core identity
    role: str
    intent: str
    phase: PhaseType

    # Context references (structured, not raw)
    context_refs: List[str]

    # Constraints and requirements
    constraints: List[str]
    output_requirements: Dict[str, Any]

    # Resource management
    token_budget: int
    priority: int = 5

    # Model hints (suggestions, not mandates)
    model_hint: Optional[str] = None
    temperature_hint: float = 0.7

    # Schema reference
    schema_id: str = "default"

    # Versioning
    ir_version: str = "1.0"

    # Metadata (extensibility point)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Tracking
    ir_id: Optional[str] = None
    created_at: Optional[datetime] = None
```

---

## Field Reference

### Core Identity Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `role` | `str` | Yes | -- | Agent role identifier. Matches the agent name in the registry (e.g., `"architect"`, `"implementer"`, `"reviewer"`). Used for template selection during compilation. |
| `intent` | `str` | Yes | -- | High-level objective from the Conductor. Describes what the agent should accomplish, not how. Inspected by governance before tokens are spent. |
| `phase` | `PhaseType` | Yes | -- | Execution phase enum value. Determines budget multipliers and optimization strategies. |

### Context Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `context_refs` | `List[str]` | Yes | -- | Structured references to context data. Each entry uses a prefixed format (see [Context Reference Format](#context-reference-format)). References are resolved to actual data during compilation. |

### Constraint Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `constraints` | `List[str]` | Yes | -- | Must-follow rules for the agent. Each entry is a natural-language constraint string. Plugins may append additional constraints. Governance may inspect constraints for policy violations. |
| `output_requirements` | `Dict[str, Any]` | Yes | -- | Schema requirements for the agent output. Passed through to the Schema Validator for post-execution validation. |

### Resource Management Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `token_budget` | `int` | Yes | -- | Hard token limit for the compiled prompt. The BudgetOptimizerPlugin may adjust this value based on phase and priority. The Prompt Compiler enforces this as a ceiling. |
| `priority` | `int` | No | `5` | Priority level from 1 (lowest) to 10 (highest). Affects budget allocation via the formula `(priority - 5) * 0.1`, yielding a bonus range of -0.4 to +0.5. Default of 5 applies no bonus. |

### Model Hint Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `model_hint` | `Optional[str]` | No | `None` | Suggested model provider (e.g., `"anthropic"`, `"openai"`, `"ollama"`). This is a hint, not a mandate. The orchestrator may override based on availability or cost. When `None`, defaults to `"anthropic"` during compilation. |
| `temperature_hint` | `float` | No | `0.7` | Suggested sampling temperature. Lower values (0.1-0.3) produce more deterministic output. Higher values (0.7-1.0) produce more creative output. The model client may override. |

### Schema Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `schema_id` | `str` | No | `"default"` | Validation schema reference. Identifies which output schema definition to use for post-execution validation. The value `"default"` uses the template-defined schema for the agent role. |

### Version Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `ir_version` | `str` | No | `"1.0"` | IR schema version. Frozen at `"1.0"` for this release. Do not change without a major version bump. Used for forwards-compatibility detection: if a consumer receives an IR with an unknown version, it should reject or handle gracefully. |

### Extensibility Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `metadata` | `Dict[str, Any]` | No | `{}` | Open-ended extensibility point. Plugins store transformation records here (e.g., `original_context_refs`, `context_digest`, `original_budget`, `budget_multiplier`). Custom plugins should use namespaced keys to avoid collisions (e.g., `"myplugin_scan_results"`). |

### Tracking Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `ir_id` | `Optional[str]` | No | Auto-generated | Unique identifier for this IR instance. Auto-generated as `uuid4()[:8]` in `__post_init__` if not provided. A new ID is generated on `clone()`. Used for audit trail correlation. |
| `created_at` | `Optional[datetime]` | No | Auto-generated | UTC timestamp of IR creation. Auto-generated as `datetime.now(timezone.utc)` in `__post_init__` if not provided. Serialized as ISO 8601 string. |

---

## PhaseType Enum

```python
class PhaseType(Enum):
    PLANNING = "planning"
    RESEARCH = "research"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    SYNTHESIS = "synthesis"
```

| Value | String | Description | Budget Multiplier |
|-------|--------|-------------|-------------------|
| `PLANNING` | `"planning"` | Initial analysis and design. Needs more exploration room. | 1.2x |
| `RESEARCH` | `"research"` | Documentation and prior art gathering. Needs the most context. | 1.3x |
| `IMPLEMENTATION` | `"implementation"` | Concrete code and content production. Baseline budget. | 1.0x |
| `REVIEW` | `"review"` | Critical analysis and quality checks. Can be concise. | 0.8x |
| `SYNTHESIS` | `"synthesis"` | Output integration and conflict resolution. Moderate needs. | 1.1x |

The orchestrator maps phase names from the Conductor plan to PhaseType values
using a case-insensitive lookup. The mapping includes aliases:

- `"analysis"` and `"planning"` both map to `PLANNING`
- `"integration"` maps to `SYNTHESIS`
- Unrecognized phase names default to `IMPLEMENTATION`

---

## Serialization Format

PromptIR uses JSON as its serialization format, implemented through the
`to_dict()` and `from_dict()` methods. The serialization format is stable and
backwards-compatible under the v1.0 guarantee.

### to_dict()

Converts a PromptIR instance to a plain Python dictionary suitable for JSON
serialization.

```python
ir = PromptIRBuilder("architect", "Design auth system") \
    .phase(PhaseType.PLANNING) \
    .add_context_ref("file:src/auth.py") \
    .set_token_budget(3000) \
    .build()

data = ir.to_dict()
```

Output structure:

```json
{
    "ir_id": "a1b2c3d4",
    "role": "architect",
    "intent": "Design auth system",
    "phase": "planning",
    "context_refs": ["file:src/auth.py"],
    "constraints": [],
    "output_requirements": {},
    "token_budget": 3000,
    "priority": 5,
    "model_hint": null,
    "temperature_hint": 0.7,
    "schema_id": "default",
    "ir_version": "1.0",
    "metadata": {},
    "created_at": "2026-02-18T12:00:00+00:00"
}
```

Serialization rules:

- `phase` is serialized as its string value (e.g., `"planning"`), not the enum
  member name.
- `created_at` is serialized as an ISO 8601 string with timezone.
- `model_hint` serializes as `null` when `None`.
- `metadata` contains whatever plugins have stored; values must be
  JSON-serializable.

### from_dict()

Reconstructs a PromptIR instance from a dictionary. Handles type conversions
automatically.

```python
ir = PromptIR.from_dict(data)
```

Deserialization rules:

- `phase` string values are converted to `PhaseType` enum members.
- `created_at` ISO 8601 strings are converted to `datetime` objects via
  `datetime.fromisoformat()`.
- Unknown keys in the dictionary are passed through to the constructor. If the
  constructor does not accept them, a `TypeError` will be raised.

### clone()

Creates a deep copy of the IR with a new `ir_id`. The original `ir_id` is
discarded and a fresh UUID is generated.

```python
ir_copy = ir.clone()
assert ir_copy.ir_id != ir.ir_id
assert ir_copy.intent == ir.intent
```

Plugins must use `clone()` before mutating an IR to preserve the original for
audit trail purposes.

---

## Context Reference Format

Context references in `context_refs` use a prefix-based format to distinguish
reference types. The Prompt Compiler resolves these references to actual data
during the `compile_from_ir()` step.

### Prefix Types

| Prefix | Format | Description | Resolution |
|--------|--------|-------------|------------|
| `file:` | `file:<path>` | Reference to a file on disk. | Compiler reads the file content (capped at 10,000 characters). |
| `diff:` | `diff:<ref>` | Reference to a git diff. | Compiler stores the diff reference in git context. |
| `memory:` | `memory:<key>` | Reference to a memory block in metadata. | Compiler retrieves the value from `ir.metadata[key]`. |
| `__CONTEXT_DIGEST__` | (literal) | Marker indicating that context has been compressed. | Compiler retrieves the digest string from `ir.metadata["context_digest"]`. |
| (no prefix) | `<raw string>` | Raw string reference, treated as a file path. | Compiler stores as `[Reference: <value>]` in filesystem context. |

### Examples

```python
context_refs = [
    "file:src/auth/login.py",        # File reference
    "file:src/auth/middleware.py",    # File reference
    "diff:main",                      # Git diff against main branch
    "memory:previous_analysis",       # Memory block from metadata
]
```

### Context Digest Marker

When the `ContextDigestPlugin` compresses context references, it replaces all
refs with a single `__CONTEXT_DIGEST__` marker and stores the original
references and the digest text in metadata:

```python
# Before ContextDigestPlugin:
ir.context_refs = ["file:a.py", "file:b.py", ..., "file:z.py"]  # 26 refs

# After ContextDigestPlugin (threshold exceeded):
ir.context_refs = ["__CONTEXT_DIGEST__"]
ir.metadata["original_context_refs"] = ["file:a.py", "file:b.py", ..., "file:z.py"]
ir.metadata["context_digest"] = "Context summary: 26 files related to: ..."
```

---

## Pipeline Flow

The PromptIRPipeline processes an IR through governance checks and plugin
transformations before handing it off to the Prompt Compiler.

```
                    +-------------------+
                    |  PromptIRBuilder  |
                    |     .build()      |
                    +---------+---------+
                              |
                              v
                    +---------+---------+
                    |     PromptIR      |
                    | (structured data) |
                    +---------+---------+
                              |
              +---------------+---------------+
              |                               |
              v                               |
    +---------+---------+                     |
    | IRGovernanceChecker|                    |
    |     .check()       |                    |
    +---------+---------+                     |
              |                               |
         +----+----+                          |
         |         |                          |
       DENY     APPROVE                      |
         |         |                          |
         v         v                          |
    [Return IR,  +---------+---------+        |
     approved=   | ContextDigestPlugin|       |
     False,      |    .transform()    |       |
     violations] +---------+---------+        |
                           |                  |
                           v                  |
                 +---------+---------+        |
                 |BudgetOptimizerPlugin|      |
                 |    .transform()     |      |
                 +---------+---------+        |
                           |                  |
                           v                  |
                 +---------+---------+        |
                 | (additional plugins|       |
                 |  if registered)    |       |
                 +---------+---------+        |
                           |                  |
                           v                  |
                 +---------+---------+        |
                 |  Pipeline Logging  |       |
                 +---------+---------+        |
                           |                  |
                           v                  |
                 +---------+---------+        |
                 |  PromptCompiler   |        |
                 | .compile_from_ir()|        |
                 +---------+---------+        |
                           |                  |
                           v                  |
                 +---------+---------+        |
                 |  CompiledPrompt   |        |
                 | (ready for model) |        |
                 +-------------------+        |
                                              |
              +-------------------------------+
```

### Pipeline Process Signature

```python
def process(self, ir: PromptIR) -> Tuple[PromptIR, bool, List[str]]:
    """
    Returns:
        transformed_ir: The IR after all plugin transforms.
        approved: True if governance approved, False if denied.
        violations: List of violation strings (empty if approved).
    """
```

### Pipeline Execution Order

1. **Governance check** (free -- no tokens spent). If denied, the original IR
   is returned immediately with `approved=False` and the list of violations.

2. **Plugin transforms** applied in registration order. Each plugin receives
   the current IR and returns a (possibly modified) IR. If a plugin raises an
   exception, the error is logged and the pipeline continues with the
   untransformed IR.

3. **Pipeline logging** records the before/after IR IDs, all transformations,
   approval status, and violations.

---

## Governance Policies

The `IRGovernanceChecker` enforces policies on the structured IR before any
tokens are spent on compilation or model calls.

### Policy Structure

```python
{
    "name": str,               # Policy identifier
    "type": str,               # "context_ref", "intent", or "constraint"
    "forbidden_patterns": [],  # For context_ref type: substring matches
    "forbidden_keywords": [],  # For intent/constraint types: substring matches
    "action": str,             # "deny" or "flag"
}
```

### Default Policies

| Policy Name | Type | Forbidden Patterns/Keywords | Action | Rationale |
|-------------|------|-----------------------------|--------|-----------|
| `protected_paths` | `context_ref` | `/sys/`, `/etc/`, `C:\Windows\System32\` | DENY | Prevents agents from reading or referencing system-critical paths. |
| `destructive_actions` | `intent` | `"delete all"`, `"drop database"`, `"rm -rf"` | FLAG | Flags potentially destructive intents for review without blocking. |
| `sensitive_constraints` | `constraint` | `"ignore policy"`, `"bypass"`, `"override"` | DENY | Prevents prompt injection attempts that try to circumvent governance. |

### Check Behavior

- **DENY** violations cause the pipeline to return `approved=False`. The IR is
  not processed through plugins and is not compiled. This saves 100% of token
  cost for rejected requests.

- **FLAG** violations are recorded in the violations list but do not block
  processing. The IR proceeds through the pipeline with `approved=True`.

### Custom Policies

Custom policies can be provided at construction time:

```python
checker = IRGovernanceChecker(policies=[
    {
        "name": "budget_limit",
        "type": "intent",
        "forbidden_keywords": ["unlimited tokens", "no budget"],
        "action": "deny",
    },
    {
        "name": "internal_only",
        "type": "context_ref",
        "forbidden_patterns": ["s3://production/", "/var/secrets/"],
        "action": "deny",
    },
])
```

### Violations Report

```python
report = checker.get_violations_report()
# {
#     "total_checks": 42,
#     "approved": 40,
#     "denied": 2,
#     "approval_rate": 0.952,
#     "recent_violations": [...]  # Last 10 violation log entries
# }
```

---

## Budget Optimization

The `BudgetOptimizerPlugin` adjusts the `token_budget` field based on the
`phase` and `priority` of the IR.

### Phase Multipliers

| Phase | Multiplier | Rationale |
|-------|------------|-----------|
| PLANNING | 1.2x | Planning tasks need more room for exploration and design alternatives. |
| RESEARCH | 1.3x | Research tasks need the most context to gather comprehensive information. |
| IMPLEMENTATION | 1.0x | Implementation is the baseline. Budget reflects standard coding tasks. |
| REVIEW | 0.8x | Review tasks can be concise. Focused critique needs fewer tokens. |
| SYNTHESIS | 1.1x | Synthesis tasks need moderate room to integrate multiple outputs. |

### Priority Bonus

The priority bonus adjusts the budget based on the `priority` field (1-10):

```
priority_bonus = (priority - 5) * 0.1
```

| Priority | Bonus | Effect |
|----------|-------|--------|
| 1 | -0.4 | 60% of phase-adjusted budget |
| 2 | -0.3 | 70% of phase-adjusted budget |
| 3 | -0.2 | 80% of phase-adjusted budget |
| 4 | -0.1 | 90% of phase-adjusted budget |
| 5 | 0.0 | 100% of phase-adjusted budget (default) |
| 6 | +0.1 | 110% of phase-adjusted budget |
| 7 | +0.2 | 120% of phase-adjusted budget |
| 8 | +0.3 | 130% of phase-adjusted budget |
| 9 | +0.4 | 140% of phase-adjusted budget |
| 10 | +0.5 | 150% of phase-adjusted budget |

### Budget Calculation Formula

```
adjusted_budget = int(original_budget * phase_multiplier * (1 + priority_bonus))
```

### Example Calculations

| Role | Phase | Priority | Original | Phase Mult | Priority Bonus | Adjusted |
|------|-------|----------|----------|------------|----------------|----------|
| architect | PLANNING | 7 | 3000 | 1.2 | +0.2 | 4320 |
| researcher | RESEARCH | 5 | 3000 | 1.3 | 0.0 | 3900 |
| implementer | IMPLEMENTATION | 5 | 3000 | 1.0 | 0.0 | 3000 |
| reviewer | REVIEW | 3 | 3000 | 0.8 | -0.2 | 1920 |
| integrator | SYNTHESIS | 8 | 3000 | 1.1 | +0.3 | 4290 |

### Metadata Records

After budget optimization, the plugin stores the following in `ir.metadata`:

```python
ir.metadata["original_budget"] = 3000       # Pre-optimization budget
ir.metadata["budget_multiplier"] = 1.2      # Phase multiplier applied
```

---

## Version Guarantees

IR schema version 1.0 is frozen. The following guarantees apply:

### Guaranteed Stable (1.x)

1. All `PromptIR` fields documented in this specification will remain present
   in all future 1.x releases. No field will be removed or renamed.

2. New **optional** fields may be added in minor releases (1.1, 1.2, etc.).
   These fields will always have default values so that existing code continues
   to work without modification.

3. The `to_dict()` output format is stable. Existing keys will not be removed
   or renamed. New keys may be added.

4. The `from_dict()` input format is backwards-compatible. Dictionaries
   produced by older versions of `to_dict()` will always be accepted by newer
   versions of `from_dict()`.

5. The plugin `transform()` method signature is stable:
   `(PromptIR) -> PromptIR`.

6. The pipeline `process()` method signature is stable:
   `(PromptIR) -> Tuple[PromptIR, bool, List[str]]`.

### Breaking Changes (2.0)

The following changes are reserved for a major version bump (2.0):

- Removing or renaming any existing `PromptIR` field.
- Changing the type of any existing field.
- Changing the `to_dict()` / `from_dict()` serialization format in an
  incompatible way.
- Changing the `transform()` or `process()` method signatures.
- Changing `PhaseType` enum values.

### Version Detection

Consumers should check `ir_version` to detect forwards-compatibility issues:

```python
if ir.ir_version != "1.0":
    if ir.ir_version.startswith("1."):
        # Compatible -- may have new optional fields
        pass
    else:
        # Incompatible -- major version mismatch
        raise ValueError(f"Unsupported IR version: {ir.ir_version}")
```

---

## IRTransformation Record

Every plugin transformation is recorded as an `IRTransformation` for audit
trail purposes.

```python
@dataclass
class IRTransformation:
    transformation_type: str   # e.g., "context_digest", "budget_optimization"
    description: str           # Human-readable description of what changed
    before_hash: str           # SHA-256 hash (first 16 chars) of IR before
    after_hash: str            # SHA-256 hash (first 16 chars) of IR after
    applied_by: str            # Plugin class name
    timestamp: datetime        # UTC timestamp
```

The hash is computed by JSON-serializing the IR via `to_dict()` with sorted
keys and applying SHA-256, then taking the first 16 hexadecimal characters.

Plugins record transformations by calling `self._record_transformation()`:

```python
self._record_transformation(
    ir_before,
    ir_after,
    "context_digest",
    f"Compressed {len(ir.context_refs)} refs into digest",
)
```

---

## Examples

### Constructing an IR with the Builder

```python
from core.prompt_ir import PromptIRBuilder, PhaseType

ir = (
    PromptIRBuilder("architect", "Design a REST API for user authentication")
    .phase(PhaseType.PLANNING)
    .add_context_ref("file:src/auth/login.py")
    .add_context_ref("file:src/auth/middleware.py")
    .add_context_ref("diff:main")
    .add_constraint("Must support OAuth 2.0")
    .add_constraint("Must not expose user credentials in logs")
    .set_output_requirements({
        "system_design": "string",
        "components": ["string"],
        "risks": ["string"],
    })
    .set_token_budget(3000)
    .set_priority(7)
    .set_model_hint("anthropic")
    .set_temperature_hint(0.5)
    .build()
)
```

### Processing through the Pipeline

```python
from core.prompt_ir import (
    PromptIRPipeline,
    IRGovernanceChecker,
    ContextDigestPlugin,
    BudgetOptimizerPlugin,
)

pipeline = PromptIRPipeline(
    plugins=[
        ContextDigestPlugin(config={"max_context_refs": 10}),
        BudgetOptimizerPlugin(),
    ],
    governance=IRGovernanceChecker(),
)

transformed_ir, approved, violations = pipeline.process(ir)

if approved:
    print(f"IR approved: {transformed_ir.ir_id}")
    print(f"Adjusted budget: {transformed_ir.token_budget}")
else:
    print(f"IR denied: {violations}")
```

### Compiling from IR

```python
from core.prompt_compiler import PromptCompiler

compiler = PromptCompiler(templates_path="config")
compiled = compiler.compile_from_ir(transformed_ir)

print(f"Compiled prompt: {compiled.estimated_tokens} tokens")
print(f"Model provider: {compiled.model_provider}")
print(f"IR metadata: {compiled.compilation_metadata}")
```

### Serialization Round-Trip

```python
import json

# Serialize
data = ir.to_dict()
json_str = json.dumps(data, indent=2, default=str)

# Deserialize
data_back = json.loads(json_str)
ir_restored = PromptIR.from_dict(data_back)

assert ir_restored.role == ir.role
assert ir_restored.intent == ir.intent
assert ir_restored.phase == ir.phase
```
