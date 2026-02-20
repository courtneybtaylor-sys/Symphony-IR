"""
Credential storage backed by the OS secret store.

  Windows → Windows Credential Manager
  macOS   → Keychain
  Linux   → SecretService / libsecret

Namespaced as  SERVICE="SymphonyIR"  USERNAME="<credential_type>"
so multiple installations don't collide with each other or generic names.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------- keyring
try:
    import keyring
    from keyring.errors import PasswordDeleteError
    _KEYRING_OK = True
except ImportError:
    _KEYRING_OK = False
    logger.warning("keyring not installed — credentials cannot be stored securely. "
                   "Run:  pip install keyring")

# Unambiguous, versioned service name — survives side-by-side installs.
_SERVICE = "SymphonyIR-v1"

# Credential identifiers (used as the keyring "username" field)
KEY_ANTHROPIC  = "anthropic_api_key"
KEY_OPENAI     = "openai_api_key"
KEY_OLLAMA_URL = "ollama_base_url"

_DEFAULT_OLLAMA = "http://localhost:11434"


class CredentialService:
    """Get / set / delete credentials from the system secret store."""

    # ----------------------------------------------------------------- public

    @staticmethod
    def available() -> bool:
        return _KEYRING_OK

    @staticmethod
    def store(credential_id: str, value: str) -> bool:
        """
        Encrypt *value* under *credential_id* in the OS secret store.

        Returns True on success, False if keyring unavailable or error.
        """
        if not _KEYRING_OK:
            return False
        try:
            keyring.set_password(_SERVICE, credential_id, value)
            logger.debug("Stored credential: %s", credential_id)
            return True
        except Exception as exc:
            logger.error("Failed to store credential %s: %s", credential_id, exc)
            return False

    @staticmethod
    def retrieve(credential_id: str) -> Optional[str]:
        """Return the stored value or None."""
        if not _KEYRING_OK:
            return None
        try:
            return keyring.get_password(_SERVICE, credential_id)
        except Exception as exc:
            logger.debug("Failed to retrieve credential %s: %s", credential_id, exc)
            return None

    @staticmethod
    def delete(credential_id: str) -> bool:
        """Delete a stored credential. Returns True if deleted or not found."""
        if not _KEYRING_OK:
            return False
        try:
            keyring.delete_password(_SERVICE, credential_id)
            logger.debug("Deleted credential: %s", credential_id)
            return True
        except PasswordDeleteError:
            return True  # already gone — that's fine
        except Exception as exc:
            logger.error("Failed to delete credential %s: %s", credential_id, exc)
            return False

    @staticmethod
    def has(credential_id: str) -> bool:
        return CredentialService.retrieve(credential_id) is not None

    # ---------------------------------------------------------------- helpers

    @staticmethod
    def get_api_key() -> Optional[str]:
        return CredentialService.retrieve(KEY_ANTHROPIC)

    @staticmethod
    def set_api_key(value: str) -> bool:
        return CredentialService.store(KEY_ANTHROPIC, value)

    @staticmethod
    def delete_api_key() -> bool:
        return CredentialService.delete(KEY_ANTHROPIC)

    @staticmethod
    def get_ollama_url() -> str:
        return CredentialService.retrieve(KEY_OLLAMA_URL) or _DEFAULT_OLLAMA

    @staticmethod
    def set_ollama_url(value: str) -> bool:
        return CredentialService.store(KEY_OLLAMA_URL, value or _DEFAULT_OLLAMA)

    # ------------------------------------------------------- plaintext migration

    @staticmethod
    def migrate_from_config(config: dict) -> tuple[int, int]:
        """
        Move plaintext credentials found in *config* dict into secure storage.

        Modifies *config* in place (sets migrated keys to None).
        Returns (migrated_count, failed_count).
        """
        migrated = failed = 0

        mapping = {
            "api_key":          KEY_ANTHROPIC,
            "ANTHROPIC_API_KEY": KEY_ANTHROPIC,
            "openai_api_key":   KEY_OPENAI,
            "ollama_url":       KEY_OLLAMA_URL,
        }

        for config_key, cred_id in mapping.items():
            value = config.get(config_key)
            if not value or "REDACTED" in str(value):
                continue
            if CredentialService.store(cred_id, value):
                config[config_key] = None
                migrated += 1
                logger.info("Migrated %s → secure storage", config_key)
            else:
                failed += 1
                logger.error("Failed to migrate %s", config_key)

        return migrated, failed
