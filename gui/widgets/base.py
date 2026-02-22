"""
Base styled widgets and mixins for Symphony-IR desktop GUI.

Provides foundation classes for consistent theming and styling across all custom components.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QCheckBox,
    QLabel,
    QFrame,
)
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtCore import Qt
from typing import Optional

from .colors import get_theme, ColorPalette
from .animations import LiftButtonAnimation, ANIMATION_PRESETS


class StyledWidget(QWidget):
    """Base widget with consistent styling and theming."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_styling()

    def _setup_styling(self):
        """Setup base styling. Override in subclasses."""
        pass

    def update_theme(self, dark_mode: bool):
        """Update widget theme on dark mode change."""
        self.theme.set_dark_mode(dark_mode)
        self._update_colors()

    def _update_colors(self):
        """Update colors after theme change. Override in subclasses."""
        pass


class PrimaryButton(QPushButton):
    """Primary action button with lift-on-hover animation."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.theme = get_theme()
        self._setup_styling()
        LiftButtonAnimation.apply_lift_animation(self, **ANIMATION_PRESETS['button_hover'])

    def _setup_styling(self):
        """Setup primary button styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QPushButton {{
                background-color: {palette.primary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {palette.primary_dark};
            }}
            QPushButton:pressed {{
                background-color: {palette.primary_dark};
            }}
            QPushButton:disabled {{
                background-color: {palette.text_secondary};
                color: {palette.text_secondary};
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setMinimumHeight(36)
        self.setMinimumWidth(80)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class SecondaryButton(QPushButton):
    """Secondary action button (outlined style)."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.theme = get_theme()
        self._setup_styling()
        LiftButtonAnimation.apply_lift_animation(self, **ANIMATION_PRESETS['button_hover'])

    def _setup_styling(self):
        """Setup secondary button styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QPushButton {{
                background-color: transparent;
                color: {palette.primary};
                border: 2px solid {palette.primary};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {palette.primary};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {palette.primary_dark};
                border-color: {palette.primary_dark};
                color: white;
            }}
            QPushButton:disabled {{
                border-color: {palette.border};
                color: {palette.text_secondary};
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setMinimumHeight(36)
        self.setMinimumWidth(80)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class DangerButton(QPushButton):
    """Danger/destructive action button (red)."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.theme = get_theme()
        self._setup_styling()
        LiftButtonAnimation.apply_lift_animation(self, **ANIMATION_PRESETS['button_hover'])

    def _setup_styling(self):
        """Setup danger button styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QPushButton {{
                background-color: {palette.error};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {palette.error};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {palette.error};
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

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class StyledLineEdit(QLineEdit):
    """Styled text input with focus effects."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_styling()

    def _setup_styling(self):
        """Setup text input styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QLineEdit {{
                background-color: {palette.background};
                color: {palette.text_primary};
                border: 2px solid {palette.border};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: {palette.primary};
            }}
            QLineEdit:focus {{
                border: 2px solid {palette.primary};
                background-color: {palette.surface};
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setMinimumHeight(36)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class StyledTextEdit(QTextEdit):
    """Styled multi-line text input with focus effects."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_styling()

    def _setup_styling(self):
        """Setup text edit styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QTextEdit {{
                background-color: {palette.background};
                color: {palette.text_primary};
                border: 2px solid {palette.border};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: {palette.primary};
            }}
            QTextEdit:focus {{
                border: 2px solid {palette.primary};
                background-color: {palette.surface};
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setMinimumHeight(60)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class StyledCheckBox(QCheckBox):
    """Styled checkbox with enhanced visibility."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.theme = get_theme()
        self._setup_styling()

    def _setup_styling(self):
        """Setup checkbox styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QCheckBox {{
                color: {palette.text_primary};
                spacing: 8px;
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {palette.border};
                border-radius: 4px;
                background-color: {palette.background};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {palette.primary};
            }}
            QCheckBox::indicator:checked {{
                background-color: {palette.primary};
                border: 2px solid {palette.primary};
                image: url(none);
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setMinimumHeight(32)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class StyledLabel(QLabel):
    """Styled label with semantic coloring."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None, semantic_color: Optional[str] = None):
        super().__init__(text, parent)
        self.theme = get_theme()
        self.semantic_color = semantic_color  # 'primary', 'success', 'warning', 'error', 'info', or None
        self._setup_styling()

    def _setup_styling(self):
        """Setup label styling."""
        palette = self.theme.palette

        if self.semantic_color:
            color = getattr(palette, self.semantic_color, palette.text_primary)
        else:
            color = palette.text_primary

        stylesheet = f"""
            QLabel {{
                color: {color};
                font-size: 13px;
            }}
        """
        self.setStyleSheet(stylesheet)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class GradientBorder(QFrame):
    """Frame with gradient border effect (cyan → purple)."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._setup_styling()

    def _setup_styling(self):
        """Setup gradient border styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QFrame {{
                border: 2px solid;
                border-color: {palette.gradient_start};
                border-radius: 8px;
                background-color: {palette.surface};
                padding: 12px;
            }}
        """
        self.setStyleSheet(stylesheet)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class GlassmorphicPanel(QFrame):
    """Panel with glassmorphism effect (semi-transparent with blur)."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._setup_styling()

    def _setup_styling(self):
        """Setup glassmorphism styling."""
        palette = self.theme.palette
        # Note: true blur effect requires shader/composition, but we can simulate with opacity
        stylesheet = f"""
            QFrame {{
                background-color: rgba({self._hex_to_rgb(palette.surface)}, 0.8);
                border: 1px solid {palette.border_light};
                border-radius: 12px;
                padding: 12px;
            }}
        """
        self.setStyleSheet(stylesheet)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB format for rgba()."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r},{g},{b}"

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()
