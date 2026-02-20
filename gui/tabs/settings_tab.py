"""
Settings Tab — Tab 4.

Manages AI provider selection, API credentials, and orchestrator tuning.
Credentials are stored exclusively in the OS secret store (keyring) —
nothing sensitive ever goes to disk.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from services.credential_service import CredentialService
from services.error_service import ErrorHandler, show_error_dialog

logger = logging.getLogger(__name__)

_QS_ORG  = "Symphony-IR"
_QS_APP  = "Desktop"


def _spin(lo: int, hi: int, val: int, suffix: str = "") -> QSpinBox:
    s = QSpinBox()
    s.setRange(lo, hi)
    s.setValue(val)
    if suffix:
        s.setSuffix(suffix)
    return s


def _btn(label: str, color: str = "#4CAF50") -> QPushButton:
    b = QPushButton(label)
    b.setStyleSheet(
        f"QPushButton{{background:{color};color:white;font-weight:bold;padding:9px 18px;}}"
        f"QPushButton:hover{{background:{color}cc;}}"
    )
    return b


class SettingsTab(QWidget):
    """Tab 4 — provider, credentials, and tuning."""

    def __init__(self, project_root: Path):
        super().__init__()
        self._project_root = project_root
        self._showing_key  = False
        self._build_ui()
        self._load()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Provider & Model
        prov_grp = QGroupBox("🤖  AI Provider & Model")
        prov_form = QFormLayout(prov_grp)
        self.provider = QComboBox()
        self.provider.addItems(["Claude (Cloud)", "Ollama (Local — Free)", "OpenAI"])
        self.provider.currentTextChanged.connect(self._on_provider_changed)
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
        self._eye_btn = QPushButton("👁")
        self._eye_btn.setMaximumWidth(36)
        self._eye_btn.setToolTip("Show / hide key")
        self._eye_btn.clicked.connect(self._toggle_key_vis)
        key_row.addWidget(self.api_key)
        key_row.addWidget(self._eye_btn)
        cred_form.addRow("Anthropic API Key:", key_row)

        avail = CredentialService.available()
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

        # Orchestrator tuning
        orch_grp = QGroupBox("⚙️  Orchestrator Tuning")
        orch_form = QFormLayout(orch_grp)
        self.max_phases = _spin(1, 100, 10)
        self.confidence = _spin(0, 100, 85, " %")
        self.parallel   = QCheckBox("Enable parallel agent execution")
        self.parallel.setChecked(True)
        orch_form.addRow("Max Phases:",           self.max_phases)
        orch_form.addRow("Confidence Threshold:", self.confidence)
        orch_form.addRow(self.parallel)
        layout.addWidget(orch_grp)

        # Action buttons
        btn_row = QHBoxLayout()
        save_btn = _btn("💾  Save Settings",    "#4CAF50")
        mig_btn  = _btn("🔄  Migrate Old Keys", "#FF9800")
        del_btn  = _btn("🗑  Delete Key",        "#F44336")
        save_btn.clicked.connect(self._save)
        mig_btn.clicked.connect(self._migrate)
        del_btn.clicked.connect(self._delete_key)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(mig_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addStretch()

    # ---------------------------------------------------------------- slots

    def _toggle_key_vis(self):
        self._showing_key = not self._showing_key
        self.api_key.setEchoMode(
            QLineEdit.EchoMode.Normal if self._showing_key
            else QLineEdit.EchoMode.Password
        )

    def _on_provider_changed(self, text: str):
        is_ollama = "Ollama" in text
        self.api_key.setEnabled(not is_ollama)
        self.api_key.setPlaceholderText(
            "Not needed for Ollama" if is_ollama
            else "sk-ant-…  (encrypted — never saved to disk)"
        )

    def _load(self):
        qs = QSettings(_QS_ORG, _QS_APP)
        self.provider.setCurrentText(qs.value("provider", "Claude (Cloud)"))
        self.model.setCurrentIndex(qs.value("model_idx", 0, type=int))
        self.max_phases.setValue(qs.value("max_phases", 10, type=int))
        self.confidence.setValue(qs.value("confidence", 85, type=int))
        self.parallel.setChecked(qs.value("parallel", True, type=bool))
        if CredentialService.has(CredentialService.available() and "anthropic_api_key"):
            self.api_key.setPlaceholderText("✅  Key stored securely (type to replace)")
        self.ollama_url.setText(CredentialService.get_ollama_url())

    def _save(self):
        raw_key = self.api_key.text().strip()
        if raw_key and "REDACTED" not in raw_key:
            if not CredentialService.set_api_key(raw_key):
                QMessageBox.warning(
                    self, "⚠️  Could Not Save Key",
                    "keyring is required to store keys securely.\n\n"
                    "Run:  pip install keyring\n\nKey was NOT saved."
                )
                return
            self.api_key.clear()
            self.api_key.setPlaceholderText("✅  Key saved securely")

        url = self.ollama_url.text().strip() or "http://localhost:11434"
        CredentialService.set_ollama_url(url)

        qs = QSettings(_QS_ORG, _QS_APP)
        qs.setValue("provider",   self.provider.currentText())
        qs.setValue("model_idx",  self.model.currentIndex())
        qs.setValue("max_phases", self.max_phases.value())
        qs.setValue("confidence", self.confidence.value())
        qs.setValue("parallel",   self.parallel.isChecked())

        QMessageBox.information(
            self, "✅  Saved",
            "Settings saved.\n"
            "API key is encrypted in your system Credential Manager.\n"
            "No sensitive data was written to disk."
        )

    def _migrate(self):
        cfg_path = self._project_root / ".orchestrator" / "config.json"
        if not cfg_path.exists():
            QMessageBox.information(self, "Nothing to Migrate",
                                    "No config.json found.")
            return
        try:
            raw = json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception as exc:
            show_error_dialog(self, ErrorHandler.handle_error(exc, "migrate_read").to_dict())
            return

        migrated, _ = CredentialService.migrate_from_config(raw)
        if migrated == 0:
            QMessageBox.information(self, "Nothing to Migrate",
                                    "No plaintext credentials found in config.json.")
            return

        # Persist the sanitised config (nulled-out keys)
        try:
            cfg_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.error("Could not save sanitised config: %s", exc)

        self.api_key.clear()
        self.api_key.setPlaceholderText("✅  Key migrated to secure storage")
        QMessageBox.information(
            self, "✅  Done",
            f"Migrated {migrated} credential(s) to Credential Manager.\n"
            "Plaintext values removed from config.json."
        )

    def _delete_key(self):
        reply = QMessageBox.question(
            self, "Delete Stored Key?",
            "This permanently removes the stored API key.\n"
            "You will need to re-enter it to use Claude.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if CredentialService.delete_api_key():
            self.api_key.clear()
            self.api_key.setPlaceholderText("sk-ant-…  (no key stored)")
            QMessageBox.information(self, "✅  Deleted",
                                    "API key removed from Credential Manager.")
        else:
            QMessageBox.warning(self, "Not Found", "No API key was stored.")
