"""
Input components with enhanced styling and visibility.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional, Tuple

from .base import StyledLineEdit, StyledTextEdit, StyledCheckBox, PrimaryButton, SecondaryButton, StyledLabel
from .colors import get_theme


class GradientBorderedInput(StyledLineEdit):
    """Text input with gradient border and enhanced focus effect."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()

    def _setup_styling(self):
        """Setup input styling with gradient border effect."""
        palette = self.theme.palette
        stylesheet = f"""
            QLineEdit {{
                background-color: {palette.background};
                color: {palette.text_primary};
                border: 2px solid {palette.border};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                selection-background-color: {palette.primary};
            }}
            QLineEdit:focus {{
                border: 2px solid {palette.gradient_start};
                background-color: {palette.surface};
                padding: 10px 12px;
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setMinimumHeight(36)


class VariableInputGroup(QWidget):
    """Dynamic key=value input group for environment variables."""

    variables_changed = pyqtSignal(list)  # Emitted with list of (key, value) tuples

    def __init__(self, max_variables: int = 10, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self.max_variables = max_variables
        self.variable_inputs: List[Tuple[QLineEdit, QLineEdit]] = []

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        # Title
        self.title = StyledLabel("Variables")
        self.title.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.layout.addWidget(self.title)

        # Container for variable rows
        self.variables_container = QWidget()
        self.variables_layout = QVBoxLayout()
        self.variables_layout.setContentsMargins(0, 0, 0, 0)
        self.variables_layout.setSpacing(6)
        self.variables_container.setLayout(self.variables_layout)
        self.layout.addWidget(self.variables_container)

        # Add/Remove buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)

        self.add_button = PrimaryButton("+ Add Variable")
        self.add_button.clicked.connect(self._add_variable)
        buttons_layout.addWidget(self.add_button)

        self.remove_button = SecondaryButton("- Remove Last")
        self.remove_button.clicked.connect(self._remove_variable)
        self.remove_button.setEnabled(False)
        buttons_layout.addWidget(self.remove_button)

        buttons_layout.addStretch()
        self.layout.addLayout(buttons_layout)

        self.setLayout(self.layout)

    def _add_variable(self):
        """Add a new variable input row."""
        if len(self.variable_inputs) >= self.max_variables:
            return

        # Key input
        key_input = GradientBorderedInput()
        key_input.setPlaceholderText("Variable name (e.g., MODEL)")
        key_input.textChanged.connect(self._on_variables_changed)

        # Value input
        value_input = GradientBorderedInput()
        value_input.setPlaceholderText("Value (e.g., gpt-4)")
        value_input.textChanged.connect(self._on_variables_changed)

        # Add to row layout
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)
        row_layout.addWidget(QLabel("="))
        row_layout.addWidget(key_input)
        row_layout.addWidget(QLabel("="))
        row_layout.addWidget(value_input)

        # Create container for row
        row_widget = QWidget()
        row_widget.setLayout(row_layout)
        self.variables_layout.addWidget(row_widget)

        self.variable_inputs.append((key_input, value_input))

        # Update button states
        self.remove_button.setEnabled(True)
        if len(self.variable_inputs) >= self.max_variables:
            self.add_button.setEnabled(False)

        self._on_variables_changed()

    def _remove_variable(self):
        """Remove the last variable input row."""
        if not self.variable_inputs:
            return

        key_input, value_input = self.variable_inputs.pop()

        # Remove widget from layout
        widget = key_input.parent()
        if widget:
            widget.deleteLater()

        # Update button states
        self.add_button.setEnabled(True)
        self.remove_button.setEnabled(len(self.variable_inputs) > 0)

        self._on_variables_changed()

    def _on_variables_changed(self):
        """Emit variables_changed signal."""
        variables = self.get_variables()
        self.variables_changed.emit(variables)

    def get_variables(self) -> List[Tuple[str, str]]:
        """Get current variables as list of (key, value) tuples."""
        variables = []
        for key_input, value_input in self.variable_inputs:
            key = key_input.text().strip()
            value = value_input.text().strip()
            if key:  # Only include if key is not empty
                variables.append((key, value))
        return variables

    def set_variables(self, variables: List[Tuple[str, str]]):
        """Set variables from a list of (key, value) tuples."""
        # Clear existing
        while self.variable_inputs:
            self._remove_variable()

        # Add new variables
        for key, value in variables:
            self._add_variable()
            key_input, value_input = self.variable_inputs[-1]
            key_input.setText(key)
            value_input.setText(value)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self.title.update_theme(dark_mode)
        self.add_button.update_theme(dark_mode)
        self.remove_button.update_theme(dark_mode)
        for key_input, value_input in self.variable_inputs:
            key_input.update_theme(dark_mode)
            value_input.update_theme(dark_mode)


class StyledComboBox(QComboBox):
    """Styled dropdown with enhanced visibility."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_styling()

    def _setup_styling(self):
        """Setup combo box styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QComboBox {{
                background-color: {palette.background};
                color: {palette.text_primary};
                border: 2px solid {palette.border};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QComboBox:focus {{
                border: 2px solid {palette.primary};
                background-color: {palette.surface};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                padding-right: 4px;
            }}
            QComboBox::down-arrow {{
                image: url(none);
                width: 12px;
                height: 12px;
            }}
            QListView {{
                background-color: {palette.background};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                selection-background-color: {palette.primary};
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setMinimumHeight(36)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class StyledSpinBox(QSpinBox):
    """Styled number input with enhanced visibility."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_styling()

    def _setup_styling(self):
        """Setup spin box styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QSpinBox {{
                background-color: {palette.background};
                color: {palette.text_primary};
                border: 2px solid {palette.border};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QSpinBox:focus {{
                border: 2px solid {palette.primary};
                background-color: {palette.surface};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                border: 1px solid {palette.border};
                background-color: {palette.surface};
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {palette.primary};
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setMinimumHeight(36)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()
