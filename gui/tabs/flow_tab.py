"""
Symphony Flow Tab — Tab 2.

Runs a bounded decision-tree workflow driven by one of the bundled YAML
templates.  Variables can be injected at runtime via a comma-separated
key=value string.

UX improvements
---------------
* Cancel button.
* Double-submit blocked (Run button disabled while worker is active).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QGroupBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QProgressBar, QPushButton, QTextEdit, QVBoxLayout, QWidget,
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


def _output_box() -> QTextEdit:
    tb = QTextEdit()
    tb.setReadOnly(True)
    tb.setFont(QFont("Consolas", 9))
    return tb


def _btn(label: str, color: str = "#2196F3") -> QPushButton:
    b = QPushButton(label)
    b.setStyleSheet(
        f"QPushButton{{background:{color};color:white;font-weight:bold;padding:9px 18px;}}"
        f"QPushButton:hover{{background:{color}cc;}}"
        f"QPushButton:disabled{{background:#aaa;}}"
    )
    return b


class FlowTab(QWidget):
    """Tab 2 — run a Symphony Flow workflow template."""

    def __init__(self, project_root: Path):
        super().__init__()
        self._project_root = project_root
        self._worker: Optional[OrchestratorWorker] = None
        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        layout = QVBoxLayout(self)

        tmpl_grp = QGroupBox("Workflow Template")
        tmpl_form = QFormLayout(tmpl_grp)
        self.tmpl_cb = QComboBox()
        for key, (name, _) in _TEMPLATES.items():
            self.tmpl_cb.addItem(f"{name}  ({key})", userData=key)
        self.tmpl_cb.currentIndexChanged.connect(self._update_desc)
        self.desc_lbl = QLabel()
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet("color:#555;font-style:italic;")
        tmpl_form.addRow("Template:", self.tmpl_cb)
        tmpl_form.addRow("",         self.desc_lbl)
        layout.addWidget(tmpl_grp)

        var_grp = QGroupBox("Variables  (optional)")
        var_form = QFormLayout(var_grp)
        self.var_input = QLineEdit()
        self.var_input.setPlaceholderText(
            "key=value  (comma-separated)   e.g.  component=auth.py, api_name=orders"
        )
        var_form.addRow("Variables:", self.var_input)
        layout.addWidget(var_grp)

        btn_row = QHBoxLayout()
        self.run_btn    = _btn("▶  Start Workflow", "#2196F3")
        self.cancel_btn = _btn("⏹  Cancel",         "#F44336")
        self.cancel_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        self.cancel_btn.clicked.connect(self._cancel)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        out_grp = QGroupBox("Workflow Output  (auto-redacted)")
        out_layout = QVBoxLayout(out_grp)
        self.output = _output_box()
        out_layout.addWidget(self.output)
        layout.addWidget(out_grp)

        self._update_desc()

    # ---------------------------------------------------------------- slots

    def _update_desc(self):
        key = self.tmpl_cb.currentData()
        _, desc = _TEMPLATES.get(key, ("", ""))
        self.desc_lbl.setText(desc)

    def _run(self):
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

        self.output.clear()
        self._set_busy(True)
        self._worker = OrchestratorWorker(
            "flow", self._project_root, template=template, variables=variables
        )
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
        self.output.append("\n" + "─" * 60 + "\n✅  Workflow Complete\n" + "─" * 60)

    def _on_error(self, err: dict):
        self._set_busy(False)
        show_error_dialog(self, err)

    # --------------------------------------------------------------- helpers

    def _set_busy(self, active: bool):
        self.run_btn.setEnabled(not active)
        self.cancel_btn.setEnabled(active)
        self.progress.setVisible(active)
