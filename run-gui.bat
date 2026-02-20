@echo off
REM Symphony-IR GUI Launcher for Windows
REM Double-click this file to start the application

setlocal enabledelayedexpansion

echo.
echo ================================================
echo           Symphony-IR Desktop Application
echo   Deterministic Multi-Agent Orchestration Engine
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.9+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Get current directory
set "SCRIPT_DIR=%~dp0"

REM Check if running from correct directory
if not exist "%SCRIPT_DIR%gui\main.py" (
    echo ERROR: gui/main.py not found!
    echo.
    echo Please run this script from the Symphony-IR root directory.
    echo.
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
python -m pip show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo Installing required packages (this may take a minute)...
    python -m pip install -r gui\requirements-desktop.txt -q
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo.
        echo Please run: pip install -r gui\requirements-desktop.txt
        echo.
        pause
        exit /b 1
    )
)

echo Dependencies OK
echo.
echo Starting Symphony-IR...
echo.

REM Set environment variables
set PYTHONPATH=%SCRIPT_DIR%
set SYMPHONY_HOME=%SCRIPT_DIR%

REM Start the application
python "%SCRIPT_DIR%gui\main.py"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application
    echo.
    pause
    exit /b 1
)
