"""
Card and panel components with gradient borders and glassmorphism.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from typing import Optional

from .base import GradientBorder, GlassmorphicPanel, StyledLabel
from .colors import get_theme


class GradientCard(QWidget):
    """Premium card with gradient border (cyan → purple) and glassmorphism."""

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.theme = get_theme()
        self.title_text = title
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Create gradient border frame
        self.border_frame = GradientBorder()
        self.border_layout = QVBoxLayout()
        self.border_layout.setContentsMargins(0, 0, 0, 0)

        # Add title if provided
        if title:
            self.title_label = StyledLabel(title)
            self.title_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 14px;
                    margin-bottom: 8px;
                }
            """)
            self.border_layout.addWidget(self.title_label)

        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(12, 8, 12, 12)
        self.content_layout.setSpacing(8)
        self.content_widget.setLayout(self.content_layout)
        self.border_layout.addWidget(self.content_widget)

        self.border_frame.setLayout(self.border_layout)
        self.layout.addWidget(self.border_frame)
        self.setLayout(self.layout)

    def add_widget(self, widget: QWidget):
        """Add a widget to the card's content area."""
        self.content_layout.addWidget(widget)

    def set_title(self, title: str):
        """Update card title."""
        self.title_text = title
        if hasattr(self, 'title_label'):
            self.title_label.setText(title)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self.border_frame.update_theme(dark_mode)
        if hasattr(self, 'title_label'):
            self.title_label.update_theme(dark_mode)


class GlassmorphicCard(QWidget):
    """Card with glassmorphism effect (semi-transparent panel)."""

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.theme = get_theme()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Glassmorphic panel
        self.panel = GlassmorphicPanel()
        self.panel_layout = QVBoxLayout()
        self.panel_layout.setContentsMargins(16, 12, 16, 12)
        self.panel_layout.setSpacing(12)

        # Add title if provided
        if title:
            self.title_label = StyledLabel(title)
            self.title_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            self.panel_layout.addWidget(self.title_label)

        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.content_widget.setLayout(self.content_layout)
        self.panel_layout.addWidget(self.content_widget)

        self.panel.setLayout(self.panel_layout)
        self.layout.addWidget(self.panel)
        self.setLayout(self.layout)

    def add_widget(self, widget: QWidget):
        """Add a widget to the card's content area."""
        self.content_layout.addWidget(widget)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self.panel.update_theme(dark_mode)
        if hasattr(self, 'title_label'):
            self.title_label.update_theme(dark_mode)


class MetricsCard(QWidget):
    """Card displaying a large metric number with label."""

    def __init__(
        self,
        label: str = "",
        value: str = "0",
        unit: str = "",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.theme = get_theme()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)

        # Use gradient card as base
        self.card = GradientCard(label)
        self.card_layout = self.card.content_layout

        # Metric value display
        self.value_label = QLabel(value)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {self.theme.palette.primary};
            }}
        """)
        self.card_layout.addWidget(self.value_label)

        # Unit label (optional)
        if unit:
            self.unit_label = QLabel(unit)
            self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.unit_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 12px;
                    color: {self.theme.palette.text_secondary};
                }}
            """)
            self.card_layout.addWidget(self.unit_label)

        self.layout.addWidget(self.card)
        self.setLayout(self.layout)

    def set_value(self, value: str):
        """Update metric value."""
        self.value_label.setText(value)

    def set_label(self, label: str):
        """Update metric label."""
        self.card.set_title(label)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self.card.update_theme(dark_mode)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {self.theme.palette.primary};
            }}
        """)
        if hasattr(self, 'unit_label'):
            self.unit_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 12px;
                    color: {self.theme.palette.text_secondary};
                }}
            """)


class StatusCard(GradientCard):
    """Card showing status with semantic coloring."""

    def __init__(
        self,
        title: str = "",
        status: str = "idle",  # 'idle', 'running', 'success', 'error', 'warning'
        parent: Optional[QWidget] = None,
    ):
        super().__init__(title, parent)
        self.status = status
        self._update_status_styling()

    def set_status(self, status: str):
        """Update status and styling."""
        self.status = status
        self._update_status_styling()

    def _update_status_styling(self):
        """Update card styling based on status."""
        palette = self.theme.palette
        colors = {
            'idle': palette.text_secondary,
            'running': palette.info,
            'success': palette.success,
            'error': palette.error,
            'warning': palette.warning,
        }
        border_color = colors.get(self.status, palette.border)

        # Update border frame styling with status color
        stylesheet = f"""
            QFrame {{
                border: 2px solid {border_color};
                border-radius: 8px;
                background-color: {palette.surface};
                padding: 12px;
            }}
        """
        self.border_frame.setStyleSheet(stylesheet)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        super().update_theme(dark_mode)
        self._update_status_styling()
