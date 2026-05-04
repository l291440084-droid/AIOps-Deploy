# AI API 一键部署工具 / AI API One-Click Deploy

[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)](#)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](#)
[![Providers](https://img.shields.io/badge/providers-50+-orange.svg)](#)
[![Languages](https://img.shields.io/badge/languages-6%20UN-purple.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**可视化配置 50+ AI 模型 API Key，6 种联合国语言，一键部署 Claude Code。**

> Visual API key management for 50+ AI providers. 6 UN official languages. Cross-platform wizard.

---

## 🚀 快速开始 / Quick Start

### 从 GitHub 克隆自动打开（推荐）

```bash
# 第一步：从终端克隆项目（项目会自动启动安装向导）
git clone https://github.com/<your-username>/claude-deploy.git
cd claude-deploy
python3 launch.py          # Linux / macOS / Windows

# 也可以直接运行一键脚本：
bash setup.sh              # Linux / macOS
.\setup.ps1                # Windows PowerShell
```

### 启动后流程

1. **选择语言** — 6 种联合国语言（中文/English/Français/Español/Русский/العربية）
2. **选择安装目录** — 默认 npm 全局或自定义路径
3. **系统检测** — 自动检查 OS / Node.js / npm / Claude Code
4. **一键安装** — 自动安装 Claude Code CLI
5. **配置 API Key** — 50+ 提供商可视化卡片，点击即可配置
6. **完成** — 在终端运行 `claude` 开始使用

---

## 🌐 支持的语言 / Languages (6 UN Official)

| 语言 | Language |
|------|----------|
| 🇨🇳 中文 | Chinese (默认/default) |
| 🇬🇧 English | English |
| 🇫🇷 Français | French |
| 🇪🇸 Español | Spanish |
| 🇷🇺 Русский | Russian |
| 🇸🇦 العربية | Arabic |

语言在启动时选择，随时可在设置中切换。详见 [i18n.py](i18n.py)。

---

## 📦 支持的提供商 / Providers (50+)

### 🌍 国际云平台 International Cloud (18)
Anthropic · OpenAI · Google Gemini · Azure OpenAI · Mistral · Cohere · Groq · Together AI · xAI Grok · Perplexity · Replicate · HuggingFace · Fireworks · DeepSeek · Voyage AI · Jina AI · AI21 · NLP Cloud

### 🇨🇳 国内模型 Chinese Providers (12)
阿里云百炼(Qwen) · 百度千帆(ERNIE) · 智谱GLM · 月之暗面Kimi · MiniMax · 零一万物Yi · 百川Baichuan · 讯飞星火 · 腾讯混元 · 字节豆包 · 商汤日日新 · 昆仑万维Skywork

### 🏠 本地/开源 Local & Open Source (6)
Ollama · LM Studio · vLLM · LocalAI · Text Gen WebUI · OpenAI 兼容接口

### ⚡ 自定义 Custom (不限)
添加任意 API — 填写名称/环境变量/Key前缀/Base URL 即可。

---

## 📁 项目结构 / Project Structure

```
claude-deploy/
├── claude_deploy_gui.py   # GUI 主程序（向导式，500+ 行）
├── deploy_core.py         # 核心逻辑（安装/配置/连接测试）
├── providers.py           # 50+ 提供商数据库（可扩展）
├── i18n.py                # 6 种联合国语言翻译
├── launch.py              # 跨平台启动器（自动检测环境）
├── setup.sh               # Linux/macOS 一键启动脚本
├── setup.ps1              # Windows PowerShell 一键启动脚本
├── install.sh             # Linux/macOS CLI 备用脚本
├── install.ps1            # Windows CLI 备用脚本
├── build.py               # PyInstaller 打包脚本
├── requirements.txt       # 仅 pyinstaller
├── README.md              # 本文件
└── LICENSE                # MIT
```

---

## 🔧 打包为独立可执行文件

```bash
pip install pyinstaller
python build.py
# 输出:
#   Windows: dist/AIDeploy.exe
#   macOS:   dist/AIDeploy.app
#   Linux:   dist/AIDeploy
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

重启终端或执行 `source ~/.bashrc`。

### 如何添加不在列表中的提供商？

点击「⚡ 自定义」标签页 →「添加自定义」→ 填写表单 → 保存。数据持久化在 `~/.ai-deploy/custom_providers.json`。

---

## 📤 上传到 GitHub / Upload to GitHub

```bash
cd /home/one/claude-deploy
git init
git add -A
git commit -m "Initial release: AI API one-click deploy tool with 6 UN languages, 50+ providers"

# 在 GitHub 创建仓库后:
git remote add origin https://github.com/<your-username>/claude-deploy.git
git branch -M main
git push -u origin main
```

---

## 💡 改进建议 / Improvement Suggestions

1. **模型选择器** — 每个提供商卡片中增加具体模型选择和切换功能
2. **连接速度测试** — 测试各提供商的 API 响应延迟并排名
3. **用量统计** — 记录各 API 的调用次数和 token 消耗
4. **配置文件同步** — 支持导出/导入全量配置（加密），多设备同步
5. **Docker 部署** — 将 Claude Code + 依赖打包为 Docker 镜像
6. **自动更新** — 检测 GitHub Release 版本并自动更新提供商列表
7. **RTL 完整支持** — 阿拉伯语界面完整 RTL（从右到左）布局适配
8. **暗色模式** — Dark mode 主题支持
9. **CLI 多语言** — 将 install.sh/install.ps1 也国际化
10. **OAuth 登录** — 支持通过 OAuth 自动获取 API Key（减少手动复制）

## License

MIT © 2025
