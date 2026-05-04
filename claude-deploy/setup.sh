#!/usr/bin/env bash
# ================================================================
# Claude Code Deploy — Auto-Setup (Linux / macOS)
# ================================================================
# Usage:
#   git clone <repo-url> && cd claude-deploy && bash setup.sh
# ================================================================

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${CYAN}  ╔═══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║     Claude Code Deploy — Setup           ║${NC}"
echo -e "${CYAN}  ║     Cross-Platform Install Wizard        ║${NC}"
echo -e "${CYAN}  ╚═══════════════════════════════════════════╝${NC}"
echo ""

# Find Python
PYTHON=""
for py in python3 python; do
    if command -v "$py" &>/dev/null; then
        ver=$("$py" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        major=$(echo "$ver" | cut -d. -f1)
        if [ "$major" -ge 3 ]; then
            PYTHON="$py"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "${YELLOW}  Python 3.8+ not found.${NC}"
    echo "  Install it from https://python.org"
    echo ""
    echo "  Ubuntu/Debian:  sudo apt install python3 python3-pip"
    echo "  macOS:          brew install python3"
    echo "  Fedora:         sudo dnf install python3"
    echo ""
    exit 1
fi

echo -e "${GREEN}  Using: $PYTHON ($($PYTHON --version 2>&1))${NC}"
echo ""

# Check tkinter
if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    echo -e "${YELLOW}  tkinter not found. Attempting to install...${NC}"
    if command -v apt &>/dev/null; then
        echo "  Running: sudo apt install -y python3-tk"
        sudo apt install -y python3-tk 2>/dev/null || true
    elif command -v dnf &>/dev/null; then
        echo "  Running: sudo dnf install -y python3-tkinter"
        sudo dnf install -y python3-tkinter 2>/dev/null || true
    elif command -v brew &>/dev/null; then
        echo "  Running: brew install python-tk@3"
        brew install python-tk@3 2>/dev/null || true
    fi
fi

echo -e "${GREEN}  Launching setup wizard...${NC}"
echo ""

# Run the launcher
exec "$PYTHON" launch.py "$@"
