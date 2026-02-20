"""
Unit tests for RedactionService.

Run with:
    python -m pytest gui/tests/test_redaction.py -v
or from the gui/ directory:
    python -m pytest tests/test_redaction.py -v
"""

import sys
from pathlib import Path

# Ensure gui/ is on the path when running from the project root.
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from services.redaction_service import RedactionService, PLACEHOLDER


# ─────────────────────────────────────────────────────────────────────────────
# Positive tests — these SHOULD be redacted
# ─────────────────────────────────────────────────────────────────────────────

class TestApiKeyPatterns:
    def test_anthropic_key(self):
        text = "key=sk-ant-api03-ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        assert PLACEHOLDER in RedactionService.redact_text(text)

    def test_openai_style_key(self):
        text = "Using sk-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno"
        assert PLACEHOLDER in RedactionService.redact_text(text)

    def test_aws_access_key(self):
        assert PLACEHOLDER in RedactionService.redact_text("AKIAIOSFODNN7EXAMPLE1234")

    def test_bearer_token(self):
        assert PLACEHOLDER in RedactionService.redact_text(
            "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6Ikp"
        )

    def test_token_assignment_equals(self):
        assert PLACEHOLDER in RedactionService.redact_text("token=supersecretvalue123")

    def test_password_assignment(self):
        assert PLACEHOLDER in RedactionService.redact_text("password=hunter2secret")

    def test_api_key_assignment(self):
        assert PLACEHOLDER in RedactionService.redact_text(
            'api_key="abc123defghij456klmnop"'
        )

    def test_unix_home_path(self):
        assert PLACEHOLDER in RedactionService.redact_text("/home/alice/projects/app")

    def test_windows_home_path(self):
        assert PLACEHOLDER in RedactionService.redact_text(
            r"C:\Users\alice\Documents\project"
        )

    def test_email_address(self):
        assert PLACEHOLDER in RedactionService.redact_text(
            "Contact us at alice@example.com for support."
        )

    def test_public_ipv4(self):
        assert PLACEHOLDER in RedactionService.redact_text(
            "Connected to 203.0.113.42 on port 443."
        )


class TestSensitiveKeys:
    def test_api_key_dict_key(self):
        result = RedactionService.redact_dict({"api_key": "sk-secret"})
        assert result["api_key"] == PLACEHOLDER

    def test_password_dict_key(self):
        result = RedactionService.redact_dict({"password": "hunter2"})
        assert result["password"] == PLACEHOLDER

    def test_token_dict_key(self):
        result = RedactionService.redact_dict({"token": "abc123"})
        assert result["token"] == PLACEHOLDER

    def test_nested_sensitive_key(self):
        data = {"auth": {"api_key": "sk-secret", "user": "alice"}}
        result = RedactionService.redact_dict(data)
        assert result["auth"]["api_key"] == PLACEHOLDER
        assert result["auth"]["user"] == "alice"

    def test_sensitive_key_with_list_replaces_whole_value(self):
        # "token" (singular) IS in _SENSITIVE_KEYS — entire value replaced.
        data = {"token": ["tok_abc123456789012345", "tok_def123456789012345"]}
        result = RedactionService.redact_dict(data)
        assert result["token"] == PLACEHOLDER

    def test_list_under_non_sensitive_key_traversed(self):
        # A list under a non-sensitive key is recursively traversed.
        data = {"outputs": ["/home/alice/project/notes.txt", "safe text"]}
        result = RedactionService.redact_dict(data)
        assert PLACEHOLDER in result["outputs"][0]
        assert result["outputs"][1] == "safe text"


# ─────────────────────────────────────────────────────────────────────────────
# Negative tests — these should NOT be redacted (false-positive guard)
# ─────────────────────────────────────────────────────────────────────────────

class TestFalsePositives:
    def test_loopback_not_redacted(self):
        result = RedactionService.redact_text("http://127.0.0.1:11434/api/chat")
        assert "127.0.0.1" in result

    def test_private_rfc1918_not_redacted(self):
        result = RedactionService.redact_text("http://192.168.1.1/path")
        assert "192.168.1.1" in result

    def test_class_a_private_not_redacted(self):
        result = RedactionService.redact_text("10.0.0.1")
        assert "10.0.0.1" in result

    def test_short_token_not_redacted(self):
        # Fewer than 8 chars after = should not match the generic token= pattern
        result = RedactionService.redact_text("count=7")
        assert PLACEHOLDER not in result

    def test_safe_key_not_redacted(self):
        result = RedactionService.redact_dict({"name": "alice", "status": "active"})
        assert result["name"] == "alice"
        assert result["status"] == "active"


# ─────────────────────────────────────────────────────────────────────────────
# JSON redaction
# ─────────────────────────────────────────────────────────────────────────────

class TestJsonRedaction:
    def test_json_string_round_trip(self):
        import json
        data = {"api_key": "sk-secret123", "task": "review auth"}
        out = RedactionService.redact_json(json.dumps(data))
        parsed = json.loads(out)
        assert parsed["api_key"] == PLACEHOLDER
        assert parsed["task"] == "review auth"

    def test_invalid_json_falls_back_to_text_redact(self):
        raw = "not json but has sk-ant-ABCDEFGHIJKLMNOPQRSTUVWXYZ in it"
        result = RedactionService.redact_json(raw)
        assert PLACEHOLDER in result

    def test_nested_json(self):
        import json
        data = {
            "context": {
                "file": "/home/alice/project/auth.py",
                "api_key": "sk-ant-ABCDEF123456789012345678901234567",
            }
        }
        out = json.loads(RedactionService.redact_json(json.dumps(data)))
        assert out["context"]["api_key"] == PLACEHOLDER
        assert PLACEHOLDER in out["context"]["file"]


# ─────────────────────────────────────────────────────────────────────────────
# Session redaction
# ─────────────────────────────────────────────────────────────────────────────

class TestSessionRedaction:
    def test_output_field_text_redacted(self):
        session = {
            "task": "review",
            "output": "Running as alice@example.com with key sk-ant-XYZ0123456789012345678901234",
        }
        result = RedactionService.redact_session(session)
        assert PLACEHOLDER in result["output"]

    def test_non_sensitive_fields_preserved(self):
        session = {"run_id": "abc-123", "success": True, "confidence": 0.9}
        result = RedactionService.redact_session(session)
        assert result["run_id"] == "abc-123"
        assert result["success"] is True
