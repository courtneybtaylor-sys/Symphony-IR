"""Prompt IR (Intermediate Representation) - Structured compiler pipeline.

This is the AST (Abstract Syntax Tree) for prompts. Transforms the system from
"string plumbing" into a real compiler pipeline with inspectable IR.

Before: Conductor -> (strings) -> Compiler -> (strings) -> Model
After:  Conductor -> PromptIR -> IR Pipeline -> Compiler -> CompiledPrompt -> Model

Why this matters:
  - Governance can inspect intent before tokens are spent
  - Plugins can mutate structured fields safely
  - Token budgeting becomes deterministic
  - Meaningful metrics per field
  - Versioned IR schemas
  - Safe extensibility
"""

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PhaseType(Enum):
    """Phase types for optimization strategies."""

    PLANNING = "planning"
    RESEARCH = "research"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    SYNTHESIS = "synthesis"


@dataclass
class PromptIR:
    """Intermediate Representation of a prompt before compilation.

    This is the structured, inspectable representation that sits between
    high-level intent and low-level compiled prompts.

    Think of this as the AST (Abstract Syntax Tree) of a prompt.
    """

    # Core identity
    role: str  # Agent role (architect, implementer, etc.)
    intent: str  # High-level objective from Conductor
    phase: PhaseType  # Execution phase

    # Context references (structured, not raw)
    context_refs: List[str]  # File IDs, diff IDs, memory block IDs

    # Constraints and requirements
    constraints: List[str]  # Must-follow rules
    output_requirements: Dict[str, Any]  # Schema requirements

    # Resource management
    token_budget: int  # Hard token limit
    priority: int = 5  # 1-10, affects budget allocation

    # Model hints (suggestions, not mandates)
    model_hint: Optional[str] = None  # Preferred model provider
    temperature_hint: float = 0.7  # Suggested temperature

    # Schema reference
    schema_id: str = "default"  # Validation schema reference

    # Versioning
    ir_version: str = "1.0"  # IR schema version

    # Metadata (extensibility point)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Tracking
    ir_id: Optional[str] = None  # Unique IR identifier
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize tracking fields."""
        if not self.ir_id:
            self.ir_id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "ir_id": self.ir_id,
            "role": self.role,
            "intent": self.intent,
            "phase": self.phase.value,
            "context_refs": self.context_refs,
            "constraints": self.constraints,
            "output_requirements": self.output_requirements,
            "token_budget": self.token_budget,
            "priority": self.priority,
            "model_hint": self.model_hint,
            "temperature_hint": self.temperature_hint,
            "schema_id": self.schema_id,
            "ir_version": self.ir_version,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptIR":
        """Deserialize from dict."""
        data = dict(data)  # shallow copy

        # Convert phase string to enum
        if isinstance(data.get("phase"), str):
            data["phase"] = PhaseType(data["phase"])

        # Convert datetime string
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        return cls(**data)

    def clone(self) -> "PromptIR":
        """Create a copy of this IR with a new IR ID."""
        data = self.to_dict()
        data["ir_id"] = None  # Will get a new ID in __post_init__
        return self.from_dict(data)


@dataclass
class IRTransformation:
    """Record of a transformation applied to an IR."""

    transformation_type: str  # e.g., "context_digest", "constraint_add"
    description: str  # What changed
    before_hash: str  # IR hash before
    after_hash: str  # IR hash after
    applied_by: str  # Plugin/module name
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize."""
        return {
            "transformation_type": self.transformation_type,
            "description": self.description,
            "before_hash": self.before_hash,
            "after_hash": self.after_hash,
            "applied_by": self.applied_by,
            "timestamp": self.timestamp.isoformat(),
        }


class PromptIRBuilder:
    """Fluent builder for constructing PromptIR.

    Makes IR construction clean and explicit.
    """

    def __init__(self, role: str, intent: str):
        self._role = role
        self._intent = intent
        self._phase = PhaseType.IMPLEMENTATION
        self._context_refs: List[str] = []
        self._constraints: List[str] = []
        self._output_requirements: Dict[str, Any] = {}
        self._token_budget = 3000
        self._priority = 5
        self._model_hint: Optional[str] = None
        self._temperature_hint = 0.7
        self._schema_id = "default"
        self._metadata: Dict[str, Any] = {}

    def phase(self, phase: PhaseType) -> "PromptIRBuilder":
        """Set execution phase."""
        self._phase = phase
        return self

    def add_context_ref(self, ref: str) -> "PromptIRBuilder":
        """Add context reference."""
        self._context_refs.append(ref)
        return self

    def add_context_refs(self, refs: List[str]) -> "PromptIRBuilder":
        """Add multiple context references."""
        self._context_refs.extend(refs)
        return self

    def add_constraint(self, constraint: str) -> "PromptIRBuilder":
        """Add constraint."""
        self._constraints.append(constraint)
        return self

    def set_output_requirements(
        self, requirements: Dict[str, Any]
    ) -> "PromptIRBuilder":
        """Set output requirements."""
        self._output_requirements = requirements
        return self

    def set_token_budget(self, budget: int) -> "PromptIRBuilder":
        """Set token budget."""
        self._token_budget = budget
        return self

    def set_priority(self, priority: int) -> "PromptIRBuilder":
        """Set priority (1-10)."""
        assert 1 <= priority <= 10, "Priority must be 1-10"
        self._priority = priority
        return self

    def set_model_hint(self, model: str) -> "PromptIRBuilder":
        """Set model hint."""
        self._model_hint = model
        return self

    def set_temperature_hint(self, temperature: float) -> "PromptIRBuilder":
        """Set temperature hint."""
        self._temperature_hint = temperature
        return self

    def set_schema_id(self, schema_id: str) -> "PromptIRBuilder":
        """Set schema ID."""
        self._schema_id = schema_id
        return self

    def set_metadata(self, key: str, value: Any) -> "PromptIRBuilder":
        """Set metadata field."""
        self._metadata[key] = value
        return self

    def build(self) -> PromptIR:
        """Construct the PromptIR."""
        return PromptIR(
            role=self._role,
            intent=self._intent,
            phase=self._phase,
            context_refs=self._context_refs,
            constraints=self._constraints,
            output_requirements=self._output_requirements,
            token_budget=self._token_budget,
            priority=self._priority,
            model_hint=self._model_hint,
            temperature_hint=self._temperature_hint,
            schema_id=self._schema_id,
            metadata=self._metadata,
        )


class PromptIRPlugin:
    """Base class for IR transformation plugins.

    Plugins can safely mutate IR before compilation.
    This is the extensibility point.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.transformations: List[IRTransformation] = []

    def transform(self, ir: PromptIR) -> PromptIR:
        """Transform the IR.

        Must return a (possibly modified) PromptIR.
        Should not have side effects.
        """
        raise NotImplementedError

    def _record_transformation(
        self,
        ir_before: PromptIR,
        ir_after: PromptIR,
        transformation_type: str,
        description: str,
    ):
        """Record transformation for audit trail."""
        transformation = IRTransformation(
            transformation_type=transformation_type,
            description=description,
            before_hash=self._hash_ir(ir_before),
            after_hash=self._hash_ir(ir_after),
            applied_by=self.__class__.__name__,
        )
        self.transformations.append(transformation)

    def _hash_ir(self, ir: PromptIR) -> str:
        """Generate hash of IR state."""
        content = json.dumps(ir.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class ContextDigestPlugin(PromptIRPlugin):
    """Dual-stage compression plugin.

    If context references exceed max_context_refs, compresses them
    into a digest. In production, uses a cheap model to summarize.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_context_refs = self.config.get("max_context_refs", 10)
        self.cheap_model = self.config.get("cheap_model")

    def transform(self, ir: PromptIR) -> PromptIR:
        """Apply context digest if needed."""
        if len(ir.context_refs) <= self.max_context_refs:
            return ir

        # Clone IR
        ir_before = ir
        ir_after = ir.clone()

        # Create digest
        digest = self._create_digest(ir.context_refs, ir.intent)

        # Store original refs in metadata
        ir_after.metadata["original_context_refs"] = ir.context_refs.copy()
        ir_after.metadata["context_digest"] = digest

        # Replace refs with digest marker
        ir_after.context_refs = ["__CONTEXT_DIGEST__"]

        # Record transformation
        self._record_transformation(
            ir_before,
            ir_after,
            "context_digest",
            f"Compressed {len(ir.context_refs)} refs into digest",
        )

        return ir_after

    def _create_digest(self, context_refs: List[str], intent: str) -> str:
        """Create context digest.

        In production, this would use a cheap model to summarize.
        """
        if self.cheap_model:
            # Production path: use cheap model for summarization
            try:
                from models.client import Message

                messages = [
                    Message(
                        role="user",
                        content=(
                            f"Summarize these context references for the task: {intent}\n"
                            f"References: {', '.join(context_refs)}"
                        ),
                    )
                ]
                response = self.cheap_model.call(messages)
                return response.content
            except Exception as e:
                logger.warning("Cheap model digest failed: %s", e)

        # Fallback: simple summary
        return f"Context summary: {len(context_refs)} files related to: {intent}"


class BudgetOptimizerPlugin(PromptIRPlugin):
    """Adjust token budgets based on priority and phase."""

    PHASE_MULTIPLIERS = {
        PhaseType.PLANNING: 1.2,
        PhaseType.RESEARCH: 1.3,
        PhaseType.IMPLEMENTATION: 1.0,
        PhaseType.REVIEW: 0.8,
        PhaseType.SYNTHESIS: 1.1,
    }

    def transform(self, ir: PromptIR) -> PromptIR:
        """Optimize budget allocation."""
        ir_after = ir.clone()
        original_budget = ir.token_budget

        # Phase-based adjustment
        multiplier = self.PHASE_MULTIPLIERS.get(ir.phase, 1.0)

        # Priority-based adjustment (-0.4 to +0.5)
        priority_bonus = (ir.priority - 5) * 0.1

        # Calculate new budget
        adjusted_budget = int(original_budget * multiplier * (1 + priority_bonus))

        ir_after.token_budget = adjusted_budget
        ir_after.metadata["original_budget"] = original_budget
        ir_after.metadata["budget_multiplier"] = multiplier

        self._record_transformation(
            ir,
            ir_after,
            "budget_optimization",
            f"Adjusted budget: {original_budget} -> {adjusted_budget}",
        )

        return ir_after


class IRGovernanceChecker:
    """Governance layer for PromptIR.

    Inspects IR before compilation to enforce policies.
    Cost-efficient governance: check intent before spending tokens.
    """

    def __init__(self, policies: Optional[List[Dict[str, Any]]] = None):
        self.policies = policies or self._default_policies()
        self.violations_log: List[Dict[str, Any]] = []

    def _default_policies(self) -> List[Dict[str, Any]]:
        """Default governance policies."""
        return [
            {
                "name": "protected_paths",
                "type": "context_ref",
                "forbidden_patterns": ["/sys/", "/etc/", "C:\\Windows\\System32\\"],
                "action": "deny",
            },
            {
                "name": "destructive_actions",
                "type": "intent",
                "forbidden_keywords": ["delete all", "drop database", "rm -rf"],
                "action": "flag",
            },
            {
                "name": "sensitive_constraints",
                "type": "constraint",
                "forbidden_keywords": ["ignore policy", "bypass", "override"],
                "action": "deny",
            },
        ]

    def check(self, ir: PromptIR) -> Tuple[bool, List[str]]:
        """Check IR against policies.

        Returns: (approved, violations)
        """
        violations = []

        for policy in self.policies:
            policy_violations = self._check_policy(ir, policy)
            violations.extend(policy_violations)

        # Log check
        self._log_check(ir, violations)

        # Determine if approved
        has_deny = any("DENY" in v for v in violations)
        approved = not has_deny

        return approved, violations

    def _check_policy(self, ir: PromptIR, policy: Dict[str, Any]) -> List[str]:
        """Check a single policy."""
        violations = []
        policy_name = policy["name"]
        policy_type = policy["type"]
        action = policy["action"].upper()

        if policy_type == "context_ref":
            forbidden = policy.get("forbidden_patterns", [])
            for ref in ir.context_refs:
                for pattern in forbidden:
                    if pattern in ref:
                        violations.append(
                            f"{action}: {policy_name} - "
                            f"Context ref '{ref}' matches forbidden pattern '{pattern}'"
                        )

        elif policy_type == "intent":
            forbidden = policy.get("forbidden_keywords", [])
            intent_lower = ir.intent.lower()
            for keyword in forbidden:
                if keyword.lower() in intent_lower:
                    violations.append(
                        f"{action}: {policy_name} - "
                        f"Intent contains forbidden keyword '{keyword}'"
                    )

        elif policy_type == "constraint":
            forbidden = policy.get("forbidden_keywords", [])
            for constraint in ir.constraints:
                constraint_lower = constraint.lower()
                for keyword in forbidden:
                    if keyword.lower() in constraint_lower:
                        violations.append(
                            f"{action}: {policy_name} - "
                            f"Constraint contains forbidden keyword '{keyword}'"
                        )

        return violations

    def _log_check(self, ir: PromptIR, violations: List[str]):
        """Log governance check."""
        self.violations_log.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ir_id": ir.ir_id,
                "role": ir.role,
                "violations": violations,
                "approved": len([v for v in violations if "DENY" in v]) == 0,
            }
        )

    def get_violations_report(self) -> Dict[str, Any]:
        """Get violations report."""
        if not self.violations_log:
            return {
                "total_checks": 0,
                "approved": 0,
                "denied": 0,
                "approval_rate": 1.0,
                "recent_violations": [],
            }

        total_checks = len(self.violations_log)
        denied = sum(1 for log in self.violations_log if not log["approved"])

        return {
            "total_checks": total_checks,
            "approved": total_checks - denied,
            "denied": denied,
            "approval_rate": (total_checks - denied) / total_checks,
            "recent_violations": self.violations_log[-10:],
        }


class PromptIRPipeline:
    """Pipeline for transforming PromptIR through plugins.

    This is the extensibility framework:
    1. Governance check (free - before tokens spent)
    2. Plugin transformations (structured, auditable)
    3. Output: transformed IR ready for compilation
    """

    def __init__(
        self,
        plugins: Optional[List[PromptIRPlugin]] = None,
        governance: Optional[IRGovernanceChecker] = None,
    ):
        self.plugins = plugins or []
        self.governance = governance
        self.pipeline_log: List[Dict[str, Any]] = []

    def process(self, ir: PromptIR) -> Tuple[PromptIR, bool, List[str]]:
        """Process IR through pipeline.

        Returns: (transformed_ir, approved, violations)
        """
        # Governance check first (free - no tokens spent)
        if self.governance:
            approved, violations = self.governance.check(ir)
            if not approved:
                return ir, False, violations
        else:
            approved = True
            violations = []

        # Apply plugins
        current_ir = ir
        transformations = []

        for plugin in self.plugins:
            try:
                transformed_ir = plugin.transform(current_ir)

                # Record plugin transformations
                if plugin.transformations:
                    transformations.extend(
                        [t.to_dict() for t in plugin.transformations]
                    )

                current_ir = transformed_ir

            except Exception as e:
                # Plugin failed - log but continue
                self._log_plugin_error(plugin, current_ir, e)

        # Log pipeline execution
        self._log_pipeline_run(ir, current_ir, transformations, approved, violations)

        return current_ir, approved, violations

    def _log_plugin_error(
        self, plugin: PromptIRPlugin, ir: PromptIR, error: Exception
    ):
        """Log plugin error."""
        logger.warning(
            "Plugin %s failed on IR %s: %s",
            plugin.__class__.__name__,
            ir.ir_id,
            error,
        )

    def _log_pipeline_run(
        self,
        ir_before: PromptIR,
        ir_after: PromptIR,
        transformations: List[Dict[str, Any]],
        approved: bool,
        violations: List[str],
    ):
        """Log pipeline run."""
        self.pipeline_log.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ir_id_before": ir_before.ir_id,
                "ir_id_after": ir_after.ir_id,
                "transformations": transformations,
                "approved": approved,
                "violations": violations,
            }
        )

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        if not self.pipeline_log:
            return {
                "total_runs": 0,
                "total_transformations": 0,
                "avg_transformations_per_run": 0,
            }

        total_runs = len(self.pipeline_log)
        total_transformations = sum(
            len(log["transformations"]) for log in self.pipeline_log
        )

        return {
            "total_runs": total_runs,
            "total_transformations": total_transformations,
            "avg_transformations_per_run": total_transformations / total_runs,
        }
