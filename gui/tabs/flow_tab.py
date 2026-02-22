"""
Symphony Flow Tab — Tab 2.

Runs a bounded decision-tree workflow driven by one of the bundled YAML
templates.  Variables can be injected at runtime via a comma-separated
key=value string.

Uses custom widgets with "Deterministic Elegance" design system.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QHBoxLayout, QWidget, QLabel

from widgets import (
    GradientCard,
    StyledComboBox,
    GradientBorderedInput,
    PrimaryButton,
    DangerButton,
    SyntaxHighlightedLog,
    ProgressCard,
    SubtitleLabel,
)
from services.orchestrator_service import OrchestratorWorker
from services.credential_service import CredentialService
from services.error_service import show_error_dialog, get_api_key_error


# Template registry — key: (display_name, description)
_TEMPLATES: dict[str, tuple[str, str]] = {
    "code_review":      ("Code Review",       "Guided analysis: bugs, style, or performance"),
    "refactor_code":    ("Refactor Code",     "Design improvements, quick fixes, or dependencies"),
    "new_feature":      ("New Feature",       "Architecture, checklist, or risk analysis"),
    "api_design":       ("API Design",        "REST, GraphQL, or hybrid API specification"),
    "database_schema":  ("Database Schema",   "SQL, NoSQL, or hybrid schema design"),
    "testing_strategy": ("Testing Strategy",  "Unit, integration, performance, or security"),
    "documentation":    ("Documentation",     "User guides, developer docs, or architecture"),
}


class FlowTab(QWidget):
    """Tab 2 — run a Symphony Flow workflow template."""

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

        # Template selection card
        tmpl_card = GradientCard("Select Workflow Template")

        self.tmpl_cb = StyledComboBox()
        for key, (name, _) in _TEMPLATES.items():
            self.tmpl_cb.addItem(f"{name}  ({key})", userData=key)
        self.tmpl_cb.currentIndexChanged.connect(self._update_desc)
        tmpl_card.add_widget(self.tmpl_cb)

        # Description label
        self.desc_lbl = SubtitleLabel()
        self.desc_lbl.setWordWrap(True)
        tmpl_card.add_widget(self.desc_lbl)

        main_layout.addWidget(tmpl_card)

        # Variables input card
        var_card = GradientCard("Variables (Optional)")

        self.var_input = GradientBorderedInput()
        self.var_input.setPlaceholderText(
            "key=value  (comma-separated)   e.g.  component=auth.py, api_name=orders"
        )
        var_card.add_widget(self.var_input)

        main_layout.addWidget(var_card)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(8)

        self.run_btn = PrimaryButton("▶ Start Workflow")
        self.cancel_btn = DangerButton("⏹ Cancel")
        self.cancel_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        self.cancel_btn.clicked.connect(self._cancel)

        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()

        main_layout.addLayout(btn_row)

        # Output section
        self.output = SyntaxHighlightedLog()
        main_layout.addWidget(self.output)

        # Progress indicator
        self.progress_card = ProgressCard("Workflow Status")
        self.progress_card.set_progress(0, "idle")
        main_layout.addWidget(self.progress_card)

        self._update_desc()

    # ---------------------------------------------------------------- slots

    def _update_desc(self):
        """Update description label based on selected template."""
        key = self.tmpl_cb.currentData()
        _, desc = _TEMPLATES.get(key, ("", ""))
        self.desc_lbl.setText(desc)

    def _run(self):
        """Start the workflow."""
        template = self.tmpl_cb.currentData()
        variables: Dict[str, str] = {}

        raw = self.var_input.text().strip()
        if raw:
            for part in raw.split(","):
                part = part.strip()
                if "=" not in part:
                    QMessageBox.warning(
                        self, "Invalid Variable",
                        f"Variables must be  key=value\n\nGot: {part!r}"
                    )
                    return
                k, v = part.split("=", 1)
                variables[k.strip()] = v.strip()

        qs = QSettings("Symphony-IR", "Desktop")
        provider = qs.value("provider", "Claude (Cloud)")
        if "Claude" in provider and not CredentialService.get_api_key():
            show_error_dialog(self, get_api_key_error().to_dict())
            return

        self.output.clear_logs()
        self.output.append_log("Starting workflow...", "info")
        self._set_busy(True)
        self._worker = OrchestratorWorker(
            "flow", self._project_root, template=template, variables=variables
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, text: str):
        """Handle progress updates from worker."""
        if "error" in text.lower() or "failed" in text.lower():
            level = "error"
        elif "success" in text.lower() or "complete" in text.lower():
            level = "success"
        elif "warning" in text.lower():
            level = "warning"
        else:
            level = "info"
        self.output.append_log(text, level)
        self.progress_card.set_progress(50, "running")

    def _cancel(self):
        """Cancel the running workflow."""
        if self._worker:
            self._worker.cancel()
        self._set_busy(False)
        self.output.append_log("Cancelled by user.", "warning")
        self.progress_card.set_progress(0, "idle")

    def _on_done(self, result: dict):
        """Handle workflow completion."""
        self._set_busy(False)
        self.output.append_log("✅ Workflow complete", "success")
        self.progress_card.set_progress(100, "success")

    def _on_error(self, err: dict):
        """Handle workflow errors."""
        self._set_busy(False)
        self.output.append_log("❌ Error during workflow", "error")
        self.progress_card.set_progress(0, "error")
        show_error_dialog(self, err)

    # --------------------------------------------------------------- helpers

    def _set_busy(self, active: bool):
        """Update UI state when workflow is running/idle."""
        self.run_btn.setEnabled(not active)
        self.cancel_btn.setEnabled(active)
        self.tmpl_cb.setEnabled(not active)
        self.var_input.setReadOnly(active)

        if active:
            self.progress_card.set_progress(0, "running")
        else:
            self.progress_card.set_progress(0, "idle")
