# Symphony-IR Windows Installer
# This script installs Symphony-IR as a Windows desktop application
# Run as Administrator for best results

param(
    [string]$InstallPath = "$env:ProgramFiles\Symphony-IR"
)

# Requires -RunAsAdministrator

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║                  Symphony-IR Installer                     ║"
Write-Host "║         Deterministic Multi-Agent Orchestration Engine     ║"
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  This installer should be run as Administrator for best results" -ForegroundColor Yellow
    Write-Host "   Right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    Write-Host ""
}

# Step 1: Check Python
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
Write-Host ""

# Step 2: Create installation directory
Write-Host "2️⃣  Creating installation directory..." -ForegroundColor Cyan
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}
Write-Host "✅ Installation directory: $InstallPath" -ForegroundColor Green
Write-Host ""

# Step 3: Download or copy source
Write-Host "3️⃣  Setting up source files..." -ForegroundColor Cyan
$sourceDir = Split-Path -Parent (Get-Item $PSCommandPath).Directory
Write-Host "   Source: $sourceDir" -ForegroundColor Gray

# Copy files
Write-Host "   Copying files..." -ForegroundColor Gray
Copy-Item "$sourceDir\ai-orchestrator" -Destination "$InstallPath\" -Recurse -Force -ErrorAction Continue
Copy-Item "$sourceDir\gui" -Destination "$InstallPath\" -Recurse -Force -ErrorAction Continue
Copy-Item "$sourceDir\docs" -Destination "$InstallPath\" -Recurse -Force -ErrorAction Continue
Copy-Item "$sourceDir\README.md" -Destination "$InstallPath\" -Force -ErrorAction Continue

Write-Host "✅ Files copied" -ForegroundColor Green
Write-Host ""

# Step 4: Install Python dependencies
Write-Host "4️⃣  Installing Python dependencies..." -ForegroundColor Cyan
Write-Host "   This may take a few minutes..." -ForegroundColor Gray
Write-Host ""

python -m pip install --upgrade pip -q
python -m pip install -r "$InstallPath\gui\requirements-desktop.txt" -q

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some dependencies may have failed to install" -ForegroundColor Yellow
    Write-Host "   Try running: pip install -r gui\requirements-desktop.txt" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Initialize orchestrator
Write-Host "5️⃣  Initializing Symphony-IR..." -ForegroundColor Cyan
Push-Location "$InstallPath\ai-orchestrator"
python orchestrator.py init --project "$InstallPath" --force | Out-Null
Pop-Location
Write-Host "✅ Initialized .orchestrator directory" -ForegroundColor Green
Write-Host ""

# Step 6: Create shortcuts
Write-Host "6️⃣  Creating Windows shortcuts..." -ForegroundColor Cyan

$ShortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Symphony-IR.lnk"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "python.exe"
$Shortcut.Arguments = "`"$InstallPath\gui\main.py`""
$Shortcut.WorkingDirectory = $InstallPath
$Shortcut.Description = "Symphony-IR - AI Orchestrator"
$Shortcut.Save()

Write-Host "✅ Created Start Menu shortcut" -ForegroundColor Green

# Desktop shortcut
$DesktopPath = "$env:USERPROFILE\Desktop\Symphony-IR.lnk"
$DesktopShortcut = $WshShell.CreateShortcut($DesktopPath)
$DesktopShortcut.TargetPath = "python.exe"
$DesktopShortcut.Arguments = "`"$InstallPath\gui\main.py`""
$DesktopShortcut.WorkingDirectory = $InstallPath
$DesktopShortcut.Description = "Symphony-IR - AI Orchestrator"
$DesktopShortcut.Save()

Write-Host "✅ Created Desktop shortcut" -ForegroundColor Green
Write-Host ""

# Step 7: Add to PATH
Write-Host "7️⃣  Adding to Windows PATH..." -ForegroundColor Cyan
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
Write-Host ""

# Step 8: Optional - Get API key
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
        Write-Host "✅ API key saved" -ForegroundColor Green
    }
} else {
    Write-Host "ℹ️  You can add an API key later through the Settings tab" -ForegroundColor Gray
}
Write-Host ""

# Installation complete
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              Installation Complete! ✅                     ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Installation Path: $InstallPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 To start Symphony-IR:" -ForegroundColor Cyan
Write-Host "   • Click 'Symphony-IR' in Start Menu" -ForegroundColor Gray
Write-Host "   • Or double-click 'Symphony-IR' on Desktop" -ForegroundColor Gray
Write-Host "   • Or run: python $InstallPath\gui\main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   • README: $InstallPath\README.md" -ForegroundColor Gray
Write-Host "   • Flows: $InstallPath\docs\FLOW.md" -ForegroundColor Gray
Write-Host "   • Ollama: $InstallPath\docs\OLLAMA.md" -ForegroundColor Gray
Write-Host ""
Write-Host "ℹ️  First time setup:" -ForegroundColor Cyan
Write-Host "   1. Open Symphony-IR" -ForegroundColor Gray
Write-Host "   2. Go to Settings tab" -ForegroundColor Gray
Write-Host "   3. Choose Claude or Ollama" -ForegroundColor Gray
Write-Host "   4. Start creating AI workflows!" -ForegroundColor Gray
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Gray
[Console]::ReadKey() | Out-Null
