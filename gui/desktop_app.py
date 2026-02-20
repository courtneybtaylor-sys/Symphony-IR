"""
Symphony-IR Desktop Application
Modern PyQt6 GUI for Windows, macOS, and Linux
No terminal commands needed - everything through GUI
"""

import sys
import json
import subprocess
import threading
import os
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
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis
from PyQt6.QtCore import QDate


class OrchestratorWorker(QThread):
    """Run orchestrator tasks in background thread"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, task: str, command_type: str = "run", **kwargs):
        super().__init__()
        self.task = task
        self.command_type = command_type
        self.kwargs = kwargs

    def run(self):
        try:
            project_root = Path.home() / "Symphony-IR"
            os_cmd = []

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

            self.progress.emit("Starting orchestrator...")
            process = subprocess.Popen(
                os_cmd,
                cwd=str(project_root / "ai-orchestrator"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.error.emit(f"Error: {stderr}")
                return

            self.finished.emit({
                "success": True,
                "output": stdout,
                "command_type": self.command_type
            })

        except Exception as e:
            self.error.emit(str(e))


class OrchestratorTab(QWidget):
    """Main orchestration tab"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.worker = None

    def init_ui(self):
        layout = QVBoxLayout()

        # Task input section
        input_group = QGroupBox("Task Description")
        input_layout = QFormLayout()

        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText(
            "Enter your task description here...\n\n"
            "Examples:\n"
            "- Review authentication system for security vulnerabilities\n"
            "- Design a REST API for a todo application\n"
            "- Refactor the payment processing module"
        )
        self.task_input.setMinimumHeight(150)

        input_layout.addRow("Task:", self.task_input)

        # Project root
        project_layout = QHBoxLayout()
        self.project_path = QLineEdit()
        self.project_path.setText(str(Path.home() / "Symphony-IR"))
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_project)
        project_layout.addWidget(self.project_path)
        project_layout.addWidget(browse_btn)

        input_layout.addRow("Project:", project_layout)

        # Options
        self.dry_run = QCheckBox("Dry run (show plan without executing)")
        self.verbose = QCheckBox("Verbose output")
        input_layout.addRow(self.dry_run)
        input_layout.addRow(self.verbose)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Run button
        run_layout = QHBoxLayout()
        self.run_btn = QPushButton("▶ Run Orchestrator")
        self.run_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }"
        )
        self.run_btn.clicked.connect(self.run_orchestrator)
        run_layout.addWidget(self.run_btn)
        run_layout.addStretch()
        layout.addLayout(run_layout)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Output section
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        self.setLayout(layout)

    def browse_project(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if path:
            self.project_path.setText(path)

    def run_orchestrator(self):
        task = self.task_input.toPlainText().strip()
        if not task:
            QMessageBox.warning(self, "Error", "Please enter a task description")
            return

        self.output_text.clear()
        self.progress.setVisible(True)
        self.run_btn.setEnabled(False)

        self.worker = OrchestratorWorker(task)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, message: str):
        self.output_text.append(f"[*] {message}")

    def on_finished(self, result: dict):
        self.output_text.append(f"\n{'='*60}\n✅ Execution Complete\n{'='*60}\n")
        self.output_text.append(result["output"])
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)

    def on_error(self, error: str):
        self.output_text.append(f"\n❌ Error: {error}")
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)


class FlowTab(QWidget):
    """Symphony Flow workflow tab"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.worker = None

    def init_ui(self):
        layout = QVBoxLayout()

        # Template selection
        template_group = QGroupBox("Select Workflow Template")
        template_layout = QFormLayout()

        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "code_review - Code quality review",
            "refactor_code - Refactoring guidance",
            "new_feature - Feature planning",
            "api_design - API design",
            "database_schema - Database design",
            "testing_strategy - Testing plans",
            "documentation - Documentation planning"
        ])
        self.template_combo.currentTextChanged.connect(self.on_template_changed)

        template_layout.addRow("Template:", self.template_combo)

        # Template description
        self.template_desc = QTextEdit()
        self.template_desc.setReadOnly(True)
        self.template_desc.setMaximumHeight(100)
        template_layout.addRow("Description:", self.template_desc)

        template_group.setLayout(template_layout)
        layout.addWidget(template_group)

        # Variables section
        var_group = QGroupBox("Template Variables")
        var_layout = QFormLayout()

        self.var_input = QLineEdit()
        self.var_input.setPlaceholderText("e.g., component=auth.py or api_name=user-service")
        var_layout.addRow("Variable:", self.var_input)

        var_group.setLayout(var_layout)
        layout.addWidget(var_group)

        # Run button
        run_layout = QHBoxLayout()
        self.run_flow_btn = QPushButton("▶ Start Workflow")
        self.run_flow_btn.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 10px; }"
        )
        self.run_flow_btn.clicked.connect(self.run_flow)
        run_layout.addWidget(self.run_flow_btn)
        run_layout.addStretch()
        layout.addLayout(run_layout)

        # Progress
        self.flow_progress = QProgressBar()
        self.flow_progress.setVisible(False)
        layout.addWidget(self.flow_progress)

        # Output
        output_group = QGroupBox("Workflow Progress")
        output_layout = QVBoxLayout()
        self.flow_output = QTextEdit()
        self.flow_output.setReadOnly(True)
        output_layout.addWidget(self.flow_output)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        self.setLayout(layout)
        self.on_template_changed()

    def on_template_changed(self):
        descriptions = {
            "code_review": "Review code quality with focused analysis paths (bugs, style, performance)",
            "refactor_code": "Get structured refactoring guidance (design improvements, quick fixes)",
            "new_feature": "Plan and implement new features with architecture and risk analysis",
            "api_design": "Design robust APIs (REST, GraphQL, hybrid approaches)",
            "database_schema": "Design database schemas (SQL, NoSQL, hybrid databases)",
            "testing_strategy": "Create comprehensive testing plans (unit, integration, performance)",
            "documentation": "Plan documentation (user guides, API docs, architecture)"
        }

        current = self.template_combo.currentText().split(" - ")[0]
        self.template_desc.setText(descriptions.get(current, ""))

    def run_flow(self):
        template = self.template_combo.currentText().split(" - ")[0]
        variables_str = self.var_input.text().strip()

        variables = {}
        if variables_str:
            for var in variables_str.split(","):
                if "=" in var:
                    key, val = var.split("=", 1)
                    variables[key.strip()] = val.strip()

        self.flow_output.clear()
        self.flow_progress.setVisible(True)
        self.run_flow_btn.setEnabled(False)

        self.worker = OrchestratorWorker(
            "workflow",
            command_type="flow",
            template=template,
            variables=variables
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, message: str):
        self.flow_output.append(f"[*] {message}")

    def on_finished(self, result: dict):
        self.flow_output.append("\n✅ Workflow Complete!\n")
        self.flow_output.append(result["output"])
        self.flow_progress.setVisible(False)
        self.run_flow_btn.setEnabled(True)

    def on_error(self, error: str):
        self.flow_output.append(f"\n❌ Error: {error}")
        self.flow_progress.setVisible(False)
        self.run_flow_btn.setEnabled(True)


class HistoryTab(QWidget):
    """View execution history"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_history()

    def init_ui(self):
        layout = QVBoxLayout()

        # Toolbar
        toolbar_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_history)
        toolbar_layout.addWidget(refresh_btn)
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
        details_group = QGroupBox("Details")
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
            run_files = sorted(runs_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:20]

            self.history_table.setRowCount(len(run_files))

            for row, run_file in enumerate(run_files):
                try:
                    with open(run_file) as f:
                        data = json.load(f)

                    timestamp = data.get("metadata", {}).get("timestamp", "N/A")
                    task = data.get("task", "N/A")[:50]
                    status = "✅" if data.get("success", False) else "❌"
                    run_id = data.get("run_id", "N/A")[:12]

                    self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
                    self.history_table.setItem(row, 1, QTableWidgetItem(task))
                    self.history_table.setItem(row, 2, QTableWidgetItem(status))
                    self.history_table.setItem(row, 3, QTableWidgetItem(run_id))
                    self.history_table.setItem(row, 4, QTableWidgetItem("📄 View"))

                except Exception as e:
                    pass

        except Exception as e:
            self.details_text.setText(f"Error loading history: {str(e)}")


class SettingsTab(QWidget):
    """Configuration and settings"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()

        # API Configuration
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Claude (Cloud)", "Ollama (Local)", "OpenAI"])
        api_layout.addRow("AI Model Provider:", self.provider_combo)

        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("sk-... (leave blank for Ollama)")
        api_layout.addRow("API Key:", self.api_key)

        self.ollama_url = QLineEdit()
        self.ollama_url.setText("http://localhost:11434")
        api_layout.addRow("Ollama URL:", self.ollama_url)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Model Selection
        model_group = QGroupBox("Model Selection")
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
        settings_group = QGroupBox("Orchestrator Settings")
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

        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addStretch()
        self.setLayout(layout)

    def load_settings(self):
        settings = QSettings("Symphony-IR", "Orchestra")
        self.provider_combo.setCurrentText(
            settings.value("provider", "Claude (Cloud)")
        )
        self.api_key.setText(settings.value("api_key", ""))
        self.ollama_url.setText(settings.value("ollama_url", "http://localhost:11434"))
        self.model_combo.setCurrentText(
            settings.value("model", "Claude Sonnet 4 (Recommended)")
        )

    def save_settings(self):
        settings = QSettings("Symphony-IR", "Orchestra")
        settings.setValue("provider", self.provider_combo.currentText())
        settings.setValue("api_key", self.api_key.text())
        settings.setValue("ollama_url", self.ollama_url.text())
        settings.setValue("model", self.model_combo.currentText())

        QMessageBox.information(self, "Success", "Settings saved successfully!")

    def reset_settings(self):
        reply = QMessageBox.question(
            self, "Confirm",
            "Reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            settings = QSettings("Symphony-IR", "Orchestra")
            settings.clear()
            self.load_settings()


class SymphonyIRApp(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symphony-IR - AI Orchestrator")
        self.setWindowIcon(QIcon("symphony_icon.png"))
        self.setGeometry(100, 100, 1200, 800)

        # Create menu bar
        self.create_menus()

        # Create central widget with tabs
        tabs = QTabWidget()
        tabs.addTab(OrchestratorTab(), "🎼 Orchestrator")
        tabs.addTab(FlowTab(), "🗺️ Symphony Flow")
        tabs.addTab(HistoryTab(), "📋 History")
        tabs.addTab(SettingsTab(), "⚙️ Settings")

        self.setCentralWidget(tabs)

        # Status bar
        self.statusBar().showMessage("Ready")

        # Apply styling
        self.setStyleSheet(self.get_stylesheet())

    def create_menus(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        docs_action = QAction("Documentation", self)
        docs_action.triggered.connect(self.open_documentation)
        help_menu.addAction(docs_action)

    def show_about(self):
        QMessageBox.information(
            self,
            "About Symphony-IR",
            "Symphony-IR v1.0\n\n"
            "Deterministic multi-agent orchestration engine with "
            "structured guidance and beautiful GUI.\n\n"
            "https://github.com/courtneybtaylor-sys/Symphony-IR"
        )

    def open_documentation(self):
        import webbrowser
        webbrowser.open("https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/README.md")

    def get_stylesheet(self):
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QGroupBox {
                color: #333;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QStatusBar {
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
            }
        """


def main():
    app = QApplication(sys.argv)
    window = SymphonyIRApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
