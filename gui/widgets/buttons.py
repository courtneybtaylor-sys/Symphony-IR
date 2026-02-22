"""
Button components with enhanced styling and animations.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Optional, Callable

from .base import PrimaryButton, SecondaryButton, DangerButton
from .colors import get_theme


class SuccessButton(PrimaryButton):
    """Green success button for confirmation actions."""

    def _setup_styling(self):
        """Setup success button styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QPushButton {{
                background-color: {palette.success};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {palette.success};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {palette.success};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {palette.text_secondary};
                color: {palette.text_secondary};
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setMinimumHeight(36)
        self.setMinimumWidth(80)


class WarningButton(PrimaryButton):
    """Amber warning button for cautious actions."""

    def _setup_styling(self):
        """Setup warning button styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QPushButton {{
                background-color: {palette.warning};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {palette.warning};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {palette.warning};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {palette.text_secondary};
                color: {palette.text_secondary};
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setMinimumHeight(36)
        self.setMinimumWidth(80)


class CopyButton(PrimaryButton):
    """Button that shows "Copied!" feedback after click."""

    copied = pyqtSignal()  # Emitted when copy is successful

    def __init__(self, text: str = "Copy", parent: Optional[QWidget] = None, on_copy: Optional[Callable] = None):
        super().__init__(text, parent)
        self.original_text = text
        self.on_copy = on_copy
        self.clicked.connect(self._handle_click)

    def _handle_click(self):
        """Handle copy button click."""
        if self.on_copy:
            try:
                self.on_copy()
                self._show_copied_feedback()
            except Exception as e:
                # Fallback: still show feedback even if copy fails
                self._show_copied_feedback()
        else:
            self._show_copied_feedback()

    def _show_copied_feedback(self):
        """Show 'Copied!' feedback and restore after 2 seconds."""
        self.setText("✓ Copied!")
        self.setDisabled(True)

        # Use a simple timer callback instead of Qt Timer for simplicity
        from PyQt6.QtCore import QTimer
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._restore_button())
        timer.start(2000)

    def _restore_button(self):
        """Restore button to original state."""
        self.setText(self.original_text)
        self.setDisabled(False)
        self.copied.emit()


class IconButton(SecondaryButton):
    """Small icon-only button with minimal styling."""

    def __init__(self, icon_text: str = "", parent: Optional[QWidget] = None):
        super().__init__(icon_text, parent)
        self.setMaximumWidth(36)
        self.setMinimumHeight(32)
        self.setMinimumWidth(32)

    def _setup_styling(self):
        """Setup icon button styling - more compact."""
        palette = self.theme.palette
        stylesheet = f"""
            QPushButton {{
                background-color: transparent;
                color: {palette.primary};
                border: none;
                border-radius: 4px;
                padding: 4px;
                font-weight: bold;
                font-size: 14px;
                min-width: 32px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {palette.surface_variant};
            }}
            QPushButton:pressed {{
                background-color: {palette.primary};
                color: white;
            }}
        """
        self.setStyleSheet(stylesheet)


class ToggleButton(SecondaryButton):
    """Button that toggles between two states."""

    toggled = pyqtSignal(bool)  # Emitted when state changes

    def __init__(
        self,
        on_text: str = "ON",
        off_text: str = "OFF",
        initial_state: bool = False,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(off_text, parent)
        self.on_text = on_text
        self.off_text = off_text
        self.is_on = initial_state
        self.clicked.connect(self._toggle)
        self._update_appearance()

    def _toggle(self):
        """Toggle the state."""
        self.is_on = not self.is_on
        self._update_appearance()
        self.toggled.emit(self.is_on)

    def _update_appearance(self):
        """Update button appearance based on state."""
        palette = self.theme.palette
        if self.is_on:
            self.setText(self.on_text)
            stylesheet = f"""
                QPushButton {{
                    background-color: {palette.success};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {palette.success};
                    opacity: 0.9;
                }}
            """
        else:
            self.setText(self.off_text)
            stylesheet = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {palette.error};
                    border: 2px solid {palette.error};
                    border-radius: 6px;
                    padding: 6px 14px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {palette.error};
                    color: white;
                }}
            """
        self.setStyleSheet(stylesheet)

    def set_state(self, state: bool):
        """Set button state without emitting signal."""
        self.is_on = state
        self._update_appearance()

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._update_appearance()
