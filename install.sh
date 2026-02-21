#!/bin/bash
set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# Symphony-IR Unified Installer — macOS / Linux
# ============================================================

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║                  Symphony-IR Setup                    ║"
echo "║        Deterministic Multi-Agent Orchestration        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Step 1: Detect OS
echo -e "${BLUE}1️⃣  Detecting OS...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    OS_DISPLAY="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    OS_DISPLAY="Linux"
else
    echo -e "${RED}❌ Unsupported OS: $OSTYPE${NC}"
    echo "   Symphony-IR requires macOS or Linux"
    exit 1
fi

echo -e "${GREEN}✅ Detected: $OS_DISPLAY${NC}"
echo ""

# Step 2: Check Python installation
echo -e "${BLUE}2️⃣  Checking Python 3...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found!${NC}"
    echo ""
    echo "Please install Python 3.9 or later:"
    if [[ "$OS" == "macos" ]]; then
        echo "   • Option 1: brew install python3"
        echo "   • Option 2: Download from https://www.python.org"
    else
        echo "   • Option 1: sudo apt install python3-dev python3-venv"
        echo "   • Option 2: Download from https://www.python.org"
    fi
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Found Python $PYTHON_VERSION${NC}"

# Check Python version >= 3.9
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 9 ]]; then
    echo -e "${RED}❌ Python 3.9+ required (you have $PYTHON_VERSION)${NC}"
    exit 1
fi

echo ""

# Step 3: Check virtualenv recommendation
echo -e "${BLUE}3️⃣  Checking virtual environment...${NC}"

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Not running in a virtual environment${NC}"
    read -p "   Create one now? (recommended) [y/N]: " create_venv

    if [[ "$create_venv" == "y" || "$create_venv" == "Y" ]]; then
        echo "   Creating virtualenv..."
        python3 -m venv venv
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment created and activated${NC}"
    else
        echo -e "${YELLOW}⚠️  Proceeding without virtualenv (not recommended)${NC}"
    fi
else
    echo -e "${GREEN}✅ Running in virtualenv: $VIRTUAL_ENV${NC}"
fi

echo ""

# Step 4: Ask about AI provider
echo -e "${BLUE}4️⃣  Choosing AI Provider...${NC}"
echo ""
echo "Which AI provider would you like to use?"
echo ""
echo "  1) Claude (Cloud API)"
echo "     • Best for production workloads"
echo "     • Requires API key (get free at console.anthropic.com)"
echo "     • Pay per token (~\$0.0008 per 1K tokens)"
echo ""
echo "  2) Ollama (Local, Free)"
echo "     • Best for privacy and offline work"
echo "     • Runs on your machine"
echo "     • Completely free, no API key needed"
echo "     • Requires ~4-45GB disk space for models"
echo ""
echo "  3) Both"
echo "     • Use Claude for production, Ollama for testing"
echo "     • Maximum flexibility"
echo ""
echo "  4) Skip for now"
echo "     • Install both, configure later"
echo ""

read -p "Choose (1-4): " provider_choice

case $provider_choice in
    1)
        PROVIDERS="anthropic"
        PROVIDER_DISPLAY="Claude"
        ;;
    2)
        PROVIDERS="ollama"
        PROVIDER_DISPLAY="Ollama"
        ;;
    3)
        PROVIDERS="both"
        PROVIDER_DISPLAY="Claude and Ollama"
        ;;
    *)
        PROVIDERS="skip"
        PROVIDER_DISPLAY="Skip (install both libraries)"
        ;;
esac

echo -e "${GREEN}✅ Selected: $PROVIDER_DISPLAY${NC}"
echo ""

# Step 5: Install dependencies
echo -e "${BLUE}5️⃣  Installing dependencies...${NC}"
echo "   (This may take 2-5 minutes)"
echo ""

# Upgrade pip (best-effort — system-managed pip may not be upgradeable)
python3 -m pip install --upgrade pip --quiet 2>/dev/null || true

# Install core dependencies
echo "   Installing core packages..."
python3 -m pip install pyyaml python-dotenv --quiet

# Install providers based on choice
case $PROVIDERS in
    anthropic)
        echo "   Installing Claude SDK..."
        python3 -m pip install 'anthropic>=0.25.0' --quiet
        ;;
    ollama)
        echo "   Installing Ollama support..."
        python3 -m pip install requests --quiet
        ;;
    both)
        echo "   Installing Claude and Ollama support..."
        python3 -m pip install 'anthropic>=0.25.0' requests --quiet
        ;;
    skip)
        echo "   Installing both Claude and Ollama support..."
        python3 -m pip install 'anthropic>=0.25.0' requests --quiet
        ;;
esac

# Install desktop GUI
echo "   Installing desktop GUI..."
python3 -m pip install PyQt6==6.6.1 PyQt6-Charts==6.6.0 keyring==24.3.0 --quiet

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Some dependencies may have failed to install${NC}"
    echo "   Try running: python3 -m pip install -r requirements.txt"
fi

echo ""

# Step 6: Initialize orchestrator
echo -e "${BLUE}6️⃣  Initializing Orchestra...${NC}"

if [ -f "ai-orchestrator/orchestrator.py" ]; then
    python3 ai-orchestrator/orchestrator.py init --project . --force 2>/dev/null || true
    echo -e "${GREEN}✅ Orchestrator initialized${NC}"
else
    echo -e "${YELLOW}⚠️  Orchestrator not found (expected if not in project root)${NC}"
fi

echo ""

# Step 7: API key configuration (if Claude selected)
if [[ "$PROVIDERS" == "anthropic" ]] || [[ "$PROVIDERS" == "both" ]] || [[ "$PROVIDERS" == "skip" ]]; then
    echo -e "${BLUE}7️⃣  API Key Configuration${NC}"
    read -p "   Do you have a Claude API key? [y/N]: " has_api_key

    if [[ "$has_api_key" == "y" || "$has_api_key" == "Y" ]]; then
        read -p "   Paste your API key (or 'skip' to do later): " api_key

        if [[ "$api_key" != "skip" && ! -z "$api_key" ]]; then
            export ANTHROPIC_API_KEY="$api_key"

            # Write to .orchestrator/.env (where orchestrator.py reads it from)
            mkdir -p .orchestrator
            env_target=".orchestrator/.env"
            if [ -f "$env_target" ]; then
                # Remove old key if present
                sed -i '/^ANTHROPIC_API_KEY=/d' "$env_target"
            fi
            echo "ANTHROPIC_API_KEY=$api_key" >> "$env_target"

            echo -e "${GREEN}✅ API key saved to $env_target${NC}"
        fi
    else
        echo "   You can add your API key later by running:"
        echo "   export ANTHROPIC_API_KEY=sk-ant-..."
        echo "   Or in the app: Settings → API Keys"
    fi
    echo ""
fi

# Step 8: Ollama check (if Ollama selected)
if [[ "$PROVIDERS" == "ollama" ]] || [[ "$PROVIDERS" == "both" ]] || [[ "$PROVIDERS" == "skip" ]]; then
    echo -e "${BLUE}8️⃣  Ollama Setup${NC}"

    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}✅ Ollama is installed${NC}"
        echo "   Run: ollama pull llama2 (or another model)"
    else
        echo -e "${YELLOW}⚠️  Ollama not found${NC}"
        echo "   Download from: https://ollama.ai"
        echo "   Then run: ollama pull llama2"
    fi
    echo ""
fi

# Step 9: Launch app
echo -e "${BLUE}9️⃣  Ready to launch!${NC}"
echo ""
read -p "   Would you like to launch Symphony-IR now? [Y/n]: " launch_now

if [[ -z "$launch_now" || "$launch_now" == "y" || "$launch_now" == "Y" ]]; then
    if [ -f "gui/main.py" ]; then
        echo -e "${GREEN}🚀 Launching Symphony-IR...${NC}"
        python3 gui/main.py &
        sleep 2
    else
        echo -e "${YELLOW}⚠️  gui/main.py not found${NC}"
        echo "   Run this from the project root directory"
    fi
else
    echo "   To launch later, run:"
    echo "   python3 gui/main.py"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗"
echo "║              Setup Complete! ✅                          ║"
echo "╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📍 What's next?"
echo "   1. Open Symphony-IR"
echo "   2. Try the sample tasks in Orchestrator tab"
echo "   3. Explore Symphony Flow workflows"
echo ""
echo "📚 Documentation:"
echo "   • README.md — Overview"
echo "   • docs/ARCHITECTURE.md — How it works"
echo "   • docs/FLOW.md — Guided workflows"
echo ""
echo "💬 Need help?"
echo "   • GitHub Issues: https://github.com/courtneybtaylor-sys/Symphony-IR/issues"
echo "   • GitHub Discussions: https://github.com/courtneybtaylor-sys/Symphony-IR/discussions"
echo ""
