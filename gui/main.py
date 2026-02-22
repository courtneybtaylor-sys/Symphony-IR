# Copyright 2024 Kheper LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Symphony-IR Desktop Application — entry point.

Launch with:
    python gui/main.py
or (from the gui/ directory):
    python main.py

PyInstaller target:
    gui/main.py  (see windows/build.py)
"""

from __future__ import annotations

import logging
import sys
import webbrowser
from pathlib import Path

# Ensure gui/ is on sys.path so sub-packages resolve correctly whether this
# file is run as a script or via PyInstaller.
_GUI_DIR = Path(__file__).parent
if str(_GUI_DIR) not in sys.path:
    sys.path.insert(0, str(_GUI_DIR))

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QAction
from PyQt6.QtCore import QTimer

from version import VERSION, APP_NAME, ORG_NAME
from widgets import TabPanel, set_dark_mode, get_theme
from services.credential_service import CredentialService
from services.error_service import setup_file_logging
from tabs.orchestrator_tab import OrchestratorTab
from tabs.flow_tab import FlowTab
from tabs.history_tab import HistoryTab
from tabs.settings_tab import SettingsTab
from setup_wizard import SetupWizard, should_run_setup_wizard

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path.home() / "Symphony-IR"


# ─────────────────────────────────────────────────────────────────────────────
# Main window
# ─────────────────────────────────────────────────────────────────────────────

class SymphonyIRApp(QMainWindow):
    """Top-level application window with theme support and modern UI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"🎼 Symphony-IR  {VERSION}")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)

        # Get theme manager for later use
        self.theme = get_theme()

        # Create custom tab widget with enhanced styling
        self.tabs = TabPanel()

        # Add tabs with emoji icons
        self.tabs.addTab(OrchestratorTab(PROJECT_ROOT), "🎼  Orchestrator")
        self.tabs.addTab(FlowTab(PROJECT_ROOT),          "🗺️  Symphony Flow")
        self.tabs.addTab(HistoryTab(PROJECT_ROOT),       "📋  History")
        self.tabs.addTab(SettingsTab(PROJECT_ROOT),       "⚙️  Settings")

        self.setCentralWidget(self.tabs)

        self._build_menus()
        self._apply_theme()

        keyring_status = (
            "🔐 keyring available — keys encrypted"
            if CredentialService.available()
            else "⚠️  keyring not installed — run:  pip install keyring"
        )
        self.statusBar().showMessage(
            f"Symphony-IR {VERSION}  ·  {keyring_status}"
        )

    def _apply_theme(self):
        """Apply current theme to application."""
        palette = self.theme.palette
        stylesheet = f"""
            QMainWindow, QDialog {{
                background-color: {palette.background};
                color: {palette.text_primary};
            }}

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

            QGroupBox {{
                border: 1px solid {palette.border};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: {palette.surface};
                color: {palette.text_primary};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: {palette.primary};
                font-weight: bold;
            }}

            QTableWidget {{
                gridline-color: {palette.border};
                background-color: {palette.background};
                alternate-background-color: {palette.surface};
                color: {palette.text_primary};
            }}

            QHeaderView::section {{
                background-color: {palette.primary};
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }}

            QStatusBar {{
                background-color: {palette.surface};
                border-top: 1px solid {palette.border};
                color: {palette.text_primary};
            }}

            QMessageBox {{
                background-color: {palette.background};
                color: {palette.text_primary};
            }}

            QMessageBox QLabel {{
                color: {palette.text_primary};
            }}

            QMessageBox QPushButton {{
                min-width: 60px;
            }}
        """
        self.setStyleSheet(stylesheet)

    def _build_menus(self):
        """Build application menu bar."""
        mb = self.menuBar()

        # File menu
        fm = mb.addMenu("File")
        qa = QAction("Quit", self)
        qa.triggered.connect(self.close)
        fm.addAction(qa)

        # View menu - for theme control
        vm = mb.addMenu("View")
        dark_mode_action = QAction("Dark Mode", self, checkable=True)
        dark_mode_action.setChecked(self.theme.dark_mode)
        dark_mode_action.triggered.connect(self._toggle_dark_mode)
        vm.addAction(dark_mode_action)

        # Help menu
        hm = mb.addMenu("Help")
        _gh = "https://github.com/courtneybtaylor-sys/Symphony-IR"
        for label, url in [
            ("Online Documentation",     f"{_gh}#readme"),
            ("Set up Ollama (Local AI)", "https://ollama.ai"),
            ("Security Guide",           f"{_gh}/blob/main/docs/SECURITY.md"),
            ("Report an Issue",          f"{_gh}/issues"),
        ]:
            a = QAction(label, self)
            a.triggered.connect(lambda _, u=url: webbrowser.open(u))
            hm.addAction(a)

        hm.addSeparator()
        about_a = QAction("About Symphony-IR", self)
        about_a.triggered.connect(self._about)
        hm.addAction(about_a)

    def _toggle_dark_mode(self, checked: bool):
        """Toggle dark mode."""
        set_dark_mode(checked)
        self._apply_theme()

    def _about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, f"About Symphony-IR {VERSION}",
            f"Symphony-IR  {VERSION}\n"
            "Deterministic multi-agent AI orchestration\n\n"
            "Design: Deterministic Elegance™\n"
            "  • Gradient borders (Cyan → Purple)\n"
            "  • Glassmorphism effects\n"
            "  • Smooth animations\n"
            "  • Light/Dark theme support\n\n"
            "Security:\n"
            "  🔐  API keys → system Credential Manager\n"
            "  📋  Sessions → auto-redacted before display\n"
            "  💬  Errors  → plain English + actionable suggestions\n\n"
            "github.com/courtneybtaylor-sys/Symphony-IR"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # File logging — full stack traces go here; users see friendly summaries.
    log_file = setup_file_logging(PROJECT_ROOT)
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)-8s %(name)s — %(message)s",
    )
    logger.info("Symphony-IR %s starting  (log: %s)", VERSION, log_file)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setOrganizationName(ORG_NAME)

    # Show setup wizard on first run
    if should_run_setup_wizard():
        logger.info("First run detected — showing setup wizard")
        wizard = SetupWizard()
        wizard_result = wizard.exec()
        logger.info("Setup wizard completed (result: %s)", wizard_result)

    window = SymphonyIRApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
