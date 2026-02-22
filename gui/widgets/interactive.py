"""
Interactive components for user decision-making and feedback.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Optional, List, Callable, Dict, Any

from .colors import get_theme
from .base import StyledLabel, PrimaryButton, SecondaryButton
from .displays import StatusBadge, HeaderLabel, SubtitleLabel


class InteractiveFlowTree(QWidget):
    """Visual tree navigation with bounded choices (2-4 options per step)."""

    option_selected = pyqtSignal(str)  # Emitted when an option is selected
    navigation_changed = pyqtSignal(list)  # Emitted with breadcrumb path

    def __init__(
        self,
        nodes: Optional[Dict[str, Dict[str, Any]]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.theme = get_theme()
        self.nodes = nodes or {}
        self.current_node_id = "root"
        self.navigation_path: List[str] = ["root"]

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(12)

        # Breadcrumb navigation
        self.breadcrumb = QLabel()
        self.breadcrumb.setStyleSheet(f"""
            QLabel {{
                color: {self.theme.palette.text_secondary};
                font-size: 11px;
            }}
        """)
        self.layout.addWidget(self.breadcrumb)

        # Current node description
        self.description = SubtitleLabel()
        self.layout.addWidget(self.description)

        # Options container
        self.options_container = QWidget()
        self.options_layout = QVBoxLayout()
        self.options_layout.setContentsMargins(0, 8, 0, 0)
        self.options_layout.setSpacing(8)
        self.options_container.setLayout(self.options_layout)
        self.layout.addWidget(self.options_container)

        self.layout.addStretch()

        self.setLayout(self.layout)
        self._render_current_node()

    def set_nodes(self, nodes: Dict[str, Dict[str, Any]]):
        """Set tree structure.

        Expected format:
        {
            "root": {
                "title": "Choose a task type",
                "description": "What would you like to do?",
                "options": [
                    {"label": "Option 1", "target": "node_id_1"},
                    {"label": "Option 2", "target": "node_id_2"},
                ]
            },
            "node_id_1": {...},
            ...
        }
        """
        self.nodes = nodes
        self._render_current_node()

    def _render_current_node(self):
        """Render the current node and its options."""
        if self.current_node_id not in self.nodes:
            self.description.setText("Node not found")
            return

        node = self.nodes[self.current_node_id]

        # Update description
        description_text = node.get("description", "")
        self.description.setText(description_text)

        # Clear previous options
        for i in reversed(range(self.options_layout.count())):
            self.options_layout.itemAt(i).widget().deleteLater()

        # Render options (max 4)
        options = node.get("options", [])[:4]
        for opt in options:
            btn = PrimaryButton(opt.get("label", "Option"))
            target_id = opt.get("target")
            btn.clicked.connect(lambda checked, tid=target_id: self._navigate_to(tid))
            self.options_layout.addWidget(btn)

        # Update breadcrumb
        self._update_breadcrumb()

    def _navigate_to(self, node_id: str):
        """Navigate to a node."""
        if node_id in self.nodes:
            self.current_node_id = node_id
            self.navigation_path.append(node_id)
            self._render_current_node()
            self.option_selected.emit(node_id)

    def _update_breadcrumb(self):
        """Update breadcrumb display."""
        breadcrumb_text = " > ".join(self.navigation_path)
        self.breadcrumb.setText(f"Path: {breadcrumb_text}")
        self.navigation_changed.emit(self.navigation_path)

    def navigate_back(self):
        """Navigate back to previous node."""
        if len(self.navigation_path) > 1:
            self.navigation_path.pop()
            self.current_node_id = self.navigation_path[-1]
            self._render_current_node()

    def reset(self):
        """Reset to root node."""
        self.navigation_path = ["root"]
        self.current_node_id = "root"
        self._render_current_node()

    def get_path(self) -> List[str]:
        """Get current navigation path."""
        return self.navigation_path

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)


class Breadcrumb(QWidget):
    """Breadcrumb navigation bar."""

    item_selected = pyqtSignal(int)  # Emitted with breadcrumb index

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self.items: List[str] = []

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)

    def set_items(self, items: List[str]):
        """Set breadcrumb items."""
        self.items = items

        # Clear layout
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().deleteLater()

        # Add items
        for idx, item in enumerate(items):
            # Item button
            btn = QPushButton(item)
            btn.setFlat(True)
            btn.clicked.connect(lambda checked, i=idx: self.item_selected.emit(i))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.theme.palette.primary};
                    border: none;
                    padding: 4px 8px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    text-decoration: underline;
                }}
            """)
            self.layout.addWidget(btn)

            # Separator (except after last item)
            if idx < len(items) - 1:
                sep = QLabel(" > ")
                sep.setStyleSheet(f"""
                    QLabel {{
                        color: {self.theme.palette.text_secondary};
                        padding: 0 4px;
                    }}
                """)
                self.layout.addWidget(sep)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)


class ProgressIndicator(QWidget):
    """Multi-step progress indicator showing current phase."""

    def __init__(
        self,
        steps: List[str],
        current_step: int = 0,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.theme = get_theme()
        self.steps = steps
        self.current_step = current_step

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        # Title
        self.title = HeaderLabel("Progress")
        self.layout.addWidget(self.title)

        # Steps
        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout()
        self.steps_layout.setContentsMargins(0, 0, 0, 0)
        self.steps_layout.setSpacing(4)
        self.steps_container.setLayout(self.steps_layout)
        self.layout.addWidget(self.steps_container)

        self._render_steps()
        self.setLayout(self.layout)

    def _render_steps(self):
        """Render progress steps."""
        # Clear
        for i in reversed(range(self.steps_layout.count())):
            self.steps_layout.itemAt(i).widget().deleteLater()

        # Add steps
        for idx, step in enumerate(self.steps):
            is_current = idx == self.current_step
            is_completed = idx < self.current_step

            palette = self.theme.palette
            if is_completed:
                color = palette.success
                prefix = "✓"
            elif is_current:
                color = palette.info
                prefix = "●"
            else:
                color = palette.text_secondary
                prefix = "○"

            step_label = QLabel(f"{prefix} {step}")
            step_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-weight: {"bold" if is_current else "normal"};
                    font-size: 13px;
                    padding: 4px 0;
                }}
            """)
            self.steps_layout.addWidget(step_label)

    def set_current_step(self, step_index: int):
        """Update current step."""
        self.current_step = max(0, min(step_index, len(self.steps) - 1))
        self._render_steps()

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self.title.update_theme(dark_mode)
        self._render_steps()
