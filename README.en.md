# AIOps Deploy

[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)](#)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](#)
[![Providers](https://img.shields.io/badge/providers-50+-orange.svg)](#)
[![Languages](https://img.shields.io/badge/languages-6%20UN-purple.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**One-click deploy Claude Code. Visually manage API keys for 50+ AI providers. Cross-platform GUI wizard.**

---

## Quick Start

### Clone & Run (recommended)

```bash
git clone https://github.com/l291440084-droid/AIOps-Deploy.git
cd AIOps-Deploy
python3 launch.py          # Linux / macOS / Windows

# Or use the one-liner:
bash setup.sh              # Linux / macOS
.\setup.ps1                # Windows PowerShell
```

### Download without git

Download the [latest release](https://github.com/l291440084-droid/AIOps-Deploy/releases) ZIP, extract, then:

```bash
cd AIOps-Deploy
python3 launch.py
```

### What happens next

1. **Pick a language** — choose from 6 UN official languages
2. **Choose install directory** — default npm global or custom path
3. **System check** — auto-detects OS, Node.js, npm; **auto-installs** missing dependencies
4. **Configure API keys** — visual provider cards, click to set up
5. **Done** — run `claude` in your terminal and start using

---

## Languages (6 UN Official)

| Flag | Language | Status |
|------|----------|--------|
| 🇨🇳 | Chinese | Default |
| 🇬🇧 | English | Full |
| 🇫🇷 | Français | Full |
| 🇪🇸 | Español | Full |
| 🇷🇺 | Русский | Full |
| 🇸🇦 | العربية | Full (RTL) |

Select at launch, switch anytime in settings. See [i18n.py](i18n.py).

---

## Supported Providers (50+)

### International Cloud (18)
Anthropic · OpenAI · Google Gemini · Azure OpenAI · Mistral · Cohere · Groq · Together AI · xAI Grok · Perplexity · Replicate · HuggingFace · Fireworks · DeepSeek · Voyage AI · Jina AI · AI21 · NLP Cloud

### Chinese Providers (12)
Alibaba Qwen · Baidu Qianfan · Zhipu GLM · Moonshot Kimi · MiniMax · Lingyi Yi · Baichuan · iFlytek Spark · Tencent Hunyuan · ByteDance Doubao · SenseNova · Skywork

### Local & Open Source (6)
Ollama · LM Studio · vLLM · LocalAI · Text Generation WebUI · OpenAI-compatible endpoint

### Custom (unlimited)
Add any API — fill in name, environment variable, key prefix, and base URL.

---

## Features

- **Auto-install** — detects missing Node.js and installs it automatically (apt, brew, winget, or nvm)
- **Key validation** — checks key format per provider before saving
- **Connection test** — test any API key with one click
- **Export** — export all configured keys as `.env` file
- **Custom providers** — add your own API endpoints, persisted to disk
- **No dependencies** — uses only Python stdlib + tkinter, nothing to pip install

---

## Project Structure

```
AIOps-Deploy/
├── claude_deploy_gui.py   # GUI wizard (tkinter)
├── deploy_core.py         # Core logic (install, configure, test)
├── providers.py           # 50+ provider database
├── i18n.py                # 6-language translations (101 keys)
├── launch.py              # Cross-platform launcher
├── setup.sh / setup.ps1   # One-click setup scripts
├── install.sh / install.ps1  # CLI fallback scripts
├── build.py               # PyInstaller packager
├── requirements.txt       # pyinstaller only
├── README.md / README.en.md
└── LICENSE                # MIT
```

---

## Build Standalone Executable

```bash
pip install pyinstaller
python build.py
# Output:
#   Windows: dist/AIDeploy.exe
#   macOS:   dist/AIDeploy.app
#   Linux:   dist/AIDeploy
```

---

## FAQ

### GUI won't start (Linux tkinter)

```bash
sudo apt install python3-tk        # Debian/Ubuntu
sudo dnf install python3-tkinter   # Fedora
```

### "claude: command not found"

```bash
export PATH="$(npm config get prefix)/bin:$PATH"
# Add this line to your ~/.bashrc or ~/.zshrc to make it permanent
```

### API key not taking effect

Restart your terminal or run `source ~/.bashrc` (or `~/.zshrc`).

### Adding a provider not in the list

Click the **Custom** tab → **Add Custom** → fill the form → Save. Data persists at `~/.ai-deploy/custom_providers.json`.

---

## Roadmap

- [ ] Model selector within each provider card
- [ ] Connection latency benchmarking
- [ ] Usage & token tracking dashboard
- [ ] Encrypted config export/import for multi-device sync
- [ ] Docker image bundling
- [ ] GitHub release auto-updater
- [ ] Full RTL layout for Arabic
- [ ] Dark mode theme
- [ ] OAuth-based API key retrieval

---

## License

MIT © 2025
