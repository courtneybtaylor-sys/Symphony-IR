# Symphony-IR Windows Installer
# This script installs Symphony-IR as a Windows desktop application
# Run as Administrator for best results

param(
    [string]$InstallPath = "$env:ProgramFiles\Symphony-IR"
)

# Requires -RunAsAdministrator

# ═════════════════════════════════════════════════════════════════════════════
# ADMIN ELEVATION CHECK - Request admin rights if not running as admin
# ═════════════════════════════════════════════════════════════════════════════
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "Administrator privileges required. Restarting with elevated rights..." -ForegroundColor Yellow
    $arguments = "& '$PSCommandPath' -InstallPath '$InstallPath'"
    Start-Process powershell -ArgumentList $arguments -Verb RunAs -Wait
    exit
}

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║                  Symphony-IR Installer                     ║"
Write-Host "║         Deterministic Multi-Agent Orchestration Engine     ║"
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 0: Enable Long Path Support (Windows 11 x64 fix)
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "0️⃣  Enabling Windows long path support..." -ForegroundColor Cyan
try {
    reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f | Out-Null
    Write-Host "✅ Long path support enabled" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not enable long paths (non-critical)" -ForegroundColor Yellow
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 0.5: Check Visual C++ Redistributables (Windows 11 x64 requirement)
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "0.5️⃣  Checking Visual C++ Redistributables..." -ForegroundColor Cyan
$vcRedistKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
$vcInstalled = Get-ItemProperty $vcRedistKey -ErrorAction SilentlyContinue | Where-Object {$_.DisplayName -like "*Visual C++*" -and $_.DisplayName -like "*2015-2022*"}

if (-not $vcInstalled) {
    Write-Host "⚠️  Visual C++ 2015-2022 Redistributables may be missing" -ForegroundColor Yellow
    Write-Host "   Some PyQt6 components require this" -ForegroundColor Yellow
    Write-Host "   Download from: https://support.microsoft.com/en-us/help/2977003" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "✅ Visual C++ Redistributables found" -ForegroundColor Green
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 1: Check Python Installation
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "1️⃣  Checking Python installation..." -ForegroundColor Cyan
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.9+ from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✅ $pythonVersion found at $pythonPath" -ForegroundColor Green

# Verify Python is 3.9 or higher
$versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
if ($versionMatch) {
    [int]$major = $matches[1]
    [int]$minor = $matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 9)) {
        Write-Host "❌ Python 3.9+ required (found $major.$minor)" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 1.5: Add Antivirus Exclusion (Windows Defender)
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "1.5️⃣  Adding antivirus exclusion..." -ForegroundColor Cyan
try {
    Add-MpPreference -ExclusionPath $InstallPath -ErrorAction SilentlyContinue | Out-Null
    Write-Host "✅ Antivirus exclusion added" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not add antivirus exclusion (non-critical)" -ForegroundColor Yellow
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 2: Create Installation Directory
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "2️⃣  Creating installation directory..." -ForegroundColor Cyan
try {
    if (-not (Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    }
    Write-Host "✅ Installation directory: $InstallPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Could not create installation directory" -ForegroundColor Red
    Write-Host "   Try with a shorter path or different drive" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 3: Setup Source Files
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "3️⃣  Setting up source files..." -ForegroundColor Cyan
$sourceDir = Split-Path -Parent (Get-Item $PSCommandPath).Directory
Write-Host "   Source: $sourceDir" -ForegroundColor Gray

try {
    Write-Host "   Copying files..." -ForegroundColor Gray
    Copy-Item "$sourceDir\ai-orchestrator" -Destination "$InstallPath\" -Recurse -Force -ErrorAction Continue
    Copy-Item "$sourceDir\gui" -Destination "$InstallPath\" -Recurse -Force -ErrorAction Continue
    Copy-Item "$sourceDir\docs" -Destination "$InstallPath\" -Recurse -Force -ErrorAction Continue
    Copy-Item "$sourceDir\README.md" -Destination "$InstallPath\" -Force -ErrorAction Continue
    Write-Host "✅ Files copied" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Some files could not be copied" -ForegroundColor Yellow
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 4: Upgrade pip and Install Dependencies
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "4️⃣  Installing Python dependencies..." -ForegroundColor Cyan
Write-Host "   This may take 3-5 minutes on first install..." -ForegroundColor Gray
Write-Host ""

try {
    # Upgrade pip first
    Write-Host "   Upgrading pip..." -ForegroundColor Gray
    python -m pip install --upgrade pip --quiet
    
    # Install dependencies with better error handling for x64
    Write-Host "   Installing GUI dependencies..." -ForegroundColor Gray
    $requirementsFile = "$InstallPath\gui\requirements-desktop.txt"
    
    if (Test-Path $requirementsFile) {
        python -m pip install -r $requirementsFile --quiet --no-warn-script-location
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ All dependencies installed successfully" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Some dependencies encountered warnings (may still work)" -ForegroundColor Yellow
            Write-Host "   If issues occur, try: pip install -r gui\requirements-desktop.txt --force-reinstall" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠️  Requirements file not found at: $requirementsFile" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Error installing dependencies: $_" -ForegroundColor Yellow
    Write-Host "   You can try manual installation later:" -ForegroundColor Yellow
    Write-Host "   pip install -r gui\requirements-desktop.txt" -ForegroundColor Yellow
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 5: Initialize Orchestrator in User AppData
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "5️⃣  Initializing Symphony-IR configuration..." -ForegroundColor Cyan

# Use AppData for user config (better compatibility with Program Files write protection)
$configPath = "$env:APPDATA\Symphony-IR"
try {
    New-Item -ItemType Directory -Path $configPath -Force | Out-Null
    
    Push-Location "$InstallPath\ai-orchestrator"
    python orchestrator.py init --project $configPath --force 2>&1 | Out-Null
    Pop-Location
    
    Write-Host "✅ Configuration initialized at: $configPath" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not initialize orchestrator configuration" -ForegroundColor Yellow
    Write-Host "   You can run manually: python orchestrator.py init --project $configPath" -ForegroundColor Gray
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 6: Create Windows Shortcuts
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "6️⃣  Creating Windows shortcuts..." -ForegroundColor Cyan

try {
    $WshShell = New-Object -ComObject WScript.Shell
    
    # Start Menu shortcut
    $ShortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Symphony-IR.lnk"
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = "python.exe"
    $Shortcut.Arguments = "-m gui.main"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "Symphony-IR - AI Orchestrator"
    $Shortcut.IconLocation = "$InstallPath\gui\icon.png"
    $Shortcut.Save()
    Write-Host "✅ Created Start Menu shortcut" -ForegroundColor Green
    
    # Desktop shortcut
    $DesktopPath = "$env:USERPROFILE\Desktop\Symphony-IR.lnk"
    $DesktopShortcut = $WshShell.CreateShortcut($DesktopPath)
    $DesktopShortcut.TargetPath = "python.exe"
    $DesktopShortcut.Arguments = "-m gui.main"
    $DesktopShortcut.WorkingDirectory = $InstallPath
    $DesktopShortcut.Description = "Symphony-IR - AI Orchestrator"
    $DesktopShortcut.IconLocation = "$InstallPath\gui\icon.png"
    $DesktopShortcut.Save()
    Write-Host "✅ Created Desktop shortcut" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not create shortcuts: $_" -ForegroundColor Yellow
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 7: Add to PATH (Optional)
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "7️⃣  Adding to Windows PATH..." -ForegroundColor Cyan
try {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if (-not $currentPath.Contains($InstallPath)) {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$currentPath;$InstallPath",
            "Machine"
        )
        Write-Host "✅ Added to PATH" -ForegroundColor Green
    } else {
        Write-Host "✅ Already in PATH" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Could not modify PATH (non-critical)" -ForegroundColor Yellow
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 8: API Key Configuration (Optional)
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "8️⃣  API Key Configuration (Optional)" -ForegroundColor Cyan
$getKey = Read-Host "   Do you want to add an Anthropic API key now? (y/n)"
if ($getKey -eq "y" -or $getKey -eq "Y") {
    $apiKey = Read-Host "   Enter your API key (or leave blank for Ollama)"
    if ($apiKey) {
        [Environment]::SetEnvironmentVariable(
            "ANTHROPIC_API_KEY",
            $apiKey,
            "User"
        )
        Write-Host "✅ API key saved to user environment variables" -ForegroundColor Green
    }
} else {
    Write-Host "ℹ️  You can add an API key later through the Settings tab" -ForegroundColor Gray
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# Installation Summary
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              Installation Complete! SUCCESS                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Installation Directory: $InstallPath" -ForegroundColor Cyan
Write-Host "📍 Configuration Directory: $configPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 To start Symphony-IR:" -ForegroundColor Cyan
Write-Host "   • Click 'Symphony-IR' in Start Menu" -ForegroundColor Gray
Write-Host "   • Or double-click 'Symphony-IR' on Desktop" -ForegroundColor Gray
Write-Host "   • Or run: python -m gui.main" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   • README: $InstallPath\README.md" -ForegroundColor Gray
Write-Host "   • Flows: $InstallPath\docs\FLOW.md" -ForegroundColor Gray
Write-Host "   • Ollama: $InstallPath\docs\OLLAMA.md" -ForegroundColor Gray
Write-Host "   • Windows Setup: $InstallPath\docs\WINDOWS-SETUP.md" -ForegroundColor Gray
Write-Host ""
Write-Host "ℹ️  First time setup:" -ForegroundColor Cyan
Write-Host "   1. Open Symphony-IR" -ForegroundColor Gray
Write-Host "   2. Go to Settings tab" -ForegroundColor Gray
Write-Host "   3. Choose Claude (cloud) or Ollama (local free)" -ForegroundColor Gray
Write-Host "   4. Add API key if using Claude" -ForegroundColor Gray
Write-Host "   5. Start creating AI workflows!" -ForegroundColor Gray
Write-Host ""
Write-Host "❓ Troubleshooting:" -ForegroundColor Cyan
Write-Host "   If you encounter issues on Windows 11 x64:" -ForegroundColor Gray
Write-Host "   • Check: docs/WINDOWS-11-X64-ISSUES.md" -ForegroundColor Gray
Write-Host "   • Run: pip install --upgrade -r gui\requirements-desktop.txt" -ForegroundColor Gray
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Gray
[Console]::ReadKey() | Out-Null
