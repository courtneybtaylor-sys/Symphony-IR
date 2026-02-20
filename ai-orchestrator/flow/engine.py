"""BranchEngine - State machine for guided flow execution.

The engine loads templates, tracks state, and navigates the decision tree.
It does NOT execute prompts, calculate tokens, or handle governance -
that's delegated to Symphony-IR's orchestrator.
"""

import yaml
import uuid
from pathlib import Path
from typing import Dict, Optional

from .models import FlowNode, FlowOption, ProjectState


class BranchEngine:
    """State machine for guided, bounded decision-tree execution.

    Responsibilities:
    - Load YAML templates into a node graph
    - Track current position and history
    - Navigate based on option selections
    - Persist state to JSON

    Does NOT:
    - Execute prompts (delegated to Orchestrator)
    - Calculate tokens (delegated to PromptCompiler)
    - Check governance (delegated to governance layer)
    """

    def __init__(self, template_path: str):
        """Initialize engine with a YAML template.

        Args:
            template_path: Path to YAML template file
        """
        self.template_path = template_path
        self.nodes: Dict[str, FlowNode] = {}
        self.template_id = ""
        self.state: ProjectState

        self._load_template()
        root_id = self._find_root_id()

        # Initialize state
        self.state = ProjectState(
            project_id=str(uuid.uuid4())[:8],
            template_id=self.template_id,
            current_node_id=root_id,
            selected_path=[root_id],
            decisions=[],
            node_ledger_ids={},
            variables={},
        )

    def _load_template(self):
        """Load YAML template and build node index."""
        with open(self.template_path) as f:
            data = yaml.safe_load(f)

        self.template_id = data.get("template_id", "unknown")

        # Build nodes from template
        for node_id, node_data in data.get("nodes", {}).items():
            options = [
                FlowOption(
                    id=opt["id"],
                    label=opt["label"],
                    description=opt.get("description", ""),
                    next_node_id=opt["next_node_id"],
                )
                for opt in node_data.get("options", [])
            ]

            self.nodes[node_id] = FlowNode(
                id=node_id,
                summary=node_data.get("summary", ""),
                role=node_data.get("role", "assistant"),
                intent=node_data.get("intent", ""),
                phase=node_data.get("phase", "IMPLEMENTATION"),
                priority=node_data.get("priority", 5),
                context_refs=node_data.get("context_refs", []),
                constraints=node_data.get("constraints", []),
                token_budget_hint=node_data.get("token_budget_hint", 3000),
                options=options,
                parent_id=node_data.get("parent_id"),
            )

    def _find_root_id(self) -> str:
        """Find root node (node with no parent).

        Returns first node without parent_id, or first node in dict.
        """
        for node_id, node in self.nodes.items():
            if node.parent_id is None:
                return node_id

        # Fallback: return first node
        return list(self.nodes.keys())[0] if self.nodes else "start"

    def get_current_node(self) -> FlowNode:
        """Get the current node."""
        return self.nodes[self.state.current_node_id]

    def select_option(self, option_id: str) -> FlowNode:
        """Navigate to next node based on option selection.

        Args:
            option_id: Option ID (e.g., "A", "B", "C")

        Returns:
            The next FlowNode

        Raises:
            ValueError: If option_id is invalid
        """
        current = self.get_current_node()
        option = None

        for opt in current.options:
            if opt.id == option_id:
                option = opt
                break

        if not option:
            valid_ids = [o.id for o in current.options]
            raise ValueError(
                f"Invalid option '{option_id}'. Valid options: {valid_ids}"
            )

        next_node = self.nodes[option.next_node_id]

        # Update state
        self.state.selected_path.append(next_node.id)
        self.state.decisions.append(option_id)
        self.state.current_node_id = next_node.id

        return next_node

    def record_execution(self, node_id: str, ledger_id: str):
        """Record result of executing a node via Symphony-IR.

        Args:
            node_id: Node that was executed
            ledger_id: RunLedger ID from orchestrator
        """
        self.state.node_ledger_ids[node_id] = ledger_id

    def save_state(self, filepath: str):
        """Save project state to JSON file.

        Args:
            filepath: Path to save JSON to
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(self.state.to_json())

    @classmethod
    def load_state(
        cls, filepath: str, template_path: str
    ) -> "BranchEngine":
        """Load engine with previously saved state.

        Args:
            filepath: Path to saved JSON state
            template_path: Path to YAML template (for reference)

        Returns:
            BranchEngine with restored state
        """
        engine = cls(template_path)

        with open(filepath) as f:
            engine.state = ProjectState.from_json(f.read())

        return engine

    def is_terminal(self) -> bool:
        """Check if current node is a terminal node (no options)."""
        return len(self.get_current_node().options) == 0

    def get_path_summary(self) -> str:
        """Get human-readable summary of path taken.

        Returns:
            String describing nodes visited and options chosen
        """
        lines = []
        for i, (node_id, option_id) in enumerate(
            zip(self.state.selected_path[:-1], self.state.decisions)
        ):
            node = self.nodes.get(node_id)
            if node:
                lines.append(f"{i+1}. {node.summary} -> {option_id}")

        return "\n".join(lines)
