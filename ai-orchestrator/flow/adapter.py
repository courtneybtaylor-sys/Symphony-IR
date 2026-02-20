"""IRAdapter - Convert FlowNode to PromptIR for execution via Symphony-IR."""

from .models import FlowNode, ProjectState
from core.prompt_ir import PromptIR, PromptIRBuilder, PhaseType


class IRAdapter:
    """Translate FlowNode to PromptIR for execution.

    Handles:
    - Variable resolution ({variable} -> actual value)
    - Phase mapping (string -> PhaseType enum)
    - PromptIR construction with all fields
    - Metadata tagging for flow context
    """

    def __init__(self, project_state: ProjectState):
        """Initialize adapter with project state.

        Args:
            project_state: Current ProjectState with variables
        """
        self.state = project_state

    def from_node(self, node: FlowNode) -> PromptIR:
        """Convert FlowNode to PromptIR.

        Args:
            node: FlowNode to convert

        Returns:
            PromptIR ready for execution by Orchestra

        Resolves variables in intent, context_refs, and constraints.
        """
        # Resolve variables
        intent = self._resolve(node.intent)
        context_refs = [self._resolve(ref) for ref in node.context_refs]
        constraints = [self._resolve(c) for c in node.constraints]

        # Map phase string to enum
        phase_type = self._map_phase(node.phase)

        # Build PromptIR with all fields
        builder = PromptIRBuilder(node.role, intent)
        builder.phase(phase_type)
        builder.set_priority(node.priority)
        builder.set_token_budget(node.token_budget_hint)

        # Add context refs if any
        if context_refs:
            builder.add_context_refs(context_refs)

        # Add constraints if any
        for constraint in constraints:
            builder.add_constraint(constraint)

        # Tag with flow metadata
        builder.set_metadata("flow_node_id", node.id)
        builder.set_metadata("flow_project_id", self.state.project_id)
        builder.set_metadata("flow_template_id", self.state.template_id)

        return builder.build()

    def _resolve(self, text: str) -> str:
        """Resolve {variable} placeholders to actual values.

        Args:
            text: Text with {var} placeholders

        Returns:
            Text with variables substituted

        Example:
            {component} with variables={'component': 'auth.py'} -> 'auth.py'
        """
        try:
            return text.format(**self.state.variables)
        except KeyError as e:
            # If variable not found, return original (will fail at execution)
            return text

    def _map_phase(self, phase_str: str) -> PhaseType:
        """Map phase string to PhaseType enum.

        Args:
            phase_str: Phase name (e.g., "PLANNING", "implementation")

        Returns:
            PhaseType enum value

        Handles both uppercase and mixed case.
        """
        phase_upper = phase_str.upper()

        phase_map = {
            "PLANNING": PhaseType.PLANNING,
            "RESEARCH": PhaseType.RESEARCH,
            "IMPLEMENTATION": PhaseType.IMPLEMENTATION,
            "REVIEW": PhaseType.REVIEW,
            "SYNTHESIS": PhaseType.SYNTHESIS,
        }

        return phase_map.get(phase_upper, PhaseType.IMPLEMENTATION)
