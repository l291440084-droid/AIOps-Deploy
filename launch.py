#!/usr/bin/env python3
"""
Claude Code Deploy — Cross-Platform Launcher
Checks Python / tkinter, installs deps if needed, then opens the GUI.

Usage:
    python3 launch.py              # Auto-detect language from system
    python3 launch.py --lang zh    # Force language
    python3 launch.py --cli        # Run CLI mode instead of GUI
"""

import sys
import os
import subprocess
import platform

MIN_PYTHON = (3, 8)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def print_step(msg, ok=None):
    icon = " ✓" if ok is True else (" ✗" if ok is False else " ...")
    print(f"  [{icon}]  {msg}")


def check_python():
    """Verify Python version is sufficient."""
    ver = sys.version_info
    if ver < MIN_PYTHON:
        print(f"\n  ERROR: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required.")
        print(f"  Current: Python {ver.major}.{ver.minor}.{ver.micro}")
        print(f"  Download: https://python.org\n")
        sys.exit(1)
    print_step(f"Python {ver.major}.{ver.minor}.{ver.micro}", True)


def check_tkinter():
    """Check if tkinter is available; guide install if missing."""
    try:
        import tkinter
        print_step("tkinter (GUI toolkit)", True)
        return True
    except ImportError:
        print_step("tkinter (GUI toolkit)", False)
        system = platform.system()
        if system == "Linux":
            print("\n  [FIX] Install tkinter:")
            print("    Ubuntu/Debian:  sudo apt install python3-tk")
            print("    Fedora:         sudo dnf install python3-tkinter")
            print("    Arch:           sudo pacman -S tk")
            print("    Or run:         pip install tk")
        elif system == "Darwin":
            print("\n  [FIX] tkinter is built into macOS Python.")
            print("    Use the official Python from python.org,")
            print("    or:  brew install python-tk@3.12")
        elif system == "Windows":
            print("\n  [FIX] Reinstall Python and check 'tcl/tk and IDLE' during install.")
            print("    Download: https://python.org")
        return False


def check_deps():
    """Check all needed dependencies."""
    print("\n  ═══ Checking Environment ═══\n")
    check_python()
    has_tk = check_tkinter()
    print("\n  ════════════════════════════\n")
    return has_tk


def launch_gui(lang=None):
    """Launch the GUI application."""
    os.chdir(SCRIPT_DIR)
    sys.path.insert(0, SCRIPT_DIR)

    # Set language if specified
    if lang:
        from i18n import set_language, LANGUAGES
        if lang in LANGUAGES:
            set_language(lang)

    from claude_deploy_gui import main
    print("  Launching GUI application...\n")
    main()


def launch_cli():
    """Fallback: run the shell installer."""
    system = platform.system()
    if system == "Windows":
        script = os.path.join(SCRIPT_DIR, "install.ps1")
        print(f"\n  Running CLI installer: {script}\n")
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script])
    else:
        script = os.path.join(SCRIPT_DIR, "install.sh")
        print(f"\n  Running CLI installer: {script}\n")
        subprocess.run(["bash", script])


def parse_args():
    """Parse command line arguments."""
    args = {
        "lang": None,
        "cli": False,
    }
    for a in sys.argv[1:]:
        if a.startswith("--lang="):
            args["lang"] = a.split("=", 1)[1]
        elif a == "--cli":
            args["cli"] = True
        elif a in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
    return args


def main():
    args = parse_args()

    # Always show banner
    print(r"""
  ╔═══════════════════════════════════════════╗
  ║     Claude Code Deploy — Launcher        ║
  ║     Cross-Platform Setup Wizard          ║
  ╚═══════════════════════════════════════════╝
    """)

    if args["cli"]:
        launch_cli()
        return

    has_tk = check_deps()

    if has_tk:
        launch_gui(args["lang"])
    else:
        print("\n  GUI mode requires tkinter.")
        choice = input("  Continue with CLI mode? [Y/n]: ").strip().lower()
        if choice in ("", "y", "yes"):
            launch_cli()
        else:
            print("  Exiting. Install tkinter and re-run: python3 launch.py\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
