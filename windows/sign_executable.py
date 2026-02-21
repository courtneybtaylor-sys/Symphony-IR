#!/usr/bin/env python3
"""
Windows Code Signing for Symphony-IR

Signs built executables and installers with an EV (Extended Validation)
or OV (Organization Validation) code signing certificate to eliminate
SmartScreen warnings.

Usage:
    python windows/sign_executable.py dist/Symphony-IR.exe
    python windows/sign_executable.py dist/Symphony-IR-Setup.exe --verify

Requirements:
    - Windows SDK signtool.exe in PATH  (installed with Visual Studio or
      Windows SDK from https://developer.microsoft.com/windows/downloads/windows-sdk/)
    - A valid PFX certificate file

Environment variables:
    SIGN_CERT_PATH     Path to .pfx certificate file
    SIGN_CERT_PASS     Certificate password
    SIGN_TIMESTAMP_URL Timestamp authority URL (default: http://timestamp.digicert.com)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_TIMESTAMP_URLS = [
    "http://timestamp.digicert.com",
    "http://timestamp.sectigo.com",
    "http://timestamp.comodoca.com",
]

CERT_PATH = os.environ.get("SIGN_CERT_PATH", "windows/certificates/windows-cert.pfx")
CERT_PASS = os.environ.get("SIGN_CERT_PASS", "")
TIMESTAMP_URL = os.environ.get("SIGN_TIMESTAMP_URL", DEFAULT_TIMESTAMP_URLS[0])


# ─────────────────────────────────────────────────────────────────────────────
# Locate signtool.exe
# ─────────────────────────────────────────────────────────────────────────────

def find_signtool() -> Optional[Path]:
    """Locate signtool.exe from Windows SDK."""
    # Try PATH first
    if shutil.which("signtool"):
        return Path("signtool")

    # Common Windows SDK install locations
    sdk_roots = [
        Path("C:/Program Files (x86)/Windows Kits/10/bin"),
        Path("C:/Program Files/Windows Kits/10/bin"),
    ]
    for root in sdk_roots:
        if not root.exists():
            continue
        # Prefer the highest SDK version
        versions = sorted(root.iterdir(), reverse=True)
        for ver in versions:
            candidate = ver / "x64" / "signtool.exe"
            if candidate.exists():
                return candidate

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Signing helpers
# ─────────────────────────────────────────────────────────────────────────────

def sign_file(
    target: Path,
    cert_path: str = CERT_PATH,
    cert_pass: str = CERT_PASS,
    timestamp_url: str = TIMESTAMP_URL,
    description: str = "Symphony-IR",
    verbose: bool = True,
) -> bool:
    """
    Sign a PE binary (EXE, DLL, MSI) using signtool.

    Returns True on success.
    """
    signtool = find_signtool()
    if not signtool:
        print("ERROR: signtool.exe not found.")
        print("  Install Windows SDK: https://developer.microsoft.com/windows/downloads/windows-sdk/")
        return False

    if not Path(cert_path).exists():
        print(f"ERROR: Certificate not found: {cert_path}")
        print("  Set SIGN_CERT_PATH or place certificate at windows/certificates/windows-cert.pfx")
        return False

    if not target.exists():
        print(f"ERROR: Target file not found: {target}")
        return False

    print(f"  Signing: {target.name}")
    print(f"  Cert   : {cert_path}")
    print(f"  TSA    : {timestamp_url}")

    cmd = [
        str(signtool),
        "sign",
        "/f",  target.resolve(),       # ← wrong flag; corrected below
        "/fd", "SHA256",
        "/td", "SHA256",
        "/d",  description,
        "/du", "https://github.com/courtneybtaylor-sys/Symphony-IR",
        "/t",  timestamp_url,
        str(target),
    ]
    # Rebuild with correct /f flag for cert path
    cmd = [
        str(signtool), "sign",
        "/f", cert_path,
        "/fd", "SHA256",
        "/td", "SHA256",
        "/d", description,
        "/du", "https://github.com/courtneybtaylor-sys/Symphony-IR",
        "/t", timestamp_url,
    ]
    if cert_pass:
        cmd += ["/p", cert_pass]
    cmd.append(str(target))

    try:
        result = subprocess.run(
            cmd,
            capture_output=not verbose,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print(f"  OK Signed: {target.name}")
            return True
        else:
            print(f"  FAIL Signing failed (exit {result.returncode})")
            if result.stderr:
                print(f"     {result.stderr.strip()}")
            # Retry with next timestamp server
            for alt_url in DEFAULT_TIMESTAMP_URLS:
                if alt_url != timestamp_url:
                    print(f"  Retrying with {alt_url}...")
                    cmd_retry = [c if c != timestamp_url else alt_url for c in cmd]
                    r2 = subprocess.run(cmd_retry, capture_output=True, text=True, check=False)
                    if r2.returncode == 0:
                        print(f"  OK Signed (alt TSA): {target.name}")
                        return True
            return False
    except FileNotFoundError:
        print(f"  ERROR: Could not execute: {signtool}")
        return False


def verify_file(target: Path) -> bool:
    """Verify the signature on a signed PE binary."""
    signtool = find_signtool()
    if not signtool:
        print("ERROR: signtool.exe not found.")
        return False

    print(f"  Verifying: {target.name}")
    result = subprocess.run(
        [str(signtool), "verify", "/pa", str(target)],
        capture_output=False,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        print(f"  OK Signature valid: {target.name}")
        return True
    else:
        print(f"  FAIL Signature invalid or absent: {target.name}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Sign Symphony-IR Windows binaries"
    )
    parser.add_argument("target", nargs="?", help="File to sign (EXE, DLL, MSI)")
    parser.add_argument("--verify", action="store_true", help="Verify existing signature")
    parser.add_argument("--cert", default=CERT_PATH, help="PFX certificate path")
    parser.add_argument("--password", default=CERT_PASS, help="Certificate password")
    parser.add_argument("--tsa", default=TIMESTAMP_URL, help="Timestamp authority URL")
    parser.add_argument(
        "--all", dest="sign_all", action="store_true",
        help="Sign all EXE/MSI files in dist/"
    )
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  Symphony-IR Windows Code Signer")
    print("=" * 60)
    print()

    targets = []

    if args.sign_all:
        dist = Path("dist")
        if dist.exists():
            targets = list(dist.glob("*.exe")) + list(dist.glob("*.msi"))
        if not targets:
            print("No EXE/MSI files found in dist/")
            sys.exit(1)
    elif args.target:
        targets = [Path(args.target)]
    else:
        parser.print_help()
        sys.exit(1)

    if args.verify:
        ok = all(verify_file(t) for t in targets)
    else:
        ok = all(
            sign_file(t, cert_path=args.cert, cert_pass=args.password, timestamp_url=args.tsa)
            for t in targets
        )

    print()
    if ok:
        print("All operations succeeded.")
    else:
        print("One or more operations FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
