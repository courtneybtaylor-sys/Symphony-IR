"""Deterministic state machine orchestration engine.

The orchestrator coordinates multiple AI agents through structured phases,
enforcing hard termination limits and confidence thresholds. The LLM never
decides when to stop—deterministic rules do.
"""

import json
import logging
import re
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class OrchestratorState(Enum):
    """States in the orchestration state machine."""

    INIT = "init"
    PLAN = "plan"
    EXECUTE_PHASE = "execute_phase"
    SYNTHESIZE = "synthesize"
    VALIDATE = "validate"
    TERMINATE = "terminate"
    ERROR = "error"


@dataclass
class Phase:
    """A single execution phase in the orchestration plan."""

    name: str
    agents: List[str]
    brief: str
    context: Dict[str, Any] = field(default_factory=dict)
    termination_condition: str = ""
    confidence_threshold: float = 0.85


@dataclass
class AgentResponse:
    """Response from a single agent execution."""

    agent_name: str
    role: str
    output: str
    confidence: float
    risk_flags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """A decision made by the orchestrator during execution."""

    timestamp: str
    state: str
    action: str
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunLedger:
    """Complete audit trail of an orchestration run."""

    run_id: str
    task: str
    timestamp: str
    phases: List[Phase] = field(default_factory=list)
    agent_responses: List[AgentResponse] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)
    final_output: str = ""
    confidence: float = 0.0
    state: str = OrchestratorState.INIT.value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "run_id": self.run_id,
            "task": self.task,
            "timestamp": self.timestamp,
            "phases": [
                {
                    "name": p.name,
                    "agents": p.agents,
                    "brief": p.brief,
                    "context": p.context,
                    "termination_condition": p.termination_condition,
                    "confidence_threshold": p.confidence_threshold,
                }
                for p in self.phases
            ],
            "agent_responses": [
                {
                    "agent_name": r.agent_name,
                    "role": r.role,
                    "output": r.output,
                    "confidence": r.confidence,
                    "risk_flags": r.risk_flags,
                    "metadata": r.metadata,
                }
                for r in self.agent_responses
            ],
            "decisions": [
                {
                    "timestamp": d.timestamp,
                    "state": d.state,
                    "action": d.action,
                    "reason": d.reason,
                    "details": d.details,
                }
                for d in self.decisions
            ],
            "final_output": self.final_output,
            "confidence": self.confidence,
            "state": self.state,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


class Orchestrator:
    """Deterministic multi-agent orchestration engine.

    Coordinates agents through a state machine with hard termination limits,
    confidence thresholds, and risk flag checks.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        agent_executor: Optional[Callable] = None,
        conductor_executor: Optional[Callable] = None,
        governance_checker: Optional[Callable] = None,
        prompt_compiler: Optional[Any] = None,
        schema_validator: Optional[Any] = None,
        agent_provider_resolver: Optional[Callable] = None,
    ):
        """Initialize the orchestrator.

        Args:
            config: System configuration (max_phases, confidence_threshold, etc.)
            agent_executor: Callable(agent_name, phase_brief, context) -> AgentResponse
            conductor_executor: Callable(task, context) -> List[Phase]
            governance_checker: Callable(action_type, details, context) -> GovernanceResult
            prompt_compiler: Optional PromptCompiler for token-optimized prompts
            schema_validator: Optional SchemaValidator for output format enforcement
            agent_provider_resolver: Callable(agent_name) -> str (model provider name)
        """
        config = config or {}
        self.max_phases = config.get("max_phases", 10)
        self.confidence_threshold = config.get("confidence_threshold", 0.85)
        self.enable_parallel = config.get("enable_parallel_execution", True)
        self.max_workers = config.get("max_workers", 5)

        self._agent_executor = agent_executor
        self._conductor_executor = conductor_executor
        self._governance_checker = governance_checker
        self._prompt_compiler = prompt_compiler
        self._schema_validator = schema_validator
        self._agent_provider_resolver = agent_provider_resolver

        self._state = OrchestratorState.INIT
        self._ledger: Optional[RunLedger] = None

    @property
    def state(self) -> OrchestratorState:
        return self._state

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> RunLedger:
        """Execute the full orchestration loop.

        Args:
            task: The task description to orchestrate
            context: Additional context (file system, git, etc.)

        Returns:
            Complete RunLedger with audit trail
        """
        context = context or {}
        self._state = OrchestratorState.INIT
        self._ledger = RunLedger(
            run_id=str(uuid.uuid4())[:8],
            task=task,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self._record_decision("Orchestration started", f"Task: {task[:200]}")

        try:
            # PLAN phase
            self._transition(OrchestratorState.PLAN)
            phases = self._execute_plan(task, context)
            self._ledger.phases = phases
            self._record_decision(
                "Plan created",
                f"{len(phases)} phases defined",
                {"phase_names": [p.name for p in phases]},
            )

            # Execute phases with hard limit
            phase_count = 0
            for phase in phases:
                # Hard phase limit check
                if phase_count >= self.max_phases:
                    self._record_decision(
                        "Force terminated",
                        f"Hit max phase limit ({self.max_phases})",
                    )
                    break

                # EXECUTE_PHASE
                self._transition(OrchestratorState.EXECUTE_PHASE)
                responses = self._execute_phase(phase, context)
                self._ledger.agent_responses.extend(responses)
                phase_count += 1

                self._record_decision(
                    f"Phase '{phase.name}' completed",
                    f"{len(responses)} agent responses collected",
                    {
                        "agents": [r.agent_name for r in responses],
                        "confidences": [r.confidence for r in responses],
                    },
                )

                # SYNTHESIZE
                self._transition(OrchestratorState.SYNTHESIZE)
                synthesis = self._synthesize(responses)

                # VALIDATE
                self._transition(OrchestratorState.VALIDATE)
                should_continue = self._validate(responses)

                if not should_continue:
                    self._record_decision(
                        "Validation passed",
                        "Confidence threshold met, no critical flags",
                    )

            # Final synthesis of all responses
            all_responses = self._ledger.agent_responses
            if all_responses:
                self._ledger.final_output = self._synthesize(all_responses)
                self._ledger.confidence = sum(
                    r.confidence for r in all_responses
                ) / len(all_responses)

            # Governance check on final output
            if self._governance_checker and self._ledger.final_output:
                gov_result = self._governance_checker(
                    "final_output",
                    {"output": self._ledger.final_output},
                    context,
                )
                self._record_decision(
                    "Governance check",
                    f"Decision: {gov_result.decision.value if hasattr(gov_result, 'decision') else gov_result}",
                )

            # Record compiler/validator stats if available
            if self._prompt_compiler:
                stats = self._prompt_compiler.get_compilation_stats()
                self._record_decision(
                    "Prompt compiler stats",
                    f"compilations={stats.get('total_compilations', 0)}, "
                    f"avg_tokens={stats.get('average_tokens_per_prompt', 0)}, "
                    f"compression_rate={stats.get('compression_rate', 0)}",
                    stats,
                )

            if self._schema_validator:
                stats = self._schema_validator.get_validation_stats()
                self._record_decision(
                    "Schema validator stats",
                    f"validations={stats.get('total_validations', 0)}, "
                    f"success_rate={stats.get('success_rate', 0)}, "
                    f"repair_rate={stats.get('repair_rate', 0)}",
                    stats,
                )

            # TERMINATE
            self._transition(OrchestratorState.TERMINATE)
            self._ledger.state = OrchestratorState.TERMINATE.value
            self._record_decision("Orchestration completed", "Run terminated normally")

        except Exception as e:
            self._transition(OrchestratorState.ERROR)
            self._ledger.state = OrchestratorState.ERROR.value
            self._record_decision("Error occurred", str(e))
            logger.error(f"Orchestration error: {e}", exc_info=True)

        return self._ledger

    def _execute_plan(self, task: str, context: Dict) -> List[Phase]:
        """Call the Conductor to create an execution plan."""
        if self._conductor_executor:
            return self._conductor_executor(task, context)

        # Default plan if no conductor is set
        return [
            Phase(
                name="Analysis",
                agents=["architect", "researcher"],
                brief=f"Analyze: {task}",
                termination_condition="Requirements documented",
            ),
            Phase(
                name="Implementation",
                agents=["implementer"],
                brief=f"Implement: {task}",
                termination_condition="Solution implemented",
            ),
            Phase(
                name="Review",
                agents=["reviewer", "integrator"],
                brief=f"Review and integrate: {task}",
                termination_condition="Quality validated",
            ),
        ]

    def _execute_phase(
        self, phase: Phase, context: Dict
    ) -> List[AgentResponse]:
        """Execute all agents in a phase, optionally in parallel.

        When a PromptCompiler is configured, prompts are compiled before dispatch.
        When a SchemaValidator is configured, outputs are validated after execution.
        """
        responses = []

        if not self._agent_executor:
            logger.warning("No agent executor set, returning empty responses")
            return responses

        # Compile prompts if compiler is available
        compiled_briefs = {}
        if self._prompt_compiler:
            for agent_name in phase.agents:
                try:
                    provider = "mock"
                    if self._agent_provider_resolver:
                        provider = self._agent_provider_resolver(agent_name)
                    if self._prompt_compiler.has_template(agent_name):
                        compiled = self._prompt_compiler.compile(
                            role=agent_name,
                            phase_brief=phase.brief,
                            context=context,
                            model_provider=provider,
                        )
                        compiled_briefs[agent_name] = compiled
                        self._record_decision(
                            f"Prompt compiled for {agent_name}",
                            f"tokens={compiled.estimated_tokens}, "
                            f"adapter={compiled.compilation_metadata.get('model_adapter')}",
                            compiled.compilation_metadata,
                        )
                except Exception as e:
                    logger.warning(
                        "Prompt compilation failed for %s: %s, using raw brief",
                        agent_name,
                        e,
                    )

        def _run_agent(agent_name: str) -> AgentResponse:
            """Execute a single agent with optional compiled prompt."""
            # Use compiled prompt content if available, otherwise raw brief
            brief = phase.brief
            if agent_name in compiled_briefs:
                brief = compiled_briefs[agent_name].content

            result = self._agent_executor(
                agent_name,
                brief,
                {**context, "phase": phase.name},
            )

            if isinstance(result, AgentResponse):
                response = result
            elif isinstance(result, dict):
                response = AgentResponse(
                    agent_name=result.get("agent_name", agent_name),
                    role=result.get("role", "unknown"),
                    output=result.get("output", ""),
                    confidence=result.get("confidence", 0.0),
                    risk_flags=result.get("risk_flags", []),
                    metadata=result.get("metadata", {}),
                )
            else:
                response = AgentResponse(
                    agent_name=agent_name,
                    role="unknown",
                    output=str(result),
                    confidence=0.0,
                    risk_flags=[],
                )

            # Validate output if validator and compiled schema are available
            if self._schema_validator and agent_name in compiled_briefs:
                compiled = compiled_briefs[agent_name]
                schema = compiled.output_schema
                try:
                    validation = self._schema_validator.validate(
                        output=response.output,
                        schema=schema.schema_definition,
                        format_type=schema.format_type.value,
                        role=agent_name,
                    )
                    if validation.is_valid():
                        if validation.repaired_output and validation.warnings:
                            response.metadata["schema_repaired"] = True
                            response.metadata["repair_warnings"] = validation.warnings
                    else:
                        response.metadata["schema_validation_errors"] = validation.errors
                        self._record_decision(
                            f"Schema validation failed for {agent_name}",
                            f"errors={validation.errors}",
                        )
                except Exception as e:
                    logger.warning(
                        "Schema validation failed for %s: %s", agent_name, e
                    )

            # Record compilation metadata on response
            if agent_name in compiled_briefs:
                response.metadata["compiled"] = True
                response.metadata["estimated_tokens"] = (
                    compiled_briefs[agent_name].estimated_tokens
                )

            return response

        if self.enable_parallel and len(phase.agents) > 1:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(_run_agent, agent_name): agent_name
                    for agent_name in phase.agents
                }
                for future in as_completed(futures):
                    agent_name = futures[future]
                    try:
                        responses.append(future.result())
                    except Exception as e:
                        logger.error(f"Agent {agent_name} failed: {e}")
                        responses.append(
                            AgentResponse(
                                agent_name=agent_name,
                                role="error",
                                output=f"Agent failed: {e}",
                                confidence=0.0,
                                risk_flags=["CRITICAL_agent_failure"],
                            )
                        )
        else:
            for agent_name in phase.agents:
                try:
                    responses.append(_run_agent(agent_name))
                except Exception as e:
                    logger.error(f"Agent {agent_name} failed: {e}")
                    responses.append(
                        AgentResponse(
                            agent_name=agent_name,
                            role="error",
                            output=f"Agent failed: {e}",
                            confidence=0.0,
                            risk_flags=["CRITICAL_agent_failure"],
                        )
                    )

        return responses

    def _synthesize(self, responses: List[AgentResponse]) -> str:
        """Combine agent outputs into a synthesis."""
        if not responses:
            return ""

        parts = []
        for r in responses:
            parts.append(f"[{r.agent_name} ({r.role})] confidence={r.confidence:.2f}")
            parts.append(r.output)
            if r.risk_flags:
                parts.append(f"  Risk flags: {', '.join(r.risk_flags)}")
            parts.append("")

        return "\n".join(parts)

    def _validate(self, responses: List[AgentResponse]) -> bool:
        """Deterministic validation: check confidence and risk flags.

        Returns True if execution should CONTINUE (validation failed),
        False if execution can STOP (validation passed).
        """
        if not responses:
            return False

        # Calculate aggregate confidence
        avg_confidence = sum(r.confidence for r in responses) / len(responses)

        # Check for critical risk flags
        all_flags = []
        for r in responses:
            all_flags.extend(r.risk_flags)
        critical_flags = [f for f in all_flags if f.startswith("CRITICAL")]

        # Determine if we should continue looping
        should_continue = (
            avg_confidence < self.confidence_threshold or len(critical_flags) > 0
        )

        if should_continue:
            self._record_decision(
                "Validation failed - continuing",
                f"avg_confidence={avg_confidence:.2f} "
                f"(threshold={self.confidence_threshold}), "
                f"critical_flags={critical_flags}",
            )
        else:
            self._record_decision(
                "Validation passed",
                f"avg_confidence={avg_confidence:.2f} >= {self.confidence_threshold}, "
                f"no critical flags",
            )

        return should_continue

    def _transition(self, new_state: OrchestratorState):
        """Transition the state machine to a new state."""
        old_state = self._state
        self._state = new_state
        logger.debug(f"State: {old_state.value} -> {new_state.value}")

    def _record_decision(
        self, action: str, reason: str, details: Optional[Dict] = None
    ):
        """Record a decision in the ledger."""
        if self._ledger:
            self._ledger.decisions.append(
                Decision(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    state=self._state.value,
                    action=action,
                    reason=reason,
                    details=details or {},
                )
            )

    def save_ledger(self, path: str):
        """Save the RunLedger as JSON to disk.

        Args:
            path: File path to save the JSON ledger
        """
        if self._ledger is None:
            raise RuntimeError("No ledger to save. Run orchestrator first.")

        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(self._ledger.to_json())
        logger.info(f"Ledger saved to {path}")
