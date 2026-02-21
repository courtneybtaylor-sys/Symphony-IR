"""
Error service — file logging + re-export of friendly-error helpers.

Design
------
* Full stack traces go to the log file (.orchestrator/logs/symphony.log).
* Only the friendly summary reaches the UI.
* Call setup_file_logging() once at startup from main.py.
* All other modules import ErrorTranslator / ErrorHandler from here so there
  is a single import path for error handling.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

# Re-export the public API so callers only need one import.
from user_friendly_errors import (         # noqa: F401  (re-export)
    UserFriendlyError,
    ErrorSeverity,
    ErrorTranslator,
    ErrorHandler,
    get_api_key_error,
    get_ollama_not_running_error,
    get_model_not_available_error,
    get_internet_error,
)

logger = logging.getLogger(__name__)

_LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s"
_MAX_BYTES  = 5 * 1024 * 1024   # 5 MB per file
_BACKUP_COUNT = 3


def setup_file_logging(
    project_root: Path,
    level: int = logging.DEBUG,
) -> Path:
    """
    Attach a rotating file handler to the root logger.

    Parameters
    ----------
    project_root:
        The Symphony-IR project root.  Log files are written to
        ``<project_root>/.orchestrator/logs/symphony.log``.
    level:
        Logging level for the file handler (default DEBUG so full traces
        are captured even if the console handler is at INFO).

    Returns
    -------
    Path to the log file.
    """
    log_dir = project_root / ".orchestrator" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "symphony.log"

    root_logger = logging.getLogger()

    # Avoid adding duplicate handlers if called more than once.
    for h in root_logger.handlers:
        if isinstance(h, logging.handlers.RotatingFileHandler):
            if getattr(h, "baseFilename", None) == str(log_file):
                return log_file

    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    root_logger.addHandler(handler)

    logger.info("File logging initialised → %s", log_file)
    return log_file


def show_error_dialog(parent, err_dict: dict) -> None:
    """
    Show a user-friendly error dialog.

    Uses QMessageBox with:
    - Severity-appropriate icon (Critical / Warning / Information)
    - Numbered suggestions in the body
    - Clickable help link (opens browser)
    - "Copy details" button for support
    """
    from PyQt6.QtWidgets import QMessageBox, QPushButton
    from PyQt6.QtCore import QUrl
    from PyQt6.QtGui import QDesktopServices

    severity = err_dict.get("severity", "ERROR")
    title    = err_dict.get("title", "Error")
    body     = err_dict.get("message", "An error occurred.")

    suggestions = err_dict.get("suggestions", [])
    if suggestions:
        body += "\n\nWhat you can do:\n" + "\n".join(
            f"  {i+1}. {s}" for i, s in enumerate(suggestions)
        )

    link = err_dict.get("help_link", "")
    if link:
        body += f"\n\nLearn more: {link}"

    # Choose icon based on severity
    if severity in ("CRITICAL", "ERROR"):
        icon = QMessageBox.Icon.Critical
    elif severity == "WARNING":
        icon = QMessageBox.Icon.Warning
    else:
        icon = QMessageBox.Icon.Information

    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(body)
    box.setIcon(icon)
    box.addButton(QMessageBox.StandardButton.Ok)

    # Add "Open Docs" button if there is a help link
    docs_btn = None
    if link:
        docs_btn = box.addButton("Open Docs", QMessageBox.ButtonRole.HelpRole)

    # Add "Copy Error" button so users can paste it into a bug report
    copy_btn = box.addButton("Copy Error", QMessageBox.ButtonRole.ActionRole)

    box.exec()

    clicked = box.clickedButton()
    if docs_btn and clicked == docs_btn:
        QDesktopServices.openUrl(QUrl(link))
    elif clicked == copy_btn:
        from PyQt6.QtWidgets import QApplication
        clipboard_text = f"{title}\n\n{err_dict.get('message', '')}"
        if suggestions:
            clipboard_text += "\n\nSuggestions:\n" + "\n".join(
                f"  {i+1}. {s}" for i, s in enumerate(suggestions)
            )
        QApplication.clipboard().setText(clipboard_text)
