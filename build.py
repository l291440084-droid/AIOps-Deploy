#!/usr/bin/env python3
"""
PyInstaller build script for Claude Code Deploy GUI.
Produces standalone executables for the current platform.

Usage:
    python build.py              # Build for current platform
    python build.py --clean      # Clean build
"""

import os
import sys
import shutil
import platform

APP_NAME = "AIDeploy"
ENTRY_POINT = "claude_deploy_gui.py"
MODULES = ["deploy_core.py", "providers.py", "i18n.py"]

def clean():
    for d in ["build", "dist", "__pycache__"]:
        if os.path.exists(d):
            shutil.rmtree(d)
    for f in os.listdir("."):
        if f.endswith(".spec"):
            os.remove(f)
    print("[clean] Done.")

def build():
    system = platform.system()
    sep = ";" if system == "Windows" else ":"

    if system == "Windows":
        exe_name = f"{APP_NAME}.exe"
    elif system == "Darwin":
        exe_name = f"{APP_NAME}.app"
    else:
        exe_name = APP_NAME

    # Build --add-data args for all modules
    add_data = " ".join(f'--add-data "{m}{sep}."' for m in MODULES)

    cmd = (
        f'pyinstaller'
        f' --onefile'
        f' --windowed'
        f' --name "{APP_NAME}"'
        f' {add_data}'
        f' --hidden-import tkinter'
        f' --hidden-import providers'
        f' --hidden-import i18n'
        f' --hidden-import deploy_core'
        f' --clean'
        f' "{ENTRY_POINT}"'
    )

    print(f"[build] Building for {system}...")
    print(f"[build] {cmd}")
    exit_code = os.system(cmd)

    if exit_code == 0:
        print(f"\n[build] Success: dist/{exe_name}")
    else:
        print(f"\n[build] Failed (exit code {exit_code})")
        sys.exit(exit_code)

if __name__ == "__main__":
    if "--clean" in sys.argv:
        clean()
    else:
        build()
