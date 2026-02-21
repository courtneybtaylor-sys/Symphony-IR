# Build Symphony-IR as Windows .exe Installer

Complete guide to packaging Symphony-IR as a professional Windows executable and installer.

## Overview

Symphony-IR can be distributed in two ways:

1. **Portable Executable** (`Symphony-IR.exe`)
   - Single file, no installation needed
   - Users run directly from any location
   - Perfect for testing and portable USB distribution

2. **Professional Installer** (`Symphony-IR-Setup-1.0.0-x64.exe`)
   - Standard Windows installation experience
   - Creates Start Menu shortcuts
   - Adds to Program Files
   - Uninstall functionality
   - Professional look and feel

## Quick Start (3 Steps)

### Step 1: Build Standalone Executable

```bash
cd your_project_directory
python windows/build_pyinstaller.py
```

This creates:
- `dist/Symphony-IR.exe` (main executable)
- `dist/docs/` (documentation)
- `dist/ai-orchestrator/` (orchestrator files)
- `dist/README.txt` (for users)
- `dist/run.bat` (launcher helper)

**Test the executable:**
```bash
dist/Symphony-IR.exe
```

### Step 2 (Optional): Build Professional Installer

First install Inno Setup:
- Download: https://jrsoftware.org/isdl.php
- Install and add to PATH
- Or let the script find it automatically

Then build:
```bash
python windows/build_innosetup.py
```

This creates:
- `installer_output/Symphony-IR-Setup-1.0.0-x64.exe`

**Test the installer:**
```bash
installer_output/Symphony-IR-Setup-1.0.0-x64.exe
```

## Detailed Build Process

### Prerequisites

**Windows 10/11 x64**
- Python 3.9+
- Git (optional)

**Python packages** (installed automatically):
```
PyInstaller>=6.1.0
PyQt6==6.7.0
PyQt6-Charts==6.7.0
keyring==25.1.0
setuptools>=65.0.0
wheel>=0.38.0
```

**For installer only:**
- Inno Setup 6.0+ (https://jrsoftware.org/isdl.php)

### Installation Instructions

1. **Install Python packages:**
```bash
pip install -r gui/requirements-desktop.txt
```

2. **Install Inno Setup** (if making installer):
   - Download: https://jrsoftware.org/isdl.php
   - Run installer, follow prompts
   - Accept default install location

3. **Verify installations:**
```bash
# Check PyInstaller
python -m PyInstaller --version

# Check Inno Setup (if installed)
where ISCC.exe
```

### Building Step-by-Step

#### Method 1: Single File Executable (Recommended for Distribution)

```bash
python windows/build_pyinstaller.py
```

**Output:**
- `dist/Symphony-IR.exe` (~200-300 MB)
- Includes all dependencies
- Can be distributed as single file

**Pros:**
- Single file distribution
- No installation needed
- Users can run from any location
- Portable USB distribution

**Cons:**
- Larger file size
- Longer startup time
- No uninstall mechanism

#### Method 2: Folder Distribution (Faster Build)

```bash
python windows/build_pyinstaller.py --onedir
```

**Output:**
- `dist/Symphony-IR/` folder
- Entire folder must be distributed
- Faster build time
- Faster startup

**Pros:**
- Faster build (~2-3 minutes)
- Faster startup
- Easier to debug

**Cons:**
- Must distribute entire folder
- Larger total size

#### Method 3: Professional Installer

```bash
# First build executable
python windows/build_pyinstaller.py

# Then build installer
python windows/build_innosetup.py
```

**Output:**
- `installer_output/Symphony-IR-Setup-1.0.0-x64.exe` (~150-200 MB)

**Pros:**
- Standard Windows installer experience
- Creates Start Menu shortcuts
- Installs to Program Files
- Professional appearance
- Uninstall support

**Cons:**
- Requires Inno Setup installation
- Requires user to accept license
- Installation takes disk space

## Build Script Details

### build_pyinstaller.py

**Purpose:** Converts Python application to standalone Windows executable

**Features:**
- Automatic dependency bundling
- PyQt6 library inclusion
- Data files packaging
- Icon support
- Error handling and validation
- Progress reporting

**Usage:**
```bash
# Single file (default)
python windows/build_pyinstaller.py

# Folder mode
python windows/build_pyinstaller.py --onedir

# With custom options
python windows/build_pyinstaller.py --help
```

**Output:**
```
dist/
├── Symphony-IR.exe          (main executable)
├── README.txt              (quick start)
├── SHORTCUTS.txt           (shortcut help)
├── run.bat                 (launcher)
├── docs/                   (documentation)
├── ai-orchestrator/        (orchestrator files)
└── _internal/              (dependencies, internal)
```

### build_innosetup.py

**Purpose:** Creates professional Windows installer

**Features:**
- Automatic Inno Setup detection
- Prerequisite verification
- Installation automation
- Error reporting
- Summary generation

**Usage:**
```bash
python windows/build_innosetup.py
```

**Output:**
```
installer_output/
└── Symphony-IR-Setup-1.0.0-x64.exe
```

### Symphony-IR.iss

**Purpose:** Inno Setup configuration script

**Contains:**
- Application metadata
- File packaging instructions
- Start Menu integration
- Desktop shortcuts
- Custom installation logic
- System requirement checks
- License text (optional)

**Customization:**
Edit these values to customize installer:
```inno
AppName=Symphony-IR
AppVersion=1.0.0
AppPublisher=Your Organization
DefaultDirName={autopf}\Symphony-IR
```

## Troubleshooting

### Issue: "PyInstaller not found"

```bash
pip install PyInstaller>=6.1.0
```

### Issue: "Could not find icon file"

The script will still work without icon, but executable won't have custom icon.
To fix, add an icon:

```bash
# Get icon from project
cp icon.png windows/symphony_icon.ico

# Or create one online: https://convertio.co/png-ico/
```

### Issue: "ISCC.exe not found"

Inno Setup not installed or not in PATH.

**Solution:**
1. Install Inno Setup: https://jrsoftware.org/isdl.php
2. Add to PATH manually:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Add: `C:\Program Files (x86)\Inno Setup 6`

Or let script find it:
```bash
python windows/build_innosetup.py
```

### Issue: "Access denied" during build

Close any programs using the dist folder and try again.

### Issue: Antivirus warning about executable

This is common for newly built executables. Options:

1. **Code Signing:**
```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.server dist/Symphony-IR.exe
```

2. **Whitelist the folder:**
Add `dist/` and `build/` to antivirus exclusions

3. **Submit for scanning:**
Upload to VirusTotal or other services for reputation

## Distribution

### Option 1: Direct .exe Distribution

**Best for:**
- Testing
- Portable USB distribution
- Internal use

**Steps:**
1. Build executable: `python windows/build_pyinstaller.py`
2. Share `dist/Symphony-IR.exe` to users
3. Users double-click to run (no installation)

**Include:**
- `dist/README.txt` (quick start guide)
- `dist/SHORTCUTS.txt` (help creating shortcuts)

### Option 2: Installer Distribution

**Best for:**
- Public releases
- Professional appearance
- System integration

**Steps:**
1. Build executable: `python windows/build_pyinstaller.py`
2. Build installer: `python windows/build_innosetup.py`
3. Share `installer_output/Symphony-IR-Setup-1.0.0-x64.exe`

**Users run installer and get:**
- Start Menu shortcuts
- Desktop shortcut (optional)
- Program Files installation
- Uninstall support

### Option 3: GitHub Releases

**Steps:**
1. Create GitHub release
2. Upload both options:
   - `dist/Symphony-IR.exe` (portable)
   - `installer_output/Symphony-IR-Setup-1.0.0-x64.exe` (installer)
3. Users choose which to download

**Example release notes:**
```markdown
# Symphony-IR v1.0.0

## Downloads

**Portable (No Installation)**
- `Symphony-IR.exe` - Run directly, no setup needed

**Standard Installer**
- `Symphony-IR-Setup-1.0.0-x64.exe` - Full Windows installation

## System Requirements
- Windows 10 or later
- 4GB+ RAM
- 500MB disk space

## Quick Start
1. Download and run
2. Go to Settings tab
3. Choose AI provider (Claude or Ollama)
4. Start creating workflows!
```

## Advanced: Code Signing

For production releases, code sign the executable to avoid Windows security warnings:

```bash
# Export certificate if you have one
# signtool sign /f certificate.pfx /p password /t http://timestamp.server dist/Symphony-IR.exe

# For installer too
# signtool sign /f certificate.pfx /p password /t http://timestamp.server installer_output/Symphony-IR-Setup-1.0.0-x64.exe
```

Get certificate from:
- DigiCert: https://www.digicert.com/code-signing/windows-code-signing-certificate
- Sectigo: https://sectigo.com/ssl-certificates-tls/code-signing
- Other CAs

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Windows Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r gui/requirements-desktop.txt
      
      - name: Build executable
        run: python windows/build_pyinstaller.py
      
      - name: Build installer
        run: python windows/build_innosetup.py
      
      - name: Upload Release Assets
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/Symphony-IR.exe
            installer_output/Symphony-IR-Setup-*.exe
```

## File Size Optimization

If executable is too large:

1. **Use --onedir mode:**
```bash
python windows/build_pyinstaller.py --onedir
```

2. **Remove unused dependencies:**
Edit `build_pyinstaller.py` and remove unnecessary `--hidden-import` lines

3. **Compress installer:**
Inno Setup has built-in LZMA compression (default)

## Testing Checklist

Before distributing:

- [ ] Extract and run `Symphony-IR.exe` on fresh Windows 10/11
- [ ] Verify all tabs load (Orchestrator, Flow, History, Settings)
- [ ] Test Claude mode with valid API key
- [ ] Test Ollama mode (if available)
- [ ] Test creating and running workflows
- [ ] Verify documentation is readable
- [ ] Check Start Menu shortcuts (for installer)
- [ ] Check Desktop shortcuts (for installer)
- [ ] Test uninstall functionality (for installer)
- [ ] Verify no file left behind after uninstall
- [ ] Test with UAC enabled
- [ ] Test with antivirus enabled

## Support

For issues:
- GitHub Issues: https://github.com/courtneybtaylor-sys/Symphony-IR/issues
- Include: Windows version, error message, steps to reproduce

---

**Version:** 1.0.0  
**Updated:** 2024  
**For:** Symphony-IR Project
