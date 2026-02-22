"""
Orchestrator Tab — Tab 1.

Lets the user describe a task and run the Symphony-IR multi-agent
orchestrator.  Output is streamed in real time and auto-redacted.

Uses custom widgets with "Deterministic Elegance" design system.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QHBoxLayout, QWidget

from widgets import (
    SplitViewPanel,
    GradientCard,
    StyledTextEdit,
    StyledCheckBox,
    PrimaryButton,
    DangerButton,
    SyntaxHighlightedLog,
    ProgressCard,
)
from services.orchestrator_service import OrchestratorWorker
from services.credential_service import CredentialService
from services.error_service import show_error_dialog, get_api_key_error


class OrchestratorTab(QWidget):
    """Tab 1 — run an arbitrary task through the agent orchestrator."""

    def __init__(self, project_root: Path):
        super().__init__()
        self._project_root = project_root
        self._worker: Optional[OrchestratorWorker] = None
        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Create split view (45% left for input, 55% right for output)
        self.split_view = SplitViewPanel(
            left_title="Task Input",
            right_title="Execution Output"
        )

        # ---- LEFT PANEL: Task Input with Gradient Card ----
        input_card = GradientCard("Task Definition")

        self.task_input = StyledTextEdit()
        self.task_input.setPlaceholderText(
            "Describe what you want the AI agents to do…\n\n"
            "Examples:\n"
            "  • Review the authentication module for security issues\n"
            "  • Design a REST API for a todo application\n"
            "  • Refactor the payment service for better testability"
        )
        self.task_input.setMinimumHeight(120)
        input_card.add_widget(self.task_input)

        # Checkboxes for options
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout()
        checkbox_layout.setContentsMargins(0, 8, 0, 0)
        checkbox_layout.setSpacing(6)

        self.dry_run = StyledCheckBox("Dry run mode  (show plan only, no execution)")
        self.verbose = StyledCheckBox("Verbose output")
        checkbox_layout.addWidget(self.dry_run)
        checkbox_layout.addWidget(self.verbose)

        checkbox_container.setLayout(checkbox_layout)
        input_card.add_widget(checkbox_container)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 12, 0, 0)
        button_layout.setSpacing(8)

        self.run_btn = PrimaryButton("▶ Run Orchestrator")
        self.cancel_btn = DangerButton("⏹ Cancel")
        self.cancel_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        self.cancel_btn.clicked.connect(self._cancel)

        button_layout.addWidget(self.run_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()

        button_container = QWidget()
        button_container.setLayout(button_layout)
        input_card.add_widget(button_container)

        self.split_view.add_left_widget(input_card)

        # ---- RIGHT PANEL: Output with Syntax Highlighting ----
        self.output = SyntaxHighlightedLog()
        self.split_view.add_right_widget(self.output)

        main_layout.addWidget(self.split_view)

        # Progress indicator below split view
        self.progress_card = ProgressCard("Execution Status")
        self.progress_card.set_progress(0, "idle")
        main_layout.addWidget(self.progress_card)

    # ---------------------------------------------------------------- slots

    def _run(self):
        task = self.task_input.toPlainText().strip()
        if not task:
            QMessageBox.warning(self, "No Task", "Please enter a task description.")
            return

        qs = QSettings("Symphony-IR", "Desktop")
        provider = qs.value("provider", "Claude (Cloud)")
        if "Claude" in provider and not CredentialService.get_api_key():
            show_error_dialog(self, get_api_key_error().to_dict())
            return

        self.output.clear_logs()
        self.output.append_log("Initializing orchestrator...", "info")
        self._set_busy(True)
        self._worker = OrchestratorWorker("run", self._project_root, task=task)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _cancel(self):
        if self._worker:
            self._worker.cancel()
        self._set_busy(False)
        self.output.append_log("Cancelled by user.", "warning")
        self.progress_card.set_progress(0, "idle")

    def _on_progress(self, text: str):
        """Handle progress updates from worker."""
        # Determine log level based on content
        if "error" in text.lower() or "failed" in text.lower():
            level = "error"
        elif "success" in text.lower() or "complete" in text.lower():
            level = "success"
        elif "warning" in text.lower():
            level = "warning"
        else:
            level = "info"

        self.output.append_log(text, level)
        self.progress_card.set_progress(50, "running")  # Mid-progress indicator

    def _on_done(self, result: dict):
        self._set_busy(False)
        self.output.append_log("✅ Execution complete", "success")
        self.progress_card.set_progress(100, "success")

    def _on_error(self, err: dict):
        self._set_busy(False)
        self.output.append_log("❌ Error during execution", "error")
        self.progress_card.set_progress(0, "error")
        show_error_dialog(self, err)

    # --------------------------------------------------------------- helpers

    def _set_busy(self, active: bool):
        """Update UI state when task is running/idle."""
        self.run_btn.setEnabled(not active)
        self.cancel_btn.setEnabled(active)
        self.task_input.setReadOnly(active)

        if active:
            self.progress_card.set_progress(0, "running")
        else:
            self.progress_card.set_progress(0, "idle")
