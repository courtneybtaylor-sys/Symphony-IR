"""
Redaction service — remove sensitive data before any display or export.

Design goals
------------
* No false negatives on common secret patterns (API keys, tokens, paths).
* Preserve JSON structure / formatting (replace values, not whole lines).
* Recursive — handles arbitrarily nested dicts and lists.
* Testable — all patterns and key-sets are module-level constants.
"""

from __future__ import annotations

import re
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

PLACEHOLDER = "***REDACTED***"

# ------------------------------------------------------------------ patterns
# Each entry is (name, compiled_regex).  Ordered from most-specific to
# least-specific so earlier matches shadow later ones on the same string.

_PATTERNS: list[tuple[str, re.Pattern]] = [
    # Anthropic  sk-ant-…
    ("anthropic_key",  re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}", re.I)),
    # Generic OpenAI / Anthropic short form  sk-…
    ("openai_key",     re.compile(r"sk-[A-Za-z0-9]{20,}", re.I)),
    # AWS access key
    ("aws_access",     re.compile(r"AKIA[0-9A-Z]{16}", re.I)),
    # AWS secret key (40 hex-ish chars after common prefixes)
    ("aws_secret",     re.compile(r"(?i)aws.{0,20}secret.{0,20}['\"]?([A-Za-z0-9/+=]{40})['\"]?")),
    # Bearer / Authorization header value
    ("bearer",         re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*")),
    # Generic token= / auth= assignments (key=value or key: value)
    ("token_assign",   re.compile(
        r"(?i)(token|auth|secret|password|passwd|pwd|api[_-]?key|access[_-]?key)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9\-._~+/!=@#$%^&*]{8,}['\"]?"
    )),
    # Windows paths: C:\Users\alice\...
    ("win_path",       re.compile(r"[A-Za-z]:\\(?:Users|home)\\[A-Za-z0-9_.\- ]+(?:\\[^\s\"']*)*", re.I)),
    # Unix home paths: /home/alice/... or /Users/alice/...
    ("unix_home",      re.compile(r"(?:/home|/Users)/[A-Za-z0-9_.\-]+(?:/[^\s\"']*)*")),
    # Email addresses
    ("email",          re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")),
    # IPv4 (non-loopback)
    ("ipv4",           re.compile(
        r"\b(?!127\.|10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)(?:\d{1,3}\.){3}\d{1,3}\b"
    )),
]

# Dict / JSON keys whose values are always redacted (case-insensitive match)
_SENSITIVE_KEYS: frozenset[str] = frozenset({
    "api_key", "apikey", "api_secret", "apisecret",
    "password", "passwd", "pwd",
    "secret", "client_secret",
    "token", "access_token", "refresh_token", "auth_token", "id_token",
    "private_key", "ssh_key", "signing_key",
    "anthropic_api_key", "openai_api_key",
    "database_url", "db_password", "db_url", "connection_string",
    "credentials", "credential",
    "email", "user_email",
    "home", "home_dir", "user_home",
    "username", "user_name",
})


# ---------------------------------------------------------------------- public

class RedactionService:
    """Redact sensitive information from text, dicts, and JSON."""

    @staticmethod
    def redact_text(text: str) -> str:
        """Apply all regex patterns to a plain string."""
        if not isinstance(text, str):
            return text
        for _name, pattern in _PATTERNS:
            text = pattern.sub(PLACEHOLDER, text)
        return text

    @staticmethod
    def redact_value(value: Any) -> Any:
        """Recursively redact a value (str / dict / list / other)."""
        if isinstance(value, str):
            return RedactionService.redact_text(value)
        if isinstance(value, dict):
            return RedactionService.redact_dict(value)
        if isinstance(value, list):
            return [RedactionService.redact_value(v) for v in value]
        return value

    @staticmethod
    def redact_dict(obj: dict) -> dict:
        """Redact sensitive keys and recursively clean values."""
        if not isinstance(obj, dict):
            return obj
        result = {}
        for key, value in obj.items():
            if isinstance(key, str) and key.lower() in _SENSITIVE_KEYS:
                result[key] = PLACEHOLDER
            else:
                result[key] = RedactionService.redact_value(value)
        return result

    @staticmethod
    def redact_session(session: dict) -> dict:
        """Full session redaction — dict-level + text-level on output fields."""
        cleaned = RedactionService.redact_dict(session)
        # Belt-and-suspenders: run pattern redaction on free-text fields too
        for field in ("output", "response", "raw", "stderr", "stdout", "log"):
            if field in cleaned and isinstance(cleaned[field], str):
                cleaned[field] = RedactionService.redact_text(cleaned[field])
        return cleaned

    @staticmethod
    def redact_json(json_str: str) -> str:
        """Parse → redact → re-serialise, preserving indentation."""
        try:
            obj = json.loads(json_str)
            return json.dumps(RedactionService.redact_value(obj), indent=2)
        except json.JSONDecodeError:
            return RedactionService.redact_text(json_str)
