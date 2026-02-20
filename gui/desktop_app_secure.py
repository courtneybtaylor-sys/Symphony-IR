"""
Symphony-IR Desktop Application - SECURE VERSION
Modern PyQt6 GUI with security and user-friendly errors
No terminal commands needed - everything through GUI

Key Security Features:
1. API keys stored in Windows Credential Manager (never plaintext)
2. Sessions automatically redacted before saving
3. User-friendly error messages with actionable suggestions
"""

import sys
import json
import subprocess
import threading
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QSpinBox, QCheckBox, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QProgressBar, QStatusBar, QMenuBar, QMenu, QDialog, QListWidget, QListWidgetItem,
    QSplitter, QGroupBox, QFormLayout, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QIcon, QColor, QFont, QAction

# Import security modules
from secure_credentials import SecureConfig, CredentialManager
from session_redaction import SessionRedactor, RedactionLevel
from user_friendly_errors import (
    ErrorHandler, ErrorTranslator, get_api_key_error,
    get_ollama_not_running_error
)

logger = logging.getLogger(__name__)


class SecureOrchestratorWorker(QThread):
    """Run orchestrator tasks with security and error handling."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(dict)  # Now emits dict with friendly error info

    def __init__(
        self,
        task: str,
        command_type: str = "run",
        config: SecureConfig = None,
        **kwargs
    ):
        super().__init__()
        self.task = task
        self.command_type = command_type
        self.config = config
        self.kwargs = kwargs

    def run(self):
        try:
            project_root = Path.home() / "Symphony-IR"
            os_cmd = []

            # Get API key from secure storage
            api_key = self.config.get_api_key() if self.config else None

            if self.command_type == "run":
                os_cmd = [
                    sys.executable, "-m", "orchestrator.orchestrator",
                    "run", self.task,
                    "--project", str(project_root)
                ]

            elif self.command_type == "flow":
                template = self.kwargs.get("template", "code_review")
                variables = self.kwargs.get("variables", {})
                os_cmd = [
                    sys.executable, "-m", "orchestrator.orchestrator",
                    "flow", "--template", template,
                    "--project", str(project_root)
                ]
                for key, val in variables.items():
                    os_cmd.extend(["--var", f"{key}={val}"])

            elif self.command_type == "status":
                os_cmd = [
                    sys.executable, "-m", "orchestrator.orchestrator",
                    "status", "--project", str(project_root)
                ]

            elif self.command_type == "history":
                os_cmd = [
                    sys.executable, "-m", "orchestrator.orchestrator",
                    "history", "--limit", "20",
                    "--project", str(project_root)
                ]

            # Set environment variables with secure credentials
            env = os.environ.copy()
            if api_key:
                env["ANTHROPIC_API_KEY"] = api_key
            if self.config:
                env["OLLAMA_BASE_URL"] = self.config.get_ollama_url()

            self.progress.emit("Starting orchestrator...")

            process = subprocess.Popen(
                os_cmd,
                cwd=str(project_root / "ai-orchestrator"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                # Translate error to user-friendly message
                user_error = ErrorTranslator.translate(stderr)
                self.error.emit(user_error.to_dict())
                return

            # Redact output before returning
            redacted_output = SessionRedactor.redact_text(stdout)

            self.finished.emit({
                "success": True,
                "output": redacted_output,
                "command_type": self.command_type
            })

        except Exception as e:
            user_error = ErrorHandler.handle_error(e, "OrchestratorWorker")
            self.error.emit(user_error.to_dict())


class SecureSettingsTab(QWidget):
    """Settings tab with secure credential storage."""

    def __init__(self):
        super().__init__()
        self.config = None
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()

        # API Configuration
        api_group = QGroupBox("🔐 API Configuration (Secure)")
        api_layout = QFormLayout()

        # Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Claude (Cloud)", "Ollama (Local)", "OpenAI"])
        api_layout.addRow("AI Model Provider:", self.provider_combo)

        # API Key (secure input)
        key_layout = QHBoxLayout()
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("sk-... (encrypted in Windows Credential Manager)")

        # Show/hide button
        show_key_btn = QPushButton("👁️")
        show_key_btn.setMaximumWidth(40)
        show_key_btn.clicked.connect(self.toggle_api_key_visibility)
        self.show_key = False

        key_layout.addWidget(self.api_key)
        key_layout.addWidget(show_key_btn)

        api_layout.addRow("API Key:", key_layout)

        # Security info
        security_info = QLabel(
            "🔒 Your API key is encrypted and stored securely.\n"
            "It will never be saved to configuration files."
        )
        security_info.setStyleSheet("color: #4CAF50; font-size: 10px;")
        api_layout.addRow("Security:", security_info)

        # Ollama configuration
        self.ollama_url = QLineEdit()
        self.ollama_url.setText("http://localhost:11434")
        api_layout.addRow("Ollama URL:", self.ollama_url)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Model Selection
        model_group = QGroupBox("🤖 Model Selection")
        model_layout = QFormLayout()

        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "Claude Sonnet 4 (Recommended)",
            "Claude 3.5 Opus",
            "Llama 2 (Local)",
            "Mistral (Local - Recommended)",
            "Dolphin Mixtral (Local)"
        ])
        model_layout.addRow("Model:", self.model_combo)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # Orchestrator Settings
        settings_group = QGroupBox("⚙️ Orchestrator Settings")
        settings_layout = QFormLayout()

        self.max_phases = QSpinBox()
        self.max_phases.setMinimum(1)
        self.max_phases.setMaximum(100)
        self.max_phases.setValue(10)
        settings_layout.addRow("Max Phases:", self.max_phases)

        self.confidence_threshold = QSpinBox()
        self.confidence_threshold.setMinimum(0)
        self.confidence_threshold.setMaximum(100)
        self.confidence_threshold.setValue(85)
        self.confidence_threshold.setSuffix("%")
        settings_layout.addRow("Confidence Threshold:", self.confidence_threshold)

        self.parallel_execution = QCheckBox("Enable parallel execution")
        self.parallel_execution.setChecked(True)
        settings_layout.addRow(self.parallel_execution)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        reset_btn = QPushButton("⚙️ Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        migrate_btn = QPushButton("🔄 Migrate Credentials")
        migrate_btn.clicked.connect(self.migrate_credentials)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(migrate_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addStretch()
        self.setLayout(layout)

    def toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        self.show_key = not self.show_key
        if self.show_key:
            self.api_key.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key.setEchoMode(QLineEdit.EchoMode.Password)

    def load_settings(self):
        """Load settings from secure storage."""
        try:
            project_root = Path.home() / "Symphony-IR"
            self.config = SecureConfig(project_root / ".orchestrator" / "config.json")

            # Check if keyring is available
            if not CredentialManager.is_available():
                QMessageBox.warning(
                    self,
                    "⚠️ Secure Storage Not Available",
                    "Keyring library not installed. API keys may not be stored securely.\n\n"
                    "Install with: pip install keyring"
                )

            # Load from secure storage
            api_key = self.config.get_api_key()
            if api_key:
                self.api_key.setText(api_key)

            self.provider_combo.setCurrentText(
                self.config.get("provider", "Claude (Cloud)")
            )
            self.ollama_url.setText(self.config.get_ollama_url())
            self.model_combo.setCurrentText(
                self.config.get("model", "Claude Sonnet 4 (Recommended)")
            )

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")

    def save_settings(self):
        """Save settings to secure storage."""
        try:
            # Store API key securely (never in plaintext)
            api_key = self.api_key.text().strip()
            if api_key:
                if not self.config.set_api_key(api_key):
                    QMessageBox.warning(
                        self,
                        "⚠️ Warning",
                        "Could not save API key securely.\n"
                        "Make sure keyring library is installed: pip install keyring"
                    )

            # Store other settings
            self.config.set("provider", self.provider_combo.currentText())
            self.config.set("model", self.model_combo.currentText())
            self.config.set_ollama_url(self.ollama_url.text())

            self.config.save()

            QMessageBox.information(
                self,
                "✅ Success",
                "Settings saved securely!\n\n"
                "Your API key is encrypted in Windows Credential Manager."
            )

        except Exception as e:
            error = ErrorHandler.handle_error(e, "save_settings", show_technical=False)
            QMessageBox.critical(
                self,
                error.title,
                error.message + "\n\n" + "\n".join(error.suggestions)
            )

    def reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings?",
            "Reset all settings to defaults?\n\nYour API key will NOT be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_key.clear()
            self.provider_combo.setCurrentText("Claude (Cloud)")
            self.ollama_url.setText("http://localhost:11434")
            self.model_combo.setCurrentText("Claude Sonnet 4 (Recommended)")

    def migrate_credentials(self):
        """Migrate credentials from plaintext to secure storage."""
        project_root = Path.home() / "Symphony-IR"

        # Check for plaintext config
        config_file = project_root / ".orchestrator" / "config.json"
        if not config_file.exists():
            QMessageBox.information(self, "ℹ️ No Migration Needed", "No plaintext configuration found.")
            return

        try:
            with open(config_file) as f:
                config = json.load(f)

            if not config.get("api_key"):
                QMessageBox.information(self, "ℹ️ No Migration Needed", "No API keys to migrate.")
                return

            # Ask for confirmation
            reply = QMessageBox.question(
                self,
                "Migrate Credentials?",
                "Found API key in plaintext.\n\n"
                "Migrate to secure storage?\n"
                "(This will remove the key from plaintext config)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Perform migration
            api_key = config.get("api_key")
            if self.config.set_api_key(api_key):
                config["api_key"] = None
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)

                self.api_key.setText(api_key)

                QMessageBox.information(
                    self,
                    "✅ Migration Complete",
                    "API key migrated to secure storage!\n"
                    "Plaintext config has been updated."
                )
            else:
                QMessageBox.warning(
                    self,
                    "⚠️ Migration Failed",
                    "Could not store key securely.\n"
                    "Install keyring: pip install keyring"
                )

        except Exception as e:
            error = ErrorHandler.handle_error(e, "migrate_credentials")
            QMessageBox.critical(self, error.title, str(error))


class SecureHistoryTab(QWidget):
    """History tab with session redaction and export options."""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_history()

    def init_ui(self):
        layout = QVBoxLayout()

        # Toolbar with export options
        toolbar_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_history)

        export_btn = QPushButton("💾 Export Sanitized")
        export_btn.clicked.connect(self.export_sanitized)

        toolbar_layout.addWidget(refresh_btn)
        toolbar_layout.addWidget(export_btn)
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(
            ["Timestamp", "Task", "Status", "Run ID", "Details"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.history_table)

        # Details section
        details_group = QGroupBox("Details (Auto-Redacted)")
        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        self.setLayout(layout)

    def load_history(self):
        """Load execution history from .orchestrator/runs/"""
        try:
            runs_dir = Path.home() / "Symphony-IR" / ".orchestrator" / "runs"
            if not runs_dir.exists():
                self.history_table.setRowCount(0)
                return

            # Get recent run files
            run_files = sorted(
                runs_dir.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:20]

            self.history_table.setRowCount(len(run_files))

            for row, run_file in enumerate(run_files):
                try:
                    with open(run_file) as f:
                        data = json.load(f)

                    # Redact data before displaying
                    redacted_data = SessionRedactor.redact_session(data)

                    timestamp = redacted_data.get("metadata", {}).get("timestamp", "N/A")
                    task = redacted_data.get("task", "N/A")[:50]
                    status = "✅" if redacted_data.get("success", False) else "❌"
                    run_id = redacted_data.get("run_id", "N/A")[:12]

                    self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
                    self.history_table.setItem(row, 1, QTableWidgetItem(task))
                    self.history_table.setItem(row, 2, QTableWidgetItem(status))
                    self.history_table.setItem(row, 3, QTableWidgetItem(run_id))
                    self.history_table.setItem(row, 4, QTableWidgetItem("📄 View"))

                except Exception as e:
                    logger.debug(f"Error loading run file: {e}")

        except Exception as e:
            logger.error(f"Error loading history: {e}")

    def export_sanitized(self):
        """Export sanitized session (with redaction)."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Sanitized Session",
            str(Path.home() / "Desktop" / "symphony-session-sanitized.json"),
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            # Get first selected run or all runs
            # For this example, we'll export all visible runs as a summary
            runs = []
            runs_dir = Path.home() / "Symphony-IR" / ".orchestrator" / "runs"

            for run_file in sorted(runs_dir.glob("*.json"))[:20]:
                try:
                    with open(run_file) as f:
                        data = json.load(f)
                    redacted = SessionRedactor.redact_session(data)
                    runs.append(redacted)
                except:
                    pass

            with open(file_path, 'w') as f:
                json.dump({"runs": runs}, f, indent=2)

            QMessageBox.information(
                self,
                "✅ Export Complete",
                f"Sanitized session exported to:\n{file_path}\n\n"
                "All sensitive information has been redacted."
            )

        except Exception as e:
            error = ErrorHandler.handle_error(e, "export_sanitized")
            QMessageBox.critical(self, error.title, str(error))


class SymphonyIRSecureApp(QMainWindow):
    """Main application with security features."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symphony-IR - AI Orchestrator (Secure)")
        self.setGeometry(100, 100, 1200, 800)

        # Create menu bar
        self.create_menus()

        # Create central widget with tabs
        tabs = QTabWidget()
        # tabs.addTab(OrchestratorTab(), "🎼 Orchestrator")
        # tabs.addTab(FlowTab(), "🗺️ Symphony Flow")
        tabs.addTab(SecureHistoryTab(), "📋 History (Auto-Redacted)")
        tabs.addTab(SecureSettingsTab(), "⚙️ Settings (Secure)")

        self.setCentralWidget(tabs)

        # Status bar
        self.statusBar().showMessage("Ready")

        # Apply styling
        self.setStyleSheet(self.get_stylesheet())

        # Show security info on startup
        self.show_security_info()

    def create_menus(self):
        """Create application menus."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_security_info(self):
        """Show security information on startup."""
        keyring_status = "✅ Available" if CredentialManager.is_available() else "⚠️ Not installed"
        QMessageBox.information(
            self,
            "🔐 Security Features",
            f"Symphony-IR Secure Edition Features:\n\n"
            f"1. 🔑 API Key Security\n"
            f"   Stored in Windows Credential Manager\n"
            f"   Never stored in plaintext\n"
            f"   Status: {keyring_status}\n\n"
            f"2. 📋 Session Redaction\n"
            f"   Automatically redacts sensitive data\n"
            f"   Safe for sharing and archiving\n\n"
            f"3. 💬 User-Friendly Errors\n"
            f"   Plain English error messages\n"
            f"   Actionable suggestions\n"
            f"   Help links included"
        )

    def show_about(self):
        """Show about dialog."""
        QMessageBox.information(
            self,
            "About Symphony-IR",
            "Symphony-IR v1.0 - Secure Edition\n\n"
            "Deterministic multi-agent orchestration with:\n"
            "✅ Secure credential storage\n"
            "✅ Automatic session redaction\n"
            "✅ User-friendly error messages\n\n"
            "https://github.com/courtneybtaylor-sys/Symphony-IR"
        )

    def get_stylesheet(self) -> str:
        """Get application stylesheet."""
        return """
            QMainWindow { background-color: #f5f5f5; }
            QTabBar::tab { background-color: #e0e0e0; padding: 8px 20px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #2196F3; color: white; }
            QGroupBox { color: #333; border: 1px solid #ddd; border-radius: 5px;
                       margin-top: 10px; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QPushButton { background-color: #2196F3; color: white; border: none;
                         border-radius: 4px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #1976D2; }
            QLineEdit, QTextEdit, QComboBox { border: 1px solid #ccc; border-radius: 4px;
                                             padding: 5px; background-color: white; }
            QStatusBar { background-color: #f5f5f5; border-top: 1px solid #ddd; }
        """


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = SymphonyIRSecureApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
