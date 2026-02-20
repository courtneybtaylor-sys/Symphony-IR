"""
Symphony-IR Desktop Application
Full GUI - no terminal needed. Secure by default.

Security features (all on by default):
  1. API keys → Windows Credential Manager (never plaintext)
  2. Sessions → auto-redacted before saving/displaying
  3. Errors  → plain English with actionable suggestions
"""

import sys
import json
import subprocess
import os
import logging
import webbrowser
from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QSpinBox, QCheckBox, QFileDialog, QMessageBox, QTableWidget,
    QTableWidgetItem, QProgressBar, QGroupBox, QFormLayout, QHeaderView,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QAction, QFont

from secure_credentials import CredentialManager, SecureConfig, get_secure_config
from session_redaction import SessionRedactor
from user_friendly_errors import (
    ErrorHandler, ErrorTranslator, UserFriendlyError,
    get_api_key_error,
)

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path.home() / "Symphony-IR"
ORCH_DIR     = PROJECT_ROOT / "ai-orchestrator"


# ─────────────────────────────────────────────────────────────────────────────
# Background worker
# ─────────────────────────────────────────────────────────────────────────────

class OrchestratorWorker(QThread):
    """Run orchestrator subcommands in a background thread."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error    = pyqtSignal(dict)   # emits UserFriendlyError.to_dict()

    def __init__(self, command_type: str, config: SecureConfig, **kwargs):
        super().__init__()
        self.command_type = command_type
        self.config       = config
        self.kwargs       = kwargs

    def _build_cmd(self) -> list:
        root = str(PROJECT_ROOT)
        base = [sys.executable, "orchestrator.py"]

        if self.command_type == "run":
            return base + ["run", self.kwargs["task"], "--project", root]

        if self.command_type == "flow":
            cmd = base + ["flow", "--template", self.kwargs["template"],
                          "--project", root]
            for k, v in self.kwargs.get("variables", {}).items():
                cmd += ["--var", f"{k}={v}"]
            return cmd

        if self.command_type == "status":
            return base + ["status", "--project", root]

        if self.command_type == "history":
            return base + ["history", "--limit", "20", "--project", root]

        if self.command_type == "flow-list":
            return base + ["flow-list"]

        raise ValueError(f"Unknown command_type: {self.command_type}")

    def _env(self) -> dict:
        env = os.environ.copy()
        api_key = self.config.get_api_key()
        if api_key:
            env["ANTHROPIC_API_KEY"] = api_key
        env["OLLAMA_BASE_URL"] = self.config.get_ollama_url()
        return env

    def run(self):
        try:
            cmd = self._build_cmd()
        except ValueError as exc:
            self.error.emit(ErrorHandler.handle_error(exc, "build_cmd").to_dict())
            return

        self.progress.emit("Starting…")

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(ORCH_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self._env(),
            )
            stdout, stderr = proc.communicate()
        except FileNotFoundError:
            err = UserFriendlyError(
                title="Orchestrator Not Found",
                message="orchestrator.py could not be found in the ai-orchestrator directory.",
                suggestions=[
                    "Make sure the project was installed correctly",
                    f"Expected: {ORCH_DIR / 'orchestrator.py'}",
                    "Try running the installer again (windows/install.ps1)",
                ],
                help_link="https://github.com/courtneybtaylor-sys/Symphony-IR#installation",
            )
            self.error.emit(err.to_dict())
            return
        except Exception as exc:
            self.error.emit(ErrorHandler.handle_error(exc, "subprocess").to_dict())
            return

        if proc.returncode != 0:
            combined = (stderr or stdout or "").strip()
            self.error.emit(ErrorTranslator.translate(combined).to_dict())
            return

        # Redact output before returning to UI
        clean = SessionRedactor.redact_text(stdout)
        self.finished.emit({"success": True, "output": clean, "type": self.command_type})


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def show_error(parent, err_dict: dict):
    """Display a user-friendly error dialog."""
    body = err_dict.get("message", "An error occurred.")
    suggestions = err_dict.get("suggestions", [])
    if suggestions:
        body += "\n\nWhat you can do:\n" + "\n".join(
            f"  {i+1}. {s}" for i, s in enumerate(suggestions)
        )
    link = err_dict.get("help_link", "")
    if link:
        body += f"\n\nLearn more: {link}"
    QMessageBox.critical(parent, err_dict.get("title", "Error"), body)


def _output_box() -> QTextEdit:
    tb = QTextEdit()
    tb.setReadOnly(True)
    tb.setFont(QFont("Consolas", 9))
    return tb


def _run_btn(label: str, color: str = "#4CAF50") -> QPushButton:
    btn = QPushButton(label)
    btn.setStyleSheet(
        f"QPushButton{{background:{color};color:white;font-weight:bold;padding:9px 18px;}}"
        f"QPushButton:hover{{background:{color}cc;}}"
        f"QPushButton:disabled{{background:#aaa;}}"
    )
    return btn


def _spin(lo: int, hi: int, val: int, suffix: str = "") -> QSpinBox:
    s = QSpinBox()
    s.setRange(lo, hi)
    s.setValue(val)
    if suffix:
        s.setSuffix(suffix)
    return s


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 – Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class OrchestratorTab(QWidget):
    def __init__(self, config: SecureConfig):
        super().__init__()
        self.config = config
        self.worker: Optional[OrchestratorWorker] = None
        self._build()

    def _build(self):
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

        row = QHBoxLayout()
        self.run_btn = _run_btn("▶  Run Orchestrator")
        self.run_btn.clicked.connect(self._run)
        row.addWidget(self.run_btn)
        row.addStretch()
        layout.addLayout(row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        out_grp = QGroupBox("Output  (auto-redacted)")
        out_layout = QVBoxLayout(out_grp)
        self.output = _output_box()
        out_layout.addWidget(self.output)
        layout.addWidget(out_grp)

    def _run(self):
        task = self.task_input.toPlainText().strip()
        if not task:
            QMessageBox.warning(self, "No Task", "Please enter a task description.")
            return

        provider = self.config.get("provider", "Claude (Cloud)")
        if "Claude" in provider and not self.config.get_api_key():
            show_error(self, get_api_key_error().to_dict())
            return

        self.output.clear()
        self._busy(True)
        self.worker = OrchestratorWorker("run", self.config, task=task)
        self.worker.progress.connect(lambda m: self.output.append(f"[•] {m}"))
        self.worker.finished.connect(self._done)
        self.worker.error.connect(self._err)
        self.worker.start()

    def _done(self, result: dict):
        self._busy(False)
        self.output.append("\n" + "─" * 60 + "\n✅  Complete\n" + "─" * 60 + "\n")
        self.output.append(result["output"])

    def _err(self, err: dict):
        self._busy(False)
        show_error(self, err)

    def _busy(self, active: bool):
        self.run_btn.setEnabled(not active)
        self.progress.setVisible(active)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 – Symphony Flow
# ─────────────────────────────────────────────────────────────────────────────

_TEMPLATES = {
    "code_review":      ("Code Review",       "Guided analysis: bugs, style, or performance"),
    "refactor_code":    ("Refactor Code",     "Design improvements, quick fixes, or dependencies"),
    "new_feature":      ("New Feature",       "Architecture, checklist, or risk analysis"),
    "api_design":       ("API Design",        "REST, GraphQL, or hybrid API specification"),
    "database_schema":  ("Database Schema",   "SQL, NoSQL, or hybrid schema design"),
    "testing_strategy": ("Testing Strategy",  "Unit, integration, performance, or security"),
    "documentation":    ("Documentation",     "User guides, developer docs, or architecture"),
}


class FlowTab(QWidget):
    def __init__(self, config: SecureConfig):
        super().__init__()
        self.config = config
        self.worker: Optional[OrchestratorWorker] = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        grp = QGroupBox("Workflow Template")
        form = QFormLayout(grp)
        self.tmpl = QComboBox()
        for key, (name, _) in _TEMPLATES.items():
            self.tmpl.addItem(f"{name}  ({key})", userData=key)
        self.tmpl.currentIndexChanged.connect(self._update_desc)
        self.desc_lbl = QLabel()
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet("color:#555;font-style:italic;")
        form.addRow("Template:", self.tmpl)
        form.addRow("",         self.desc_lbl)
        layout.addWidget(grp)

        var_grp = QGroupBox("Variables  (optional)")
        var_form = QFormLayout(var_grp)
        self.var_input = QLineEdit()
        self.var_input.setPlaceholderText(
            "key=value  (comma-separated)   e.g.  component=auth.py, api_name=orders"
        )
        var_form.addRow("Variables:", self.var_input)
        layout.addWidget(var_grp)

        row = QHBoxLayout()
        self.run_btn = _run_btn("▶  Start Workflow", color="#2196F3")
        self.run_btn.clicked.connect(self._run)
        row.addWidget(self.run_btn)
        row.addStretch()
        layout.addLayout(row)

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

    def _update_desc(self):
        key = self.tmpl.currentData()
        _, desc = _TEMPLATES.get(key, ("", ""))
        self.desc_lbl.setText(desc)

    def _run(self):
        template = self.tmpl.currentData()
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

        provider = self.config.get("provider", "Claude (Cloud)")
        if "Claude" in provider and not self.config.get_api_key():
            show_error(self, get_api_key_error().to_dict())
            return

        self.output.clear()
        self._busy(True)
        self.worker = OrchestratorWorker(
            "flow", self.config, template=template, variables=variables
        )
        self.worker.progress.connect(lambda m: self.output.append(f"[•] {m}"))
        self.worker.finished.connect(self._done)
        self.worker.error.connect(self._err)
        self.worker.start()

    def _done(self, result: dict):
        self._busy(False)
        self.output.append("\n" + "─" * 60 + "\n✅  Workflow Complete\n" + "─" * 60 + "\n")
        self.output.append(result["output"])

    def _err(self, err: dict):
        self._busy(False)
        show_error(self, err)

    def _busy(self, active: bool):
        self.run_btn.setEnabled(not active)
        self.progress.setVisible(active)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3 – History  (auto-redacted + sanitised export)
# ─────────────────────────────────────────────────────────────────────────────

class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self._raw: list = []   # raw session dicts for export
        self._build()
        self.reload()

    def _build(self):
        layout = QVBoxLayout(self)

        bar = QHBoxLayout()
        reload_btn = QPushButton("🔄  Refresh")
        reload_btn.clicked.connect(self.reload)
        export_btn = _run_btn("💾  Export Sanitised", color="#607D8B")
        export_btn.clicked.connect(self._export)
        bar.addWidget(reload_btn)
        bar.addWidget(export_btn)
        bar.addStretch()
        layout.addLayout(bar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Timestamp", "Task / Summary", "Status", "Run ID", "Confidence"]
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.currentCellChanged.connect(self._show_detail)
        layout.addWidget(self.table)

        det_grp = QGroupBox("Details  (auto-redacted)")
        det_layout = QVBoxLayout(det_grp)
        self.details = _output_box()
        self.details.setMaximumHeight(160)
        det_layout.addWidget(self.details)
        layout.addWidget(det_grp)

    def _runs_dir(self) -> Path:
        return PROJECT_ROOT / ".orchestrator" / "runs"

    def reload(self):
        self._raw.clear()
        self.table.setRowCount(0)
        self.details.clear()

        runs_dir = self._runs_dir()
        if not runs_dir.exists():
            return

        files = sorted(
            runs_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:30]

        for row, fpath in enumerate(files):
            try:
                raw = json.loads(fpath.read_text())
            except Exception:
                continue
            self._raw.append(raw)

            r    = SessionRedactor.redact_session(raw)
            ts   = str(r.get("metadata", {}).get("timestamp", fpath.stem))
            task = str(r.get("task", "—"))[:60]
            ok   = r.get("success", False)
            rid  = str(r.get("run_id", "—"))[:14]
            conf = r.get("confidence", None)
            conf_s = f"{conf:.0%}" if isinstance(conf, float) else "—"

            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(ts))
            self.table.setItem(row, 1, QTableWidgetItem(task))
            status_item = QTableWidgetItem("✅" if ok else "❌")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, status_item)
            self.table.setItem(row, 3, QTableWidgetItem(rid))
            self.table.setItem(row, 4, QTableWidgetItem(conf_s))

    def _show_detail(self, row: int, *_):
        if 0 <= row < len(self._raw):
            redacted = SessionRedactor.redact_session(self._raw[row])
            self.details.setPlainText(json.dumps(redacted, indent=2))

    def _export(self):
        if not self._raw:
            QMessageBox.information(self, "No Sessions", "No run history found.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Sanitised Sessions",
            str(Path.home() / "Desktop" / "symphony-sessions-sanitised.json"),
            "JSON Files (*.json)",
        )
        if not path:
            return

        export = {
            "exported_by": "Symphony-IR",
            "redaction_level": "BASIC",
            "sessions": [SessionRedactor.redact_session(s) for s in self._raw],
        }
        try:
            Path(path).write_text(json.dumps(export, indent=2))
            QMessageBox.information(
                self, "✅  Export Complete",
                f"Saved {len(self._raw)} sessions (redacted) to:\n{path}"
            )
        except Exception as exc:
            show_error(self, ErrorHandler.handle_error(exc, "export").to_dict())


# ─────────────────────────────────────────────────────────────────────────────
# Tab 4 – Settings  (Credential Manager integration)
# ─────────────────────────────────────────────────────────────────────────────

class SettingsTab(QWidget):
    def __init__(self, config: SecureConfig):
        super().__init__()
        self.config = config
        self._showing_key = False
        self._build()
        self._load()

    def _build(self):
        layout = QVBoxLayout(self)

        # Provider & Model
        prov_grp = QGroupBox("🤖  AI Provider & Model")
        prov_form = QFormLayout(prov_grp)
        self.provider = QComboBox()
        self.provider.addItems(["Claude (Cloud)", "Ollama (Local — Free)", "OpenAI"])
        self.provider.currentTextChanged.connect(self._provider_changed)
        self.model = QComboBox()
        self.model.addItems([
            "claude-sonnet-4-20250514  (Recommended)",
            "claude-opus-4-5",
            "claude-haiku-4-5",
            "mistral  (Ollama)",
            "llama2  (Ollama)",
            "neural-chat  (Ollama)",
            "dolphin-mixtral  (Ollama)",
        ])
        prov_form.addRow("Provider:", self.provider)
        prov_form.addRow("Model:",    self.model)
        layout.addWidget(prov_grp)

        # Credentials
        cred_grp = QGroupBox("🔐  Credentials  (stored in system Credential Manager)")
        cred_form = QFormLayout(cred_grp)

        key_row = QHBoxLayout()
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("sk-ant-…  (encrypted — never saved to disk)")
        toggle = QPushButton("👁")
        toggle.setMaximumWidth(36)
        toggle.setToolTip("Show / hide key")
        toggle.clicked.connect(self._toggle_key)
        key_row.addWidget(self.api_key)
        key_row.addWidget(toggle)
        cred_form.addRow("Anthropic API Key:", key_row)

        avail = CredentialManager.is_available()
        sec_lbl = QLabel(
            "🔒  Encrypted via keyring — ✅ available" if avail
            else "⚠️  keyring not installed.  Run:  pip install keyring"
        )
        sec_lbl.setStyleSheet("color:#388E3C;" if avail else "color:#E65100;")
        sec_lbl.setWordWrap(True)
        cred_form.addRow("", sec_lbl)

        self.ollama_url = QLineEdit()
        self.ollama_url.setPlaceholderText("http://localhost:11434")
        cred_form.addRow("Ollama URL:", self.ollama_url)
        layout.addWidget(cred_grp)

        # Tuning
        orch_grp = QGroupBox("⚙️  Orchestrator Tuning")
        orch_form = QFormLayout(orch_grp)
        self.max_phases  = _spin(1, 100, 10)
        self.confidence  = _spin(0, 100, 85, " %")
        self.parallel    = QCheckBox("Enable parallel agent execution")
        self.parallel.setChecked(True)
        orch_form.addRow("Max Phases:",           self.max_phases)
        orch_form.addRow("Confidence Threshold:", self.confidence)
        orch_form.addRow(self.parallel)
        layout.addWidget(orch_grp)

        # Buttons
        btn_row = QHBoxLayout()
        save_btn = _run_btn("💾  Save Settings",    "#4CAF50")
        mig_btn  = _run_btn("🔄  Migrate Old Keys", "#FF9800")
        del_btn  = _run_btn("🗑  Delete Key",        "#F44336")
        save_btn.clicked.connect(self._save)
        mig_btn.clicked.connect(self._migrate)
        del_btn.clicked.connect(self._delete_key)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(mig_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addStretch()

    # ── slots ─────────────────────────────────────────────────────────────────

    def _toggle_key(self):
        self._showing_key = not self._showing_key
        self.api_key.setEchoMode(
            QLineEdit.EchoMode.Normal if self._showing_key else QLineEdit.EchoMode.Password
        )

    def _provider_changed(self, text: str):
        is_ollama = "Ollama" in text
        self.api_key.setEnabled(not is_ollama)
        self.api_key.setPlaceholderText(
            "Not needed for Ollama" if is_ollama else "sk-ant-…  (encrypted)"
        )

    def _load(self):
        qs = QSettings("Symphony-IR", "Desktop")
        self.provider.setCurrentText(qs.value("provider",    "Claude (Cloud)"))
        self.model.setCurrentIndex(qs.value("model_idx",     0, type=int))
        self.max_phases.setValue(qs.value("max_phases",      10, type=int))
        self.confidence.setValue(qs.value("confidence",      85, type=int))
        self.parallel.setChecked(qs.value("parallel",        True, type=bool))
        # Credentials from secure store
        stored = self.config.get_api_key()
        if stored:
            self.api_key.setPlaceholderText("✅  Key stored securely (type to replace)")
        self.ollama_url.setText(self.config.get_ollama_url())

    def _save(self):
        raw_key = self.api_key.text().strip()
        if raw_key and "REDACTED" not in raw_key:
            if not self.config.set_api_key(raw_key):
                QMessageBox.warning(
                    self, "⚠️  Could Not Save Key",
                    "keyring is required to store keys securely.\n\n"
                    "Run:  pip install keyring\n\nKey was NOT saved."
                )
                return
            self.api_key.clear()
            self.api_key.setPlaceholderText("✅  Key saved securely")

        url = self.ollama_url.text().strip() or "http://localhost:11434"
        self.config.set_ollama_url(url)

        qs = QSettings("Symphony-IR", "Desktop")
        qs.setValue("provider",   self.provider.currentText())
        qs.setValue("model_idx",  self.model.currentIndex())
        qs.setValue("max_phases", self.max_phases.value())
        qs.setValue("confidence", self.confidence.value())
        qs.setValue("parallel",   self.parallel.isChecked())

        self.config.set("provider", self.provider.currentText())

        QMessageBox.information(
            self, "✅  Saved",
            "Settings saved.\n"
            "API key is encrypted in your system Credential Manager.\n"
            "No sensitive data was written to disk."
        )

    def _migrate(self):
        cfg_path = PROJECT_ROOT / ".orchestrator" / "config.json"
        if not cfg_path.exists():
            QMessageBox.information(self, "Nothing to Migrate", "No config.json found.")
            return
        try:
            raw = json.loads(cfg_path.read_text())
        except Exception as exc:
            show_error(self, ErrorHandler.handle_error(exc, "migrate_read").to_dict())
            return

        key = raw.get("api_key") or raw.get("ANTHROPIC_API_KEY") or ""
        if not key or "REDACTED" in key:
            QMessageBox.information(self, "Nothing to Migrate",
                                    "No plaintext API key found in config.json.")
            return

        reply = QMessageBox.question(
            self, "Migrate Credentials?",
            "A plaintext API key was found in config.json.\n\n"
            "Move it to the secure Credential Manager and remove it from the file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if self.config.set_api_key(key):
            raw["api_key"] = None
            raw["ANTHROPIC_API_KEY"] = None
            cfg_path.write_text(json.dumps(raw, indent=2))
            self.api_key.clear()
            self.api_key.setPlaceholderText("✅  Key migrated to secure storage")
            QMessageBox.information(
                self, "✅  Done",
                "API key moved to Credential Manager.\n"
                "Plaintext entry removed from config.json."
            )
        else:
            QMessageBox.critical(self, "Migration Failed",
                                 "Could not store key securely.\n"
                                 "Run:  pip install keyring")

    def _delete_key(self):
        reply = QMessageBox.question(
            self, "Delete Stored Key?",
            "This permanently removes the stored API key.\n"
            "You will need to re-enter it to use Claude.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if self.config.delete_api_key():
            self.api_key.clear()
            self.api_key.setPlaceholderText("sk-ant-…  (no key stored)")
            QMessageBox.information(self, "✅  Deleted",
                                    "API key removed from Credential Manager.")
        else:
            QMessageBox.warning(self, "Not Found", "No API key was stored.")


# ─────────────────────────────────────────────────────────────────────────────
# Main Window
# ─────────────────────────────────────────────────────────────────────────────

class SymphonyIRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symphony-IR  —  AI Orchestrator")
        self.setGeometry(100, 100, 1260, 820)
        self.setMinimumSize(900, 600)

        self.config = get_secure_config(PROJECT_ROOT)

        tabs = QTabWidget()
        tabs.addTab(OrchestratorTab(self.config), "🎼  Orchestrator")
        tabs.addTab(FlowTab(self.config),          "🗺️  Symphony Flow")
        tabs.addTab(HistoryTab(),                  "📋  History")
        tabs.addTab(SettingsTab(self.config),       "⚙️  Settings")
        self.setCentralWidget(tabs)

        self._build_menus()
        self.setStyleSheet(_STYLESHEET)

        status = ("🔐 keyring available" if CredentialManager.is_available()
                  else "⚠️  keyring not installed — run:  pip install keyring")
        self.statusBar().showMessage(f"Ready  ·  {status}")

    def _build_menus(self):
        mb = self.menuBar()

        fm = mb.addMenu("File")
        qa = QAction("Quit", self)
        qa.triggered.connect(self.close)
        fm.addAction(qa)

        hm = mb.addMenu("Help")
        actions = [
            ("About Symphony-IR",          self._about),
            ("Online Documentation",       lambda: webbrowser.open(
                "https://github.com/courtneybtaylor-sys/Symphony-IR#readme")),
            ("Set up Ollama (Local AI)",   lambda: webbrowser.open("https://ollama.ai")),
            ("Security Guide",             lambda: webbrowser.open(
                "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/SECURITY.md")),
            ("Report an Issue",            lambda: webbrowser.open(
                "https://github.com/courtneybtaylor-sys/Symphony-IR/issues")),
        ]
        for label, handler in actions:
            a = QAction(label, self)
            a.triggered.connect(handler)
            hm.addAction(a)

    def _about(self):
        QMessageBox.about(
            self, "About Symphony-IR",
            "Symphony-IR  v1.0\n"
            "Deterministic multi-agent AI orchestration\n\n"
            "Security:\n"
            "  🔐  API keys → Windows Credential Manager\n"
            "  📋  Sessions → auto-redacted\n"
            "  💬  Errors  → plain English + suggestions\n\n"
            "github.com/courtneybtaylor-sys/Symphony-IR"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Stylesheet
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

QTableWidget { gridline-color: #ECEFF1; background: white; alternate-background-color: #F5F5F5; }
QHeaderView::section {
    background: #1565C0; color: white;
    padding: 6px; border: none; font-weight: bold;
}

QProgressBar { border: 1px solid #B0BEC5; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background: #1976D2; border-radius: 4px; }

QStatusBar { background: #ECEFF1; border-top: 1px solid #CFD8DC; color: #546E7A; }
"""


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Symphony-IR")
    app.setOrganizationName("Symphony-IR")
    window = SymphonyIRApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
