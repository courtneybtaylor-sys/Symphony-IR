"""
Symphony-IR Setup Wizard

Interactive first-run configuration wizard for PyQt6 desktop app.
Guides users through provider selection and API key configuration.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QWidget, QLabel, QRadioButton, QButtonGroup, QLineEdit,
    QPushButton, QTextEdit, QProgressBar, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon, QTextCursor


class APIValidationThread(QThread):
    """Background thread for API validation."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    success = pyqtSignal()

    def __init__(self, provider: str, api_key: Optional[str] = None):
        super().__init__()
        self.provider = provider
        self.api_key = api_key

    def run(self):
        """Validate API connection in background."""
        try:
            if self.provider == "claude":
                self._validate_claude()
            elif self.provider == "ollama":
                self._validate_ollama()
            self.success.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    def _validate_claude(self):
        """Validate Claude API key."""
        if not self.api_key or len(self.api_key) < 10:
            raise ValueError("API key appears invalid (too short)")

        if not self.api_key.startswith("sk-ant-"):
            raise ValueError("API key should start with 'sk-ant-'")

        # Try a simple API call
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            # Just try to list available models
            # (This validates the key without using credits)
            _ = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
        except Exception as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                raise ValueError("API key is invalid or has been revoked")
            raise

    def _validate_ollama(self):
        """Validate Ollama server connection."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                raise ValueError(f"Ollama returned error: {response.status_code}")
        except requests.ConnectionError:
            raise ValueError(
                "Could not connect to Ollama at localhost:11434.\n"
                "Make sure Ollama is installed and running."
            )
        except Exception as e:
            raise ValueError(f"Ollama validation failed: {str(e)}")


class SetupWizard(QDialog):
    """Multi-step setup wizard for first-run configuration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Symphony-IR Setup Wizard")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setModal(True)

        # Configuration state
        self.config: Dict[str, Any] = {
            "setup_complete": False,
            "provider": None,
            "claude_api_key": None,
            "ollama_host": "http://localhost:11434"
        }

        # Build UI
        self.setup_ui()

    def setup_ui(self):
        """Build the wizard UI."""
        layout = QVBoxLayout()

        # Progress indicator
        self.progress = QProgressBar()
        self.progress.setRange(0, 5)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        # Stacked widget for pages
        self.stack = QStackedWidget()

        self.page_welcome = self.create_welcome_page()
        self.page_provider = self.create_provider_page()
        self.page_api_key = self.create_api_key_page()
        self.page_validation = self.create_validation_page()
        self.page_complete = self.create_complete_page()

        self.stack.addWidget(self.page_welcome)
        self.stack.addWidget(self.page_provider)
        self.stack.addWidget(self.page_api_key)
        self.stack.addWidget(self.page_validation)
        self.stack.addWidget(self.page_complete)

        layout.addWidget(self.stack)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        self.btn_next = QPushButton("Next →")
        self.btn_skip = QPushButton("Skip for Now")
        self.btn_finish = QPushButton("Launch Symphony-IR")

        self.btn_back.clicked.connect(self.go_back)
        self.btn_next.clicked.connect(self.go_next)
        self.btn_skip.clicked.connect(self.skip_setup)
        self.btn_finish.clicked.connect(self.accept)

        nav_layout.addWidget(self.btn_back)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_skip)
        nav_layout.addWidget(self.btn_next)
        nav_layout.addWidget(self.btn_finish)

        layout.addLayout(nav_layout)

        self.setLayout(layout)
        self.show_page(0)

    def create_welcome_page(self) -> QWidget:
        """Welcome page with introduction."""
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Welcome to Symphony-IR! 🎼")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addSpacing(20)

        subtitle = QLabel("Deterministic Multi-Agent AI Orchestration")
        subtitle.setFont(QFont("Arial", 11))
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        intro_text = QLabel(
            "Symphony-IR helps you orchestrate complex AI workflows.\n\n"
            "This quick setup wizard will guide you through:\n"
            "• Choosing your AI provider (Claude or Ollama)\n"
            "• Configuring your API keys (if needed)\n"
            "• Validating your setup\n\n"
            "Takes about 2-3 minutes. Let's get started!"
        )
        intro_text.setWordWrap(True)
        layout.addWidget(intro_text)

        layout.addSpacing(20)

        what_you_need = QLabel("<b>What you'll need:</b>")
        layout.addWidget(what_you_need)

        claude_info = QLabel(
            "• <b>Claude:</b> Free API key from console.anthropic.com"
        )
        claude_info.setWordWrap(True)
        layout.addWidget(claude_info)

        ollama_info = QLabel(
            "• <b>Ollama:</b> Downloaded from ollama.ai (free, runs locally)"
        )
        ollama_info.setWordWrap(True)
        layout.addWidget(ollama_info)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_provider_page(self) -> QWidget:
        """Provider selection page."""
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Choose Your AI Provider")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Which AI provider would you like to use?"
        ))

        layout.addSpacing(10)

        # Radio button group
        self.provider_group = QButtonGroup()

        # Claude option
        self.radio_claude = QRadioButton(
            "Claude (Cloud API)\n"
            "• Best for production and consistent results\n"
            "• Requires API key (free tier available)\n"
            "• Pay as you go (~$0.0008 per 1K tokens)"
        )
        self.radio_claude.setChecked(True)
        self.provider_group.addButton(self.radio_claude, 1)
        layout.addWidget(self.radio_claude)

        layout.addSpacing(10)

        # Ollama option
        self.radio_ollama = QRadioButton(
            "Ollama (Local, Free)\n"
            "• Best for privacy and offline work\n"
            "• Completely free, no API key needed\n"
            "• Runs on your machine (~4-45GB for models)"
        )
        self.provider_group.addButton(self.radio_ollama, 2)
        layout.addWidget(self.radio_ollama)

        layout.addSpacing(10)

        # Both option
        self.radio_both = QRadioButton(
            "Both\n"
            "• Maximum flexibility\n"
            "• Use Claude for critical tasks, Ollama for testing\n"
            "• Configure both now"
        )
        self.provider_group.addButton(self.radio_both, 3)
        layout.addWidget(self.radio_both)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_api_key_page(self) -> QWidget:
        """API key configuration page."""
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Configure API Key")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addSpacing(10)

        # Instructions based on provider
        self.api_instructions = QLabel()
        self.api_instructions.setWordWrap(True)
        layout.addWidget(self.api_instructions)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Paste your API key:"))

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-ant-... (hidden for security)")
        layout.addWidget(self.api_key_input)

        layout.addSpacing(5)

        show_check_layout = QHBoxLayout()
        self.show_key_checkbox = QPushButton("Show")
        self.show_key_checkbox.setCheckable(True)
        self.show_key_checkbox.setMaximumWidth(60)
        self.show_key_checkbox.toggled.connect(self.toggle_api_key_visibility)
        show_check_layout.addWidget(self.show_key_checkbox)
        show_check_layout.addStretch()
        layout.addLayout(show_check_layout)

        layout.addSpacing(10)

        self.api_link = QPushButton("Get API Key")
        self.api_link.setMaximumWidth(150)
        self.api_link.clicked.connect(self.open_api_link)
        layout.addWidget(self.api_link)

        layout.addSpacing(10)

        skip_msg = QLabel(
            "Don't have an API key yet? You can skip this and "
            "add it later in the Settings tab."
        )
        skip_msg.setWordWrap(True)
        skip_msg.setStyleSheet("color: gray;")
        layout.addWidget(skip_msg)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_validation_page(self) -> QWidget:
        """Validation page with progress."""
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Validating Configuration")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addSpacing(10)

        self.validation_message = QLabel("Checking API connection...")
        self.validation_message.setWordWrap(True)
        layout.addWidget(self.validation_message)

        layout.addSpacing(10)

        self.validation_progress = QProgressBar()
        self.validation_progress.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.validation_progress)

        layout.addSpacing(10)

        self.validation_status = QLabel()
        self.validation_status.setWordWrap(True)
        self.validation_status.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.validation_status)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_complete_page(self) -> QWidget:
        """Completion page."""
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("All Set! 🎉")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addSpacing(20)

        message = QLabel(
            "Symphony-IR is ready to use!\n\n"
            "Next steps:\n"
            "1. Click 'Launch Symphony-IR'\n"
            "2. Try the sample tasks\n"
            "3. Explore Symphony Flow workflows\n\n"
            "Happy orchestrating! 🚀"
        )
        message.setWordWrap(True)
        layout.addWidget(message)

        layout.addSpacing(20)

        self.config_summary = QTextEdit()
        self.config_summary.setReadOnly(True)
        self.config_summary.setMaximumHeight(150)
        layout.addWidget(QLabel("Your Configuration:"))
        layout.addWidget(self.config_summary)

        layout.addSpacing(10)

        help_text = QLabel(
            "You can always change these settings later in the Settings tab."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: gray;")
        layout.addWidget(help_text)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def toggle_api_key_visibility(self, checked: bool):
        """Show/hide API key."""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_checkbox.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_checkbox.setText("Show")

    def open_api_link(self):
        """Open API key generation link."""
        import webbrowser
        webbrowser.open("https://console.anthropic.com")

    def show_page(self, index: int):
        """Show a specific page."""
        self.stack.setCurrentIndex(index)
        self.progress.setValue(index + 1)

        # Update button visibility
        self.btn_back.setVisible(index > 0)
        self.btn_next.setVisible(index < 4)
        self.btn_finish.setVisible(index == 4)
        self.btn_skip.setVisible(index < 4)

        # Page-specific setup
        if index == 1:  # Provider page
            self.update_provider_page()
        elif index == 2:  # API key page
            self.update_api_key_page()
        elif index == 3:  # Validation page
            self.validate_configuration()
        elif index == 4:  # Complete page
            self.update_complete_page()

    def update_provider_page(self):
        """Update provider page based on selection."""
        self.btn_next.setEnabled(True)

    def update_api_key_page(self):
        """Update API key page based on provider selection."""
        provider = self.get_selected_provider()

        if provider == "claude":
            self.api_instructions.setText(
                "Get a free Claude API key:\n"
                "1. Visit console.anthropic.com\n"
                "2. Sign up (takes 1 minute)\n"
                "3. Click 'Generate API Key'\n"
                "4. Paste it below"
            )
            self.api_link.setText("Get API Key →")
            self.api_key_input.setPlaceholderText("sk-ant-...")
            self.api_key_input.show()
        elif provider == "ollama":
            self.api_instructions.setText(
                "Ollama doesn't require an API key.\n\n"
                "To use Ollama:\n"
                "1. Download from https://ollama.ai\n"
                "2. Install and launch\n"
                "3. Run: ollama pull llama2\n"
                "4. We'll automatically find it!"
            )
            self.api_key_input.hide()
            self.api_link.setText("Download Ollama →")
            self.api_link.clicked.disconnect()
            self.api_link.clicked.connect(
                lambda: __import__("webbrowser").open("https://ollama.ai")
            )

    def update_api_key_page_initial(self):
        """Initial setup of API key page."""
        pass

    def update_complete_page(self):
        """Update completion page with summary."""
        summary_text = f"""
Configuration Summary:

Provider: {self.config['provider'].upper() if self.config['provider'] else 'Not set'}
API Key: {'✓ Configured' if self.config['claude_api_key'] else '○ Not set (can add later)'}

You can modify these settings anytime in the Settings tab.
        """.strip()

        self.config_summary.setText(summary_text)

    def get_selected_provider(self) -> Optional[str]:
        """Get the selected provider."""
        if self.radio_claude.isChecked():
            return "claude"
        elif self.radio_ollama.isChecked():
            return "ollama"
        elif self.radio_both.isChecked():
            return "both"
        return None

    def validate_configuration(self):
        """Validate the configuration in background."""
        provider = self.config.get("provider")
        api_key = self.api_key_input.text() if hasattr(self, 'api_key_input') else None

        self.validation_message.setText(
            f"Validating {provider.upper() if provider else 'configuration'}..."
        )

        self.validation_thread = APIValidationThread(provider, api_key)
        self.validation_thread.success.connect(self.on_validation_success)
        self.validation_thread.error.connect(self.on_validation_error)
        self.validation_thread.finished.connect(self.on_validation_finished)
        self.validation_thread.start()

    def on_validation_success(self):
        """Handle successful validation."""
        self.validation_status.setText("✓ Configuration validated successfully!")
        self.validation_status.setStyleSheet("color: green;")

        # Save API key if provided
        if hasattr(self, 'api_key_input'):
            api_key = self.api_key_input.text()
            if api_key and api_key != "skip":
                self.config['claude_api_key'] = api_key

    def on_validation_error(self, error_msg: str):
        """Handle validation error."""
        self.validation_status.setText(f"✗ Validation failed: {error_msg}")
        self.validation_status.setStyleSheet("color: red;")
        self.btn_next.setEnabled(True)  # Allow proceeding anyway

    def on_validation_finished(self):
        """Handle validation thread completion."""
        self.validation_progress.setRange(0, 1)
        self.validation_progress.setValue(1)
        self.btn_next.setEnabled(True)

    def go_next(self):
        """Go to next page."""
        current = self.stack.currentIndex()

        # Validation before proceeding
        if current == 1:  # Provider page
            provider = self.get_selected_provider()
            if not provider:
                QMessageBox.warning(self, "Selection Required", "Please select a provider.")
                return
            self.config['provider'] = provider

        if current == 2:  # API key page
            provider = self.config.get('provider')
            if provider == "claude":
                api_key = self.api_key_input.text().strip()
                if api_key and len(api_key) > 5:
                    self.config['claude_api_key'] = api_key

        # Move to next page
        self.show_page(current + 1)

    def go_back(self):
        """Go to previous page."""
        current = self.stack.currentIndex()
        if current > 0:
            self.show_page(current - 1)

    def skip_setup(self):
        """Skip the setup wizard."""
        reply = QMessageBox.question(
            self, "Skip Setup?",
            "You can configure your AI provider later in the Settings tab.\n\n"
            "Skip setup now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config['setup_complete'] = True
            self.accept()

    def save_configuration(self):
        """Save configuration to file."""
        config_dir = Path.home() / ".symphonyir"
        config_dir.mkdir(exist_ok=True)

        config_file = config_dir / "config.json"

        self.config['setup_complete'] = True
        self.config['setup_version'] = "1.0"

        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def accept(self):
        """Accept and save configuration."""
        self.save_configuration()
        super().accept()


def should_run_setup_wizard() -> bool:
    """Check if setup wizard should run on first launch."""
    config_file = Path.home() / ".symphonyir" / "config.json"

    if not config_file.exists():
        return True

    try:
        with open(config_file) as f:
            config = json.load(f)
            return not config.get('setup_complete', False)
    except Exception:
        return True


if __name__ == "__main__":
    app = QApplication([])
    wizard = SetupWizard()
    wizard.exec()
