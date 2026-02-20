"""
Orchestrator Tab — Tab 1.

Lets the user describe a task and run the Symphony-IR multi-agent
orchestrator.  Output is streamed in real time and auto-redacted.

UX improvements over the original monolith
-------------------------------------------
* Cancel button terminates the running subprocess immediately.
* Run button disabled while a job is active (prevents double-submit).
* Progress spinner hidden when idle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox, QGroupBox, QFormLayout, QHBoxLayout, QMessageBox,
    QProgressBar, QPushButton, QTextEdit, QVBoxLayout, QWidget,
)

from services.orchestrator_service import OrchestratorWorker
from services.credential_service import CredentialService
from services.error_service import show_error_dialog, get_api_key_error


def _output_box() -> QTextEdit:
    tb = QTextEdit()
    tb.setReadOnly(True)
    tb.setFont(QFont("Consolas", 9))
    return tb


def _btn(label: str, color: str = "#4CAF50") -> QPushButton:
    b = QPushButton(label)
    b.setStyleSheet(
        f"QPushButton{{background:{color};color:white;font-weight:bold;padding:9px 18px;}}"
        f"QPushButton:hover{{background:{color}cc;}}"
        f"QPushButton:disabled{{background:#aaa;}}"
    )
    return b


class OrchestratorTab(QWidget):
    """Tab 1 — run an arbitrary task through the agent orchestrator."""

    def __init__(self, project_root: Path):
        super().__init__()
        self._project_root = project_root
        self._worker: Optional[OrchestratorWorker] = None
        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        layout = QVBoxLayout(self)

        grp = QGroupBox("Task Description")
        form = QFormLayout(grp)
        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText(
            "Describe what you want the AI agents to do…\n\n"
            "Examples:\n"
            "  • Review the authentication module for security issues\n"
            "  • Design a REST API for a todo application\n"
            "  • Refactor the payment service for better testability"
        )
        self.task_input.setMinimumHeight(130)
        form.addRow("Task:", self.task_input)
        self.dry_run = QCheckBox("Dry run  (show plan only, no execution)")
        self.verbose = QCheckBox("Verbose output")
        form.addRow(self.dry_run)
        form.addRow(self.verbose)
        layout.addWidget(grp)

        btn_row = QHBoxLayout()
        self.run_btn    = _btn("▶  Run Orchestrator", "#4CAF50")
        self.cancel_btn = _btn("⏹  Cancel",           "#F44336")
        self.cancel_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        self.cancel_btn.clicked.connect(self._cancel)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)          # indeterminate
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        out_grp = QGroupBox("Output  (auto-redacted)")
        out_layout = QVBoxLayout(out_grp)
        self.output = _output_box()
        out_layout.addWidget(self.output)
        layout.addWidget(out_grp)

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

        self.output.clear()
        self._set_busy(True)
        self._worker = OrchestratorWorker("run", self._project_root, task=task)
        self._worker.progress.connect(self.output.append)
        self._worker.finished.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _cancel(self):
        if self._worker:
            self._worker.cancel()
        self._set_busy(False)
        self.output.append("\n⏹  Cancelled.")

    def _on_done(self, result: dict):
        self._set_busy(False)
        self.output.append("\n" + "─" * 60 + "\n✅  Complete\n" + "─" * 60)

    def _on_error(self, err: dict):
        self._set_busy(False)
        show_error_dialog(self, err)

    # --------------------------------------------------------------- helpers

    def _set_busy(self, active: bool):
        self.run_btn.setEnabled(not active)
        self.cancel_btn.setEnabled(active)
        self.progress.setVisible(active)
