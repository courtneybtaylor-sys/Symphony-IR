"""
Build Symphony-IR as a standalone Windows executable with PyInstaller

Usage:
    python windows/build.py

This creates:
    - dist/Symphony-IR.exe (portable application)
    - dist/Symphony-IR/ (application directory)
"""

import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__

# Determine paths
PROJECT_ROOT = Path(__file__).parent.parent
GUI_DIR = PROJECT_ROOT / "gui"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"

print("🔨 Building Symphony-IR for Windows...")
print(f"   Project: {PROJECT_ROOT}")
print()

# Clean previous builds
if BUILD_DIR.exists():
    print("🧹 Cleaning previous builds...")
    shutil.rmtree(BUILD_DIR)
if DIST_DIR.exists():
    shutil.rmtree(DIST_DIR)

# PyInstaller spec
spec = [
    str(GUI_DIR / "desktop_app.py"),
    # Output
    f"--name=Symphony-IR",
    f"--distpath={DIST_DIR}",
    f"--buildpath={BUILD_DIR}",
    # Windows
    "--windowed",  # No console window
    "--icon=windows/symphony_icon.ico",  # Add icon (optional)
    # Packages
    "--hidden-import=PyQt6",
    "--hidden-import=PyQt6.QtCore",
    "--hidden-import=PyQt6.QtGui",
    "--hidden-import=PyQt6.QtWidgets",
    "--hidden-import=PyQt6.QtCharts",
    # Data files
    f"--add-data={PROJECT_ROOT}/docs:docs",
    f"--add-data={PROJECT_ROOT}/README.md:.",
    # Optimization
    "-y",  # Overwrite without asking
    "--onefile",  # Single executable (takes longer but cleaner)
    # OR use "--onedir" for faster builds
]

print("📦 Running PyInstaller...")
try:
    PyInstaller.__main__.run(spec)
    print()
    print("✅ Build successful!")
    print()
    print("📍 Output locations:")
    print(f"   Executable: {DIST_DIR}/Symphony-IR.exe")
    print(f"   Directory:  {DIST_DIR}/Symphony-IR/")
    print()
    print("🚀 To run:")
    print(f"   {DIST_DIR}/Symphony-IR.exe")
    print()

except Exception as e:
    print(f"❌ Build failed: {e}")
    sys.exit(1)

# Create additional files
print("📄 Creating additional files...")

# Create a README for distribution
readme_content = """# Symphony-IR - AI Orchestrator

This is a standalone Windows executable for Symphony-IR.

## First Run

1. Run Symphony-IR.exe
2. Go to Settings tab
3. Choose your AI provider (Claude or Ollama)
4. Start creating AI workflows

## Requirements

### For Claude (Cloud AI)
- Anthropic API key (get from https://console.anthropic.com)
- Internet connection
- Free to paid tiers available

### For Ollama (Local AI - Free)
- Ollama installed (https://ollama.ai)
- ~4-45GB disk space for models
- No API key needed
- Completely free

## Getting Help

- Documentation: See docs/ folder
- GitHub: https://github.com/courtneybtaylor-sys/Symphony-IR
- Issues: https://github.com/courtneybtaylor-sys/Symphony-IR/issues

## System Requirements

- Windows 10 or later
- 4GB+ RAM (8GB+ for best experience)
- 500MB disk space for application
- Optional: GPU for faster Ollama inference

Enjoy using Symphony-IR!
"""

with open(DIST_DIR / "README.txt", "w") as f:
    f.write(readme_content)

print("✅ All done!")
