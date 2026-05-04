# ============================================================
# Claude Code One-Click Installer (Windows)
# ============================================================
# Repository: https://github.com/<your-username>/claude-deploy
# Usage: Right-click -> Run with PowerShell
# Or:     powershell -ExecutionPolicy Bypass -File install.ps1
# ============================================================

param()

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Claude Code Installer"

# Colors
function Write-Info  { Write-Host "[✓] $args" -ForegroundColor Green }
function Write-Warn  { Write-Host "[!] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[✗] $args" -ForegroundColor Red }
function Write-Step  { Write-Host "`n==> $args" -ForegroundColor Cyan }
function Write-Prompt { Write-Host -NoNewline "[?] $args" -ForegroundColor Yellow }

# Banner
Write-Host @"
`n
  ┌──────────────────────────────────────────────┐
  │                                              │
  │     Claude Code - One-Click Installer        │
  │     Windows (PowerShell)                     │
  │                                              │
  └──────────────────────────────────────────────┘
"@ -ForegroundColor Cyan

# Admin check
function Check-Admin {
    Write-Step "Checking privileges..."
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Warn "Not running as Administrator."
        Write-Warn "npm global install may fail without admin rights."
        Write-Warn "If installation fails, right-click this script and choose 'Run with PowerShell' as Administrator."
        Write-Host ""
    } else {
        Write-Info "Running as Administrator"
    }
}

# Node.js check
function Check-NodeJS {
    Write-Step "Checking Node.js environment..."

    $nodeVersion = $null
    try {
        $nodeVersion = (node --version 2>$null) -replace 'v', ''
    } catch {}

    if (-not $nodeVersion) {
        Write-Warn "Node.js is not installed or not on PATH."
        Write-Host ""
        Write-Host "  Install options:"
        Write-Host ""
        Write-Host "  Option 1 - winget (Recommended):"
        Write-Host "    winget install OpenJS.NodeJS.LTS"
        Write-Host ""
        Write-Host "  Option 2 - Direct download:"
        Write-Host "    https://nodejs.org (download LTS, run installer)"
        Write-Host ""
        Write-Host "  Option 3 - nvm-windows:"
        Write-Host "    winget install CoreyButler.NVMforWindows"
        Write-Host "    nvm install lts"
        Write-Host "    nvm use lts"
        Write-Host ""

        $choice = Read-Host "Try to install Node.js via winget now? [y/N]"
        if ($choice -eq 'y' -or $choice -eq 'Y') {
            Write-Host "  Running: winget install OpenJS.NodeJS.LTS"
            winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
            Write-Warn "Node.js installed. Please RESTART this PowerShell window and re-run the script."
            Write-Warn "After restart, run: .\install.ps1"
            Write-Host "Press any key to exit..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            exit 0
        }

        Write-Error "Node.js is required. Please install it and re-run this script."
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }

    $major = [int]($nodeVersion.Split('.')[0])
    if ($major -lt 18) {
        Write-Error "Node.js $nodeVersion detected, but >= 18 is required. Please upgrade."
        exit 1
    }

    Write-Info "Node.js $nodeVersion detected"

    try {
        $npmVersion = npm --version 2>$null
        Write-Info "npm $npmVersion detected"
    } catch {
        Write-Error "npm not found. Please reinstall Node.js."
        exit 1
    }
}

# Install Claude Code
function Install-ClaudeCode {
    Write-Step "Installing Claude Code CLI..."

    $alreadyInstalled = $false
    try {
        $currentVersion = claude --version 2>$null
        if ($currentVersion) {
            Write-Info "Claude Code is already installed ($currentVersion)"
            $choice = Read-Host "Reinstall / upgrade to latest version? [y/N]"
            if ($choice -ne 'y' -and $choice -ne 'Y') {
                Write-Info "Skipping install. Using existing installation."
                $script:skipInstall = $true
                return
            }
        }
    } catch {}

    Write-Host "  Running: npm install -g @anthropic-ai/claude-code"
    Write-Host ""
    npm install -g @anthropic-ai/claude-code
    Write-Host ""

    try {
        $version = claude --version 2>$null
        Write-Info "Claude Code installed successfully: $version"
    } catch {
        Write-Warn "Claude CLI not found on PATH after install."
        Write-Warn "Check that npm global bin directory is in your PATH."
    }
}

# Configure API key
function Set-APIKey {
    Write-Step "Configuring Anthropic API Key..."

    $currentKey = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
    if ($currentKey) {
        Write-Info "ANTHROPIC_API_KEY is already configured."
        $choice = Read-Host "Do you want to update it? [y/N]"
        if ($choice -ne 'y' -and $choice -ne 'Y') {
            Write-Info "Keeping existing API key."
            return
        }
    }

    Write-Host ""
    Write-Host "  Get your API key from: https://console.anthropic.com/settings/keys"
    Write-Host ""

    $secureKey = Read-Host "Paste your Anthropic API key" -AsSecureString
    $apiKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    )

    if (-not $apiKey) {
        Write-Warn "No API key provided. You can set it later:"
        Write-Host '  [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")'
        return
    }

    # Set persistent environment variable
    [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $apiKey, "User")
    # Also set for current session
    $env:ANTHROPIC_API_KEY = $apiKey

    # Try claude config
    try {
        claude config set apiKey $apiKey 2>$null
    } catch {}

    Write-Info "API key configured as a persistent User environment variable."
    Write-Info "Restart your terminal or run: `$env:ANTHROPIC_API_KEY = '...'"
}

# Verify
function Verify-Install {
    Write-Step "Verifying installation..."

    try {
        $version = claude --version 2>$null
        if ($version) {
            Write-Info "Claude Code version: $version"
        }
    } catch {
        Write-Warn "Claude CLI not found. Check PATH configuration."
        return
    }

    if ($env:ANTHROPIC_API_KEY) {
        Write-Info "API key is configured and ready to use."
    } else {
        Write-Warn "API key not set. Set it before running claude."
    }
}

# Summary
function Show-Summary {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host "  Installation Complete!" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Quick Start:" -ForegroundColor White
    Write-Host "    claude                          # Start Claude Code"
    Write-Host "    claude --help                   # Show help"
    Write-Host '    claude -p "your prompt"         # Single prompt mode'
    Write-Host ""
    Write-Host "  Resources:" -ForegroundColor White
    Write-Host "    Docs:     https://docs.anthropic.com/en/docs/claude-code"
    Write-Host "    Console:  https://console.anthropic.com"
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Main
function Main {
    Check-Admin
    Check-NodeJS
    Install-ClaudeCode
    Set-APIKey
    Verify-Install
    Show-Summary
}

Main
