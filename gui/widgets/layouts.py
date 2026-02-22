"""
Layout and container components for responsive UI design.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QTabWidget,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Callable

from .colors import get_theme
from .base import StyledLabel


class SplitViewPanel(QWidget):
    """Responsive split-view panel (45% left, 55% right)."""

    def __init__(
        self,
        left_title: str = "Left",
        right_title: str = "Right",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.theme = get_theme()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Splitter for resizable split
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStretchFactor(0, 45)
        self.splitter.setStretchFactor(1, 55)

        # Left panel
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        left_header = StyledLabel(left_title)
        left_header.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px;")
        self.left_layout.addWidget(left_header)

        self.left_content = QWidget()
        self.left_content_layout = QVBoxLayout()
        self.left_content_layout.setContentsMargins(0, 0, 0, 0)
        self.left_content.setLayout(self.left_content_layout)
        self.left_layout.addWidget(self.left_content)

        self.left_panel.setLayout(self.left_layout)
        self.splitter.addWidget(self.left_panel)

        # Right panel
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        right_header = StyledLabel(right_title)
        right_header.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px;")
        self.right_layout.addWidget(right_header)

        self.right_content = QWidget()
        self.right_content_layout = QVBoxLayout()
        self.right_content_layout.setContentsMargins(0, 0, 0, 0)
        self.right_content.setLayout(self.right_content_layout)
        self.right_layout.addWidget(self.right_content)

        self.right_panel.setLayout(self.right_layout)
        self.splitter.addWidget(self.right_panel)

        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

    def add_left_widget(self, widget: QWidget):
        """Add widget to left panel."""
        self.left_content_layout.addWidget(widget)

    def add_right_widget(self, widget: QWidget):
        """Add widget to right panel."""
        self.right_content_layout.addWidget(widget)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)


class TabPanel(QTabWidget):
    """Custom tab widget with enhanced styling."""

    tab_changed = pyqtSignal(int)  # Emitted when tab changes

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self._setup_styling()
        self.currentChanged.connect(self._on_tab_changed)

    def _setup_styling(self):
        """Setup tab widget styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QTabWidget::pane {{
                border: 1px solid {palette.border};
                border-radius: 6px;
            }}
            QTabBar::tab {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 13px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {palette.primary};
                color: white;
                border-color: {palette.primary};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {palette.primary};
                opacity: 0.7;
            }}
        """
        self.setStyleSheet(stylesheet)

    def _on_tab_changed(self, index: int):
        """Handle tab change."""
        self.tab_changed.emit(index)

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class CollapsibleSection(QWidget):
    """Collapsible/accordion section for grouping related controls."""

    toggled = pyqtSignal(bool)  # Emitted when collapsed/expanded

    def __init__(
        self,
        title: str = "Section",
        is_expanded: bool = True,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.theme = get_theme()
        self.is_expanded = is_expanded
        self.title_text = title

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Header button
        self.header_button = QPushButton()
        self.header_button.setFlat(True)
        self.header_button.setCheckable(True)
        self.header_button.setChecked(is_expanded)
        self.header_button.clicked.connect(self._toggle_expanded)
        self._update_header_text()
        self.layout.addWidget(self.header_button)

        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(12, 8, 12, 8)
        self.content_layout.setSpacing(8)
        self.content_widget.setLayout(self.content_layout)
        self.content_widget.setVisible(is_expanded)
        self.layout.addWidget(self.content_widget)

        self.setLayout(self.layout)
        self._setup_styling()

    def _setup_styling(self):
        """Setup styling."""
        palette = self.theme.palette
        stylesheet = f"""
            QPushButton {{
                text-align: left;
                padding: 8px 12px;
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {palette.surface_variant};
            }}
            QPushButton:pressed {{
                background-color: {palette.primary};
                color: white;
            }}
        """
        self.header_button.setStyleSheet(stylesheet)

    def _update_header_text(self):
        """Update header text with expand/collapse indicator."""
        indicator = "▼" if self.is_expanded else "▶"
        self.header_button.setText(f"{indicator}  {self.title_text}")

    def _toggle_expanded(self):
        """Toggle expanded state."""
        self.is_expanded = not self.is_expanded
        self.content_widget.setVisible(self.is_expanded)
        self._update_header_text()
        self.toggled.emit(self.is_expanded)

    def add_widget(self, widget: QWidget):
        """Add widget to content area."""
        self.content_layout.addWidget(widget)

    def set_title(self, title: str):
        """Update section title."""
        self.title_text = title
        self._update_header_text()

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
        self._setup_styling()


class ResponsiveGrid(QWidget):
    """Responsive grid layout (adapts columns based on width)."""

    def __init__(self, columns: int = 2, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_theme()
        self.columns = columns
        self.widgets: list[QWidget] = []

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)

        # Create column layouts
        self.column_layouts: list[QVBoxLayout] = []
        for _ in range(columns):
            col_layout = QVBoxLayout()
            col_layout.setContentsMargins(0, 0, 0, 0)
            col_layout.setSpacing(12)
            self.column_layouts.append(col_layout)

            # Wrap in widget for column
            col_widget = QWidget()
            col_widget.setLayout(col_layout)
            self.layout.addWidget(col_widget)

        self.setLayout(self.layout)

    def add_widget(self, widget: QWidget, column: Optional[int] = None):
        """Add widget to a column.

        Args:
            widget: Widget to add
            column: Column index (auto-distributes if None)
        """
        if column is None:
            # Auto-distribute: add to column with fewest widgets
            column = min(range(self.columns), key=lambda i: len([w for w, c in zip(self.widgets, [j for j in range(len(self.widgets))])]))

        self.column_layouts[column].addWidget(widget)
        self.widgets.append(widget)

    def add_stretch(self, column: int):
        """Add stretch to a column."""
        self.column_layouts[column].addStretch()

    def update_theme(self, dark_mode: bool):
        """Update theme."""
        self.theme.set_dark_mode(dark_mode)
