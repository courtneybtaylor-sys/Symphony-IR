#!/usr/bin/env python3
"""
Build Symphony-IR macOS DMG Installer

Creates a professional macOS disk image (.dmg) with:
  - Drag-to-Applications install experience
  - Custom background image support
  - License agreement
  - Automatic code signing (if APPLE_DEVELOPER_ID is set)

Usage:
    python windows/build_dmg.py
    python windows/build_dmg.py --no-sign

Requirements:
    pip install dmgbuild
    PyInstaller output must exist at dist/Symphony-IR.app

Output:
    dist/Symphony-IR-{version}.dmg

macOS only — must run on a macOS host.
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).parent.parent
DIST_DIR      = PROJECT_ROOT / "dist"
WINDOWS_DIR   = PROJECT_ROOT / "windows"
APP_NAME      = "Symphony-IR"
VERSION       = "1.0.0"
BUNDLE_ID     = "dev.symphonyir.app"

APP_PATH      = DIST_DIR / f"{APP_NAME}.app"
DMG_OUT       = DIST_DIR / f"{APP_NAME}-{VERSION}.dmg"
DMG_TEMP      = DIST_DIR / f"{APP_NAME}-{VERSION}-unsigned.dmg"

DEVELOPER_ID  = os.environ.get("APPLE_DEVELOPER_ID", "")


# ─────────────────────────────────────────────────────────────────────────────
# Prerequisites
# ─────────────────────────────────────────────────────────────────────────────

def check_prerequisites() -> bool:
    print("Checking prerequisites...")

    if sys.platform != "darwin":
        print("ERROR: macOS DMG build must run on a macOS host.")
        return False

    if not APP_PATH.exists():
        print(f"ERROR: .app bundle not found: {APP_PATH}")
        print("  Run first: python windows/build_pyinstaller.py")
        return False
    print(f"  OK  App bundle: {APP_PATH}")

    try:
        import dmgbuild as _  # noqa
        print("  OK  dmgbuild installed")
    except ImportError:
        print("  ERROR: dmgbuild not installed.")
        print("    pip install dmgbuild")
        return False

    return True


# ─────────────────────────────────────────────────────────────────────────────
# Info.plist (embedded in .app if PyInstaller hasn't set it)
# ─────────────────────────────────────────────────────────────────────────────

def ensure_info_plist() -> None:
    plist_path = APP_PATH / "Contents" / "Info.plist"
    if plist_path.exists():
        return

    plist_path.parent.mkdir(parents=True, exist_ok=True)
    plist_content = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>     <string>{APP_NAME}</string>
    <key>CFBundleExecutable</key>      <string>{APP_NAME}</string>
    <key>CFBundleIdentifier</key>      <string>{BUNDLE_ID}</string>
    <key>CFBundleName</key>            <string>{APP_NAME}</string>
    <key>CFBundleShortVersionString</key><string>{VERSION}</string>
    <key>CFBundleVersion</key>         <string>{VERSION}</string>
    <key>CFBundlePackageType</key>     <string>APPL</string>
    <key>LSMinimumSystemVersion</key>  <string>10.14</string>
    <key>NSHighResolutionCapable</key> <true/>
    <key>NSHumanReadableCopyright</key><string>Copyright 2024 Symphony-IR Contributors</string>
</dict>
</plist>
"""
    plist_path.write_text(plist_content)
    print(f"  Created Info.plist: {plist_path}")


# ─────────────────────────────────────────────────────────────────────────────
# DMG build settings (dmgbuild format)
# ─────────────────────────────────────────────────────────────────────────────

def _write_dmg_settings(settings_path: Path) -> None:
    """Write a dmgbuild settings file."""
    background = WINDOWS_DIR / "dmg_background.png"
    icon = WINDOWS_DIR / "symphony_icon.icns"

    settings = f"""\
# dmgbuild settings for Symphony-IR
# See: https://dmgbuild.readthedocs.io/

application = r'{APP_PATH}'
appname = '{APP_NAME}.app'

files = [r'{APP_PATH}']

symlinks = {{'Applications': '/Applications'}}

badge_icon = r'{icon}' if {icon.exists()} else None

background = r'{background}' if {background.exists()} else 'builtin-arrow'

icon_locations = {{
    '{APP_NAME}.app':   (160, 200),
    'Applications':     (480, 200),
}}

window_rect = ((200, 200), (660, 400))

icon_size = 128
text_size = 14
"""
    settings_path.write_text(settings)


# ─────────────────────────────────────────────────────────────────────────────
# Build DMG
# ─────────────────────────────────────────────────────────────────────────────

def build_dmg() -> bool:
    """Create the .dmg using dmgbuild."""
    import dmgbuild

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Remove existing DMG
    for f in [DMG_OUT, DMG_TEMP]:
        if f.exists():
            f.unlink()

    # Write temp settings file
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tf:
        settings_path = Path(tf.name)
    _write_dmg_settings(settings_path)

    print(f"\n  Building DMG: {DMG_OUT.name}")
    try:
        dmgbuild.build_dmg(
            filename=str(DMG_OUT),
            volume_name=APP_NAME,
            settings=str(settings_path),
        )
        print(f"  OK  DMG created: {DMG_OUT}")
        return True
    except Exception as exc:
        print(f"  ERROR: dmgbuild failed: {exc}")
        return False
    finally:
        settings_path.unlink(missing_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Code signing (optional)
# ─────────────────────────────────────────────────────────────────────────────

def sign_dmg() -> bool:
    """Sign the DMG if APPLE_DEVELOPER_ID is set."""
    if not DEVELOPER_ID:
        print("\n  INFO: APPLE_DEVELOPER_ID not set; skipping signing.")
        return True

    sign_script = WINDOWS_DIR / "sign_macos.py"
    if not sign_script.exists():
        print("  WARN: sign_macos.py not found; skipping signing.")
        return True

    print(f"\n  Signing DMG with: {DEVELOPER_ID}")
    result = subprocess.run(
        [sys.executable, str(sign_script), str(DMG_OUT)],
        check=False,
    )
    return result.returncode == 0


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(ok: bool) -> None:
    print()
    if not ok:
        print("BUILD FAILED")
        return

    size_mb = DMG_OUT.stat().st_size / (1024 * 1024) if DMG_OUT.exists() else 0
    print("=" * 60)
    print("  macOS DMG Build Complete")
    print("=" * 60)
    print(f"  Output : {DMG_OUT}")
    print(f"  Size   : {size_mb:.1f} MB")
    print()
    print("  Test locally:")
    print(f"    open {DMG_OUT}")
    print()
    print("  Notarize before distributing:")
    print(f"    python windows/sign_macos.py {DMG_OUT} --notarize")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build Symphony-IR macOS DMG")
    parser.add_argument(
        "--no-sign", dest="no_sign", action="store_true",
        help="Skip code signing even if APPLE_DEVELOPER_ID is set"
    )
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  Symphony-IR macOS DMG Builder")
    print("=" * 60)
    print()

    if not check_prerequisites():
        sys.exit(1)

    ensure_info_plist()

    ok = build_dmg()
    if not ok:
        sys.exit(1)

    if not args.no_sign:
        sign_dmg()

    print_summary(ok)


if __name__ == "__main__":
    main()
