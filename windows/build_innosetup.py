#!/usr/bin/env python3
"""
Build Symphony-IR Windows Installer using Inno Setup

This script automates the creation of a professional Windows installer.

Usage:
    python windows/build_innosetup.py

Requirements:
    1. PyInstaller executable built (dist/Symphony-IR.exe)
    2. Inno Setup 6.0+ installed (https://jrsoftware.org/isdl.php)
    3. Inno Setup in system PATH or ISCC.exe available

This creates:
    - installer_output/Symphony-IR-Setup-{version}-x64.exe
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import re

# ═════════════════════════════════════════════════════════════════════════════
# Configuration
# ═════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
WINDOWS_DIR = PROJECT_ROOT / "windows"
ISS_FILE = WINDOWS_DIR / "Symphony-IR.iss"
INSTALLER_OUTPUT = PROJECT_ROOT / "installer_output"
VERSION = "1.0.0"


def find_inno_setup():
    """Find Inno Setup installation."""
    
    # Common installation paths for Inno Setup
    common_paths = [
        Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files (x86)/Inno Setup/ISCC.exe"),
        Path("C:/Program Files/Inno Setup/ISCC.exe"),
    ]
    
    # Try common paths
    for path in common_paths:
        if path.exists():
            return path
    
    # Try system PATH
    try:
        result = subprocess.run(
            ["where", "ISCC.exe"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    
    return None


def verify_prerequisites():
    """Verify all prerequisites are met."""
    
    print("Checking prerequisites...")
    print()
    
    # Check PyInstaller output
    exe_path = DIST_DIR / "Symphony-IR.exe"
    if not exe_path.exists():
        print(f"❌ PyInstaller executable not found: {exe_path}")
        print()
        print("   Run first: python windows/build_pyinstaller.py")
        return False
    print(f"✅ PyInstaller executable: {exe_path}")
    
    # Check Inno Setup script
    if not ISS_FILE.exists():
        print(f"❌ Inno Setup script not found: {ISS_FILE}")
        return False
    print(f"✅ Inno Setup script: {ISS_FILE}")
    
    # Check Inno Setup installation
    inno_setup = find_inno_setup()
    if not inno_setup:
        print("❌ Inno Setup not found!")
        print()
        print("   Download from: https://jrsoftware.org/isdl.php")
        print("   Install and add to system PATH")
        return False
    print(f"✅ Inno Setup: {inno_setup}")
    
    return True


def prepare_output_directory():
    """Create output directory for installer."""
    
    if INSTALLER_OUTPUT.exists():
        print(f"🧹 Cleaning previous installer output...")
        shutil.rmtree(INSTALLER_OUTPUT)
    
    INSTALLER_OUTPUT.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {INSTALLER_OUTPUT}")


def build_installer():
    """Build the installer using Inno Setup."""
    
    inno_setup = find_inno_setup()
    
    print()
    print("🔨 Building Inno Setup installer...")
    print()
    
    # Prepare command
    command = [
        str(inno_setup),
        str(ISS_FILE),
    ]
    
    try:
        # Run Inno Setup compiler
        result = subprocess.run(
            command,
            capture_output=False,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print()
            print(f"❌ Inno Setup compilation failed (exit code: {result.returncode})")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error running Inno Setup: {e}")
        return False


def find_installer():
    """Find the created installer."""
    
    # Look for .exe files in output directory
    exe_files = list(INSTALLER_OUTPUT.glob("*.exe"))
    
    if not exe_files:
        return None
    
    # Return the most recently created
    return max(exe_files, key=os.path.getctime)


def print_summary(installer_path):
    """Print build summary."""
    
    if not installer_path:
        print()
        print("⚠️  Could not find installer output")
        print(f"   Check: {INSTALLER_OUTPUT}")
        return
    
    file_size = installer_path.stat().st_size / (1024 * 1024)
    
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          Installer Build Complete! ✅                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print(f"📍 Installer: {installer_path}")
    print(f"📊 Size: {file_size:.1f} MB")
    print()
    print("📦 Distribution Options:")
    print()
    print("   Option A: Direct Distribution")
    print("   • Share Setup-*.exe directly to users")
    print("   • Standard Windows installer experience")
    print("   • Installs to Program Files")
    print()
    print("   Option B: Portable Distribution")
    print("   • Share dist/Symphony-IR.exe directly")
    print("   • No installation required")
    print("   • Users can run from any location")
    print()
    print("📋 Distribution Checklist:")
    print("   ☐ Test installer on clean Windows 10/11 x64")
    print("   ☐ Verify uninstall functionality")
    print("   ☐ Test both Claude and Ollama modes")
    print("   ☐ Verify shortcuts created correctly")
    print("   ☐ Check documentation displays properly")
    print()
    print("🚀 Next Steps:")
    print()
    print("   1. Test locally:")
    print(f"      {installer_path}")
    print()
    print("   2. Sign installer (optional):")
    print("      signtool sign /f cert.pfx /p password /t http://timestamp.server")
    print(f"      {installer_path}")
    print()
    print("   3. Distribute:")
    print(f"      Upload {installer_path.name} to releases")
    print()


def main():
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║      Inno Setup Installer Builder for Symphony-IR         ║")
    print("║          Professional Windows Installer                   ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Verify prerequisites
    if not verify_prerequisites():
        print()
        print("❌ Prerequisites not met. Aborting.")
        sys.exit(1)
    
    print()
    
    # Prepare output
    prepare_output_directory()
    
    # Build installer
    print()
    if not build_installer():
        sys.exit(1)
    
    # Find and report
    installer_path = find_installer()
    print_summary(installer_path)


if __name__ == "__main__":
    main()
