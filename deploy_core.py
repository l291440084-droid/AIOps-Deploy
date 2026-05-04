#!/usr/bin/env python3
"""
Claude Code Deploy Tool — Core Logic Module
No GUI dependencies. Can be used by both GUI and CLI.
"""

import os
import re
import sys
import json
import shutil
import shlex
import subprocess
import platform
from pathlib import Path
from typing import Callable, Optional

# ── Result helpers ──────────────────────────────────────────────

def ok(**kwargs) -> dict:
    d = {"success": True, "error": None, "fix": None}
    d.update(kwargs)
    return d

def fail(error: str, fix: str = "", **kwargs) -> dict:
    d = {"success": False, "error": error, "fix": fix}
    d.update(kwargs)
    return d

# ── OS Detection ────────────────────────────────────────────────

def detect_os() -> dict:
    """Return OS info dict."""
    system = platform.system()
    if system == "Linux":
        name = "Linux"
        try:
            import distro
            dist = distro.name(pretty=True)
        except ImportError:
            dist = ""
            for f in ["/etc/os-release", "/etc/lsb-release"]:
                try:
                    with open(f) as fh:
                        for line in fh:
                            if line.startswith("PRETTY_NAME="):
                                dist = line.split("=", 1)[1].strip().strip('"')
                                break
                except Exception:
                    pass
        name = dist or "Linux"
    elif system == "Darwin":
        name = "macOS " + platform.mac_ver()[0]
    elif system == "Windows":
        name = "Windows " + platform.win32_ver()[0]
    else:
        name = system

    return ok(
        system=system,
        name=name,
        arch=platform.machine(),
        is_admin= _check_admin(system),
    )

def _check_admin(system: str) -> bool:
    if system == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    elif system in ("Linux", "Darwin"):
        return os.geteuid() == 0
    return False

# ── Shell profile helpers ───────────────────────────────────────

def _get_shell() -> str:
    """Detect current shell name."""
    shell = os.environ.get("SHELL", "")
    if shell:
        return Path(shell).name
    return "bash"

def _get_profile_paths(system: str) -> list:
    """Return list of shell profile file paths to write env vars to."""
    home = Path.home()
    shell = _get_shell()
    profiles = []

    if system == "Windows":
        return []  # Handled via setx / registry

    if shell == "zsh":
        profiles.extend([home / ".zshrc", home / ".zprofile"])
    elif shell == "bash":
        if system == "Darwin":
            profiles.extend([home / ".bash_profile", home / ".bashrc"])
        else:
            profiles.extend([home / ".bashrc", home / ".profile"])
    else:
        profiles.append(home / ".profile")

    # Filter to existing or primary
    existing = [p for p in profiles if p.exists()]
    return existing or [profiles[0]]

# ── Node.js ─────────────────────────────────────────────────────

def check_node() -> dict:
    """Check Node.js installation and version."""
    path = shutil.which("node")
    if not path:
        return fail(
            error="Node.js 未安装 / Node.js not found",
            fix="请安装 Node.js >= 18",
            installed=False,
            version=None,
            path=None,
        )

    try:
        out = subprocess.check_output([path, "--version"], text=True, stderr=subprocess.STDOUT)
        version = out.strip().lstrip("v")
    except Exception as e:
        return fail(
            error=f"Node.js 无法运行: {e}",
            fix="请重新安装 Node.js",
            installed=False,
            version=None,
            path=path,
        )

    major = int(version.split(".")[0])
    if major < 18:
        return fail(
            error=f"Node.js 版本 {version} < 18",
            fix="请升级 Node.js 到 18 或更新版本",
            installed=True,
            version=version,
            path=path,
            too_old=True,
        )

    return ok(installed=True, version=version, path=path)

def check_npm() -> dict:
    """Check npm availability."""
    path = shutil.which("npm")
    if not path:
        return fail(
            error="npm 未找到 / npm not found",
            fix="请重新安装 Node.js（npm 随 Node.js 一起安装）",
            installed=False,
            version=None,
        )
    try:
        out = subprocess.check_output([path, "--version"], text=True, stderr=subprocess.STDOUT)
        version = out.strip()
    except Exception as e:
        return fail(error=f"npm 无法运行: {e}", fix="请重新安装 Node.js", installed=False, version=None)
    return ok(installed=True, version=version, path=path)


# ── Auto-Install Node.js ────────────────────────────────────────

def install_nodejs(progress_callback: Optional[Callable[[str, float], None]] = None) -> dict:
    """Auto-install Node.js >= 18 for the current platform."""
    system = platform.system()
    if progress_callback:
        progress_callback(f"检测到 {system}，准备自动安装 Node.js...", 0.02)
    if system == "Linux":
        return _install_node_linux(progress_callback)
    elif system == "Darwin":
        return _install_node_macos(progress_callback)
    elif system == "Windows":
        return _install_node_windows(progress_callback)
    return fail(error=f"不支持自动安装: {system}", fix="请手动安装: https://nodejs.org")


def _run_cmd(cmd: list, desc: str, pct: float, cb: Optional[Callable] = None, timeout: int = 180) -> tuple:
    """Run a command, return (success_bool, output_str)."""
    if cb: cb(desc, pct)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return False, "超时 / Timeout"
    except Exception as e:
        return False, str(e)


def _install_node_linux(cb=None) -> dict:
    use_sudo = os.geteuid() != 0
    # apt (Debian/Ubuntu)
    if shutil.which("apt"):
        ok_, out = _run_cmd(["bash", "-c",
            f"curl -fsSL https://deb.nodesource.com/setup_20.x | {'sudo -E' if use_sudo else ''} bash -"],
            "添加 NodeSource 仓库...", 0.15, cb, timeout=60)
        if ok_:
            ok2, _ = _run_cmd(
                (["sudo", "apt-get", "install", "-y", "nodejs"] if use_sudo else ["apt-get", "install", "-y", "nodejs"]),
                "通过 apt 安装 Node.js...", 0.55, cb)
            if ok2: return _verify_node(cb)
        return _install_node_nvm(cb)

    # dnf (Fedora)
    if shutil.which("dnf") or shutil.which("yum"):
        mgr = "dnf" if shutil.which("dnf") else "yum"
        ok_, _ = _run_cmd(
            (["sudo", mgr, "install", "-y", "nodejs"] if use_sudo else [mgr, "install", "-y", "nodejs"]),
            "通过 dnf 安装 Node.js...", 0.50, cb)
        if ok_: return _verify_node(cb)
        return _install_node_nvm(cb)

    # pacman (Arch)
    if shutil.which("pacman"):
        ok_, _ = _run_cmd(
            (["sudo", "pacman", "-S", "--noconfirm", "nodejs", "npm"] if use_sudo else ["pacman", "-S", "--noconfirm", "nodejs", "npm"]),
            "通过 pacman 安装 Node.js...", 0.50, cb)
        if ok_: return _verify_node(cb)
        return _install_node_nvm(cb)

    return _install_node_nvm(cb)


def _install_node_nvm(cb=None) -> dict:
    """Install Node.js via nvm (no sudo needed)."""
    if cb: cb("通过 nvm 安装 Node.js (免 sudo)...", 0.10)
    nvm_dir = Path.home() / ".nvm"
    if not nvm_dir.exists():
        ok_, out = _run_cmd(["bash", "-c",
            "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"],
            "下载安装 nvm...", 0.30, cb)
        if not ok_:
            return fail(error=f"nvm 安装失败", fix="手动安装: https://nodejs.org")

    ok_, out = _run_cmd(["bash", "-c",
        f'export NVM_DIR="{nvm_dir}" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm install 20'],
        "nvm install 20...", 0.65, cb, timeout=300)
    if ok_: return _verify_node(cb)
    return fail(error=f"nvm install 失败: {out[-300:]}", fix="手动安装: nvm install 20")


def _install_node_macos(cb=None) -> dict:
    if shutil.which("brew"):
        ok_, _ = _run_cmd(["brew", "install", "node@20"], "brew install node@20...", 0.50, cb)
        if ok_:
            _run_cmd(["brew", "link", "--overwrite", "node@20"], "", 0.80, cb)
            return _verify_node(cb)
    return _install_node_nvm(cb)


def _install_node_windows(cb=None) -> dict:
    if shutil.which("winget"):
        ok_, _ = _run_cmd(
            ["winget", "install", "OpenJS.NodeJS.LTS", "--silent",
             "--accept-package-agreements", "--accept-source-agreements"],
            "winget 安装 Node.js LTS...", 0.50, cb)
        if ok_:
            if cb: cb("安装完成！请重启终端。", 1.0)
            return ok(installed=True, note="Node.js installed via winget. Restart terminal.")
    return fail(error="无法自动安装 Node.js",
                fix="winget install OpenJS.NodeJS.LTS\n或访问 https://nodejs.org")


def _verify_node(cb=None) -> dict:
    """Re-check Node.js after install. Handle nvm PATH."""
    nvm_dir = Path.home() / ".nvm" / "nvm.sh"
    if nvm_dir.exists():
        try:
            out = subprocess.check_output(
                ["bash", "-c", f'source "{nvm_dir}" && which node && node --version'],
                text=True, timeout=10)
            lines = out.strip().split("\n")
            if len(lines) >= 2:
                v = lines[1].lstrip("v")
                if cb: cb(f"Node.js v{v} 安装成功!", 1.0)
                return ok(installed=True, version=v, path=lines[0])
        except Exception:
            pass
    r = check_node()
    if r["success"] and cb: cb(f"Node.js v{r['version']}", 1.0)
    return r


# ── Full Auto-Deploy ────────────────────────────────────────────

def auto_deploy(install_dir: Optional[str] = None,
                progress_callback: Optional[Callable[[str, float], None]] = None) -> dict:
    """Full auto: check → install Node if needed → install Claude Code → verify."""
    results = {}
    results["os"] = detect_os()
    results["node"] = check_node()

    if not results["node"]["success"]:
        if progress_callback:
            progress_callback("Node.js 缺失，自动安装中...", 0.10)
        ni = install_nodejs(progress_callback)
        if not ni["success"]:
            results["node"] = ni
            return results
        results["node"] = check_node()

    results["npm"] = check_npm()

    if install_dir:
        os.makedirs(install_dir, exist_ok=True)
        npm = shutil.which("npm")
        if npm:
            subprocess.run([npm, "config", "set", "prefix", install_dir], capture_output=True)

    if progress_callback:
        progress_callback("安装 Claude Code CLI...", 0.60)
    results["install"] = install_claude(progress_callback)
    results["verify"] = check_claude()
    return results


# ── Claude Code ─────────────────────────────────────────────────

def check_claude() -> dict:
    """Check if claude CLI is installed."""
    path = shutil.which("claude")
    if not path:
        return ok(installed=False, version=None, path=None)

    try:
        out = subprocess.check_output([path, "--version"], text=True, stderr=subprocess.STDOUT, timeout=10)
        version = out.strip()
    except Exception:
        version = "unknown"
    return ok(installed=True, version=version, path=path)

def install_claude(progress_callback: Optional[Callable[[str, float], None]] = None) -> dict:
    """
    Install Claude Code via npm.
    progress_callback receives (line_text, progress_0_to_1)
    """
    npm = shutil.which("npm")
    if not npm:
        return fail(error="npm 未找到", fix="请先安装 Node.js")

    # Determine if we need sudo/setx
    system = platform.system()
    if system == "Windows":
        cmd = [npm, "install", "-g", "@anthropic-ai/claude-code"]
    elif system == "Linux" and os.geteuid() != 0:
        # Check if npm prefix is user-writable
        try:
            prefix = subprocess.check_output([npm, "config", "get", "prefix"], text=True).strip()
            prefix_path = Path(prefix)
            if prefix_path.exists() and os.access(prefix_path, os.W_OK):
                cmd = [npm, "install", "-g", "@anthropic-ai/claude-code"]
            else:
                cmd = ["sudo", npm, "install", "-g", "@anthropic-ai/claude-code"]
        except Exception:
            cmd = [npm, "install", "-g", "@anthropic-ai/claude-code"]
    else:
        cmd = [npm, "install", "-g", "@anthropic-ai/claude-code"]

    if progress_callback:
        progress_callback(f"运行: {' '.join(cmd)}", 0.05)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as e:
        return fail(error=f"无法启动 npm: {e}", fix="请检查 npm 安装")

    output_lines = []
    for line in proc.stdout:
        line = line.rstrip()
        output_lines.append(line)
        if progress_callback:
            progress_callback(line, 0.1 + 0.8 * min(len(output_lines) / 100, 1.0))

    proc.wait()

    full_output = "\n".join(output_lines)

    if proc.returncode != 0:
        # Diagnose common errors
        if "EACCES" in full_output or "EACCES" in full_output.lower():
            return fail(
                error="权限不足 / Permission denied (EACCES)",
                fix="请以管理员/root 运行，或配置 npm prefix",
                output=full_output,
            )
        if "ENOTFOUND" in full_output or "ETIMEDOUT" in full_output or "network" in full_output.lower():
            return fail(
                error="网络错误 / Network error",
                fix="请检查网络连接和代理设置",
                output=full_output,
            )
        return fail(
            error=f"安装失败 (exit code {proc.returncode})",
            fix="请查看输出日志了解详情",
            output=full_output,
        )

    if progress_callback:
        progress_callback("安装完成", 1.0)

    # Verify
    c = check_claude()
    return ok(
        installed=c.get("installed", True),
        version=c.get("version", ""),
        output=full_output,
    )

# ── API Key (legacy — Claude only) ───────────────────────────────

def validate_api_key(key: str) -> dict:
    """Validate Anthropic API key format (legacy)."""
    if not key or not key.strip():
        return fail(error="API Key 为空", fix="请输入有效的 API Key（以 sk-ant- 开头）")
    key = key.strip()
    if not key.startswith("sk-ant-"):
        return fail(
            error="API Key 格式不正确",
            fix="Anthropic API Key 应以 sk-ant- 开头。\n请在 https://console.anthropic.com/settings/keys 获取",
        )
    if len(key) < 30:
        return fail(error="API Key 太短", fix="请检查是否完整复制了 API Key")
    return ok()

def save_api_key(key: str) -> dict:
    """Save Anthropic API key (legacy)."""
    return save_env_var("ANTHROPIC_API_KEY", key.strip())

# ── Multi-Provider Key Management ────────────────────────────────

def validate_key_for_provider(key: str, provider: dict) -> dict:
    """Validate API key against a specific provider's rules."""
    key = key.strip() if key else ""

    category = provider.get("category", "")
    prefix = provider.get("key_prefix", "")

    # Local providers don't need API keys (they use base URLs instead)
    if category == "local":
        return ok()

    if not prefix:
        # No prefix = no format validation, but still require non-empty
        if not key:
            return fail(error="请输入 API Key", fix=f"请输入 {provider.get('name','')} 的 API Key")
        return ok()

    if not key:
        return fail(error="API Key 为空", fix=f"请输入 {provider.get('name','')} 的 API Key（以 {prefix} 开头）")

    if not key.startswith(prefix):
        return fail(
            error=f"API Key 格式不正确",
            fix=f"{provider.get('name','')} 的 Key 应以 {prefix} 开头。\n请在 {provider.get('console_url','')} 获取",
        )
    if len(key) < len(prefix) + 10:
        return fail(error="API Key 太短", fix="请检查是否完整复制了 API Key")
    return ok()

def save_env_var(env_var: str, value: str) -> dict:
    """Save an environment variable persistently (cross-platform)."""
    system = platform.system()
    results = []

    if system == "Windows":
        try:
            subprocess.run(
                ["setx", env_var, value],
                capture_output=True, text=True, timeout=10,
            )
            results.append(f"setx {env_var}")
        except Exception as e:
            return fail(error=f"保存 {env_var} 失败: {e}", fix=f"请手动设置环境变量 {env_var}")
    else:
        profiles = _get_profile_paths(system)
        export_line = f'export {env_var}="{value}"\n'
        for p in profiles:
            try:
                content = p.read_text() if p.exists() else ""
                lines = [l for l in content.splitlines() if env_var not in l]
                lines.append(export_line.rstrip())
                p.write_text("\n".join(lines) + "\n")
                results.append(str(p))
            except Exception as e:
                return fail(
                    error=f"无法写入 {p}: {e}",
                    fix=f"请手动添加: echo '{export_line.strip()}' >> {p}",
                )

    # Set for current process
    os.environ[env_var] = value

    # Also set via launchctl on macOS
    if system == "Darwin":
        try:
            subprocess.run(["launchctl", "setenv", env_var, value], capture_output=True, timeout=5)
        except Exception:
            pass

    return ok(saved_to=results, env_var=env_var)

def save_provider_key(provider_id: str, key: str) -> dict:
    """Save API key for a specific provider by ID."""
    try:
        from providers import get_provider
    except ImportError:
        return fail(error="无法加载提供商数据库", fix="请确保 providers.py 存在")
    provider = get_provider(provider_id)
    if not provider:
        return fail(error=f"未知提供商: {provider_id}", fix="请选择有效的提供商")

    # Validate
    validation = validate_key_for_provider(key, provider.to_dict())
    if not validation["success"]:
        return validation

    # Save
    return save_env_var(provider.env_var, key.strip())

def delete_provider_key(provider_id: str) -> dict:
    """Remove a provider's API key from env vars and profiles."""
    try:
        from providers import get_provider
    except ImportError:
        return fail(error="无法加载提供商数据库")
    provider = get_provider(provider_id)
    if not provider:
        return fail(error=f"未知提供商: {provider_id}")

    system = platform.system()
    env_var = provider.env_var

    if system == "Windows":
        try:
            subprocess.run(["setx", env_var, ""], capture_output=True, text=True, timeout=10)
        except Exception:
            pass
    else:
        profiles = _get_profile_paths(system)
        for p in profiles:
            try:
                if not p.exists():
                    continue
                content = p.read_text()
                lines = [l for l in content.splitlines() if env_var not in l]
                p.write_text("\n".join(lines) + "\n")
            except Exception:
                pass

    if env_var in os.environ:
        del os.environ[env_var]

    return ok(deleted=True, provider=provider.name)

def export_env_file() -> str:
    """Generate a .env file content from all configured providers."""
    from providers import get_all_providers
    lines = ["# AI Provider API Keys — Generated by AI Deploy Tool", ""]
    for p in get_all_providers():
        val = os.environ.get(p.env_var, "")
        if val:
            lines.append(f"# {p.name}")
            lines.append(f'{p.env_var}="{val}"')
            lines.append("")
    return "\n".join(lines)

def test_api_connection(provider_id: str, timeout: int = 10) -> dict:
    """Basic connectivity test: try to reach the provider's API endpoint."""
    try:
        from providers import get_provider
    except ImportError:
        return fail(error="无法加载提供商数据库")
    provider = get_provider(provider_id)
    if not provider:
        return fail(error=f"未知提供商: {provider_id}")
    if not provider.base_url:
        return fail(error="该提供商无 Base URL", fix="跳过连接测试")

    api_key = os.environ.get(provider.env_var, "")
    if not api_key and provider.env_var not in ("OLLAMA_HOST", "LMSTUDIO_HOST", "VLLM_HOST", "LOCALAI_HOST", "TEXTGEN_HOST"):
        return fail(error="未配置 API Key", fix="请先配置此提供商的 API Key")

    import urllib.request
    import urllib.error
    import ssl

    url = provider.base_url.rstrip("/")
    # Try /models endpoint (OpenAI-compatible) or root
    test_urls = [f"{url}/models", f"{url}/v1/models", url]
    ctx = ssl.create_default_context()

    last_error = ""
    for test_url in test_urls:
        try:
            req = urllib.request.Request(test_url)
            if api_key and provider.env_var not in ("OLLAMA_HOST", "LMSTUDIO_HOST", "VLLM_HOST", "LOCALAI_HOST", "TEXTGEN_HOST"):
                req.add_header("Authorization", f"Bearer {api_key}")
            resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
            resp.read()
            return ok(endpoint=test_url, status=resp.status)
        except urllib.error.HTTPError as e:
            # 401/403 = auth worked, endpoint exists — that's fine
            if e.code in (401, 403):
                return ok(endpoint=test_url, status=e.code, note="认证通过，但无权限列出模型")
            last_error = f"HTTP {e.code}"
        except Exception as e:
            last_error = str(e)

    return fail(
        error=f"无法连接到 {provider.name} API",
        fix=f"请检查网络和 Base URL: {provider.base_url}",
        detail=last_error,
    )

# ── PATH fix ─────────────────────────────────────────────────────

def get_npm_global_bin() -> Optional[str]:
    """Get npm global bin directory."""
    npm = shutil.which("npm")
    if not npm:
        return None
    try:
        prefix = subprocess.check_output([npm, "config", "get", "prefix"], text=True).strip()
        system = platform.system()
        if system == "Windows":
            return str(Path(prefix) / "node_modules" / ".bin")
        else:
            return str(Path(prefix) / "bin")
    except Exception:
        return None

def check_claude_on_path() -> dict:
    """Check if claude is accessible, and provide fix if not."""
    claude_path = shutil.which("claude")
    if claude_path:
        return ok(on_path=True, path=claude_path)

    npm_bin = get_npm_global_bin()
    if npm_bin:
        system = platform.system()
        if system == "Windows":
            fix_cmd = f'[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";{npm_bin}", "User")'
        else:
            fix_cmd = f'export PATH="{npm_bin}:$PATH"'
            shell = _get_shell()
            profiles = _get_profile_paths(system)
            profile_str = profiles[0] if profiles else f"~/.{shell}rc"
            fix_cmd += f"\necho 'export PATH=\"{npm_bin}:\\$PATH\"' >> {profile_str}"

        return fail(
            error=f"Claude CLI 不在 PATH 中（安装在 {npm_bin}）",
            fix=fix_cmd,
            on_path=False,
            npm_bin=npm_bin,
        )

    return fail(
        error="Claude CLI 未安装或不在 PATH 中",
        fix="请重新安装：npm install -g @anthropic-ai/claude-code",
        on_path=False,
    )
