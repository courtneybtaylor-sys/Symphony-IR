#!/usr/bin/env python3
"""
Build Symphony-IR Linux AppImage

Creates a self-contained portable AppImage that runs on any modern
Linux distribution without installation.

Usage:
    python windows/build_appimage.py
    python windows/build_appimage.py --no-sign

Requirements:
    - appimagetool in PATH or downloadable from GitHub
        wget -O /usr/local/bin/appimagetool \\
          https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
        chmod +x /usr/local/bin/appimagetool
    - PyInstaller output must exist at dist/Symphony-IR (directory, not --onefile)
    - Linux host (or CI runner)

Output:
    dist/Symphony-IR-{version}.AppImage

AppImage spec: https://docs.appimage.org/
"""

import os
import sys
import shutil
import stat
import subprocess
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).parent.parent
DIST_DIR      = PROJECT_ROOT / "dist"
WINDOWS_DIR   = PROJECT_ROOT / "windows"

APP_NAME      = "Symphony-IR"
APP_VERSION   = "1.0.0"
APPDIR        = DIST_DIR / f"{APP_NAME}.AppDir"
APPIMAGE_OUT  = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-x86_64.AppImage"

# PyInstaller directory output (use --onedir, not --onefile, for AppImage)
PYINSTALLER_DIR = DIST_DIR / APP_NAME   # dist/Symphony-IR/

GPG_KEY_ID    = os.environ.get("GPG_KEY_ID", "")


# ─────────────────────────────────────────────────────────────────────────────
# Prerequisites
# ─────────────────────────────────────────────────────────────────────────────

def find_appimagetool() -> str:
    """Locate appimagetool binary."""
    candidates = [
        shutil.which("appimagetool"),
        "/usr/local/bin/appimagetool",
        str(Path.home() / ".local/bin/appimagetool"),
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    return ""


def check_prerequisites() -> bool:
    print("Checking prerequisites...")

    if sys.platform == "darwin":
        print("ERROR: AppImage build must run on a Linux host.")
        return False

    if not PYINSTALLER_DIR.exists():
        print(f"ERROR: PyInstaller directory not found: {PYINSTALLER_DIR}")
        print("  Run: python windows/build_pyinstaller.py  (use --onedir, not --onefile)")
        return False
    print(f"  OK  PyInstaller dir: {PYINSTALLER_DIR}")

    tool = find_appimagetool()
    if not tool:
        print("  ERROR: appimagetool not found.")
        print("  Install:")
        print("    wget -O /usr/local/bin/appimagetool \\")
        print("      https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage")
        print("    chmod +x /usr/local/bin/appimagetool")
        return False
    print(f"  OK  appimagetool: {tool}")

    return True


# ─────────────────────────────────────────────────────────────────────────────
# AppDir structure
# ─────────────────────────────────────────────────────────────────────────────

def build_appdir() -> None:
    """Build the AppDir layout required by AppImageKit."""
    print(f"\n  Building AppDir: {APPDIR}")

    # Clean previous AppDir
    if APPDIR.exists():
        shutil.rmtree(APPDIR)

    # usr/bin/ — main executable
    bin_dir = APPDIR / "usr" / "bin"
    bin_dir.mkdir(parents=True)

    # usr/lib/ — shared libraries
    lib_dir = APPDIR / "usr" / "lib"
    lib_dir.mkdir(parents=True)

    # Copy PyInstaller output into usr/bin/
    print(f"  Copying PyInstaller output...")
    shutil.copytree(
        src=PYINSTALLER_DIR,
        dst=bin_dir / APP_NAME,
        dirs_exist_ok=True,
    )

    # AppRun entry point
    _write_apprun()

    # .desktop file
    _write_desktop()

    # Icon (copy from windows/ or create placeholder)
    _copy_icon()

    print(f"  OK  AppDir built at: {APPDIR}")


def _write_apprun() -> None:
    """Write the AppRun shell script."""
    apprun = APPDIR / "AppRun"
    apprun.write_text(f"""\
#!/bin/sh
# Symphony-IR AppImage entry point
# Sets up the runtime environment and executes the main binary.

# Use AppImage's own directory as the base
SELF=$(readlink -f "$0")
HERE=$(dirname "$SELF")
export PATH="$HERE/usr/bin/{APP_NAME}:$PATH"
export LD_LIBRARY_PATH="$HERE/usr/lib:$HERE/usr/bin/{APP_NAME}:$LD_LIBRARY_PATH"
export XDG_DATA_DIRS="$HERE/usr/share:$XDG_DATA_DIRS"

# Launch the application
exec "$HERE/usr/bin/{APP_NAME}/{APP_NAME}" "$@"
""")
    apprun.chmod(apprun.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print(f"  Created AppRun")


def _write_desktop() -> None:
    """Write the .desktop metadata file."""
    desktop = APPDIR / f"{APP_NAME}.desktop"
    desktop.write_text(f"""\
[Desktop Entry]
Name={APP_NAME}
Exec={APP_NAME}
Icon={APP_NAME}
Type=Application
Categories=Development;Utility;
Comment=Deterministic Multi-Agent AI Orchestration
StartupNotify=true
Version=1.0
""")
    print(f"  Created {APP_NAME}.desktop")


def _copy_icon() -> None:
    """Copy icon file(s) for AppImage."""
    icon_src_png = WINDOWS_DIR / "symphony_icon.png"
    icon_src_svg = WINDOWS_DIR / "symphony_icon.svg"

    icon_dst_dir = APPDIR / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps"
    icon_dst_dir.mkdir(parents=True, exist_ok=True)

    if icon_src_png.exists():
        shutil.copy2(icon_src_png, APPDIR / f"{APP_NAME}.png")
        shutil.copy2(icon_src_png, icon_dst_dir / f"{APP_NAME}.png")
        print(f"  Copied icon: {APP_NAME}.png")
    elif icon_src_svg.exists():
        shutil.copy2(icon_src_svg, APPDIR / f"{APP_NAME}.svg")
        print(f"  Copied icon: {APP_NAME}.svg")
    else:
        # Create a minimal placeholder PNG (1x1 blue pixel)
        placeholder = APPDIR / f"{APP_NAME}.png"
        try:
            import struct, zlib
            def _png_1x1(r, g, b):
                raw = b'\x00' + bytes([r, g, b, 255])
                compressed = zlib.compress(raw)
                def chunk(name, data):
                    c = struct.pack('>I', len(data)) + name + data
                    return c + struct.pack('>I', zlib.crc32(c[4:]) & 0xffffffff)
                return (b'\x89PNG\r\n\x1a\n'
                        + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
                        + chunk(b'IDAT', compressed)
                        + chunk(b'IEND', b''))
            placeholder.write_bytes(_png_1x1(59, 130, 246))
        except Exception:
            placeholder.write_bytes(b'')
        print(f"  Created placeholder icon")


# ─────────────────────────────────────────────────────────────────────────────
# Build AppImage
# ─────────────────────────────────────────────────────────────────────────────

def build_appimage() -> bool:
    """Invoke appimagetool to create the AppImage."""
    tool = find_appimagetool()
    if not tool:
        print("ERROR: appimagetool not found.")
        return False

    if APPIMAGE_OUT.exists():
        APPIMAGE_OUT.unlink()

    print(f"\n  Building AppImage: {APPIMAGE_OUT.name}")

    env = os.environ.copy()
    env["ARCH"] = "x86_64"

    result = subprocess.run(
        [tool, str(APPDIR), str(APPIMAGE_OUT)],
        env=env,
        check=False,
    )
    if result.returncode == 0 and APPIMAGE_OUT.exists():
        # Make executable
        APPIMAGE_OUT.chmod(
            APPIMAGE_OUT.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
        )
        print(f"  OK  AppImage created: {APPIMAGE_OUT.name}")
        return True
    else:
        print(f"  ERROR: appimagetool failed (exit {result.returncode})")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# GPG signing (optional)
# ─────────────────────────────────────────────────────────────────────────────

def sign_appimage() -> bool:
    if not GPG_KEY_ID:
        print("\n  INFO: GPG_KEY_ID not set; skipping GPG signature.")
        return True

    sign_script = WINDOWS_DIR / "sign_linux.py"
    if not sign_script.exists():
        print("  WARN: sign_linux.py not found; skipping signature.")
        return True

    print(f"\n  Signing AppImage with GPG key: {GPG_KEY_ID}")
    result = subprocess.run(
        [sys.executable, str(sign_script), str(APPIMAGE_OUT)],
        env={**os.environ, "GPG_KEY_ID": GPG_KEY_ID},
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

    size_mb = APPIMAGE_OUT.stat().st_size / (1024 * 1024) if APPIMAGE_OUT.exists() else 0
    print("=" * 60)
    print("  Linux AppImage Build Complete")
    print("=" * 60)
    print(f"  Output : {APPIMAGE_OUT}")
    print(f"  Size   : {size_mb:.1f} MB")
    print()
    print("  Test locally:")
    print(f"    ./{APPIMAGE_OUT.name}")
    print()
    print("  Verify signature (if signed):")
    print(f"    gpg --verify {APPIMAGE_OUT.name}.sig {APPIMAGE_OUT.name}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build Symphony-IR Linux AppImage")
    parser.add_argument(
        "--no-sign", dest="no_sign", action="store_true",
        help="Skip GPG signing even if GPG_KEY_ID is set"
    )
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  Symphony-IR Linux AppImage Builder")
    print("=" * 60)
    print()

    if not check_prerequisites():
        sys.exit(1)

    build_appdir()

    ok = build_appimage()
    if not ok:
        sys.exit(1)

    if not args.no_sign:
        sign_appimage()

    print_summary(ok)


if __name__ == "__main__":
    main()
