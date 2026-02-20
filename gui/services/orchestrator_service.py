"""
Orchestrator subprocess management — isolated from UI.

Responsibilities
----------------
* Build the correct command array for each operation type.
* Inject credentials (from CredentialService) into the subprocess env only —
  never logged, never stored in process args.
* Stream stdout line-by-line so the UI can update in real time.
* Redact output before emitting to the UI (RedactionService).
* Translate stderr to a user-friendly error (ErrorTranslator).
* Support graceful cancellation via cancel().
"""

from __future__ import annotations

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

from services.credential_service import CredentialService
from services.redaction_service import RedactionService
from user_friendly_errors import ErrorHandler, ErrorTranslator, UserFriendlyError

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------- paths
# Resolved at import time so every worker agrees on the location.
_GUI_DIR     = Path(__file__).parent.parent          # gui/
_PROJECT_ROOT = _GUI_DIR.parent                       # Symphony-IR/
_ORCH_DIR    = _PROJECT_ROOT / "ai-orchestrator"


class OrchestratorWorker(QThread):
    """
    Background QThread for all orchestrator subprocess calls.

    Signals
    -------
    progress(str)     — incremental output lines (already redacted)
    finished(dict)    — {"success": True, "output": str, "type": str}
    error(dict)       — UserFriendlyError.to_dict()
    """

    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error    = pyqtSignal(dict)

    def __init__(
        self,
        command_type: str,
        project_root: Optional[Path] = None,
        **kwargs,
    ):
        super().__init__()
        self.command_type = command_type
        self.project_root = project_root or _PROJECT_ROOT
        self.kwargs       = kwargs
        self._proc: Optional[subprocess.Popen] = None
        self._cancelled = False

    # ---------------------------------------------------------------- public

    def cancel(self) -> None:
        """Request cancellation. Terminates the subprocess if running."""
        self._cancelled = True
        if self._proc and self._proc.poll() is None:
            logger.debug("Cancelling orchestrator subprocess (pid=%s)", self._proc.pid)
            try:
                self._proc.terminate()
            except OSError:
                pass  # process already gone

    # --------------------------------------------------------------- private

    def _build_cmd(self) -> list:
        root = str(self.project_root)
        base = [sys.executable, "orchestrator.py"]

        ct = self.command_type
        if ct == "run":
            return base + ["run", self.kwargs["task"], "--project", root]
        if ct == "flow":
            cmd = base + ["flow", "--template", self.kwargs["template"],
                          "--project", root]
            for k, v in self.kwargs.get("variables", {}).items():
                cmd += ["--var", f"{k}={v}"]
            return cmd
        if ct == "status":
            return base + ["status", "--project", root]
        if ct == "history":
            return base + ["history", "--limit", "20", "--project", root]
        if ct == "flow-list":
            return base + ["flow-list"]

        raise ValueError(f"Unknown command_type: {ct!r}")

    def _build_env(self) -> dict:
        """Copy os.environ and inject credentials — nothing goes into args."""
        env = os.environ.copy()
        api_key = CredentialService.get_api_key()
        if api_key:
            env["ANTHROPIC_API_KEY"] = api_key
        env["OLLAMA_BASE_URL"] = CredentialService.get_ollama_url()
        return env

    def run(self):  # QThread entry point
        if self._cancelled:
            return

        try:
            cmd = self._build_cmd()
        except ValueError as exc:
            self.error.emit(ErrorHandler.handle_error(exc, "build_cmd").to_dict())
            return

        self.progress.emit("Starting…")

        try:
            self._proc = subprocess.Popen(
                cmd,
                cwd=str(_ORCH_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self._build_env(),
            )
        except FileNotFoundError:
            err = UserFriendlyError(
                title="Orchestrator Not Found",
                message="orchestrator.py could not be found in the ai-orchestrator directory.",
                suggestions=[
                    "Make sure the project was installed correctly",
                    f"Expected: {_ORCH_DIR / 'orchestrator.py'}",
                    "Try running the installer again (windows/install.ps1)",
                ],
                help_link="https://github.com/courtneybtaylor-sys/Symphony-IR#installation",
            )
            self.error.emit(err.to_dict())
            return
        except Exception as exc:
            self.error.emit(ErrorHandler.handle_error(exc, "subprocess_launch").to_dict())
            return

        # Stream stdout line by line so the UI updates in real time.
        output_lines: list[str] = []
        for raw_line in self._proc.stdout:
            if self._cancelled:
                self._proc.terminate()
                self.error.emit(UserFriendlyError(
                    title="Cancelled",
                    message="The operation was cancelled.",
                    suggestions=["You can start a new task at any time."],
                ).to_dict())
                return
            line = RedactionService.redact_text(raw_line.rstrip())
            output_lines.append(line)
            self.progress.emit(line)

        stderr_output = self._proc.stderr.read()
        self._proc.wait()

        if self._cancelled:
            return

        if self._proc.returncode != 0:
            combined = (stderr_output or "".join(output_lines) or "").strip()
            logger.error(
                "Orchestrator failed (rc=%s): %s", self._proc.returncode, combined
            )
            self.error.emit(ErrorTranslator.translate(combined).to_dict())
            return

        full_output = "\n".join(output_lines)
        self.finished.emit({
            "success": True,
            "output": full_output,
            "type": self.command_type,
        })
