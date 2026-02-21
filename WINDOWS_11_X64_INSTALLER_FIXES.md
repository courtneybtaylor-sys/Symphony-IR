# Windows 11 x64 Installer Issues & Fixes

## Executive Summary

Symphony-IR's Windows installer has been reviewed for compatibility with **Windows 11 x64-bit OS**. Several critical and minor issues have been identified that could prevent successful installation or execution. This document outlines all issues found and provides fixes.

---

## Critical Issues

### Issue 1: PyQt6 x64 Native Library Compatibility

**Problem:**
- PyQt6 6.6.1 has known issues with x64 Python installations on Windows 11
- Some native bindings can fail during import on x64 systems
- The `keyring` library (24.3.0) also has x64 compatibility issues with Windows Credential Manager

**Impact:** HIGH - Application won't start
**Symptom:** "ImportError: DLL load failed" or "OSError: [WinError 126]"

**Root Cause:**
- PyQt6 wheels may not include properly compiled x64 binaries
- Keyring library needs proper VC++ redistributables

**Fix:**
```powershell
# Update requirements-desktop.txt with x64-compatible versions
PyQt6==6.7.0         # Updated to latest with x64 fixes
PyQt6-Charts==6.7.0  # Must match PyQt6 version
keyring==25.1.0      # Latest version with better x64 support
```

**Implementation:**
1. Update `/vercel/share/v0-project/gui/requirements-desktop.txt`
2. Add Visual C++ Redistributables check to `install.ps1`

---

### Issue 2: Python Virtual Environment Path Length (Windows 11 Limitation)

**Problem:**
- Windows has a 260-character path limit by default (even on Windows 11)
- Installation path `$env:ProgramFiles\Symphony-IR` can exceed limits with nested venv
- Batch files use relative paths that may exceed MAX_PATH

**Impact:** MEDIUM - Installation fails or venv activation breaks
**Symptom:** "The filename or extension is too long" error

**Root Cause:**
- Program Files deep nesting + virtual environment paths exceed 260 chars
- Windows 11 doesn't auto-enable long paths

**Fix:**
1. Use shorter installation paths
2. Enable Windows long path support
3. Store venv outside of Program Files

**Implementation:**
```powershell
# In install.ps1, add long path support
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

---

### Issue 3: PowerShell Execution Policy & Admin Rights Detection

**Problem:**
- `install.ps1` requires admin rights but doesn't force restart
- Execution policy check happens AFTER script runs, not before
- Users can't easily elevate if they forget "Run as Administrator"

**Impact:** MEDIUM - Silent failures on first run
**Symptom:** Installation appears to complete but dependencies don't install

**Root Cause:**
- Admin check is informational only, not blocking
- No automatic re-elevation mechanism
- File copy operations fail silently without admin

**Fix:**
```powershell
# Add proper admin elevation with auto-restart
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    $arguments = "& '$PSCommandPath'"
    Start-Process powershell -ArgumentList $arguments -Verb RunAs
    exit
}
```

---

### Issue 4: Missing Visual C++ Redistributables Check

**Problem:**
- PyQt6 and other native libraries require Visual C++ Runtime 2015+ on Windows
- Windows 11 may have older or missing runtimes
- Silent installation failures without proper error message

**Impact:** MEDIUM - Runtime failures
**Symptom:** Application crash with "VCRUNTIME140.dll not found"

**Root Cause:**
- Installer doesn't verify VC++ redistributables
- PyQt6 dependency chain not documented

**Fix:**
```powershell
# Add check for Visual C++ Runtime in install.ps1
function Check-VCRedist {
    $vcRedistKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
    $vcInstalled = Get-ItemProperty $vcRedistKey | Where-Object {$_.DisplayName -like "*Visual C++*" -and $_.DisplayName -like "*2015-2022*"}
    
    if (-not $vcInstalled) {
        Write-Host "⚠️  Installing Visual C++ Redistributables..." -ForegroundColor Yellow
        # Download and install vc_redist.x64.exe
    }
}
```

---

### Issue 5: Batch File Encoding Issues

**Problem:**
- `launcher.bat` and `run-gui.bat` may be saved with UTF-8 BOM
- Windows batch interpreter requires ANSI/ASCII or UTF-8 without BOM
- Unicode characters (✅, ❌, etc.) cause parsing errors

**Impact:** LOW-MEDIUM - GUI launcher fails
**Symptom:** "The system cannot find the file specified" or garbled output

**Root Cause:**
- Git may convert line endings to CRLF with UTF-8 BOM on Windows
- Batch parser can't handle these characters

**Fix:**
1. Save batch files as **ANSI encoding** (no BOM)
2. Use `exit /b` instead of just `exit`
3. Escape special characters properly

---

### Issue 6: Antivirus/Defender False Positives

**Problem:**
- PyInstaller-generated .exe files often trigger Windows Defender
- NSIS installer may be flagged as suspicious
- Installation hangs or silently fails with Defender

**Impact:** MEDIUM - Installation appears stuck
**Symptom:** Installation hangs at "Installing dependencies" or "Initializing"

**Root Cause:**
- Unsigned executables and scripts
- PyInstaller is commonly flagged
- Antivirus scanning slows installation

**Fix:**
1. Add code signing to executables
2. Document Windows Defender exclusion process
3. Add Defender bypass option to installer

**Implementation:**
```powershell
# Add Defender exclusion
Add-MpPreference -ExclusionPath "$InstallPath" -ErrorAction SilentlyContinue
```

---

## Important Issues

### Issue 7: Orchestrator Initialization Path Issues

**Problem:**
- Orchestrator init creates `.orchestrator` in installation directory
- Windows may prevent writes to `Program Files` due to UAC
- No fallback to user home directory

**Impact:** MEDIUM - Config can't be saved
**Symptom:** "Permission denied" when saving settings

**Root Cause:**
- Program Files write protection on Windows
- Orchestrator doesn't check writability before init

**Fix:**
```powershell
# Store user config in AppData instead
$configPath = "$env:APPDATA\Symphony-IR"
New-Item -ItemType Directory -Path $configPath -Force | Out-Null
python orchestrator.py init --project $configPath --force
```

---

### Issue 8: Missing Dependency: setuptools

**Problem:**
- PyYAML 6.0+ requires setuptools during installation
- Fresh Python 3.9 may not have setuptools
- Silent failure during pip install

**Impact:** LOW-MEDIUM - Dependency installation fails
**Symptom:** "error: Microsoft Visual C++ 14.0 or greater is required"

**Root Cause:**
- PyYAML needs to build from source on some systems
- Missing build tools (MSVC) or setuptools

**Fix:**
```
# Add to requirements files
setuptools>=65.0.0
wheel>=0.38.0
```

---

### Issue 9: Python Path Issues in NSIS Installer

**Problem:**
- NSIS installer doesn't verify Python location
- Target paths in shortcuts may be wrong if Python not in PATH
- NSIS EnVar plugin may fail on x64 systems

**Impact:** LOW-MEDIUM - Shortcuts don't work
**Symptom:** Clicking shortcut does nothing or opens command window briefly

**Root Cause:**
- NSIS assumes python.exe is in PATH
- EnVar plugin x64 compatibility issues
- No fallback to registry Python locations

**Fix:**
```nsis
; Detect Python from registry
ReadRegStr $0 HKLM "Software\Python\PythonCore\3.11\InstallPath" ""
StrCmp $0 "" done
StrCpy $PythonPath "$0python.exe"
```

---

### Issue 10: Long File Path Handling in GUI

**Problem:**
- GUI file dialogs may crash with very long paths
- PyQt6 on x64 has issues with paths > 240 characters
- Session history paths can exceed limits

**Impact:** LOW - Specific edge case
**Symptom:** GUI crashes when saving files in deep directories

**Root Cause:**
- PyQt6 path handling on Windows
- Session storage in user's home can create deep paths

**Fix:**
- Limit session storage path depth
- Use short paths in GUI

---

## Minor Issues

### Issue 11: Missing Python Version Check

**Current:** Only checks if Python exists, not version
**Fix:** Verify Python 3.9+
```powershell
$pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
[version]$version = $pythonVersion
if ($version -lt [version]"3.9") {
    Write-Host "❌ Python 3.9+ required (found $pythonVersion)"
    exit 1
}
```

---

### Issue 12: No Uninstall Cleanup

**Current:** Uninstaller doesn't remove user data
**Fix:** Add option to remove configuration and cache
```powershell
# In uninstall
Remove-Item "$env:APPDATA\Symphony-IR" -Recurse -Force -ErrorAction SilentlyContinue
```

---

### Issue 13: Missing Telemetry/Crash Reporting Opt-in

**Current:** No telemetry consent
**Fix:** Add privacy-first telemetry (opt-in only)

---

### Issue 14: Documentation Not Comprehensive for Errors

**Current:** WINDOWS-SETUP.md doesn't cover x64-specific issues
**Fix:** Add section for Windows 11 x64 troubleshooting

---

## Recommended Priority Fixes

### Phase 1: CRITICAL (Do First) - Fixes Issues 1-3
```
1. Update PyQt6/keyring versions
2. Add long path support
3. Add proper admin elevation
```

### Phase 2: IMPORTANT (Do Next) - Fixes Issues 4-6
```
4. Add Visual C++ check
5. Fix batch file encoding
6. Add Defender bypass
```

### Phase 3: POLISH (Nice to Have) - Fixes 7-14
```
7-14. Improve paths, add version checks, cleanup
```

---

## Implementation Checklist

### Modified Files

- [ ] `gui/requirements-desktop.txt` - Update versions
- [ ] `windows/install.ps1` - Add checks and fixes
- [ ] `windows/launcher.bat` - Fix encoding
- [ ] `run-gui.bat` - Fix encoding
- [ ] `docs/WINDOWS-SETUP.md` - Add troubleshooting
- [ ] `windows/installer.nsi` - Add Python detection

### New Files

- [ ] `windows/check-compatibility.ps1` - Pre-installation checker
- [ ] `windows/fix-vcredist.ps1` - Visual C++ installer
- [ ] `docs/WINDOWS-11-X64-ISSUES.md` - This file

---

## Testing Checklist for Windows 11 x64

```
Installation:
[ ] Fresh Windows 11 x64 VM
[ ] Python 3.9 + 3.11 (test both)
[ ] Administrator mode required
[ ] Non-administrator account fallback
[ ] Antivirus enabled (Windows Defender)
[ ] Long path support disabled initially
[ ] Program Files installation
[ ] Alternate drive installation (D:, E:, etc.)

Runtime:
[ ] Application starts without errors
[ ] Settings can be saved
[ ] Session history accessible
[ ] File dialogs work correctly
[ ] Uninstall removes all files
[ ] Reinstall works without conflicts

Edge Cases:
[ ] Path length > 260 characters
[ ] Special characters in username
[ ] Multiple users on same system
[ ] Upgrade from previous version
```

---

## Quick Fix Commands

For users experiencing issues, provide:

```powershell
# 1. Enable long paths (Windows 11)
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f

# 2. Install Visual C++ Redistributables
# Download from Microsoft: https://support.microsoft.com/en-us/help/2977003

# 3. Reinstall GUI dependencies
pip uninstall PyQt6 PyQt6-Charts keyring -y
pip install -r gui\requirements-desktop.txt --force-reinstall --no-cache-dir

# 4. Add antivirus exception
Add-MpPreference -ExclusionPath "C:\Program Files\Symphony-IR" -ErrorAction SilentlyContinue

# 5. Check Python environment
python --version
python -m pip --version
python -c "import PyQt6; print('PyQt6 OK')"
```

---

## References

- [Windows 11 Path Limits](https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation)
- [PyQt6 Windows Issues](https://bugreports.qt.io/)
- [Python on Windows](https://docs.python.org/3/using/windows.html)
- [NSIS Installer](https://nsis.sourceforge.io/Docs)
- [Visual C++ Redistributables](https://support.microsoft.com/en-us/help/2977003)

---

**Status:** ANALYSIS COMPLETE - Ready for development team implementation

