# Symphony-IR: Plugin Development Guide

**IR Schema Version:** 1.0
**Module:** `core/prompt_ir.py`

---

## Table of Contents

1. [Overview](#overview)
2. [Plugin Architecture](#plugin-architecture)
3. [Creating a Custom Plugin](#creating-a-custom-plugin)
4. [Built-in Plugins](#built-in-plugins)
5. [Plugin Lifecycle and Audit Trail](#plugin-lifecycle-and-audit-trail)
6. [Registering Plugins with the Pipeline](#registering-plugins-with-the-pipeline)
7. [Example: SecurityScanPlugin](#example-securityscanplugin)
8. [Example: CostCapPlugin](#example-costcapplugin)
9. [Testing Plugins](#testing-plugins)
10. [Best Practices](#best-practices)

---

## Overview

The Symphony-IR plugin system provides a structured, auditable mechanism for
transforming PromptIR instances before they are compiled into model-specific
prompts. Plugins operate on typed, structured data rather than raw strings,
enabling safe mutations with full audit trails.

Plugins are the primary extensibility point in the IR pipeline. They sit between
governance checks and compilation, transforming the IR in well-defined ways:

```
PromptIR
    |
    v
IRGovernanceChecker.check()     <-- Policy enforcement (free)
    |
    v
Plugin 1: transform()          <-- Your custom logic
    |
    v
Plugin 2: transform()          <-- Additional transforms
    |
    v
PromptCompiler.compile_from_ir()
    |
    v
CompiledPrompt
```

---

## Plugin Architecture

### Base Class

All plugins extend `PromptIRPlugin`, which provides the transformation
interface and audit trail infrastructure.

```python
class PromptIRPlugin:
    """Base class for IR transformation plugins."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.transformations: List[IRTransformation] = []

    def transform(self, ir: PromptIR) -> PromptIR:
        """Transform the IR. Must return a (possibly modified) PromptIR."""
        raise NotImplementedError

    def _record_transformation(
        self,
        ir_before: PromptIR,
        ir_after: PromptIR,
        transformation_type: str,
        description: str,
    ):
        """Record transformation for audit trail."""
        ...

    def _hash_ir(self, ir: PromptIR) -> str:
        """Generate SHA-256 hash (first 16 hex chars) of IR state."""
        ...
```

### Key Contracts

1. `transform()` receives a `PromptIR` and must return a `PromptIR`.
2. `transform()` should not produce side effects beyond recording
   transformations.
3. Plugins must clone the IR before mutating it. Never mutate the input
   directly.
4. If a plugin has nothing to do (e.g., the IR does not meet the plugin's
   trigger condition), it should return the original IR unchanged.
5. If a plugin encounters an error, the pipeline catches the exception, logs
   it, and continues with the untransformed IR. Plugins should not swallow
   errors silently.

---

## Creating a Custom Plugin

### Step 1: Subclass PromptIRPlugin

```python
from core.prompt_ir import PromptIRPlugin, PromptIR
from typing import Any, Dict, Optional

class MyCustomPlugin(PromptIRPlugin):
    """Description of what this plugin does."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        # Read plugin-specific configuration
        self.my_threshold = self.config.get("my_threshold", 100)
```

### Step 2: Implement transform()

```python
    def transform(self, ir: PromptIR) -> PromptIR:
        """Apply custom transformation logic."""
        # Check if transformation is needed
        if not self._should_transform(ir):
            return ir  # Return original unchanged

        # Clone before mutating
        ir_after = ir.clone()

        # Apply mutations to the cloned IR
        ir_after.constraints.append("Custom constraint from MyPlugin")
        ir_after.metadata["my_plugin_applied"] = True

        # Record the transformation for audit trail
        self._record_transformation(
            ir,
            ir_after,
            "my_custom_transform",
            "Added custom constraint based on threshold check",
        )

        return ir_after

    def _should_transform(self, ir: PromptIR) -> bool:
        """Determine if this IR needs transformation."""
        return ir.token_budget > self.my_threshold
```

### Step 3: Register with the Pipeline

```python
from core.prompt_ir import PromptIRPipeline, IRGovernanceChecker

pipeline = PromptIRPipeline(
    plugins=[
        MyCustomPlugin(config={"my_threshold": 500}),
    ],
    governance=IRGovernanceChecker(),
)
```

---

## Built-in Plugins

### ContextDigestPlugin

**Purpose:** Compresses large context reference lists into a single digest when
the number of references exceeds a configurable threshold.

**When it acts:** Only when `len(ir.context_refs) > max_context_refs` (default:
10).

**What it does:**

1. Clones the IR.
2. Creates a digest summarizing all context references. In production mode,
   uses a cheap model for summarization. Falls back to a simple text summary.
3. Stores the original references in `ir.metadata["original_context_refs"]`.
4. Stores the digest text in `ir.metadata["context_digest"]`.
5. Replaces `ir.context_refs` with `["__CONTEXT_DIGEST__"]`.
6. Records the transformation.

**Configuration:**

```python
ContextDigestPlugin(config={
    "max_context_refs": 10,   # Threshold before compression (default: 10)
    "cheap_model": model,     # Optional ModelClient for summarization
})
```

**Example behavior:**

```python
# Input: IR with 15 context refs
ir.context_refs = ["file:a.py", "file:b.py", ..., "file:o.py"]

# Output: IR with compressed context
ir.context_refs = ["__CONTEXT_DIGEST__"]
ir.metadata["original_context_refs"] = ["file:a.py", ..., "file:o.py"]
ir.metadata["context_digest"] = "Context summary: 15 files related to: ..."
```

### BudgetOptimizerPlugin

**Purpose:** Adjusts token budgets based on the execution phase and priority
level of the IR.

**When it acts:** Always. Every IR gets budget optimization applied.

**What it does:**

1. Clones the IR.
2. Looks up the phase multiplier from the `PHASE_MULTIPLIERS` table.
3. Calculates the priority bonus as `(priority - 5) * 0.1`.
4. Computes: `adjusted = int(original * multiplier * (1 + bonus))`.
5. Stores `original_budget` and `budget_multiplier` in metadata.
6. Records the transformation.

**Phase Multipliers:**

| Phase | Multiplier |
|-------|------------|
| PLANNING | 1.2 |
| RESEARCH | 1.3 |
| IMPLEMENTATION | 1.0 |
| REVIEW | 0.8 |
| SYNTHESIS | 1.1 |

**Configuration:** None. The plugin uses hardcoded multipliers. To customize
multipliers, subclass `BudgetOptimizerPlugin` and override `PHASE_MULTIPLIERS`.

---

## Plugin Lifecycle and Audit Trail

### Lifecycle

1. **Instantiation.** The plugin is created with an optional configuration
   dictionary. The `self.transformations` list is initialized as empty.

2. **Pipeline registration.** The plugin instance is passed to
   `PromptIRPipeline` via the `plugins` parameter. Plugins are applied in
   list order.

3. **Transform call.** For each IR processed by the pipeline, the plugin's
   `transform()` method is called. The plugin receives the current IR (which
   may have been modified by earlier plugins) and returns a new IR.

4. **Error handling.** If `transform()` raises an exception, the pipeline logs
   the error via `_log_plugin_error()` and continues with the untransformed IR.
   The plugin failure does not halt the pipeline.

5. **Audit collection.** After all plugins run, the pipeline collects
   `IRTransformation` records from each plugin's `self.transformations` list
   and includes them in the pipeline log.

### Audit Trail

Every transformation is recorded as an `IRTransformation` dataclass:

```python
@dataclass
class IRTransformation:
    transformation_type: str   # Category of the transformation
    description: str           # Human-readable description
    before_hash: str           # SHA-256[:16] of IR before
    after_hash: str            # SHA-256[:16] of IR after
    applied_by: str            # Plugin class name (auto-populated)
    timestamp: datetime        # UTC timestamp (auto-populated)
```

The `_record_transformation()` helper method automatically:

- Computes the before and after hashes from the IR's `to_dict()` representation.
- Sets `applied_by` to `self.__class__.__name__`.
- Sets `timestamp` to the current UTC time.
- Appends the record to `self.transformations`.

Pipeline-level statistics are available via `pipeline.get_pipeline_stats()`:

```python
stats = pipeline.get_pipeline_stats()
# {
#     "total_runs": 42,
#     "total_transformations": 84,
#     "avg_transformations_per_run": 2.0,
# }
```

Individual pipeline runs are logged in `pipeline.pipeline_log`, which records
the before/after IR IDs, all transformations, approval status, and violations
for each run.

---

## Registering Plugins with the Pipeline

### Basic Registration

Pass plugin instances to the `PromptIRPipeline` constructor:

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
        MyCustomPlugin(config={"threshold": 500}),
    ],
    governance=IRGovernanceChecker(),
)
```

### Plugin Order

Plugins are applied in the order they appear in the list. Order matters when
plugins depend on each other's output. For example:

1. `ContextDigestPlugin` should run before `BudgetOptimizerPlugin` because
   budget optimization may depend on the reduced context size.
2. Custom constraint plugins should run before budget optimization if the
   constraints affect budget decisions.
3. Validation or scanning plugins can run at any position since they typically
   add metadata without changing core fields.

### Optional Governance

The `governance` parameter is optional. If set to `None`, the pipeline skips
governance checks and processes all IRs through plugins unconditionally:

```python
pipeline = PromptIRPipeline(
    plugins=[BudgetOptimizerPlugin()],
    governance=None,  # No governance checks
)
```

### Integrating with the Orchestrator

The pipeline is passed to the `Orchestrator` constructor via the `ir_pipeline`
parameter. The orchestrator automatically constructs IRs from phase data and
processes them through the pipeline before compilation:

```python
from core.orchestrator import Orchestrator

orchestrator = Orchestrator(
    config=system_config,
    agent_executor=agent_executor,
    prompt_compiler=compiler,
    ir_pipeline=pipeline,
)
```

---

## Example: SecurityScanPlugin

A plugin that detects sensitive intents and adds safety constraints.

```python
from core.prompt_ir import PromptIRPlugin, PromptIR
from typing import Any, Dict, List, Optional


class SecurityScanPlugin(PromptIRPlugin):
    """Scan IR intents for sensitive topics and add safety constraints.

    When the intent references sensitive subjects (passwords, credentials,
    personal data, etc.), this plugin appends constraints that instruct the
    agent to handle the topic safely.
    """

    # Default sensitive keywords and their corresponding constraints
    DEFAULT_SENSITIVE_PATTERNS: Dict[str, str] = {
        "password": "Never log, display, or store passwords in plain text.",
        "credential": "Handle credentials through secure storage only.",
        "secret": "Do not include secrets in code or output.",
        "api_key": "Use environment variables for API keys, never hardcode.",
        "token": "Treat authentication tokens as sensitive data.",
        "personal data": "Comply with data protection principles (minimize, encrypt, audit).",
        "credit card": "Never store or log full credit card numbers.",
        "ssn": "Never process or display Social Security Numbers.",
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.sensitive_patterns = self.config.get(
            "sensitive_patterns",
            self.DEFAULT_SENSITIVE_PATTERNS,
        )
        self.scan_count = 0
        self.flag_count = 0

    def transform(self, ir: PromptIR) -> PromptIR:
        """Scan intent for sensitive topics and add constraints."""
        self.scan_count += 1
        intent_lower = ir.intent.lower()

        # Find matching sensitive patterns
        matched_constraints: List[str] = []
        matched_keywords: List[str] = []

        for keyword, constraint in self.sensitive_patterns.items():
            if keyword.lower() in intent_lower:
                matched_constraints.append(constraint)
                matched_keywords.append(keyword)

        # Also scan existing constraints for sensitive references
        for existing in ir.constraints:
            existing_lower = existing.lower()
            for keyword, constraint in self.sensitive_patterns.items():
                if keyword.lower() in existing_lower and constraint not in matched_constraints:
                    matched_constraints.append(constraint)
                    matched_keywords.append(keyword)

        # If no sensitive topics found, return unchanged
        if not matched_constraints:
            return ir

        # Clone and add safety constraints
        self.flag_count += 1
        ir_after = ir.clone()

        for constraint in matched_constraints:
            if constraint not in ir_after.constraints:
                ir_after.constraints.append(constraint)

        # Record in metadata
        ir_after.metadata["security_scan"] = {
            "flagged": True,
            "matched_keywords": matched_keywords,
            "constraints_added": len(matched_constraints),
        }

        # Record transformation
        self._record_transformation(
            ir,
            ir_after,
            "security_scan",
            f"Flagged {len(matched_keywords)} sensitive keywords: "
            f"{', '.join(matched_keywords)}. "
            f"Added {len(matched_constraints)} safety constraints.",
        )

        return ir_after

    def get_scan_stats(self) -> Dict[str, Any]:
        """Return scanning statistics."""
        return {
            "total_scans": self.scan_count,
            "total_flags": self.flag_count,
            "flag_rate": self.flag_count / self.scan_count if self.scan_count > 0 else 0.0,
        }
```

### Usage

```python
from core.prompt_ir import PromptIRPipeline, IRGovernanceChecker, BudgetOptimizerPlugin

pipeline = PromptIRPipeline(
    plugins=[
        SecurityScanPlugin(config={
            "sensitive_patterns": {
                "password": "Never log or display passwords in plain text.",
                "database": "Use parameterized queries only.",
            },
        }),
        BudgetOptimizerPlugin(),
    ],
    governance=IRGovernanceChecker(),
)
```

---

## Example: CostCapPlugin

A plugin that enforces maximum token budgets to prevent cost overruns.

```python
from core.prompt_ir import PromptIRPlugin, PromptIR
from typing import Any, Dict, Optional


class CostCapPlugin(PromptIRPlugin):
    """Enforce maximum token budget caps.

    Ensures no IR exceeds a configured maximum token budget, regardless of
    what the BudgetOptimizerPlugin or other plugins may have set. This acts
    as a hard ceiling for cost control.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_budget = self.config.get("max_budget", 5000)
        self.warning_threshold = self.config.get("warning_threshold", 4000)
        self.cap_count = 0

    def transform(self, ir: PromptIR) -> PromptIR:
        """Cap token budget if it exceeds the maximum."""
        if ir.token_budget <= self.max_budget:
            # Within limits. Add warning if close to cap.
            if ir.token_budget > self.warning_threshold:
                ir_after = ir.clone()
                ir_after.metadata["cost_cap_warning"] = (
                    f"Budget {ir.token_budget} is within "
                    f"{self.max_budget - ir.token_budget} tokens of the cap."
                )
                self._record_transformation(
                    ir,
                    ir_after,
                    "cost_cap_warning",
                    f"Budget {ir.token_budget} approaching cap of {self.max_budget}.",
                )
                return ir_after
            return ir

        # Budget exceeds cap -- enforce the limit
        self.cap_count += 1
        ir_after = ir.clone()
        original_budget = ir.token_budget

        ir_after.token_budget = self.max_budget
        ir_after.metadata["cost_cap_applied"] = True
        ir_after.metadata["cost_cap_original_budget"] = original_budget
        ir_after.metadata["cost_cap_reduction"] = original_budget - self.max_budget

        self._record_transformation(
            ir,
            ir_after,
            "cost_cap",
            f"Capped budget from {original_budget} to {self.max_budget} "
            f"(reduced by {original_budget - self.max_budget} tokens).",
        )

        return ir_after

    def get_cap_stats(self) -> Dict[str, Any]:
        """Return capping statistics."""
        return {
            "total_caps_applied": self.cap_count,
        }
```

### Usage

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
        CostCapPlugin(config={
            "max_budget": 4000,
            "warning_threshold": 3500,
        }),
    ],
    governance=IRGovernanceChecker(),
)
```

Note that `CostCapPlugin` is placed after `BudgetOptimizerPlugin` in the
plugin list. This is intentional: the budget optimizer may increase the budget
based on phase and priority, and the cost cap plugin then enforces the hard
ceiling on the result.

---

## Testing Plugins

### Unit Testing a Plugin

Test plugins in isolation by constructing an IR, running `transform()`, and
asserting on the output.

```python
import pytest
from core.prompt_ir import PromptIRBuilder, PhaseType


class TestSecurityScanPlugin:
    """Tests for SecurityScanPlugin."""

    def test_no_sensitive_intent_returns_unchanged(self):
        """Plugin should return the original IR when no sensitive keywords found."""
        plugin = SecurityScanPlugin()
        ir = (
            PromptIRBuilder("architect", "Design a caching layer")
            .phase(PhaseType.PLANNING)
            .set_token_budget(3000)
            .build()
        )

        result = plugin.transform(ir)

        # Same object returned (not cloned) when no changes needed
        assert result.ir_id == ir.ir_id
        assert len(result.constraints) == 0
        assert "security_scan" not in result.metadata

    def test_sensitive_intent_adds_constraints(self):
        """Plugin should add safety constraints for sensitive intents."""
        plugin = SecurityScanPlugin()
        ir = (
            PromptIRBuilder("implementer", "Implement password reset flow")
            .phase(PhaseType.IMPLEMENTATION)
            .set_token_budget(3000)
            .build()
        )

        result = plugin.transform(ir)

        # New IR returned (cloned) with constraints added
        assert result.ir_id != ir.ir_id
        assert any("password" in c.lower() for c in result.constraints)
        assert result.metadata["security_scan"]["flagged"] is True
        assert "password" in result.metadata["security_scan"]["matched_keywords"]

    def test_transformation_recorded(self):
        """Plugin should record transformations for audit trail."""
        plugin = SecurityScanPlugin()
        ir = (
            PromptIRBuilder("implementer", "Store user credentials securely")
            .phase(PhaseType.IMPLEMENTATION)
            .set_token_budget(3000)
            .build()
        )

        plugin.transform(ir)

        assert len(plugin.transformations) == 1
        t = plugin.transformations[0]
        assert t.transformation_type == "security_scan"
        assert t.applied_by == "SecurityScanPlugin"
        assert t.before_hash != t.after_hash

    def test_custom_patterns(self):
        """Plugin should support custom sensitive patterns via config."""
        plugin = SecurityScanPlugin(config={
            "sensitive_patterns": {
                "database": "Use parameterized queries only.",
            },
        })
        ir = (
            PromptIRBuilder("implementer", "Query the database for user records")
            .phase(PhaseType.IMPLEMENTATION)
            .set_token_budget(3000)
            .build()
        )

        result = plugin.transform(ir)

        assert "Use parameterized queries only." in result.constraints

    def test_does_not_duplicate_constraints(self):
        """Plugin should not add a constraint that already exists."""
        plugin = SecurityScanPlugin()
        ir = (
            PromptIRBuilder("implementer", "Implement password hashing")
            .phase(PhaseType.IMPLEMENTATION)
            .add_constraint("Never log, display, or store passwords in plain text.")
            .set_token_budget(3000)
            .build()
        )

        result = plugin.transform(ir)

        password_constraints = [
            c for c in result.constraints
            if "password" in c.lower()
        ]
        # Should have exactly one, not a duplicate
        assert len(password_constraints) == 1


class TestCostCapPlugin:
    """Tests for CostCapPlugin."""

    def test_within_budget_returns_unchanged(self):
        """Plugin should not modify IR when budget is within limits."""
        plugin = CostCapPlugin(config={"max_budget": 5000, "warning_threshold": 4000})
        ir = (
            PromptIRBuilder("architect", "Design system")
            .phase(PhaseType.PLANNING)
            .set_token_budget(3000)
            .build()
        )

        result = plugin.transform(ir)

        assert result.token_budget == 3000

    def test_exceeding_budget_is_capped(self):
        """Plugin should cap the budget to max_budget when exceeded."""
        plugin = CostCapPlugin(config={"max_budget": 4000})
        ir = (
            PromptIRBuilder("researcher", "Research everything")
            .phase(PhaseType.RESEARCH)
            .set_token_budget(6000)
            .build()
        )

        result = plugin.transform(ir)

        assert result.token_budget == 4000
        assert result.metadata["cost_cap_applied"] is True
        assert result.metadata["cost_cap_original_budget"] == 6000

    def test_warning_near_cap(self):
        """Plugin should add warning metadata when budget is near cap."""
        plugin = CostCapPlugin(config={"max_budget": 5000, "warning_threshold": 4000})
        ir = (
            PromptIRBuilder("implementer", "Implement feature")
            .phase(PhaseType.IMPLEMENTATION)
            .set_token_budget(4500)
            .build()
        )

        result = plugin.transform(ir)

        assert result.token_budget == 4500  # Not capped
        assert "cost_cap_warning" in result.metadata
```

### Integration Testing with the Pipeline

Test the full pipeline to verify plugin interactions:

```python
class TestPipelineIntegration:
    """Integration tests for the IR pipeline with custom plugins."""

    def test_full_pipeline_with_custom_plugins(self):
        """Test that custom plugins work correctly in the full pipeline."""
        pipeline = PromptIRPipeline(
            plugins=[
                SecurityScanPlugin(),
                BudgetOptimizerPlugin(),
                CostCapPlugin(config={"max_budget": 4000}),
            ],
            governance=IRGovernanceChecker(),
        )

        ir = (
            PromptIRBuilder("implementer", "Implement password storage")
            .phase(PhaseType.IMPLEMENTATION)
            .set_token_budget(3000)
            .set_priority(8)
            .build()
        )

        transformed, approved, violations = pipeline.process(ir)

        assert approved is True
        assert len(violations) == 0

        # SecurityScanPlugin should have added constraints
        assert any("password" in c.lower() for c in transformed.constraints)

        # BudgetOptimizerPlugin: 3000 * 1.0 * (1 + 0.3) = 3900
        # CostCapPlugin: 3900 < 4000, so not capped
        assert transformed.token_budget == 3900

    def test_governance_denial_skips_plugins(self):
        """Test that governance denial prevents plugin execution."""
        pipeline = PromptIRPipeline(
            plugins=[SecurityScanPlugin()],
            governance=IRGovernanceChecker(),
        )

        ir = (
            PromptIRBuilder("implementer", "rm -rf everything")
            .phase(PhaseType.IMPLEMENTATION)
            .add_context_ref("file:/etc/passwd")
            .set_token_budget(3000)
            .build()
        )

        transformed, approved, violations = pipeline.process(ir)

        assert approved is False
        assert len(violations) > 0
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run only plugin tests
python -m pytest tests/test_plugins.py -v

# Run with coverage
python -m pytest tests/ --cov=core.prompt_ir --cov-report=term-missing
```

---

## Best Practices

### 1. Always Clone Before Mutating

Never modify the input IR directly. Always call `ir.clone()` to create a copy
with a new `ir_id`, then mutate the copy. This preserves the original for audit
trail comparison and prevents unintended side effects when multiple plugins
share the same IR reference.

```python
# Correct
def transform(self, ir: PromptIR) -> PromptIR:
    ir_after = ir.clone()
    ir_after.constraints.append("New constraint")
    return ir_after

# Incorrect -- mutates the input
def transform(self, ir: PromptIR) -> PromptIR:
    ir.constraints.append("New constraint")  # Modifies original
    return ir
```

### 2. Record All Transformations

Always call `self._record_transformation()` when the plugin modifies the IR.
This is essential for the audit trail and for pipeline statistics. Include a
descriptive `transformation_type` and a human-readable `description`.

```python
self._record_transformation(
    ir_before=ir,
    ir_after=ir_after,
    transformation_type="my_transform",
    description=f"Added {count} constraints for {reason}",
)
```

### 3. Return the Original IR When Unchanged

If the plugin determines that no transformation is needed, return the original
IR object directly. Do not clone it. This avoids unnecessary ID changes in the
audit trail and keeps pipeline statistics accurate.

```python
def transform(self, ir: PromptIR) -> PromptIR:
    if not self._should_transform(ir):
        return ir  # Original, not cloned
    ...
```

### 4. Handle Errors Gracefully

The pipeline catches exceptions from `transform()` and continues, but plugins
should still handle expected error cases internally. Use logging for diagnostic
information, and avoid raising exceptions for recoverable situations.

```python
import logging
logger = logging.getLogger(__name__)

def transform(self, ir: PromptIR) -> PromptIR:
    try:
        result = self._expensive_operation(ir)
    except ExternalServiceError as e:
        logger.warning("External service failed: %s. Returning IR unchanged.", e)
        return ir
    ...
```

### 5. Use Namespaced Metadata Keys

When storing data in `ir.metadata`, use a prefix specific to your plugin to
avoid key collisions with other plugins or built-in components.

```python
# Good: namespaced key
ir_after.metadata["security_scan"] = {"flagged": True}
ir_after.metadata["cost_cap_applied"] = True

# Risky: generic key that may collide
ir_after.metadata["result"] = True
ir_after.metadata["flag"] = True
```

### 6. Keep Plugins Focused

Each plugin should have a single, well-defined responsibility. If a plugin
needs to do two unrelated things, split it into two plugins. This makes plugins
easier to test, reorder, and enable/disable independently.

### 7. Document Plugin Configuration

Use the `config` dictionary for all tunable parameters. Document each
configuration key with its type, default value, and purpose. This allows users
to customize plugin behavior without modifying code.

```python
class MyPlugin(PromptIRPlugin):
    """My plugin description.

    Configuration:
        threshold (int): Minimum value to trigger transformation. Default: 100.
        strict_mode (bool): If True, raise on errors instead of skipping. Default: False.
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.threshold = self.config.get("threshold", 100)
        self.strict_mode = self.config.get("strict_mode", False)
```

### 8. Make Plugins Stateless Where Possible

Plugins are instantiated once and called for every IR in the pipeline. Avoid
storing mutable state that affects transformation logic between calls. The
`self.transformations` list is the expected exception (it accumulates audit
records across calls). If you need per-call counters or statistics, document
that the plugin is stateful.

### 9. Test Edge Cases

Write tests for:

- Empty context_refs, constraints, and metadata.
- Very large token budgets (integer overflow potential).
- Intents that match multiple patterns simultaneously.
- IRs that have already been transformed by the same plugin (idempotency).
- IRs with `ir_version` values other than `"1.0"` (forward compatibility).

### 10. Consider Plugin Order

Document whether your plugin should run before or after specific built-in
plugins. If your plugin depends on `BudgetOptimizerPlugin` having already
adjusted the budget, state this clearly and recommend placement after it in the
plugin list.
