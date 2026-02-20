# Symphony-IR Build Scripts - Quick Reference

## One-Command Build

### Build Portable Executable
```bash
python windows/build_pyinstaller.py
```
✅ Creates: `dist/Symphony-IR.exe` (~250 MB)
- No installation needed
- Single file distribution
- Users run directly

### Build Professional Installer
```bash
python windows/build_pyinstaller.py
python windows/build_innosetup.py
```
✅ Creates: `installer_output/Symphony-IR-Setup-1.0.0-x64.exe` (~150 MB)
- Standard Windows installer
- Start Menu shortcuts
- Program Files installation
- Uninstall support

## File Structure After Build

```
dist/
├── Symphony-IR.exe           ← Main executable
├── README.txt               ← Quick start guide
├── SHORTCUTS.txt            ← Shortcut help
├── run.bat                  ← Batch launcher
├── docs/                    ← Documentation
├── ai-orchestrator/         ← Orchestrator files
└── _internal/               ← Dependencies (internal)

installer_output/
└── Symphony-IR-Setup-1.0.0-x64.exe  ← Professional installer
```

## Installation Flow

**For Portable .exe:**
1. Share `dist/Symphony-IR.exe`
2. Users double-click
3. App runs (no admin rights needed)

**For Installer .exe:**
1. Share `installer_output/Symphony-IR-Setup-*.exe`
2. Users run installer
3. Wizard walks through steps
4. Creates Start Menu shortcuts
5. Installs to Program Files
6. App ready to use

## Build Script Details

| Script | Purpose | Input | Output | Time |
|--------|---------|-------|--------|------|
| `build_pyinstaller.py` | PyInstaller wrapper | `gui/main.py` | `dist/Symphony-IR.exe` | 3-5 min |
| `build_innosetup.py` | Inno Setup automation | `dist/Symphony-IR.exe` | `installer_output/*.exe` | 1-2 min |
| `Symphony-IR.iss` | Installer config | Configuration file | Inno Setup uses | - |

## Prerequisites

```bash
# Install dependencies
pip install -r gui/requirements-desktop.txt

# Verify PyInstaller
python -m PyInstaller --version

# For installer: Download & install Inno Setup
# https://jrsoftware.org/isdl.php
```

## Common Commands

```bash
# Build single-file executable (default)
python windows/build_pyinstaller.py

# Build folder distribution (faster builds, faster runtime)
python windows/build_pyinstaller.py --onedir

# Build professional installer
python windows/build_innosetup.py

# Test built executable
dist/Symphony-IR.exe

# Test installer
installer_output/Symphony-IR-Setup-1.0.0-x64.exe

# Clean previous builds
rmdir /s /q build dist installer_output 2>nul
```

## Customization

### Change Application Name
Edit `build_pyinstaller.py`:
```python
APP_NAME = "Your-App-Name"
```

### Change Version
Edit `build_pyinstaller.py` and `build_innosetup.py`:
```python
VERSION = "2.0.0"
```

### Change Installation Directory
Edit `Symphony-IR.iss`:
```inno
DefaultDirName={autopf}\Your-App-Name
```

### Add Custom Icon
Place icon at `windows/symphony_icon.ico`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| PyInstaller not found | `pip install PyInstaller>=6.1.0` |
| ISCC.exe not found | Install Inno Setup, add to PATH |
| Access denied during build | Close File Explorer windows viewing dist/ |
| Missing dependencies | `pip install -r gui/requirements-desktop.txt` |
| Antivirus warning | Code sign executable or add to exclusions |

## Distribution Comparison

| Method | Size | Setup | Features | Best For |
|--------|------|-------|----------|----------|
| Portable .exe | 250 MB | None | Run anywhere | Testing, USB |
| Installer .exe | 150 MB | Yes | Full Windows integration | Public releases |
| Folder mode | 200 MB | Copy folder | Fastest builds | Development |

## CI/CD Integration

GitHub Actions automatically builds on each release tag:
- Download artifacts from Actions tab
- Or use release workflow to publish to GitHub Releases

## File Size Breakdown

Typical build sizes:
- Python runtime: ~50 MB
- PyQt6 libraries: ~100 MB
- Dependencies: ~20 MB
- Data files (docs, etc): ~20 MB
- Inno Setup compression: ~40% reduction

## Distribution Checklist

```
Before releasing:
☐ Tested on clean Windows 10 x64
☐ Tested on clean Windows 11 x64
☐ Tested Claude mode
☐ Tested Ollama mode
☐ Verified shortcuts work
☐ Tested uninstall (if installer)
☐ No files left after uninstall
☐ Documentation readable
☐ README.txt included (for portable)
☐ Version number updated
```

## Performance Tips

- **Faster startup:** Use `--onedir` mode
- **Smaller size:** Remove unused `--hidden-import` lines
- **Better compression:** Inno Setup handles automatically
- **Faster build:** Disable unused features in PyInstaller

## Support Resources

- PyInstaller Docs: https://pyinstaller.org
- Inno Setup Docs: https://jrsoftware.org/isinfo.php
- Code Signing: https://docs.microsoft.com/en-us/windows/win32/seccrypto/signtool

---

**Quick Start:**
```bash
python windows/build_pyinstaller.py
python windows/build_innosetup.py
```

Done! Share the .exe files with users.
