# Windows 11 x64 Installation - Quick Start

## TL;DR - Install in 3 Steps

### Step 1: Check System
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\windows\check-compatibility.ps1
```

### Step 2: Fix Any Issues (if found)
See output from compatibility checker - usually just need Visual C++ from Microsoft.

### Step 3: Install
```powershell
.\windows\install.ps1
```

Done! Click "Symphony-IR" in Start Menu to launch.

---

## What's Fixed

✅ **PyQt6 x64 compatibility** - Updated to latest version  
✅ **Windows long path support** - Auto-enabled during install  
✅ **Admin rights enforcement** - Auto-elevates if needed  
✅ **Visual C++ verification** - Warns before install  
✅ **Batch file encoding** - Fixed UTF-8 BOM issues  
✅ **Antivirus conflicts** - Auto-adds Defender exclusion  
✅ **Config permissions** - Uses AppData instead of Program Files  
✅ **Error messages** - Clear, actionable guidance  

---

## Troubleshooting

### Python not found?
- Install from: https://www.python.org/
- **Unchecked:** "Add Python to PATH"? Check it and reinstall.

### "Visual C++ 2015-2022 not found"?
- Download: https://support.microsoft.com/en-us/help/2977003
- Install the x64 version
- Run installer again

### "The filename or extension is too long"?
```powershell
# Enable Windows long paths
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

### Installation hangs?
- Close antivirus temporarily
- Or let it finish (can take 5-10 min with AV enabled)

### Still failing?
- Run: `python -c "import PyQt6; print('OK')"`
- If error, reinstall: `pip install --force-reinstall PyQt6==6.7.0`

---

## Files Modified

| File | What Changed | Why |
|------|-------------|-----|
| `gui/requirements-desktop.txt` | Updated PyQt6, keyring versions | x64 compatibility |
| `windows/install.ps1` | Added checks & fixes | Robust installation |
| `run-gui.bat` | Fixed encoding, errors | Windows batch compat |
| `windows/launcher.bat` | Fixed encoding, errors | Windows batch compat |

## New Files

| File | Purpose |
|------|---------|
| `windows/check-compatibility.ps1` | Pre-flight system check |
| `WINDOWS_11_X64_INSTALLER_FIXES.md` | Detailed analysis & fixes |
| `INSTALLER_FIXES_APPLIED.md` | Implementation summary |

---

## Support

For more details:
- **Technical:** See `WINDOWS_11_X64_INSTALLER_FIXES.md`
- **Setup:** See `docs/WINDOWS-SETUP.md`
- **Issues:** See `github.com/courtneybtaylor-sys/Symphony-IR/issues`

---

**Ready to install? Run: `.\windows\check-compatibility.ps1`**
