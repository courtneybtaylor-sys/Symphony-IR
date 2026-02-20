#!/usr/bin/env python3
"""
Build Symphony-IR as a standalone Windows executable with PyInstaller

Usage:
    python windows/build_pyinstaller.py [--onedir]

This creates:
    - dist/Symphony-IR.exe (portable application)
    - dist/Symphony-IR/ (application directory with all dependencies)
    
Options:
    --onedir    Use one-folder distribution (faster, easier to debug)
    --onefile   Use single executable (default, slower to build, cleaner distribution)
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# Import PyInstaller
try:
    import PyInstaller.__main__
except ImportError:
    print("❌ PyInstaller not installed!")
    print("   Run: pip install PyInstaller>=6.1.0")
    sys.exit(1)

# ═════════════════════════════════════════════════════════════════════════════
# Configuration
# ═════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent
GUI_DIR = PROJECT_ROOT / "gui"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
WINDOWS_DIR = PROJECT_ROOT / "windows"
ICON_PATH = WINDOWS_DIR / "symphony_icon.ico"

APP_NAME = "Symphony-IR"
VERSION = "1.0.0"


def clean_previous_builds():
    """Remove previous build artifacts."""
    print("🧹 Cleaning previous builds...")
    for directory in [BUILD_DIR, DIST_DIR]:
        if directory.exists():
            print(f"   Removing {directory}")
            shutil.rmtree(directory)


def build_executable(onefile=True):
    """Build the executable using PyInstaller."""
    
    mode = "--onefile" if onefile else "--onedir"
    mode_str = "single file" if onefile else "folder"
    
    print(f"📦 Building {APP_NAME} ({mode_str})...")
    print()
    
    # Prepare PyInstaller arguments
    spec = [
        # Entry point
        str(GUI_DIR / "main.py"),
        
        # Output configuration
        f"--name={APP_NAME}",
        f"--distpath={DIST_DIR}",
        f"--buildpath={BUILD_DIR}",
        f"--workpath={BUILD_DIR}/work",
        
        # Windows-specific
        "--windowed",  # No console window
        mode,  # Distribution mode
        
        # Icon (if exists)
        *([f"--icon={ICON_PATH}"] if ICON_PATH.exists() else []),
        
        # Python packages (PyQt6 internals)
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtCharts",
        "--hidden-import=keyring",
        "--hidden-import=keyring.backends",
        
        # Data files
        f"--add-data={GUI_DIR}:gui",
        f"--add-data={PROJECT_ROOT / 'docs'}:docs",
        f"--add-data={PROJECT_ROOT / 'README.md'}:.",
        f"--add-data={PROJECT_ROOT / 'ai-orchestrator'}:ai-orchestrator",
        
        # Optimization
        "-y",  # Overwrite without asking
        "--clean",  # Clean PyInstaller cache
        
        # Verbosity
        "--log-level=INFO",
    ]
    
    try:
        PyInstaller.__main__.run(spec)
        return True
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return False


def create_distribution_files():
    """Create additional distribution files."""
    
    print()
    print("📄 Creating distribution files...")
    
    # README for distribution
    readme_content = f"""# {APP_NAME} - Deterministic Multi-Agent Orchestration Engine

This is a standalone Windows executable for {APP_NAME}.

## Installation

1. Run Symphony-IR.exe
2. Choose your AI provider:
   - **Claude** (cloud): Requires Anthropic API key
   - **Ollama** (local): Free, runs on your computer

## First Time Setup

1. Launch Symphony-IR from Start Menu or double-click executable
2. Go to **Settings** tab
3. Select your AI provider
4. Enter API key (if using Claude)
5. Start creating AI workflows!

## System Requirements

- Windows 10 or later (x64)
- 4GB+ RAM (8GB+ recommended)
- 500MB+ disk space for application
- 10GB+ disk space if using Ollama

## Features

✓ Multi-Agent Coordination
✓ Real-time Execution
✓ Session History & Management
✓ Metrics Dashboard
✓ Flow-based Workflows
✓ Secure Credential Storage
✓ Dark Theme Support

## Documentation

- README: Main documentation
- FLOW.md: Creating workflows
- OLLAMA.md: Using local Ollama
- SECURITY.md: Security features

## Support

For issues, visit:
https://github.com/courtneybtaylor-sys/Symphony-IR/issues

## License

Symphony-IR is open source. See LICENSE file for details.

---
Version {VERSION}
"""
    
    with open(DIST_DIR / "README.txt", "w") as f:
        f.write(readme_content)
    print(f"✅ Created README.txt")
    
    # Create shortcut information
    shortcut_info = """Symphony-IR Shortcuts
====================

If you want to create additional shortcuts:

1. Right-click on Desktop
2. Select "New" → "Shortcut"
3. Enter target: {path}\\Symphony-IR.exe
4. Name it: Symphony-IR
5. Click Finish

To pin to Start Menu:
1. Right-click Symphony-IR.exe
2. Select "Pin to Start"
"""
    
    with open(DIST_DIR / "SHORTCUTS.txt", "w") as f:
        f.write(shortcut_info)
    print(f"✅ Created SHORTCUTS.txt")


def create_launcher_batch():
    """Create a batch file launcher for convenience."""
    
    launcher_content = """@echo off
REM Symphony-IR Launcher
REM This batch file runs Symphony-IR.exe from the current directory

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Run the executable
echo Launching Symphony-IR...
start "" "!SCRIPT_DIR!Symphony-IR.exe"

REM Exit silently
exit /b 0
"""
    
    launcher_path = DIST_DIR / "run.bat"
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    print(f"✅ Created run.bat")


def print_summary(onefile=True):
    """Print build summary."""
    
    exe_path = DIST_DIR / f"{APP_NAME}.exe"
    
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              Build Complete! ✅                           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("📍 Output locations:")
    print(f"   Executable: {exe_path}")
    print(f"   Directory:  {DIST_DIR}/{APP_NAME}/")
    print()
    print("📦 Next Steps:")
    print()
    print("   1. Test the executable:")
    print(f"      {exe_path}")
    print()
    print("   2. Create installer (Inno Setup):")
    print("      python windows/build_innosetup.py")
    print()
    print("   3. Distribute to users:")
    print("      - Share .exe directly for portable use")
    print("      - Share installer .exe for system integration")
    print()
    print("📄 Files included:")
    print("   • Symphony-IR.exe - Main application")
    print("   • README.txt - Quick start guide")
    print("   • SHORTCUTS.txt - How to create shortcuts")
    print("   • run.bat - Batch launcher (optional)")
    print()
    print("💡 Pro Tips:")
    print("   • Distribute README.txt with the .exe")
    print("   • Consider code signing for production")
    print("   • Test on clean Windows systems before release")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Build Symphony-IR as a Windows executable"
    )
    parser.add_argument(
        "--onedir",
        action="store_true",
        help="Use one-folder distribution (faster, larger)"
    )
    
    args = parser.parse_args()
    onefile = not args.onedir
    
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       PyInstaller Build for Symphony-IR                   ║")
    print("║          Windows Executable Generator                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print(f"📍 Project: {PROJECT_ROOT}")
    print(f"📍 Output: {DIST_DIR}")
    print()
    
    # Verify requirements
    print("Checking requirements...")
    if not (GUI_DIR / "main.py").exists():
        print(f"❌ Main entry point not found: {GUI_DIR / 'main.py'}")
        sys.exit(1)
    print("✅ Entry point found")
    
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} installed")
    except ImportError:
        print("❌ PyInstaller not installed. Run: pip install PyInstaller>=6.1.0")
        sys.exit(1)
    
    print()
    
    # Build
    clean_previous_builds()
    print()
    
    if not build_executable(onefile=onefile):
        sys.exit(1)
    
    print()
    create_distribution_files()
    create_launcher_batch()
    print_summary(onefile=onefile)


if __name__ == "__main__":
    main()
