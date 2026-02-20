"""
History Tab — Tab 3.

Displays the last 30 run sessions from .orchestrator/runs/*.json.
All data is auto-redacted before display.  Provides a sanitised export.

Robustness improvements
-----------------------
* Atomic writes via temp-file + rename (prevents partial writes on crash).
* Corrupted JSON files are skipped with a warning in the status bar rather
  than crashing the whole tab.
* Export uses the same atomic-write pattern.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFileDialog, QGroupBox, QHBoxLayout, QHeaderView, QMessageBox,
    QPushButton, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
)

from services.redaction_service import RedactionService
from services.error_service import ErrorHandler, show_error_dialog

logger = logging.getLogger(__name__)


def _output_box() -> QTextEdit:
    tb = QTextEdit()
    tb.setReadOnly(True)
    tb.setFont(QFont("Consolas", 9))
    return tb


def _btn(label: str, color: str = "#607D8B") -> QPushButton:
    b = QPushButton(label)
    b.setStyleSheet(
        f"QPushButton{{background:{color};color:white;font-weight:bold;padding:8px 16px;}}"
        f"QPushButton:hover{{background:{color}cc;}}"
    )
    return b


def atomic_write_json(path: Path, data) -> None:
    """
    Write *data* as JSON to *path* atomically.

    Writes to a sibling temp file first, then renames it into place so the
    original is never partially overwritten if the process crashes mid-write.
    """
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp, path)   # atomic on POSIX; best-effort on Windows
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class HistoryTab(QWidget):
    """Tab 3 — browse and export session history."""

    def __init__(self, project_root: Path):
        super().__init__()
        self._project_root = project_root
        self._raw: list = []
        self._build_ui()
        self.reload()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        layout = QVBoxLayout(self)

        bar = QHBoxLayout()
        reload_btn = QPushButton("🔄  Refresh")
        reload_btn.clicked.connect(self.reload)
        export_btn = _btn("💾  Export Sanitised")
        export_btn.clicked.connect(self._export)
        bar.addWidget(reload_btn)
        bar.addWidget(export_btn)
        bar.addStretch()
        layout.addLayout(bar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Timestamp", "Task / Summary", "Status", "Run ID", "Confidence"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.currentCellChanged.connect(self._show_detail)
        layout.addWidget(self.table)

        det_grp = QGroupBox("Details  (auto-redacted)")
        det_layout = QVBoxLayout(det_grp)
        self.details = _output_box()
        self.details.setMaximumHeight(160)
        det_layout.addWidget(self.details)
        layout.addWidget(det_grp)

    # ---------------------------------------------------------------- slots

    def reload(self):
        """Reload session list from disk."""
        self._raw.clear()
        self.table.setRowCount(0)
        self.details.clear()

        runs_dir = self._project_root / ".orchestrator" / "runs"
        if not runs_dir.exists():
            return

        files = sorted(
            runs_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:30]

        skipped = 0
        for row, fpath in enumerate(files):
            try:
                raw = json.loads(fpath.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                logger.warning("Skipping corrupted session file: %s", fpath.name)
                skipped += 1
                continue
            except OSError as exc:
                logger.warning("Cannot read %s: %s", fpath.name, exc)
                skipped += 1
                continue

            self._raw.append(raw)
            r    = RedactionService.redact_session(raw)
            ts   = str(r.get("metadata", {}).get("timestamp", fpath.stem))
            task = str(r.get("task", "—"))[:60]
            ok   = r.get("success", False)
            rid  = str(r.get("run_id", "—"))[:14]
            conf = r.get("confidence", None)
            conf_s = f"{conf:.0%}" if isinstance(conf, float) else "—"

            self.table.insertRow(row - skipped)
            idx = row - skipped
            self.table.setItem(idx, 0, QTableWidgetItem(ts))
            self.table.setItem(idx, 1, QTableWidgetItem(task))
            status_item = QTableWidgetItem("✅" if ok else "❌")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(idx, 2, status_item)
            self.table.setItem(idx, 3, QTableWidgetItem(rid))
            self.table.setItem(idx, 4, QTableWidgetItem(conf_s))

        if skipped:
            logger.warning("%d corrupted session file(s) skipped", skipped)

    def _show_detail(self, row: int, *_):
        if 0 <= row < len(self._raw):
            redacted = RedactionService.redact_session(self._raw[row])
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
            "sessions": [RedactionService.redact_session(s) for s in self._raw],
        }
        try:
            atomic_write_json(Path(path), export)
            QMessageBox.information(
                self, "✅  Export Complete",
                f"Saved {len(self._raw)} sessions (redacted) to:\n{path}"
            )
        except Exception as exc:
            show_error_dialog(self, ErrorHandler.handle_error(exc, "export").to_dict())
