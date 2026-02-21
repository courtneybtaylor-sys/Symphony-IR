@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  Symphony-IR Unified Installer — Windows
REM ============================================================

color 3F
cls

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║                  Symphony-IR Setup                    ║
echo ║        Deterministic Multi-Agent Orchestration        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Step 1: Detect Windows version
echo 1️⃣  Detecting Windows version...

for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo ✅ Windows %VERSION% detected
echo.

REM Step 2: Check Python installation
echo 2️⃣  Checking Python 3...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    color CF
    cls
    echo.
    echo ❌ Python 3 not found!
    echo.
    echo Please install Python 3.9 or later:
    echo.
    echo   Option 1: Download from https://www.python.org
    echo   • Check "Add Python to PATH" during installation
    echo.
    echo   Option 2: Use Windows Store
    echo   • Search for "Python" in Microsoft Store
    echo.
    echo After installing, close this window and run install.bat again.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%
echo.

REM Step 3: Check Python version >= 3.9
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 (
    color CF
    echo ❌ Python 3.9+ required (you have %PYTHON_VERSION%)
    pause
    exit /b 1
)

if %MAJOR% EQU 3 if %MINOR% LSS 9 (
    color CF
    echo ❌ Python 3.9+ required (you have %PYTHON_VERSION%)
    pause
    exit /b 1
)

REM Step 4: Check virtualenv recommendation
echo 3️⃣  Checking virtual environment...

if "!VIRTUAL_ENV!"=="" (
    echo ⚠️  Not running in a virtual environment
    set /p CREATE_VENV="   Create one now? (recommended) [y/N]: "

    if /i "!CREATE_VENV!"=="y" (
        echo.
        echo Creating virtualenv...
        python -m venv venv

        if exist "venv\Scripts\activate.bat" (
            call venv\Scripts\activate.bat
            echo ✅ Virtual environment created and activated
        ) else (
            echo ❌ Failed to create virtualenv
            pause
            exit /b 1
        )
    ) else (
        echo ⚠️  Proceeding without virtualenv (not recommended)
    )
) else (
    echo ✅ Running in virtualenv: !VIRTUAL_ENV!
)

echo.

REM Step 5: Ask about AI provider
echo 4️⃣  Choosing AI Provider...
echo.
echo Which AI provider would you like to use?
echo.
echo   1) Claude (Cloud API)
echo      * Best for production workloads
echo      * Requires API key (get free at console.anthropic.com)
echo      * Pay per token (~$0.0008 per 1K tokens)
echo.
echo   2) Ollama (Local, Free)
echo      * Best for privacy and offline work
echo      * Runs on your machine
echo      * Completely free, no API key needed
echo      * Requires ~4-45GB disk space for models
echo.
echo   3) Both
echo      * Use Claude for production, Ollama for testing
echo      * Maximum flexibility
echo.
echo   4) Skip for now
echo      * Install both, configure later
echo.

set /p PROVIDER_CHOICE="Choose (1-4): "

if "%PROVIDER_CHOICE%"=="1" (
    set PROVIDERS=anthropic
    set PROVIDER_DISPLAY=Claude
) else if "%PROVIDER_CHOICE%"=="2" (
    set PROVIDERS=ollama
    set PROVIDER_DISPLAY=Ollama
) else if "%PROVIDER_CHOICE%"=="3" (
    set PROVIDERS=both
    set PROVIDER_DISPLAY=Claude and Ollama
) else (
    set PROVIDERS=skip
    set PROVIDER_DISPLAY=Skip (install both libraries)
)

echo ✅ Selected: !PROVIDER_DISPLAY!
echo.

REM Step 6: Install dependencies
echo 5️⃣  Installing dependencies...
echo    (This may take 2-5 minutes)
echo.

echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel --quiet

echo Installing core packages...
python -m pip install pyyaml python-dotenv --quiet

if "!PROVIDERS!"=="anthropic" (
    echo Installing Claude SDK...
    python -m pip install "anthropic>=0.25.0" --quiet
) else if "!PROVIDERS!"=="ollama" (
    echo Installing Ollama support...
    python -m pip install requests --quiet
) else if "!PROVIDERS!"=="both" (
    echo Installing Claude and Ollama support...
    python -m pip install "anthropic>=0.25.0" requests --quiet
) else (
    echo Installing both Claude and Ollama support...
    python -m pip install "anthropic>=0.25.0" requests --quiet
)

echo Installing desktop GUI...
python -m pip install PyQt6==6.6.1 PyQt6-Charts==6.6.0 keyring==24.3.0 --quiet

if %ERRORLEVEL% EQU 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ⚠️  Some dependencies may have failed to install
    echo    Try running: python -m pip install -r requirements.txt
)

echo.

REM Step 7: Initialize orchestrator
echo 6️⃣  Initializing Orchestrator...

if exist "ai-orchestrator\orchestrator.py" (
    cd ai-orchestrator
    python orchestrator.py init --force >nul 2>&1
    cd ..
    echo ✅ Orchestrator initialized
) else (
    echo ⚠️  Orchestrator not found (expected if not in project root)
)

echo.

REM Step 8: API key configuration (if Claude selected)
if "!PROVIDERS!"=="anthropic" (
    echo 7️⃣  API Key Configuration
    set /p HAS_API_KEY="   Do you have a Claude API key? [y/N]: "

    if /i "!HAS_API_KEY!"=="y" (
        set /p API_KEY="   Paste your API key (or 'skip' to do later): "

        if not "!API_KEY!"=="skip" (
            if not "!API_KEY!"=="" (
                (
                    echo ANTHROPIC_API_KEY=!API_KEY!
                ) > .env
                echo ✅ API key saved to .env
            )
        )
    ) else (
        echo    You can add your API key later by running:
        echo    set ANTHROPIC_API_KEY=sk-ant-...
        echo    Or in the app: Settings ^> API Keys
    )
    echo.
) else if "!PROVIDERS!"=="both" (
    echo 7️⃣  API Key Configuration (Optional)
    set /p HAS_API_KEY="   Do you have a Claude API key? [y/N]: "

    if /i "!HAS_API_KEY!"=="y" (
        set /p API_KEY="   Paste your API key (or 'skip' to do later): "

        if not "!API_KEY!"=="skip" (
            if not "!API_KEY!"=="" (
                (
                    echo ANTHROPIC_API_KEY=!API_KEY!
                ) > .env
                echo ✅ API key saved to .env
            )
        )
    ) else (
        echo    You can add your API key later in the app: Settings ^> API Keys
    )
    echo.
) else if "!PROVIDERS!"=="skip" (
    echo 7️⃣  API Key Configuration (Optional)
    set /p HAS_API_KEY="   Do you have a Claude API key? [y/N]: "

    if /i "!HAS_API_KEY!"=="y" (
        set /p API_KEY="   Paste your API key (or 'skip' to do later): "

        if not "!API_KEY!"=="skip" (
            if not "!API_KEY!"=="" (
                (
                    echo ANTHROPIC_API_KEY=!API_KEY!
                ) > .env
                echo ✅ API key saved to .env
            )
        )
    )
    echo.
)

REM Step 9: Ollama check (if Ollama selected)
if "!PROVIDERS!"=="ollama" (
    echo 8️⃣  Ollama Setup

    where ollama >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Ollama is installed
        echo    Run: ollama pull llama2 (or another model)
    ) else (
        echo ⚠️  Ollama not found
        echo    Download from: https://ollama.ai
        echo    Then run: ollama pull llama2
    )
    echo.
) else if "!PROVIDERS!"=="both" (
    echo 8️⃣  Ollama Setup (Optional)

    where ollama >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Ollama is installed
        echo    Run: ollama pull llama2 (or another model)
    ) else (
        echo ⚠️  Ollama not installed yet
        echo    Download from: https://ollama.ai
        echo    Then run: ollama pull llama2
    )
    echo.
) else if "!PROVIDERS!"=="skip" (
    echo 8️⃣  Ollama Setup (Optional)

    where ollama >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Ollama is installed
        echo    Run: ollama pull llama2 (or another model)
    ) else (
        echo ⚠️  Ollama not installed yet
        echo    Download from: https://ollama.ai
    )
    echo.
)

REM Step 10: Launch app
echo 9️⃣  Ready to launch!
echo.

set /p LAUNCH_NOW="   Would you like to launch Symphony-IR now? [Y/n]: "

if "!LAUNCH_NOW!"=="" set LAUNCH_NOW=y

if /i "!LAUNCH_NOW!"=="y" (
    if exist "gui\main.py" (
        echo.
        echo 🚀 Launching Symphony-IR...
        start "" python gui\main.py
        timeout /t 3 /nobreak
    ) else (
        echo ⚠️  gui\main.py not found
        echo    Run this from the project root directory
    )
) else (
    echo    To launch later, run:
    echo    python gui\main.py
)

echo.
cls
color 2F
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║              Setup Complete! ✅                         ║
echo "╚════════════════════════════════════════════════════════╝"
echo.
echo 📍 What's next?
echo    1. Open Symphony-IR
echo    2. Try the sample tasks in Orchestrator tab
echo    3. Explore Symphony Flow workflows
echo.
echo 📚 Documentation:
echo    * README.md — Overview
echo    * docs\ARCHITECTURE.md — How it works
echo    * docs\FLOW.md — Guided workflows
echo.
echo 💬 Need help?
echo    * GitHub Issues: https://github.com/courtneybtaylor-sys/Symphony-IR/issues
echo    * GitHub Discussions: https://github.com/courtneybtaylor-sys/Symphony-IR/discussions
echo.

pause
