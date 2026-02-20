"""
Unit tests for CredentialService using a mock keyring backend.

Works even when keyring is not installed (uses create=True patching).

Run with:
    python -m pytest gui/tests/test_credentials.py -v
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

class _FakePasswordDeleteError(Exception):
    """Stand-in for keyring.errors.PasswordDeleteError when keyring not installed."""


def _make_mock_keyring():
    """Return a simple in-memory keyring mock plus the backing store."""
    store: dict = {}

    def set_password(service, username, password):
        store[(service, username)] = password

    def get_password(service, username):
        return store.get((service, username))

    def delete_password(service, username):
        if (service, username) not in store:
            raise _FakePasswordDeleteError(f"No credential: {username}")
        del store[(service, username)]

    mock_kr = MagicMock()
    mock_kr.set_password.side_effect = set_password
    mock_kr.get_password.side_effect = get_password
    mock_kr.delete_password.side_effect = delete_password
    return mock_kr, store


def _make_patches(mock_kr):
    """Return a list of patch context managers needed for one test."""
    return [
        patch("services.credential_service.keyring", mock_kr, create=True),
        patch("services.credential_service._KEYRING_OK", True),
        # PasswordDeleteError is caught in delete() — provide the fake one.
        patch("services.credential_service.PasswordDeleteError",
              _FakePasswordDeleteError, create=True),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestCredentialService:
    """Tests that exercise CredentialService against a mock keyring backend."""

    def test_store_and_retrieve(self):
        mock_kr, _ = _make_mock_keyring()
        with _make_patches(mock_kr)[0], _make_patches(mock_kr)[1]:
            from services.credential_service import CredentialService
            with _make_patches(mock_kr)[0], _make_patches(mock_kr)[1]:
                # Use the module-level patches directly
                pass

        # Re-approach: use a single nested-with block
        mock_kr, _ = _make_mock_keyring()
        pA = patch("services.credential_service.keyring", mock_kr, create=True)
        pB = patch("services.credential_service._KEYRING_OK", True)
        pC = patch("services.credential_service.PasswordDeleteError",
                   _FakePasswordDeleteError, create=True)
        with pA, pB, pC:
            from services.credential_service import CredentialService
            assert CredentialService.store("my_cred", "secret_value") is True
            assert CredentialService.retrieve("my_cred") == "secret_value"

    def test_retrieve_missing_returns_none(self):
        mock_kr, _ = _make_mock_keyring()
        with patch("services.credential_service.keyring", mock_kr, create=True), \
             patch("services.credential_service._KEYRING_OK", True):
            from services.credential_service import CredentialService
            assert CredentialService.retrieve("nonexistent_xyz") is None

    def test_delete_existing(self):
        mock_kr, _ = _make_mock_keyring()
        pA = patch("services.credential_service.keyring", mock_kr, create=True)
        pB = patch("services.credential_service._KEYRING_OK", True)
        pC = patch("services.credential_service.PasswordDeleteError",
                   _FakePasswordDeleteError, create=True)
        with pA, pB, pC:
            from services.credential_service import CredentialService
            CredentialService.store("del_cred", "value")
            assert CredentialService.delete("del_cred") is True
            assert CredentialService.retrieve("del_cred") is None

    def test_delete_nonexistent_returns_true(self):
        """Deleting a credential that doesn't exist should succeed silently."""
        mock_kr, _ = _make_mock_keyring()
        pA = patch("services.credential_service.keyring", mock_kr, create=True)
        pB = patch("services.credential_service._KEYRING_OK", True)
        pC = patch("services.credential_service.PasswordDeleteError",
                   _FakePasswordDeleteError, create=True)
        with pA, pB, pC:
            from services.credential_service import CredentialService
            assert CredentialService.delete("never_stored_xyz") is True

    def test_api_key_helpers(self):
        mock_kr, _ = _make_mock_keyring()
        pA = patch("services.credential_service.keyring", mock_kr, create=True)
        pB = patch("services.credential_service._KEYRING_OK", True)
        pC = patch("services.credential_service.PasswordDeleteError",
                   _FakePasswordDeleteError, create=True)
        with pA, pB, pC:
            from services.credential_service import CredentialService
            CredentialService.set_api_key("sk-test-12345678901234567890")
            assert CredentialService.get_api_key() == "sk-test-12345678901234567890"
            assert CredentialService.has("anthropic_api_key") is True
            CredentialService.delete_api_key()
            assert CredentialService.get_api_key() is None

    def test_ollama_url_default(self):
        mock_kr, _ = _make_mock_keyring()
        with patch("services.credential_service.keyring", mock_kr, create=True), \
             patch("services.credential_service._KEYRING_OK", True):
            from services.credential_service import CredentialService
            # Nothing stored → return the hardcoded default
            assert CredentialService.get_ollama_url() == "http://localhost:11434"

    def test_ollama_url_custom(self):
        mock_kr, _ = _make_mock_keyring()
        with patch("services.credential_service.keyring", mock_kr, create=True), \
             patch("services.credential_service._KEYRING_OK", True):
            from services.credential_service import CredentialService
            CredentialService.set_ollama_url("http://192.168.1.50:11434")
            assert CredentialService.get_ollama_url() == "http://192.168.1.50:11434"

    def test_unavailable_store_returns_false(self):
        with patch("services.credential_service._KEYRING_OK", False):
            from services.credential_service import CredentialService
            assert CredentialService.store("x", "y") is False

    def test_unavailable_retrieve_returns_none(self):
        with patch("services.credential_service._KEYRING_OK", False):
            from services.credential_service import CredentialService
            assert CredentialService.retrieve("x") is None

    def test_unavailable_delete_returns_false(self):
        with patch("services.credential_service._KEYRING_OK", False):
            from services.credential_service import CredentialService
            assert CredentialService.delete("x") is False

    def test_migrate_from_config(self):
        mock_kr, _ = _make_mock_keyring()
        pA = patch("services.credential_service.keyring", mock_kr, create=True)
        pB = patch("services.credential_service._KEYRING_OK", True)
        pC = patch("services.credential_service.PasswordDeleteError",
                   _FakePasswordDeleteError, create=True)
        with pA, pB, pC:
            from services.credential_service import CredentialService
            config = {
                "api_key": "sk-test-migrate12345678901234567890",
                "ollama_url": "http://custom:11434",
                "name": "Alice",
            }
            migrated, failed = CredentialService.migrate_from_config(config)
            assert migrated == 2
            assert failed == 0
            assert config["api_key"] is None
            assert config["ollama_url"] is None
            assert config["name"] == "Alice"   # non-credential key preserved

    def test_migrate_skips_redacted_values(self):
        mock_kr, _ = _make_mock_keyring()
        with patch("services.credential_service.keyring", mock_kr, create=True), \
             patch("services.credential_service._KEYRING_OK", True):
            from services.credential_service import CredentialService
            config = {"api_key": "***REDACTED***"}
            migrated, failed = CredentialService.migrate_from_config(config)
            assert migrated == 0
            assert failed == 0
