"""
Unit tests for ErrorTranslator and ErrorHandler.

Run with:
    python -m pytest gui/tests/test_errors.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from user_friendly_errors import (
    ErrorTranslator, ErrorHandler, UserFriendlyError, ErrorSeverity,
    get_api_key_error, get_ollama_not_running_error,
)


# ─────────────────────────────────────────────────────────────────────────────
# ErrorTranslator
# ─────────────────────────────────────────────────────────────────────────────

class TestErrorTranslator:
    def test_api_key_pattern(self):
        err = ErrorTranslator.translate("ANTHROPIC_API_KEY not set in environment")
        assert "API Key" in err.title
        assert err.suggestions

    def test_invalid_api_key_401(self):
        err = ErrorTranslator.translate("401 Unauthorized: api_key invalid")
        assert "Invalid" in err.title or "API" in err.title
        assert err.suggestions

    def test_connection_refused(self):
        err = ErrorTranslator.translate("Connection refused: [Errno 111]")
        assert "Connect" in err.title
        assert err.suggestions

    def test_timeout(self):
        err = ErrorTranslator.translate("Request timed out after 30s")
        assert "Time" in err.title or "Timeout" in err.title.title()

    def test_ollama(self):
        err = ErrorTranslator.translate("Cannot reach ollama at localhost:11434")
        assert err.suggestions  # at least one suggestion

    def test_file_not_found(self):
        err = ErrorTranslator.translate("FileNotFoundError: orchestrator.py")
        assert "File" in err.title or "Found" in err.title

    def test_permission_denied(self):
        err = ErrorTranslator.translate("Permission denied: /home/alice/.orchestrator")
        assert "Permission" in err.title

    def test_memory_error(self):
        # "OutOfMemory" is an unambiguous pattern that won't match earlier rules.
        err = ErrorTranslator.translate("OutOfMemory: Java heap space")
        assert "Memory" in err.title

    def test_json_error(self):
        err = ErrorTranslator.translate("JSON parse error at line 42")
        assert err.title  # any title is fine

    def test_unknown_falls_back_gracefully(self):
        err = ErrorTranslator.translate("some completely unknown error xyz987")
        assert isinstance(err, UserFriendlyError)
        assert err.title
        assert err.suggestions

    def test_returns_user_friendly_error_type(self):
        result = ErrorTranslator.translate("Connection refused")
        assert isinstance(result, UserFriendlyError)

    def test_technical_details_preserved(self):
        raw = "FileNotFoundError: [Errno 2] No such file"
        err = ErrorTranslator.translate(raw)
        assert err.technical_details == raw


# ─────────────────────────────────────────────────────────────────────────────
# ErrorHandler
# ─────────────────────────────────────────────────────────────────────────────

class TestErrorHandler:
    def test_handle_exception(self):
        exc = ConnectionRefusedError("Connection refused")
        result = ErrorHandler.handle_error(exc, "test_context")
        assert isinstance(result, UserFriendlyError)
        assert result.title
        assert result.suggestions

    def test_handle_file_not_found(self):
        exc = FileNotFoundError("No such file: orchestrator.py")
        result = ErrorHandler.handle_error(exc, "subprocess_launch")
        assert isinstance(result, UserFriendlyError)

    def test_to_dict_has_required_keys(self):
        exc = RuntimeError("Something went wrong")
        result = ErrorHandler.handle_error(exc).to_dict()
        assert "title" in result
        assert "message" in result
        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)


# ─────────────────────────────────────────────────────────────────────────────
# UserFriendlyError
# ─────────────────────────────────────────────────────────────────────────────

class TestUserFriendlyError:
    def test_str_includes_title_and_message(self):
        err = UserFriendlyError(
            title="Test Error",
            message="Something broke.",
            suggestions=["Try A", "Try B"],
        )
        s = str(err)
        assert "Test Error" in s
        assert "Something broke." in s
        assert "Try A" in s
        assert "1." in s

    def test_to_dict_round_trip(self):
        err = UserFriendlyError(
            title="T", message="M",
            suggestions=["S1"],
            help_link="https://example.com",
        )
        d = err.to_dict()
        assert d["title"] == "T"
        assert d["message"] == "M"
        assert d["suggestions"] == ["S1"]
        assert d["help_link"] == "https://example.com"

    def test_default_severity_is_error(self):
        err = UserFriendlyError(title="X", message="Y")
        assert err.severity == ErrorSeverity.ERROR


# ─────────────────────────────────────────────────────────────────────────────
# Pre-built helpers
# ─────────────────────────────────────────────────────────────────────────────

class TestPrebuiltHelpers:
    def test_get_api_key_error(self):
        err = get_api_key_error()
        assert isinstance(err, UserFriendlyError)
        assert "API" in err.title
        assert err.suggestions

    def test_get_ollama_not_running_error(self):
        err = get_ollama_not_running_error()
        assert isinstance(err, UserFriendlyError)
        assert "Ollama" in err.title
        assert err.suggestions
