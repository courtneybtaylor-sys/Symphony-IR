"""
Symphony-IR Unified Configuration Manager

Single source of truth for user configuration shared between:
  - GUI desktop app  (gui/setup_wizard.py)
  - CLI orchestrator (ai-orchestrator/orchestrator.py)
  - CLI setup wizard (ai-orchestrator/setup_wizard_cli.py)

Config is stored at ~/.symphonyir/config.json
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


CONFIG_DIR  = Path.home() / ".symphonyir"
CONFIG_FILE = CONFIG_DIR / "config.json"

_DEFAULTS: Dict[str, Any] = {
    "setup_complete":  False,
    "setup_version":   "1.0",
    "provider":        None,          # "claude" | "ollama" | "both"
    "claude_api_key":  None,
    "ollama_host":     "http://localhost:11434",
    "model":           "claude-sonnet-4-20250514",
}


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def load() -> Dict[str, Any]:
    """Load config from disk.  Returns defaults merged with stored values."""
    cfg = dict(_DEFAULTS)
    if CONFIG_FILE.exists():
        try:
            stored = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            cfg.update(stored)
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def save(cfg: Dict[str, Any]) -> None:
    """Persist *cfg* to disk, creating the config directory if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def get(key: str, default: Any = None) -> Any:
    """Read a single key from config."""
    return load().get(key, default)


def set_key(key: str, value: Any) -> None:
    """Update a single key and persist."""
    cfg = load()
    cfg[key] = value
    save(cfg)


def is_setup_complete() -> bool:
    """Return True if the user has completed first-run setup."""
    return bool(get("setup_complete", False))


def get_api_key() -> Optional[str]:
    """
    Return the Anthropic API key.
    Checks (in order): config file → ANTHROPIC_API_KEY env var.
    """
    key = get("claude_api_key")
    if key:
        return key
    return os.environ.get("ANTHROPIC_API_KEY")


def get_ollama_host() -> str:
    """Return the Ollama base URL."""
    return get("ollama_host") or os.environ.get(
        "OLLAMA_BASE_URL", "http://localhost:11434"
    )


def get_provider() -> Optional[str]:
    """Return the configured provider ('claude', 'ollama', or 'both')."""
    return get("provider") or os.environ.get("SYMPHONY_PROVIDER")


def apply_to_env() -> None:
    """
    Export stored credentials to environment variables so that the
    orchestrator subprocess picks them up automatically.
    """
    cfg = load()
    if cfg.get("claude_api_key"):
        os.environ.setdefault("ANTHROPIC_API_KEY", cfg["claude_api_key"])
    if cfg.get("ollama_host"):
        os.environ.setdefault("OLLAMA_BASE_URL", cfg["ollama_host"])
    if cfg.get("provider"):
        os.environ.setdefault("SYMPHONY_PROVIDER", cfg["provider"])


def reset() -> None:
    """Delete config file (used in tests or factory-reset)."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
