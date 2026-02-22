# Copyright 2024 Kheper LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Build Symphony-IR as a standalone executable with PyInstaller

Usage:
    python windows/build.py                  # auto-detect platform
    python windows/build.py --platform win   # Windows EXE
    python windows/build.py --platform mac   # macOS .app
    python windows/build.py --platform linux # Linux binary
    python windows/build.py --onedir         # directory bundle (faster, needed for AppImage)

This creates:
    - dist/Symphony-IR.exe        (Windows, --onefile)
    - dist/Symphony-IR.app        (macOS,   --onefile / app bundle)
    - dist/Symphony-IR            (Linux,   --onefile)
    - dist/Symphony-IR/           (all platforms, --onedir)
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
GUI_DIR      = PROJECT_ROOT / "gui"
BUILD_DIR    = PROJECT_ROOT / "build"
DIST_DIR     = PROJECT_ROOT / "dist"


def detect_platform() -> str:
    if sys.platform == "win32":
        return "win"
    if sys.platform == "darwin":
        return "mac"
    return "linux"


def clean_build() -> None:
    for d in [BUILD_DIR, DIST_DIR]:
        if d.exists():
            print(f"  Cleaning: {d}")
            shutil.rmtree(d)


def pyinstaller_args(platform: str, onedir: bool) -> list:
    spec = [
        str(GUI_DIR / "main.py"),
        f"--name=Symphony-IR",
        f"--distpath={DIST_DIR}",
        f"--buildpath={BUILD_DIR}",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtCharts",
        f"--add-data={PROJECT_ROOT / 'docs'}:docs",
        f"--add-data={PROJECT_ROOT / 'README.md'}:.",
        "-y",
    ]

    if onedir:
        spec.append("--onedir")
    else:
        spec.append("--onefile")

    if platform == "win":
        spec.append("--windowed")
        icon = PROJECT_ROOT / "windows" / "symphony_icon.ico"
        if icon.exists():
            spec.append(f"--icon={icon}")

    elif platform == "mac":
        spec.append("--windowed")
        icon = PROJECT_ROOT / "windows" / "symphony_icon.icns"
        if icon.exists():
            spec.append(f"--icon={icon}")
        spec += ["--target-arch", "universal2"]  # Apple Silicon + Intel

    return spec


def main():
    parser = argparse.ArgumentParser(description="Build Symphony-IR standalone executable")
    parser.add_argument(
        "--platform",
        choices=["win", "mac", "linux", "auto"],
        default="auto",
        help="Target platform (default: auto-detect)"
    )
    parser.add_argument(
        "--onedir",
        action="store_true",
        help="Build directory bundle instead of single file (required for AppImage)"
    )
    parser.add_argument(
        "--no-clean",
        dest="no_clean",
        action="store_true",
        help="Skip cleaning previous build output"
    )
    args = parser.parse_args()

    platform = detect_platform() if args.platform == "auto" else args.platform
    bundle_type = "directory" if args.onedir else "single file"

    print()
    print("=" * 60)
    print(f"  Symphony-IR PyInstaller Builder")
    print(f"  Platform : {platform.upper()}")
    print(f"  Bundle   : {bundle_type}")
    print("=" * 60)
    print()

    if not args.no_clean:
        print("Cleaning previous builds...")
        clean_build()
        print()

    try:
        import PyInstaller.__main__ as pyi
    except ImportError:
        print("ERROR: PyInstaller is not installed.")
        print("  pip install -r gui/requirements-build.txt")
        sys.exit(1)

    spec = pyinstaller_args(platform, args.onedir)

    print("Running PyInstaller...")
    try:
        pyi.run(spec)
    except SystemExit as e:
        if e.code != 0:
            print(f"\nERROR: PyInstaller failed (exit {e.code})")
            sys.exit(1)

    print()
    print("Build successful!")
    print()

    # Report outputs
    if args.onedir:
        out = DIST_DIR / "Symphony-IR"
        print(f"  Directory : {out}/")
    else:
        suffix = {"win": ".exe", "mac": ".app", "linux": ""}.get(platform, "")
        out = DIST_DIR / f"Symphony-IR{suffix}"
        print(f"  Executable: {out}")

    print()

    # Post-build hints
    if platform == "win":
        print("  Next steps:")
        print("    python windows/build_innosetup.py    # create installer")
        print("    python windows/sign_executable.py dist/Symphony-IR.exe")
    elif platform == "mac":
        print("  Next steps:")
        print("    python windows/build_dmg.py          # create DMG")
        print("    python windows/sign_macos.py dist/Symphony-IR.app --notarize")
    else:
        print("  Next steps:")
        print("    python windows/build_appimage.py     # create AppImage")
        print("    python windows/sign_linux.py dist/Symphony-IR-1.0.0-x86_64.AppImage")

    print()

    # Create distribution README
    readme = DIST_DIR / "README.txt"
    readme.write_text("""\
Symphony-IR — AI Orchestrator
==============================

First Run
---------
1. Launch Symphony-IR
2. Follow the setup wizard to choose your AI provider
3. Start creating AI workflows

AI Providers
------------
Claude  — Cloud AI, free tier available (console.anthropic.com)
Ollama  — Local, free (ollama.ai), no API key needed

System Requirements
-------------------
Windows : Windows 10+, 4GB+ RAM
macOS   : 10.14+, 4GB+ RAM
Linux   : glibc 2.29+, 4GB+ RAM

Support: https://github.com/courtneybtaylor-sys/Symphony-IR
""")


if __name__ == "__main__":
    main()
