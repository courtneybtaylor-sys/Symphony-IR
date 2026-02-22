#!/usr/bin/env python3
"""
macOS Code Signing & Notarization for Symphony-IR

Signs the .app bundle and DMG with an Apple Developer ID certificate
and submits it to Apple for notarization (required for macOS Gatekeeper).

Usage:
    python windows/sign_macos.py dist/Symphony-IR.app
    python windows/sign_macos.py dist/Symphony-IR.dmg --notarize

Requirements:
    - macOS host
    - Xcode command-line tools:  xcode-select --install
    - Apple Developer ID Application certificate in Keychain
    - Apple Developer Program account for notarization

Environment variables:
    APPLE_DEVELOPER_ID   e.g. "Developer ID Application: Your Name (TEAMID)"
    APPLE_APPLE_ID       Apple ID email for notarization
    APPLE_APP_PASSWORD   App-specific password from appleid.apple.com
    APPLE_TEAM_ID        10-character Apple team ID
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DEVELOPER_ID  = os.environ.get("APPLE_DEVELOPER_ID",   "")
APPLE_ID      = os.environ.get("APPLE_APPLE_ID",       "")
APP_PASSWORD  = os.environ.get("APPLE_APP_PASSWORD",   "")
TEAM_ID       = os.environ.get("APPLE_TEAM_ID",        "")

ENTITLEMENTS_FILE = Path(__file__).parent / "macos_entitlements.plist"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _run(cmd: list, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=check,
    )


def _ensure_entitlements() -> Path:
    """Create a minimal entitlements plist if not present."""
    if ENTITLEMENTS_FILE.exists():
        return ENTITLEMENTS_FILE

    plist = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key><false/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key><false/>
    <key>com.apple.security.cs.disable-library-validation</key><true/>
    <key>com.apple.security.network.client</key><true/>
    <key>com.apple.security.files.user-selected.read-write</key><true/>
</dict>
</plist>
"""
    ENTITLEMENTS_FILE.write_text(plist)
    print(f"  Created entitlements: {ENTITLEMENTS_FILE}")
    return ENTITLEMENTS_FILE


# ─────────────────────────────────────────────────────────────────────────────
# Signing
# ─────────────────────────────────────────────────────────────────────────────

def sign_app(app_path: Path, developer_id: str = DEVELOPER_ID) -> bool:
    """
    Deep-sign a .app bundle.
    Signs frameworks/dylibs first, then the main executable.
    """
    if not developer_id:
        print("ERROR: APPLE_DEVELOPER_ID is not set.")
        return False

    if not app_path.exists():
        print(f"ERROR: App bundle not found: {app_path}")
        return False

    print(f"\n  Signing .app bundle: {app_path.name}")
    entitlements = _ensure_entitlements()

    # 1. Sign all nested frameworks/dylibs
    frameworks_dir = app_path / "Contents" / "Frameworks"
    if frameworks_dir.exists():
        for dylib in frameworks_dir.rglob("*.dylib"):
            _run([
                "codesign", "--force", "--sign", developer_id,
                "--options", "runtime",
                str(dylib),
            ])
        for framework in frameworks_dir.glob("*.framework"):
            _run([
                "codesign", "--force", "--deep", "--sign", developer_id,
                "--options", "runtime",
                str(framework),
            ])

    # 2. Sign the main .app bundle
    _run([
        "codesign",
        "--force",
        "--sign",  developer_id,
        "--options", "runtime",
        "--entitlements", str(entitlements),
        "--timestamp",
        str(app_path),
    ])

    # 3. Verify
    result = subprocess.run(
        ["codesign", "--verify", "--deep", "--strict", str(app_path)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode == 0:
        print(f"  OK App bundle signed and verified: {app_path.name}")
        return True
    else:
        print(f"  FAIL Signature verification failed:")
        print(f"     {result.stderr.strip()}")
        return False


def sign_dmg(dmg_path: Path, developer_id: str = DEVELOPER_ID) -> bool:
    """Sign a .dmg file."""
    if not developer_id:
        print("ERROR: APPLE_DEVELOPER_ID is not set.")
        return False

    if not dmg_path.exists():
        print(f"ERROR: DMG not found: {dmg_path}")
        return False

    print(f"\n  Signing DMG: {dmg_path.name}")
    _run([
        "codesign",
        "--force",
        "--sign", developer_id,
        "--timestamp",
        str(dmg_path),
    ])
    print(f"  OK DMG signed: {dmg_path.name}")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Notarization
# ─────────────────────────────────────────────────────────────────────────────

def notarize(
    target: Path,
    apple_id: str = APPLE_ID,
    app_password: str = APP_PASSWORD,
    team_id: str = TEAM_ID,
    wait: bool = True,
) -> bool:
    """
    Submit a signed .app or .dmg to Apple's notarization service.
    Optionally poll until the submission is accepted.
    """
    if not (apple_id and app_password and team_id):
        print("ERROR: APPLE_APPLE_ID, APPLE_APP_PASSWORD, APPLE_TEAM_ID must be set.")
        return False

    print(f"\n  Submitting for notarization: {target.name}")
    result = subprocess.run(
        [
            "xcrun", "notarytool", "submit", str(target),
            "--apple-id",       apple_id,
            "--password",       app_password,
            "--team-id",        team_id,
            "--output-format",  "json",
        ],
        capture_output=True, text=True, check=False,
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  ERROR: Unexpected notarytool output:\n{result.stdout}")
        return False

    submission_id = data.get("id")
    status        = data.get("status", "")

    print(f"  Submission ID: {submission_id}")
    print(f"  Initial status: {status}")

    if not wait:
        print("  Use 'xcrun notarytool info <id>' to check status later.")
        return True

    # Poll for completion
    print("  Waiting for notarization...")
    for attempt in range(60):
        time.sleep(15)
        info = subprocess.run(
            [
                "xcrun", "notarytool", "info", submission_id,
                "--apple-id",      apple_id,
                "--password",      app_password,
                "--team-id",       team_id,
                "--output-format", "json",
            ],
            capture_output=True, text=True, check=False,
        )
        try:
            info_data = json.loads(info.stdout)
        except json.JSONDecodeError:
            continue

        current_status = info_data.get("status", "")
        print(f"  [{attempt + 1}] Status: {current_status}")

        if current_status == "Accepted":
            print(f"  OK Notarization accepted: {target.name}")
            _staple(target)
            return True
        elif current_status in ("Invalid", "Rejected"):
            print(f"  FAIL Notarization rejected.")
            _show_notarization_log(submission_id, apple_id, app_password, team_id)
            return False

    print("  FAIL Notarization timed out.")
    return False


def _staple(target: Path) -> None:
    """Staple the notarization ticket to the binary."""
    print(f"  Stapling notarization ticket: {target.name}")
    subprocess.run(["xcrun", "stapler", "staple", str(target)], check=False)


def _show_notarization_log(submission_id: str, apple_id: str, password: str, team_id: str):
    """Fetch and print the notarization log for debugging."""
    result = subprocess.run(
        [
            "xcrun", "notarytool", "log", submission_id,
            "--apple-id", apple_id, "--password", password, "--team-id", team_id,
        ],
        capture_output=True, text=True, check=False,
    )
    if result.stdout:
        print("  Notarization log:")
        print(result.stdout[:2000])  # cap output


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Sign and notarize Symphony-IR macOS binaries"
    )
    parser.add_argument("target", help="Path to .app or .dmg to sign")
    parser.add_argument(
        "--notarize", action="store_true",
        help="Submit to Apple notarization after signing"
    )
    parser.add_argument(
        "--no-wait", dest="no_wait", action="store_true",
        help="Don't wait for notarization result"
    )
    parser.add_argument(
        "--developer-id", default=DEVELOPER_ID,
        help="Apple Developer ID (overrides APPLE_DEVELOPER_ID env var)"
    )
    args = parser.parse_args()

    target = Path(args.target)

    print()
    print("=" * 60)
    print("  Symphony-IR macOS Code Signer")
    print("=" * 60)

    if target.suffix == ".dmg":
        ok = sign_dmg(target, developer_id=args.developer_id)
    else:
        ok = sign_app(target, developer_id=args.developer_id)

    if not ok:
        sys.exit(1)

    if args.notarize:
        ok = notarize(target, wait=not args.no_wait)
        if not ok:
            sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
