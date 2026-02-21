#!/usr/bin/env python3
"""
Linux GPG Signing for Symphony-IR AppImage

Creates detached GPG signatures for AppImage artifacts so users
can verify download integrity before running.

Usage:
    python windows/sign_linux.py dist/Symphony-IR.AppImage
    python windows/sign_linux.py dist/Symphony-IR.AppImage --verify

Requirements:
    - gpg (GnuPG) installed (apt install gnupg / brew install gnupg)
    - A GPG key pair generated (gpg --gen-key)

Environment variables:
    GPG_KEY_ID       Key ID or email to sign with (e.g. "releases@symphonyir.dev")
    GPG_PASSPHRASE   Passphrase (optional; GPG will prompt if absent)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional

GPG_KEY_ID   = os.environ.get("GPG_KEY_ID", "")
GPG_PASSPHRASE = os.environ.get("GPG_PASSPHRASE", "")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _gpg() -> Optional[str]:
    """Return path to gpg binary, or None if not installed."""
    return shutil.which("gpg") or shutil.which("gpg2")


def _check_gpg() -> bool:
    gpg = _gpg()
    if not gpg:
        print("ERROR: gpg / gpg2 not found.")
        print("  Install: sudo apt install gnupg  (Debian/Ubuntu)")
        print("           brew install gnupg       (macOS)")
        return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Signing
# ─────────────────────────────────────────────────────────────────────────────

def sign_file(
    target: Path,
    key_id: str = GPG_KEY_ID,
    passphrase: str = GPG_PASSPHRASE,
) -> bool:
    """
    Create a detached ASCII-armored signature file <target>.sig.

    Returns True on success.
    """
    if not _check_gpg():
        return False

    if not target.exists():
        print(f"ERROR: Target not found: {target}")
        return False

    sig_path = target.with_suffix(target.suffix + ".sig")
    # Remove stale signature
    if sig_path.exists():
        sig_path.unlink()

    print(f"\n  Signing: {target.name}")
    if key_id:
        print(f"  Key ID : {key_id}")

    cmd = [_gpg(), "--batch", "--yes", "--armor", "--detach-sign"]
    if key_id:
        cmd += ["--local-user", key_id]
    if passphrase:
        cmd += ["--passphrase", passphrase, "--pinentry-mode", "loopback"]
    cmd += ["--output", str(sig_path), str(target)]

    result = subprocess.run(cmd, capture_output=False, text=True, check=False)

    if result.returncode == 0 and sig_path.exists():
        print(f"  OK Signature created: {sig_path.name}")
        return True
    else:
        print(f"  FAIL GPG signing failed (exit {result.returncode})")
        return False


def create_sha256(target: Path) -> bool:
    """Create a SHA-256 checksum file alongside the target."""
    sha_path = target.with_suffix(target.suffix + ".sha256")
    try:
        import hashlib
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        sha_path.write_text(f"{digest}  {target.name}\n")
        print(f"  OK SHA-256 written : {sha_path.name}")
        return True
    except Exception as exc:
        print(f"  WARN Could not create checksum: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Verification
# ─────────────────────────────────────────────────────────────────────────────

def verify_file(target: Path) -> bool:
    """Verify the detached signature <target>.sig against target."""
    if not _check_gpg():
        return False

    sig_path = target.with_suffix(target.suffix + ".sig")
    if not sig_path.exists():
        print(f"ERROR: Signature file not found: {sig_path}")
        return False

    print(f"\n  Verifying: {target.name}")
    result = subprocess.run(
        [_gpg(), "--verify", str(sig_path), str(target)],
        capture_output=False, text=True, check=False,
    )
    if result.returncode == 0:
        print(f"  OK Signature valid: {target.name}")
        return True
    else:
        print(f"  FAIL Signature invalid: {target.name}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Export public key (for distribution with release)
# ─────────────────────────────────────────────────────────────────────────────

def export_public_key(key_id: str = GPG_KEY_ID, out_path: Optional[Path] = None) -> bool:
    """Export the public key to a file for inclusion in releases."""
    if not _check_gpg():
        return False

    out = out_path or Path("dist/symphony-ir-release-key.asc")
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [_gpg(), "--armor", "--export"]
    if key_id:
        cmd.append(key_id)

    result = subprocess.run(
        cmd, capture_output=True, text=True, check=False,
    )
    if result.returncode == 0 and result.stdout:
        out.write_text(result.stdout)
        print(f"  OK Public key exported: {out}")
        return True
    else:
        print("  FAIL Could not export public key.")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="GPG-sign Symphony-IR Linux AppImage artifacts"
    )
    parser.add_argument("target", nargs="?", help="AppImage or other file to sign")
    parser.add_argument(
        "--verify", action="store_true", help="Verify existing signature"
    )
    parser.add_argument(
        "--key-id", default=GPG_KEY_ID, help="GPG key ID or email address"
    )
    parser.add_argument(
        "--export-key", action="store_true", help="Export public key to dist/"
    )
    parser.add_argument(
        "--all", dest="sign_all", action="store_true",
        help="Sign all AppImage files in dist/"
    )
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  Symphony-IR Linux GPG Signer")
    print("=" * 60)
    print()

    if args.export_key:
        export_public_key(args.key_id)
        return

    targets = []
    if args.sign_all:
        targets = list(Path("dist").glob("*.AppImage"))
        if not targets:
            print("No AppImage files found in dist/")
            sys.exit(1)
    elif args.target:
        targets = [Path(args.target)]
    else:
        parser.print_help()
        sys.exit(1)

    ok = True
    for t in targets:
        if args.verify:
            ok = verify_file(t) and ok
        else:
            ok = sign_file(t, key_id=args.key_id) and ok
            ok = create_sha256(t) and ok

    print()
    if ok:
        print("All operations succeeded.")
    else:
        print("One or more operations FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
