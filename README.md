# AI API 一键部署工具 / AI API One-Click Deploy

[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)](#)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](#)
[![Providers](https://img.shields.io/badge/providers-50+-orange.svg)](#)
[![Languages](https://img.shields.io/badge/languages-6%20UN-purple.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**可视化配置 50+ AI 模型 API Key，6 种联合国语言，一键部署 Claude Code。无需 Anthropic 账号也能用替代工具。**

> Visual API key management for 50+ AI providers. 6 UN official languages. One-click Claude Code install. Alternative tools available without Anthropic account.

---

## 🚀 快速开始 / Quick Start

```bash
git clone https://github.com/l291440084-droid/AIOps-Deploy.git
cd AIOps-Deploy
python3 launch.py          # Linux / macOS / Windows

# 也可以直接运行一键脚本：
bash setup.sh              # Linux / macOS
.\setup.ps1                # Windows PowerShell
```

### 启动后流程

1. **自动语言检测** — 根据系统语言自动选择，也可手动切换（中文/English 等 6 种）
2. **选择安装目录** — 默认 npm 全局或自定义路径
3. **系统检测** — 自动检查 OS / Node.js / npm / Claude Code（缺失自动安装）
4. **一键安装 Claude Code** — 或跳过，使用替代工具
5. **配置 API Key** — 50+ 提供商可视化卡片，点击配置
6. **替代工具** — 一键安装 Aider / Open WebUI，用已配置的 Key

---

## 🆕 更新日志 / What's New

- 🔧 **替代工具安装** — 完成页面一键安装 Aider、Open WebUI
- 🗑 **Claude Code 卸载** — 系统页面可直接卸载 Claude Code
- 🌐 **自动语言检测** — 首次启动根据系统语言自动选择界面语言
- 🇨🇳 **DeepSeek 归类** — 移至国内模型分类
- 💡 **重启提醒** — 配置 API Key 后弹窗提醒重启终端

---

## 🌐 支持的语言 / Languages (6 UN Official)

| 语言 | Language |
|------|----------|
| 🇨🇳 中文 | Chinese |
| 🇬🇧 English | English |
| 🇫🇷 Français | French |
| 🇪🇸 Español | Spanish |
| 🇷🇺 Русский | Russian |
| 🇸🇦 العربية | Arabic |

首次启动自动检测系统语言，也可手动切换。详见 [i18n.py](i18n.py)。

---

## 📦 支持的提供商 / Providers (50+)

### 🌍 国际云平台 International Cloud (17)
Anthropic · OpenAI · Google Gemini · Azure OpenAI · Mistral · Cohere · Groq · Together AI · xAI Grok · Perplexity · Replicate · HuggingFace · Fireworks · Voyage AI · Jina AI · AI21 · NLP Cloud

### 🇨🇳 国内模型 Chinese Providers (13)
DeepSeek · 阿里云百炼(Qwen) · 百度千帆(ERNIE) · 智谱GLM · 月之暗面Kimi · MiniMax · 零一万物Yi · 百川Baichuan · 讯飞星火 · 腾讯混元 · 字节豆包 · 商汤日日新 · 昆仑万维Skywork

### 🏠 本地/开源 Local & Open Source (6)
Ollama · LM Studio · vLLM · LocalAI · Text Gen WebUI · OpenAI 兼容接口

### ⚡ 自定义 Custom (不限)
添加任意 API — 填写名称/环境变量/Key前缀/Base URL 即可。

---

## 🔧 替代工具 / Alternative Tools

不用 Anthropic 账号也能用已配置的 API Key：

| 工具 | 说明 | 安装 |
|------|------|------|
| **Aider** | 终端 AI 结对编程，支持 100+ 模型 | 完成页面一键安装 |
| **Open WebUI** | 自托管 ChatGPT 风格界面 | 完成页面一键安装 |

---

## 📁 项目结构 / Project Structure

```
AIOps-Deploy/
├── claude_deploy_gui.py   # GUI 主程序（向导式）
├── deploy_core.py         # 核心逻辑（安装/卸载/配置/连接测试）
├── providers.py           # 50+ 提供商数据库
├── i18n.py                # 6 种联合国语言翻译
├── launch.py              # 跨平台启动器
├── setup.sh / setup.ps1   # 一键启动脚本
├── install.sh / install.ps1  # CLI 备用脚本
├── build.py               # PyInstaller 打包脚本
├── requirements.txt       # 仅 pyinstaller
├── README.md              # 本文件
└── LICENSE                # MIT
```

---

## 🗑 如何删除 / How to Uninstall

### 卸载 Claude Code

**方法 1 (推荐)**: 在 GUI 系统页面点击 **🗑 卸载 Claude Code** 按钮
**方法 2**: 终端运行
```bash
npm uninstall -g @anthropic-ai/claude-code
```

### 删除 AIOps-Deploy 项目

```bash
rm -rf ~/AIOps-Deploy          # Linux / macOS / WSL
# Windows: 直接删除 AIOps-Deploy 文件夹
```

### 清除已保存的 API Key

```bash
# Linux / macOS — 编辑 shell 配置文件，删除包含 API Key 的行
nano ~/.bashrc                 # 或 ~/.zshrc / ~/.zprofile

# Windows — 在「系统属性 → 环境变量」中删除
# 或运行：setx ANTHROPIC_API_KEY ""
#         setx DEEPSEEK_API_KEY ""
#         ... 以此类推
```

### 清除工具配置数据

```bash
rm -rf ~/.ai-deploy/           # 删除语言设置、自定义提供商等
```

### 彻底清理（移除所有痕迹）

```bash
# 1) 卸载 Claude Code
npm uninstall -g @anthropic-ai/claude-code

# 2) 删除项目目录
rm -rf ~/AIOps-Deploy

# 3) 清理 shell 中的 API Key
# 编辑 ~/.bashrc 或 ~/.zshrc，删除 export *_API_KEY 开头的行

# 4) 清理配置
rm -rf ~/.ai-deploy/
```

---

## 🔧 打包为独立可执行文件

```bash
pip install pyinstaller
python build.py
# 输出: Windows: dist/AIDeploy.exe | macOS: dist/AIDeploy.app | Linux: dist/AIDeploy
```

---

## ❓ 常见问题 / FAQ

### GUI 无法启动 (Linux tkinter)

```bash
sudo apt install python3-tk        # Debian/Ubuntu
sudo dnf install python3-tkinter   # Fedora
```

### claude: command not found

```bash
export PATH="$(npm config get prefix)/bin:$PATH"
```

### API Key 保存后不生效

重启终端。Windows 上 `setx` 写入的变量需新终端窗口才生效。

### Claude Code 一定要 Anthropic Key 吗？

是的。没有的话可以跳过 Anthropic，用完成页面的替代工具（Aider 等）搭配其他 API Key。

### 如何添加不在列表中的提供商？

点击「⚡ 自定义」标签页 →「添加自定义」→ 填写表单 → 保存。持久化在 `~/.ai-deploy/custom_providers.json`。

---

## License

MIT © 2025
