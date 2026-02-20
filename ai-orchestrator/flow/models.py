"""Data models for Symphony Flow - Bounded decision tree workflows."""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict


@dataclass
class FlowOption:
    """A single option in a flow node.

    Represents a bounded choice (A, B, C, D) that leads to the next node.
    """

    id: str  # "A", "B", "C", "D"
    label: str  # "Design architecture"
    description: str  # Brief explanation of what this choice does
    next_node_id: str  # ID of the next node to navigate to


@dataclass
class FlowNode:
    """A single node in the flow decision tree.

    Each node represents a step in the workflow with 2-4 bounded choices.
    Nodes are mapped to PromptIR for execution through Symphony-IR.
    """

    id: str  # Node identifier (e.g., "start", "design", "review")
    summary: str  # Human-readable summary of what this step does

    # PromptIR mapping fields
    role: str  # "architect", "implementer", "reviewer", etc.
    intent: str  # High-level objective, may contain {variable} placeholders
    phase: str  # "PLANNING", "IMPLEMENTATION", "REVIEW", "RESEARCH", "SYNTHESIS"
    priority: int  # 1-10 priority level
    context_refs: List[str] = field(default_factory=list)  # ["file:{component}"]
    constraints: List[str] = field(default_factory=list)  # Output constraints
    token_budget_hint: int = 3000  # Suggested token limit for execution

    # Navigation
    options: List[FlowOption] = field(default_factory=list)  # Possible choices
    parent_id: Optional[str] = None  # Parent node ID (root has None)


@dataclass
class ProjectState:
    """Tracks the state of a flow execution (project session).

    Persists user choices, node ledger IDs, and variables throughout
    the workflow lifetime.
    """

    project_id: str  # Unique project identifier
    template_id: str  # Which template is being used
    current_node_id: str  # Current node in the decision tree
    selected_path: List[str] = field(default_factory=list)  # Node IDs visited
    decisions: List[str] = field(default_factory=list)  # Option IDs chosen
    node_ledger_ids: Dict[str, str] = field(default_factory=dict)  # node_id -> ledger_id
    variables: Dict[str, str] = field(default_factory=dict)  # User-provided context

    def to_json(self) -> str:
        """Serialize state to JSON string."""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "ProjectState":
        """Deserialize state from JSON string."""
        data = json.loads(json_str)
        return cls(**data)
