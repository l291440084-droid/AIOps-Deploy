# ================================================================
# Claude Code Deploy — Auto-Setup (Windows PowerShell)
# ================================================================
# Usage:
#   git clone <repo-url>; cd claude-deploy; .\setup.ps1
# ================================================================

Write-Host ""
Write-Host "  ╔═══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║     Claude Code Deploy — Setup           ║" -ForegroundColor Cyan
Write-Host "  ║     Cross-Platform Install Wizard        ║" -ForegroundColor Cyan
Write-Host "  ╚═══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Find Python
$python = $null
foreach ($py in @("python3", "python")) {
    try {
        $ver = & $py --version 2>$null
        if ($ver -match "(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            if ($major -ge 3) {
                $python = $py
                break
            }
        }
    } catch {}
}

if (-not $python) {
    Write-Host "  Python 3.8+ not found." -ForegroundColor Yellow
    Write-Host "  Install it from https://python.org"
    Write-Host "  Or run: winget install Python.Python.3.12"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "  Using: $python" -ForegroundColor Green
Write-Host ""

# Check tkinter
$hasTk = & $python -c "import tkinter; print('OK')" 2>$null
if (-not $hasTk) {
    Write-Host "  tkinter not found. Please reinstall Python with tcl/tk support." -ForegroundColor Yellow
    Write-Host "  Download from: https://python.org"
}

Write-Host "  Launching setup wizard..." -ForegroundColor Green
Write-Host ""

# Run the launcher
& $python launch.py @args
