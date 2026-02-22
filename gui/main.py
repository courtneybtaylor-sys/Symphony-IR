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

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTabWidget
from PyQt6.QtGui import QAction

from version import VERSION, APP_NAME, ORG_NAME
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
# Application stylesheet
# ─────────────────────────────────────────────────────────────────────────────

_STYLESHEET = """
QMainWindow, QDialog { background: #F5F5F5; }

QTabBar::tab {
    background: #E0E0E0; padding: 8px 22px;
    margin-right: 2px; border-radius: 4px 4px 0 0;
}
QTabBar::tab:selected { background: #1565C0; color: white; }
QTabBar::tab:hover:!selected { background: #BBDEFB; }

QGroupBox {
    border: 1px solid #CFD8DC; border-radius: 6px;
    margin-top: 12px; padding-top: 10px; background: white;
}
QGroupBox::title {
    subcontrol-origin: margin; left: 10px; padding: 0 4px;
    color: #1565C0; font-weight: bold;
}

QPushButton {
    background: #1976D2; color: white; border: none;
    border-radius: 4px; padding: 8px 16px; font-weight: bold;
}
QPushButton:hover   { background: #1565C0; }
QPushButton:pressed { background: #0D47A1; }
QPushButton:disabled { background: #B0BEC5; color: #ECEFF1; }

QLineEdit, QTextEdit, QComboBox, QSpinBox {
    border: 1px solid #B0BEC5; border-radius: 4px;
    padding: 5px 7px; background: white;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border-color: #1976D2; }

QTableWidget {
    gridline-color: #ECEFF1; background: white;
    alternate-background-color: #F5F5F5;
}
QHeaderView::section {
    background: #1565C0; color: white;
    padding: 6px; border: none; font-weight: bold;
}

QProgressBar { border: 1px solid #B0BEC5; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background: #1976D2; border-radius: 4px; }

QStatusBar { background: #ECEFF1; border-top: 1px solid #CFD8DC; color: #546E7A; }
"""


# ─────────────────────────────────────────────────────────────────────────────
# Main window
# ─────────────────────────────────────────────────────────────────────────────

class SymphonyIRApp(QMainWindow):
    """Top-level application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Symphony-IR  {VERSION}  —  AI Orchestrator")
        self.setGeometry(100, 100, 1260, 820)
        self.setMinimumSize(900, 600)

        tabs = QTabWidget()
        tabs.addTab(OrchestratorTab(PROJECT_ROOT), "🎼  Orchestrator")
        tabs.addTab(FlowTab(PROJECT_ROOT),          "🗺️  Symphony Flow")
        tabs.addTab(HistoryTab(PROJECT_ROOT),       "📋  History")
        tabs.addTab(SettingsTab(PROJECT_ROOT),       "⚙️  Settings")
        self.setCentralWidget(tabs)

        self._build_menus()
        self.setStyleSheet(_STYLESHEET)

        keyring_status = (
            "🔐 keyring available — keys encrypted"
            if CredentialService.available()
            else "⚠️  keyring not installed — run:  pip install keyring"
        )
        self.statusBar().showMessage(
            f"Symphony-IR {VERSION}  ·  {keyring_status}"
        )

    def _build_menus(self):
        mb = self.menuBar()

        fm = mb.addMenu("File")
        qa = QAction("Quit", self)
        qa.triggered.connect(self.close)
        fm.addAction(qa)

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

    def _about(self):
        QMessageBox.about(
            self, f"About Symphony-IR {VERSION}",
            f"Symphony-IR  {VERSION}\n"
            "Deterministic multi-agent AI orchestration\n\n"
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
