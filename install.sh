#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Claude Code One-Click Installer (Linux / macOS)
# ============================================================
# Repository: https://github.com/<your-username>/claude-deploy
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

banner() {
    echo -e "${CYAN}"
    echo "  ┌──────────────────────────────────────────────┐"
    echo "  │                                              │"
    echo "  │     Claude Code - One-Click Installer        │"
    echo "  │     Linux / macOS                            │"
    echo "  │                                              │"
    echo "  └──────────────────────────────────────────────┘"
    echo -e "${NC}"
}

info()    { echo -e "${GREEN}[✓]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
error()   { echo -e "${RED}[✗]${NC} $1"; }
step()    { echo -e "\n${BOLD}==>${NC} ${CYAN}$1${NC}"; }
prompt()  { echo -ne "${YELLOW}[?]${NC} $1"; }

detect_os() {
    OS="$(uname -s)"
    case "$OS" in
        Linux)  OS="Linux";;
        Darwin) OS="macOS";;
        *)
            error "Unsupported OS: $OS"
            error "This script supports Linux and macOS only."
            exit 1
            ;;
    esac
    info "Detected OS: $OS"
}

check_privileges() {
    if [ "$OS" = "Linux" ] && [ "$EUID" -eq 0 ]; then
        warn "Running as root. npm global install may not need sudo."
        warn "Consider running as a normal user if you use nvm or fnm."
        echo ""
    fi
}

check_node() {
    step "Checking Node.js environment..."

    NODE_VERSION=""
    if command -v node &>/dev/null; then
        NODE_VERSION=$(node --version 2>/dev/null | sed 's/v//')
    fi

    if [ -z "$NODE_VERSION" ]; then
        warn "Node.js is not installed."
        echo ""
        if [ "$OS" = "macOS" ]; then
            echo "  Install via Homebrew:"
            echo "    brew install node"
            echo ""
            echo "  Or download from: https://nodejs.org"
        elif [ "$OS" = "Linux" ]; then
            echo "  Install via package manager:"
            echo "    # Ubuntu/Debian:"
            echo "    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
            echo "    sudo apt-get install -y nodejs"
            echo ""
            echo "    # Fedora/RHEL:"
            echo "    sudo dnf install nodejs"
            echo ""
            echo "    # Arch:"
            echo "    sudo pacman -S nodejs"
            echo ""
            echo "  Or use nvm:"
            echo "    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
            echo "    nvm install 20"
            echo ""
            echo "  Or download from: https://nodejs.org"
        fi
        error "Please install Node.js >= 18 and re-run this script."
        exit 1
    fi

    MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)
    if [ "$MAJOR" -lt 18 ]; then
        warn "Node.js $NODE_VERSION detected, but >= 18 is required."
        error "Please upgrade Node.js and re-run this script."
        exit 1
    fi

    info "Node.js $NODE_VERSION detected"

    if ! command -v npm &>/dev/null; then
        error "npm not found. Please ensure npm is installed with Node.js."
        exit 1
    fi
    info "npm $(npm --version) detected"
}

install_claude_code() {
    step "Installing Claude Code CLI..."

    if command -v claude &>/dev/null; then
        CURRENT_VERSION=$(claude --version 2>/dev/null || echo "unknown")
        info "Claude Code is already installed (${CURRENT_VERSION})"
        prompt "Reinstall / upgrade to latest version? [y/N] "
        read -r REPLY
        if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
            info "Skipping install. Using existing installation."
            return
        fi
    fi

    echo "  Running: npm install -g @anthropic-ai/claude-code"
    echo ""

    INSTALL_CMD="npm install -g @anthropic-ai/claude-code"
    if [ "$OS" = "Linux" ] && [ "$EUID" -ne 0 ] && [ ! -d "$HOME/.nvm" ] && [ ! -d "$HOME/.local/share/fnm" ]; then
        if npm config get prefix | grep -q "$HOME"; then
            $INSTALL_CMD
        else
            warn "npm global prefix is system-owned. Trying with sudo..."
            sudo $INSTALL_CMD
        fi
    else
        $INSTALL_CMD
    fi

    echo ""

    if command -v claude &>/dev/null; then
        info "Claude Code installed successfully: $(claude --version 2>/dev/null || echo 'ok')"
    else
        warn "Claude CLI not found on PATH after install."
        warn "You may need to add npm global bin to your PATH:"
        echo "  export PATH=\"\$(npm config get prefix)/bin:\$PATH\""
    fi
}

configure_api_key() {
    step "Configuring Anthropic API Key..."

    # Check if already configured via env var
    if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
        info "ANTHROPIC_API_KEY environment variable is already set."
        prompt "Do you want to update it? [y/N] "
        read -r REPLY
        if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
            info "Keeping existing API key."
            return
        fi
    fi

    echo ""
    echo "  Get your API key from: https://console.anthropic.com/settings/keys"
    echo ""
    prompt "Paste your Anthropic API key: "
    read -rs API_KEY
    echo ""

    if [ -z "$API_KEY" ]; then
        warn "No API key provided. You can set it later with:"
        echo "  export ANTHROPIC_API_KEY=\"sk-ant-...\""
        return
    fi

    # Write to shell profiles
    echo ""
    echo "  Where would you like to store the API key?"

    PROFILES=()
    SHELL_NAME="$(basename "$SHELL")"

    case "$SHELL_NAME" in
        zsh)
            [ -f "$HOME/.zshrc" ] && PROFILES+=("$HOME/.zshrc")
            [ -f "$HOME/.zprofile" ] && PROFILES+=("$HOME/.zprofile")
            [ ${#PROFILES[@]} -eq 0 ] && PROFILES+=("$HOME/.zshrc")
            ;;
        bash)
            if [ "$OS" = "macOS" ]; then
                [ -f "$HOME/.bash_profile" ] && PROFILES+=("$HOME/.bash_profile")
                [ -f "$HOME/.bashrc" ] && PROFILES+=("$HOME/.bashrc")
                [ ${#PROFILES[@]} -eq 0 ] && PROFILES+=("$HOME/.bash_profile")
            else
                [ -f "$HOME/.bashrc" ] && PROFILES+=("$HOME/.bashrc")
                [ -f "$HOME/.profile" ] && PROFILES+=("$HOME/.profile")
                [ ${#PROFILES[@]} -eq 0 ] && PROFILES+=("$HOME/.bashrc")
            fi
            ;;
        *)
            [ -f "$HOME/.profile" ] && PROFILES+=("$HOME/.profile")
            [ ${#PROFILES[@]} -eq 0 ] && PROFILES+=("$HOME/.profile")
            ;;
    esac

    for PROFILE in "${PROFILES[@]}"; do
        # Remove old entry if present
        if grep -q "ANTHROPIC_API_KEY" "$PROFILE" 2>/dev/null; then
            if [ "$OS" = "macOS" ]; then
                sed -i '' '/ANTHROPIC_API_KEY/d' "$PROFILE"
            else
                sed -i '/ANTHROPIC_API_KEY/d' "$PROFILE"
            fi
        fi
        echo "export ANTHROPIC_API_KEY=\"$API_KEY\"" >> "$PROFILE"
        info "Added to $PROFILE"
    done

    # Also set for current session
    export ANTHROPIC_API_KEY="$API_KEY"

    # Try claude config if CLI supports it
    if command -v claude &>/dev/null; then
        claude config set apiKey "$API_KEY" 2>/dev/null || true
    fi

    info "API key configured. Run 'source ${PROFILES[0]}' or restart your terminal to apply."
}

verify_installation() {
    step "Verifying installation..."

    if ! command -v claude &>/dev/null; then
        warn "Claude CLI not found. Check npm global bin is on your PATH."
        return
    fi

    VERSION_OUTPUT=$(claude --version 2>&1 || echo "")
    if [ -n "$VERSION_OUTPUT" ]; then
        info "Claude Code version: $VERSION_OUTPUT"
    fi

    # Quick smoke test
    if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
        info "API key is configured and ready to use."
    else
        warn "API key not set. Set it before running claude:"
        echo "  export ANTHROPIC_API_KEY=\"sk-ant-...\""
    fi
}

print_summary() {
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  ${BOLD}Quick Start:${NC}"
    echo "    claude                          # Start Claude Code"
    echo "    claude --help                   # Show help"
    echo "    claude -p \"your prompt\"         # Single prompt mode"
    echo ""
    echo -e "  ${BOLD}Resources:${NC}"
    echo "    Docs:     https://docs.anthropic.com/en/docs/claude-code"
    echo "    Console:  https://console.anthropic.com"
}

# ============================================================
main() {
    banner
    detect_os
    check_privileges
    check_node
    install_claude_code
    configure_api_key
    verify_installation
    print_summary
}

main
