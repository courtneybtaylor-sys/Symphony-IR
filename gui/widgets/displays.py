"""
Display components for logs, status, and metrics visualization.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QTextEdit, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QTextCursor, QFont, QSyntaxHighlighter, QTextDocument
from PyQt6.QtCore import Qt, QTimer
from typing import Optional
import json
import re

from .base import StyledTextEdit, StyledLabel
from .colors import get_theme


class SyntaxHighlightedLog(StyledTextEdit):
    """Text editor with syntax highlighting for logs and code output."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self.setReadOnly(True)
        self.setFont(QFont("Courier New", 11))
        self._setup_styling()

    def _setup_styling(self):
        """Setup log viewer styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QTextEdit {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: 2px solid {palette.border};
                border-radius: 6px;
                padding: 8px 12px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }}
        """
        self.setStyleSheet(stylesheet)

    def append_log(self, text: str, level: str = "info"):
        """Append colored log text based on level.

        Args:
            text: Log message
            level: Log level ('info', 'success', 'warning', 'error', 'debug')
        """
        palette = self.theme.palette
        colors = {
            'info': palette.info,
            'success': palette.success,
            'warning': palette.warning,
            'error': palette.error,
            'debug': palette.text_secondary,
        }
        color = colors.get(level, palette.text_primary)

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Add timestamp prefix
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}] "

        # Format: [timestamp] [LEVEL] message
        full_text = f"{prefix}[{level.upper()}] {text}\n"

        # Create format with color
        fmt = cursor.charFormat()
        fmt.setForeground(self.theme.get_color('text_secondary') if level == 'debug' else self.theme.get_color(level if level in palette.__dict__ else 'info'))

        cursor.setCharFormat(fmt)
        cursor.insertText(full_text)

        # Auto-scroll to bottom
        self.ensureCursorVisible()

    def clear_logs(self):
        """Clear all log content."""
        self.clear()

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class StatusBadge(QWidget):
    """Badge showing status with semantic coloring."""

    def __init__(
        self,
        status: str = "idle",  # 'idle', 'running', 'success', 'error', 'warning'
        text: str = "Status",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.theme = get_theme()
        self.status = status
        self.text = text

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Status indicator (colored dot)
        self.indicator = QLabel("●")
        self.indicator.setMaximumWidth(20)
        self.layout.addWidget(self.indicator)

        # Status text
        self.label = StyledLabel(text)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)
        self._update_appearance()

    def set_status(self, status: str, text: Optional[str] = None):
        """Update status."""
        self.status = status
        if text:
            self.text = text
            self.label.setText(text)
        self._update_appearance()

    def _update_appearance(self):
        """Update appearance based on status."""
        palette = self.theme.palette
        colors = {
            'idle': palette.text_secondary,
            'running': palette.info,
            'success': palette.success,
            'error': palette.error,
            'warning': palette.warning,
        }
        color = colors.get(self.status, palette.text_secondary)

        # Update indicator color
        self.indicator.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 16px;
            }}
        """)

        # Update label color
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                font-size: 13px;
            }}
        """)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self.label.update_theme(dark_mode)
        self._update_appearance()


class JsonViewer(StyledTextEdit):
    """JSON viewer with formatting and syntax coloring."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self.setReadOnly(True)

    def set_json(self, json_data):
        """Display formatted JSON.

        Args:
            json_data: dict, list, or JSON string
        """
        try:
            if isinstance(json_data, str):
                parsed = json.loads(json_data)
            else:
                parsed = json_data

            formatted = json.dumps(parsed, indent=2, default=str)
            self.setText(formatted)
        except Exception as e:
            self.setText(f"Error parsing JSON:\n{str(e)}")

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class ProgressCard(QWidget):
    """Card showing progress with status indicator."""

    def __init__(
        self,
        title: str = "Progress",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.theme = get_theme()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        # Title with status
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.title = StyledLabel(title)
        self.title.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(self.title)

        self.status_badge = StatusBadge("idle", "Idle")
        title_layout.addStretch()
        title_layout.addWidget(self.status_badge)

        self.layout.addLayout(title_layout)

        # Progress text
        self.progress_label = StyledLabel("0%")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 16px;
                color: {self.theme.palette.primary};
            }}
        """)
        self.layout.addWidget(self.progress_label)

        self.setLayout(self.layout)

    def set_progress(self, percentage: int, status: str = "running"):
        """Update progress.

        Args:
            percentage: Progress percentage (0-100)
            status: Current status ('idle', 'running', 'success', 'error')
        """
        self.progress_label.setText(f"{max(0, min(100, percentage))}%")
        self.status_badge.set_status(status)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self.title.update_theme(dark_mode)
        self.status_badge.update_theme(dark_mode)
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 16px;
                color: {self.theme.palette.primary};
            }}
        """)


class HeaderLabel(StyledLabel):
    """Large bold header label."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 16px;
                color: {self.theme.palette.text_primary};
            }}
        """)


class SubtitleLabel(StyledLabel):
    """Smaller, secondary text label."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {self.theme.palette.text_secondary};
            }}
        """)
