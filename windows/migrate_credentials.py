#!/usr/bin/env python
"""
Migrate Credentials to Secure Storage

This script migrates API keys from plaintext configuration files to
Windows Credential Manager using the keyring library.

Usage:
    python windows/migrate_credentials.py
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.secure_credentials import CredentialManager, SecureConfig


def print_header():
    """Print script header."""
    print("\n" + "=" * 70)
    print("  Symphony-IR Credential Migration")
    print("  Move API keys from plaintext to Windows Credential Manager")
    print("=" * 70 + "\n")


def check_keyring_available():
    """Check if keyring is available."""
    if not CredentialManager.is_available():
        print("❌ Keyring is not installed!")
        print("\nPlease install it with:")
        print("   pip install keyring")
        print("\nThen run this script again.")
        return False
    return True


def find_config_files(project_root: Path) -> list:
    """Find configuration files that might contain API keys."""
    config_files = []

    # Check common locations
    locations = [
        project_root / ".orchestrator" / "config.json",
        project_root / ".orchestrator" / ".env",
        project_root / ".orchestrator" / "agents.yaml",
        project_root / "gui" / "config.json",
    ]

    for loc in locations:
        if loc.exists():
            config_files.append(loc)

    return config_files


def show_config_summary(config_path: Path) -> bool:
    """Show summary of config file (with redaction)."""
    try:
        with open(config_path) as f:
            content = f.read()

        # Show size and type
        size_kb = config_path.stat().st_size / 1024
        print(f"  📄 {config_path.name} ({size_kb:.1f} KB)")

        # Check for potential API keys (without showing them)
        if "sk-" in content or "ANTHROPIC" in content or "api_key" in content:
            print(f"     ⚠️  Contains potential API keys")
            return True
        else:
            print(f"     ✓ No obvious API keys found")
            return False

    except Exception as e:
        print(f"  ❌ Error reading {config_path}: {e}")
        return False


def migrate_config(config_path: Path, dry_run: bool = False) -> Tuple[int, int]:
    """
    Migrate credentials from a single config file.

    Returns:
        Tuple of (migrated_count, failed_count)
    """
    try:
        with open(config_path) as f:
            content = f.read()

        # Try to parse as JSON
        try:
            config = json.loads(content)
        except json.JSONDecodeError:
            print(f"  ℹ️  {config_path.name} is not JSON, skipping")
            return 0, 0

        migrated = 0
        failed = 0

        # Check for API key
        if "api_key" in config and config["api_key"]:
            api_key = config["api_key"]
            if not api_key.startswith("***"):  # Not already redacted
                if not dry_run:
                    if CredentialManager.store_credential(
                        CredentialManager.API_KEY_CREDENTIAL,
                        api_key
                    ):
                        config["api_key"] = None
                        migrated += 1
                        print(f"     ✓ Migrated API key")
                    else:
                        failed += 1
                        print(f"     ❌ Failed to migrate API key")
                else:
                    print(f"     [DRY RUN] Would migrate API key")
                    migrated += 1

        # Check for Ollama URL
        if "ollama_url" in config and config["ollama_url"]:
            ollama_url = config["ollama_url"]
            if not ollama_url.startswith("***"):
                if not dry_run:
                    if CredentialManager.store_credential(
                        CredentialManager.OLLAMA_URL_CREDENTIAL,
                        ollama_url
                    ):
                        config["ollama_url"] = None
                        migrated += 1
                        print(f"     ✓ Migrated Ollama URL")
                    else:
                        failed += 1
                else:
                    print(f"     [DRY RUN] Would migrate Ollama URL")
                    migrated += 1

        # Save updated config (remove plaintext keys)
        if migrated > 0 and not dry_run:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"     ✓ Saved updated config")

        return migrated, failed

    except Exception as e:
        print(f"  ❌ Error migrating {config_path}: {e}")
        return 0, 1


def main():
    """Main migration script."""
    parser = argparse.ArgumentParser(
        description="Migrate API keys to Windows Credential Manager"
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=Path.home() / "Symphony-IR",
        help="Project root directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation and migrate immediately"
    )

    args = parser.parse_args()

    print_header()

    # Check keyring
    if not check_keyring_available():
        return 1

    print("✓ Keyring available for secure storage\n")

    # Find config files
    print(f"Scanning {args.project} for configuration files...")
    config_files = find_config_files(args.project)

    if not config_files:
        print("❌ No configuration files found!")
        print(f"   Looked in: {args.project}/.orchestrator/")
        return 1

    print(f"✓ Found {len(config_files)} configuration file(s)\n")

    # Show summary
    print("Configuration files found:")
    files_with_keys = 0
    for config_file in config_files:
        if show_config_summary(config_file):
            files_with_keys += 1

    if files_with_keys == 0:
        print("\n✓ No API keys found to migrate!")
        return 0

    # Ask for confirmation (unless --force)
    print()
    if not args.dry_run and not args.force:
        response = input("Proceed with migration? (yes/no): ").strip().lower()
        if response not in ("yes", "y"):
            print("Migration cancelled.")
            return 0

    # Perform migration
    print("\n" + "=" * 70)
    if args.dry_run:
        print("Running in DRY RUN mode (no changes will be made)")
    print("=" * 70 + "\n")

    total_migrated = 0
    total_failed = 0

    for config_file in config_files:
        print(f"Processing {config_file.name}...")
        migrated, failed = migrate_config(config_file, dry_run=args.dry_run)
        total_migrated += migrated
        total_failed += failed

    # Summary
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"Credentials migrated: {total_migrated}")
    print(f"Failures: {total_failed}")

    if total_failed == 0 and total_migrated > 0:
        print("\n✅ Migration successful!")
        if not args.dry_run:
            print("\nYour API keys are now stored securely in Windows Credential Manager.")
            print("Configuration files have been updated to remove plaintext keys.")
    elif args.dry_run:
        print("\n✓ Dry run complete. Run without --dry-run to actually migrate.")
    else:
        print("\n⚠️  Some migrations failed. Please check the errors above.")

    print("\n" + "=" * 70 + "\n")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
