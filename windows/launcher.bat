@echo off
REM Symphony-IR Windows Launcher
REM This script starts the desktop GUI application

setlocal enabledelayedexpansion

REM Get the installation directory (parent of this script)
for %%I in ("%~dp0.") do set "INSTALL_DIR=%%~fI"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

REM Set environment variables
set PYTHONPATH=%INSTALL_DIR%
set SYMPHONY_HOME=%INSTALL_DIR%

REM Start the desktop application
echo Starting Symphony-IR Desktop Application...
python "%INSTALL_DIR%\gui\main.py"

if errorlevel 1 (
    echo.
    echo Error starting application. Please check that all dependencies are installed.
    echo.
    echo Run: pip install -r gui\requirements-desktop.txt
    pause
)
