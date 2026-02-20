"""
Secure Credential Storage for Symphony-IR

Uses platform-specific credential managers:
- Windows: Windows Credential Manager (via keyring)
- macOS: Keychain (via keyring)
- Linux: Secret Service or pass (via keyring)

Never stores API keys in plaintext configuration files.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import keyring for secure storage
try:
    import keyring
    from keyring.errors import PasswordDeleteError
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    logger.warning("keyring not installed. Install with: pip install keyring")


class CredentialManager:
    """Secure credential storage using system credential managers."""

    SERVICE_NAME = "Symphony-IR"

    # Credential types
    API_KEY_CREDENTIAL = "anthropic_api_key"
    OLLAMA_URL_CREDENTIAL = "ollama_base_url"

    @staticmethod
    def is_available() -> bool:
        """Check if secure credential storage is available."""
        return KEYRING_AVAILABLE

    @staticmethod
    def store_credential(credential_type: str, value: str, username: str = "symphony") -> bool:
        """
        Store a credential securely.

        Args:
            credential_type: Type of credential (e.g., API_KEY_CREDENTIAL)
            value: The credential value to store
            username: Username associated with credential (default: symphony)

        Returns:
            True if stored successfully, False otherwise
        """
        if not KEYRING_AVAILABLE:
            logger.error("Keyring not available for secure storage")
            return False

        try:
            keyring.set_password(
                CredentialManager.SERVICE_NAME,
                f"{username}:{credential_type}",
                value
            )
            logger.info(f"Stored credential: {credential_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to store credential: {e}")
            return False

    @staticmethod
    def retrieve_credential(
        credential_type: str,
        username: str = "symphony"
    ) -> Optional[str]:
        """
        Retrieve a credential securely.

        Args:
            credential_type: Type of credential to retrieve
            username: Username associated with credential (default: symphony)

        Returns:
            Credential value if found, None otherwise
        """
        if not KEYRING_AVAILABLE:
            return None

        try:
            credential = keyring.get_password(
                CredentialManager.SERVICE_NAME,
                f"{username}:{credential_type}"
            )
            return credential

        except Exception as e:
            logger.debug(f"Failed to retrieve credential: {e}")
            return None

    @staticmethod
    def delete_credential(
        credential_type: str,
        username: str = "symphony"
    ) -> bool:
        """
        Delete a stored credential.

        Args:
            credential_type: Type of credential to delete
            username: Username associated with credential

        Returns:
            True if deleted successfully, False otherwise
        """
        if not KEYRING_AVAILABLE:
            return False

        try:
            keyring.delete_password(
                CredentialManager.SERVICE_NAME,
                f"{username}:{credential_type}"
            )
            logger.info(f"Deleted credential: {credential_type}")
            return True

        except PasswordDeleteError:
            # Credential didn't exist, that's fine
            return True

        except Exception as e:
            logger.error(f"Failed to delete credential: {e}")
            return False

    @staticmethod
    def migrate_from_plaintext(plaintext_config_path: Path) -> Tuple[int, int]:
        """
        Migrate API keys from plaintext config files to secure storage.

        Args:
            plaintext_config_path: Path to config file with plaintext keys

        Returns:
            Tuple of (successfully_migrated, failed)
        """
        if not plaintext_config_path.exists():
            logger.info("No plaintext config to migrate")
            return 0, 0

        if not KEYRING_AVAILABLE:
            logger.error("Keyring not available for migration")
            return 0, 0

        migrated = 0
        failed = 0

        try:
            with open(plaintext_config_path) as f:
                config = json.load(f)

            # Migrate API key if present
            if "api_key" in config and config["api_key"]:
                if CredentialManager.store_credential(
                    CredentialManager.API_KEY_CREDENTIAL,
                    config["api_key"]
                ):
                    # Remove from plaintext config
                    config["api_key"] = None
                    migrated += 1
                else:
                    failed += 1

            # Migrate Ollama URL if present
            if "ollama_url" in config and config["ollama_url"]:
                if CredentialManager.store_credential(
                    CredentialManager.OLLAMA_URL_CREDENTIAL,
                    config["ollama_url"]
                ):
                    config["ollama_url"] = None
                    migrated += 1
                else:
                    failed += 1

            # Save updated config
            with open(plaintext_config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"Migration complete: {migrated} migrated, {failed} failed")
            return migrated, failed

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return 0, 1


class SecureConfig:
    """Configuration with secure credential retrieval."""

    def __init__(self, config_file: Path):
        """
        Initialize secure config.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    self.config = json.load(f)
            else:
                self.config = {}

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = {}

    def save(self) -> None:
        """Save configuration to file (without sensitive data)."""
        try:
            # Ensure sensitive keys are None before saving
            safe_config = self.config.copy()
            safe_config["api_key"] = None
            safe_config["ollama_url"] = None

            with open(self.config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key: str, default=None):
        """Get a config value."""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """Set a config value (does NOT persist sensitive data to disk)."""
        self.config[key] = value

    def get_api_key(self) -> Optional[str]:
        """Get API key from secure storage."""
        return CredentialManager.retrieve_credential(
            CredentialManager.API_KEY_CREDENTIAL
        )

    def set_api_key(self, api_key: str) -> bool:
        """Store API key in secure storage."""
        return CredentialManager.store_credential(
            CredentialManager.API_KEY_CREDENTIAL,
            api_key
        )

    def delete_api_key(self) -> bool:
        """Delete stored API key."""
        return CredentialManager.delete_credential(
            CredentialManager.API_KEY_CREDENTIAL
        )

    def get_ollama_url(self) -> Optional[str]:
        """Get Ollama URL from secure storage."""
        return CredentialManager.retrieve_credential(
            CredentialManager.OLLAMA_URL_CREDENTIAL
        ) or "http://localhost:11434"

    def set_ollama_url(self, url: str) -> bool:
        """Store Ollama URL in secure storage."""
        return CredentialManager.store_credential(
            CredentialManager.OLLAMA_URL_CREDENTIAL,
            url
        )

    def migrate_from_plaintext(self) -> Tuple[int, int]:
        """Migrate plaintext credentials to secure storage."""
        return CredentialManager.migrate_from_plaintext(self.config_file)

    def ensure_secure(self) -> bool:
        """
        Ensure all sensitive data is moved to secure storage.

        Returns:
            True if secure, False if keyring not available
        """
        if not KEYRING_AVAILABLE:
            logger.warning("Keyring not available - credentials may not be stored securely")
            return False

        # Move any plaintext credentials to secure storage
        if self.config.get("api_key"):
            self.set_api_key(self.config["api_key"])
            self.config["api_key"] = None

        if self.config.get("ollama_url"):
            self.set_ollama_url(self.config["ollama_url"])
            self.config["ollama_url"] = None

        self.save()
        return True


def get_secure_config(project_root: Path) -> SecureConfig:
    """Get a secure configuration instance."""
    config_file = project_root / ".orchestrator" / "config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    config = SecureConfig(config_file)

    # Ensure secure storage on first load
    if not KEYRING_AVAILABLE:
        logger.warning(
            "Keyring library not installed. Install with: pip install keyring\n"
            "Credentials may be stored in plaintext without keyring."
        )

    return config
