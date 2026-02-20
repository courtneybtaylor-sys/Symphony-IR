# Check-WindowsCompatibility.ps1
# Pre-installation compatibility checker for Symphony-IR on Windows 11 x64

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║          Symphony-IR Windows 11 x64 Compatibility         ║"
Write-Host "║                    Pre-Installation Check                  ║"
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$issues = @()
$warnings = @()

# ═════════════════════════════════════════════════════════════════════════════
# 1. Check Windows Version
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "Checking Windows version..." -ForegroundColor Yellow
$winVersion = [System.Environment]::OSVersion.Version
$osInfo = Get-WmiObject Win32_OperatingSystem
$is64Bit = $osInfo.OSArchitecture -eq "64-bit"

if ($is64Bit) {
    Write-Host "✅ Windows 64-bit: $($osInfo.Caption)" -ForegroundColor Green
} else {
    Write-Host "❌ Windows 32-bit detected" -ForegroundColor Red
    $issues += "32-bit Windows detected - Python 3.11+ requires 64-bit"
}

if ($winVersion.Major -ge 10) {
    Write-Host "✅ Windows 10/11 detected" -ForegroundColor Green
} else {
    Write-Host "⚠️  Windows 7/8 detected - Limited support" -ForegroundColor Yellow
    $warnings += "Windows 7/8 has limited support - Windows 10+ recommended"
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# 2. Check Python Installation
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source

if (-not $pythonPath) {
    Write-Host "❌ Python not found in PATH" -ForegroundColor Red
    $issues += "Python 3.9+ not installed or not in PATH"
} else {
    Write-Host "✅ Python found: $pythonPath" -ForegroundColor Green
    
    # Check version
    $versionOutput = python --version 2>&1
    Write-Host "   Version: $versionOutput" -ForegroundColor Gray
    
    $versionMatch = $versionOutput -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        [int]$major = $matches[1]
        [int]$minor = $matches[2]
        
        if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 9)) {
            Write-Host "✅ Python version OK" -ForegroundColor Green
        } else {
            Write-Host "❌ Python 3.9+ required" -ForegroundColor Red
            $issues += "Python $major.$minor is too old - upgrade to 3.9+"
        }
    }
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# 3. Check Visual C++ Redistributables
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "Checking Visual C++ Redistributables..." -ForegroundColor Yellow
$vcRedistKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
$vcVersions = Get-ItemProperty $vcRedistKey -ErrorAction SilentlyContinue | Where-Object {$_.DisplayName -like "*Visual C++*"}

if ($vcVersions) {
    Write-Host "✅ Visual C++ Redistributables found:" -ForegroundColor Green
    foreach ($vc in $vcVersions) {
        Write-Host "   - $($vc.DisplayName)" -ForegroundColor Gray
    }
    
    $vc2015_2022 = $vcVersions | Where-Object {$_.DisplayName -like "*2015-2022*"}
    if (-not $vc2015_2022) {
        Write-Host "⚠️  Visual C++ 2015-2022 not found (may cause issues)" -ForegroundColor Yellow
        $warnings += "Install Visual C++ 2015-2022 from: https://support.microsoft.com/en-us/help/2977003"
    }
} else {
    Write-Host "⚠️  Visual C++ Redistributables may be missing" -ForegroundColor Yellow
    $warnings += "Install Visual C++ 2015-2022 from: https://support.microsoft.com/en-us/help/2977003"
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# 4. Check Long Path Support
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "Checking long path support..." -ForegroundColor Yellow
$longPathKey = "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem"
$longPathValue = (Get-ItemProperty $longPathKey -Name LongPathsEnabled -ErrorAction SilentlyContinue).LongPathsEnabled

if ($longPathValue -eq 1) {
    Write-Host "✅ Long path support enabled" -ForegroundColor Green
} else {
    Write-Host "⚠️  Long path support not enabled" -ForegroundColor Yellow
    $warnings += "Long path support is disabled - may cause issues with deep directories"
    Write-Host "   To enable: reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f" -ForegroundColor Gray
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# 5. Check Administrator Rights
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "Checking administrator rights..." -ForegroundColor Yellow
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if ($isAdmin) {
    Write-Host "✅ Running as Administrator" -ForegroundColor Green
} else {
    Write-Host "⚠️  NOT running as Administrator" -ForegroundColor Yellow
    $warnings += "Installer should be run as Administrator for best results"
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# 6. Check Disk Space
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "Checking disk space..." -ForegroundColor Yellow
$programFilesDrive = $env:ProgramFiles[0]
$diskInfo = Get-PSDrive -Name $programFilesDrive[0] -ErrorAction SilentlyContinue

if ($diskInfo) {
    $freeGB = [math]::Round($diskInfo.Free / 1GB, 2)
    Write-Host "✅ Free space on $($programFilesDrive): ${freeGB} GB" -ForegroundColor Green
    
    if ($freeGB -lt 2) {
        Write-Host "⚠️  Less than 2GB free space" -ForegroundColor Yellow
        $warnings += "Less than 2GB free space - may cause installation issues"
    }
} else {
    Write-Host "⚠️  Could not determine disk space" -ForegroundColor Yellow
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# 7. Check Antivirus/Windows Defender
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "Checking antivirus status..." -ForegroundColor Yellow
try {
    $defender = Get-MpComputerStatus -ErrorAction SilentlyContinue
    if ($defender) {
        Write-Host "✅ Windows Defender detected" -ForegroundColor Green
        if ($defender.AntivirusEnabled) {
            Write-Host "   Real-time protection: ENABLED" -ForegroundColor Gray
            $warnings += "Windows Defender may slow installation - consider temporary exclusion"
        }
    } else {
        Write-Host "ℹ️  Windows Defender not found (third-party antivirus in use)" -ForegroundColor Gray
    }
} catch {
    Write-Host "ℹ️  Could not check antivirus status" -ForegroundColor Gray
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# 8. Check Pip
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = python -m pip --version 2>&1
    Write-Host "✅ pip available: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not available" -ForegroundColor Red
    $issues += "pip is not available - required for dependency installation"
}
Write-Host ""

# ═════════════════════════════════════════════════════════════════════════════
# Summary
# ═════════════════════════════════════════════════════════════════════════════
Write-Host "╔════════════════════════════════════════════════════════════╗"

if ($issues.Count -eq 0) {
    Write-Host "║                  COMPATIBILITY: PASSED                   ║" -ForegroundColor Green
} else {
    Write-Host "║              COMPATIBILITY: ISSUES FOUND                 ║" -ForegroundColor Red
}

Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

if ($issues.Count -gt 0) {
    Write-Host "CRITICAL ISSUES (must fix before installing):" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  ❌ $issue" -ForegroundColor Red
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "WARNINGS (installation may work but with issues):" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  ⚠️  $warning" -ForegroundColor Yellow
    }
    Write-Host ""
}

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "✅ System is ready for Symphony-IR installation!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process" -ForegroundColor Gray
    Write-Host "  2. Run: .\windows\install.ps1" -ForegroundColor Gray
    Write-Host ""
} elseif ($issues.Count -eq 0) {
    Write-Host "⚠️  System can proceed but resolve warnings for best results" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can still run the installer:" -ForegroundColor Cyan
    Write-Host "  1. Run: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process" -ForegroundColor Gray
    Write-Host "  2. Run: .\windows\install.ps1" -ForegroundColor Gray
    Write-Host ""
}

if ($issues.Count -gt 0) {
    Write-Host "❌ Installation cannot proceed - please fix critical issues first" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host "Press any key to exit..." -ForegroundColor Gray
[Console]::ReadKey() | Out-Null
