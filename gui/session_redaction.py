"""
Session Redaction for Symphony-IR

Automatically redacts sensitive information from session files before saving:
- API keys and tokens
- File paths
- Environment variables
- Email addresses
- IP addresses
- Credentials
"""

import re
import json
import logging
from typing import Any, Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


class SessionRedactor:
    """Redact sensitive information from sessions."""

    # Patterns to redact
    PATTERNS = {
        # API keys and tokens
        "api_key": re.compile(r'sk-[a-zA-Z0-9]{48}', re.IGNORECASE),
        "anthropic_key": re.compile(r'(ANTHROPIC_API_KEY|sk-[a-zA-Z0-9]+)', re.IGNORECASE),
        "token": re.compile(r'(token|auth|bearer)\s*[=:]\s*["\']?([a-zA-Z0-9_\-\.]+)["\']?', re.IGNORECASE),

        # Environment variables
        "env_var": re.compile(r'([A-Z_]+)=([a-zA-Z0-9_\-\.]+)', re.IGNORECASE),

        # File paths (common patterns)
        "home_path": re.compile(r'(/home/[a-zA-Z0-9_\-\.]+|C:\\Users\\[a-zA-Z0-9_\-\.]+)', re.IGNORECASE),
        "project_path": re.compile(r'([A-Za-z]:\\[a-zA-Z0-9_\-\\\.]+|/[a-zA-Z0-9_\-/\.]+)', re.IGNORECASE),

        # Email addresses
        "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),

        # IP addresses
        "ipv4": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),

        # Database credentials
        "db_password": re.compile(r'(password|passwd|pwd)\s*[=:]\s*["\']?([a-zA-Z0-9_\-!@#$%^&*]+)["\']?', re.IGNORECASE),
    }

    # Sensitive keys in JSON/dict
    SENSITIVE_KEYS = {
        "api_key",
        "apikey",
        "api_secret",
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "auth_token",
        "access_token",
        "refresh_token",
        "private_key",
        "ssh_key",
        "database_url",
        "db_password",
        "credentials",
        "credential",
        "home_path",
        "user_home",
        "username",
        "user_name",
        "email",
        "api_url",
        "endpoint",
        "host",
        "server",
    }

    REDACTION_PLACEHOLDER = "***REDACTED***"

    @classmethod
    def redact_text(cls, text: str) -> str:
        """
        Redact sensitive information from text.

        Args:
            text: Text to redact

        Returns:
            Text with sensitive info replaced with REDACTED markers
        """
        if not isinstance(text, str):
            return text

        redacted = text

        # Apply pattern-based redactions
        for pattern_type, pattern in cls.PATTERNS.items():
            redacted = pattern.sub(cls.REDACTION_PLACEHOLDER, redacted)

        return redacted

    @classmethod
    def redact_dict(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact sensitive information from dictionary.

        Args:
            obj: Dictionary to redact

        Returns:
            Dictionary with sensitive values redacted
        """
        if not isinstance(obj, dict):
            return obj

        redacted = {}

        for key, value in obj.items():
            # Check if key is sensitive
            if key.lower() in cls.SENSITIVE_KEYS:
                redacted[key] = cls.REDACTION_PLACEHOLDER
                continue

            # Recursively redact nested structures
            if isinstance(value, dict):
                redacted[key] = cls.redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = cls.redact_list(value)
            elif isinstance(value, str):
                redacted[key] = cls.redact_text(value)
            else:
                redacted[key] = value

        return redacted

    @classmethod
    def redact_list(cls, lst: List[Any]) -> List[Any]:
        """
        Redact sensitive information from list.

        Args:
            lst: List to redact

        Returns:
            List with sensitive values redacted
        """
        if not isinstance(lst, list):
            return lst

        return [
            cls.redact_dict(item) if isinstance(item, dict)
            else cls.redact_list(item) if isinstance(item, list)
            else cls.redact_text(item) if isinstance(item, str)
            else item
            for item in lst
        ]

    @classmethod
    def redact_json(cls, json_str: str) -> str:
        """
        Redact sensitive information from JSON string.

        Args:
            json_str: JSON string to redact

        Returns:
            JSON string with sensitive values redacted
        """
        try:
            obj = json.loads(json_str)
            redacted = cls.redact_dict(obj)
            return json.dumps(redacted, indent=2)
        except json.JSONDecodeError:
            # If not valid JSON, treat as text
            return cls.redact_text(json_str)

    @classmethod
    def redact_session(cls, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact sensitive information from session object.

        Args:
            session: Session dictionary

        Returns:
            Session with sensitive data redacted
        """
        redacted = cls.redact_dict(session)

        # Also redact the output and raw response
        if "output" in redacted and isinstance(redacted["output"], str):
            redacted["output"] = cls.redact_text(redacted["output"])

        if "response" in redacted and isinstance(redacted["response"], str):
            redacted["response"] = cls.redact_text(redacted["response"])

        return redacted

    @classmethod
    def redact_file(cls, file_path: Path, output_path: Path = None) -> bool:
        """
        Redact sensitive information from a session file.

        Args:
            file_path: Path to session file
            output_path: Path to save redacted version (default: overwrite original)

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path) as f:
                content = f.read()

            try:
                session = json.loads(content)
                redacted = cls.redact_session(session)
                redacted_content = json.dumps(redacted, indent=2)
            except json.JSONDecodeError:
                # Not JSON, redact as text
                redacted_content = cls.redact_text(content)

            # Save to output path or overwrite original
            save_path = output_path or file_path
            with open(save_path, 'w') as f:
                f.write(redacted_content)

            logger.info(f"Redacted session file: {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to redact session file: {e}")
            return False


class RedactionLevel:
    """Redaction levels for different export scenarios."""

    # No redaction - for local, trusted use
    NONE = "none"

    # Basic redaction - redact only known sensitive keys and patterns
    BASIC = "basic"

    # Full redaction - aggressive redaction of anything that looks sensitive
    FULL = "full"

    @staticmethod
    def redact(session: Dict[str, Any], level: str = BASIC) -> Dict[str, Any]:
        """
        Redact session according to level.

        Args:
            session: Session to redact
            level: Redaction level (none, basic, full)

        Returns:
            Redacted session
        """
        if level == RedactionLevel.NONE:
            return session
        elif level == RedactionLevel.BASIC:
            return SessionRedactor.redact_session(session)
        elif level == RedactionLevel.FULL:
            # For full redaction, even more aggressive
            redacted = SessionRedactor.redact_session(session)
            # Additional aggressive redactions
            if "context" in redacted and isinstance(redacted["context"], dict):
                for key in redacted["context"]:
                    if not key.startswith("_"):
                        redacted["context"][key] = SessionRedactor.REDACTION_PLACEHOLDER
            return redacted
        else:
            return session


def create_sanitized_export(session: Dict[str, Any], level: str = RedactionLevel.BASIC) -> str:
    """
    Create a sanitized/redacted export of a session.

    Args:
        session: Session dictionary
        level: Redaction level

    Returns:
        JSON string of redacted session
    """
    redacted = RedactionLevel.redact(session, level)
    return json.dumps(redacted, indent=2)
