#!/usr/bin/env python3
"""
AI Provider Database — 50+ providers across 4 categories.
Each provider defines its env var, key format, endpoints, and models.
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# ── Data structures ──────────────────────────────────────────────

@dataclass
class Provider:
    id: str                # unique slug
    name: str              # display name
    category: str          # international / china / local / custom
    env_var: str           # environment variable name
    key_prefix: str = ""   # expected prefix ("" = no validate)
    base_url: str = ""     # default API endpoint
    console_url: str = ""  # where to get the key
    models: list = field(default_factory=list)
    description: str = ""  # Chinese description
    icon: str = "🔧"       # emoji icon

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Provider":
        return cls(**{k: d.get(k, "") for k in [
            "id","name","category","env_var","key_prefix","base_url","console_url","models","description","icon"
        ]})

# ── Category definitions ─────────────────────────────────────────

CATEGORIES = {
    "international": {"name": "🌍 国际云平台 International Cloud", "order": 1},
    "china":        {"name": "🇨🇳 国内模型 Chinese Providers",     "order": 2},
    "local":        {"name": "🏠 本地/开源 Local & Open Source",  "order": 3},
    "custom":       {"name": "⚡ 自定义 Custom",                  "order": 4},
}

# ── All built-in providers ───────────────────────────────────────

PROVIDERS: list[Provider] = [
    # ── International Cloud ──────────────────────────────────────
    Provider(
        id="anthropic", name="Anthropic (Claude)", category="international",
        env_var="ANTHROPIC_API_KEY", key_prefix="sk-ant-",
        base_url="https://api.anthropic.com",
        console_url="https://console.anthropic.com/settings/keys",
        models=["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5"],
        description="Claude 系列模型，擅长长文本分析、编程和复杂推理", icon="🧠",
    ),
    Provider(
        id="openai", name="OpenAI", category="international",
        env_var="OPENAI_API_KEY", key_prefix="sk-",
        base_url="https://api.openai.com/v1",
        console_url="https://platform.openai.com/api-keys",
        models=["gpt-4.1", "gpt-4o", "gpt-4o-mini", "o4-mini", "o3"],
        description="GPT 系列模型，综合能力最强的通用大模型之一", icon="🔵",
    ),
    Provider(
        id="google", name="Google Gemini", category="international",
        env_var="GEMINI_API_KEY", key_prefix="AIza",
        base_url="https://generativelanguage.googleapis.com",
        console_url="https://aistudio.google.com/app/apikey",
        models=["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
        description="Google 多模态大模型，支持文本/图片/视频/音频", icon="🟢",
    ),
    Provider(
        id="azure", name="Azure OpenAI", category="international",
        env_var="AZURE_OPENAI_API_KEY", key_prefix="",
        base_url="https://{resource}.openai.azure.com",
        console_url="https://portal.azure.com",
        models=["gpt-4.1", "gpt-4o", "gpt-4o-mini"],
        description="微软 Azure 托管的 OpenAI 模型，企业级合规", icon="☁️",
    ),
    Provider(
        id="mistral", name="Mistral AI", category="international",
        env_var="MISTRAL_API_KEY", key_prefix="",
        base_url="https://api.mistral.ai/v1",
        console_url="https://console.mistral.ai/api-keys",
        models=["mistral-large-latest", "mistral-small-latest", "codestral-latest"],
        description="法国 AI 公司，开源模型先驱，模型轻量高效", icon="🔮",
    ),
    Provider(
        id="cohere", name="Cohere", category="international",
        env_var="COHERE_API_KEY", key_prefix="",
        base_url="https://api.cohere.ai/v2",
        console_url="https://dashboard.cohere.com/api-keys",
        models=["command-r-plus", "command-r", "command-a"],
        description="企业级 RAG 和检索优化模型，Embedding 能力强", icon="🟠",
    ),
    Provider(
        id="groq", name="Groq", category="international",
        env_var="GROQ_API_KEY", key_prefix="gsk_",
        base_url="https://api.groq.com/openai/v1",
        console_url="https://console.groq.com/keys",
        models=["llama-4-scout", "llama-4-maverick", "mixtral-8x7b", "gemma2-9b"],
        description="超快推理 LPU 芯片，支持 Llama/Mixtral 等开源模型", icon="⚡",
    ),
    Provider(
        id="together", name="Together AI", category="international",
        env_var="TOGETHER_API_KEY", key_prefix="",
        base_url="https://api.together.xyz/v1",
        console_url="https://api.together.ai/settings/api-keys",
        models=["llama-4-maverick", "deepseek-v3", "qwen3-235b", "stripedhyena"],
        description="开源模型托管平台，按量计费，覆盖主流开源模型", icon="🤝",
    ),
    Provider(
        id="xai", name="xAI Grok", category="international",
        env_var="XAI_API_KEY", key_prefix="xai-",
        base_url="https://api.x.ai/v1",
        console_url="https://x.ai/api",
        models=["grok-4", "grok-4-mini"],
        description="Elon Musk 旗下，Grok 系列模型，实时信息见长", icon="🚀",
    ),
    Provider(
        id="perplexity", name="Perplexity", category="international",
        env_var="PERPLEXITY_API_KEY", key_prefix="pplx-",
        base_url="https://api.perplexity.ai",
        console_url="https://www.perplexity.ai/settings/api",
        models=["sonar-pro", "sonar", "sonar-reasoning"],
        description="AI 搜索引擎，Sonar 模型支持联网搜索增强", icon="🔍",
    ),
    Provider(
        id="replicate", name="Replicate", category="international",
        env_var="REPLICATE_API_TOKEN", key_prefix="r8_",
        base_url="https://api.replicate.com/v1",
        console_url="https://replicate.com/account/api-tokens",
        models=["meta/llama-4-maverick", "deepseek-ai/deepseek-v3"],
        description="模型托管社区，支持数千个开源模型一键部署", icon="🐳",
    ),
    Provider(
        id="huggingface", name="HuggingFace", category="international",
        env_var="HF_TOKEN", key_prefix="hf_",
        base_url="https://api-inference.huggingface.co",
        console_url="https://huggingface.co/settings/tokens",
        models=["meta-llama/Llama-4", "Qwen/Qwen3", "deepseek-ai/DeepSeek-V3"],
        description="最大 AI 模型社区，Inference API 可直接调用模型", icon="🤗",
    ),
    Provider(
        id="fireworks", name="Fireworks AI", category="international",
        env_var="FIREWORKS_API_KEY", key_prefix="",
        base_url="https://api.fireworks.ai/inference/v1",
        console_url="https://fireworks.ai/account/api-keys",
        models=["llama-4-maverick", "qwen3-235b", "deepseek-v3", "mixtral-8x22b"],
        description="快速推理平台，开源模型优化，兼容 OpenAI API", icon="🎆",
    ),
    Provider(
        id="deepseek", name="DeepSeek", category="china",
        env_var="DEEPSEEK_API_KEY", key_prefix="sk-",
        base_url="https://api.deepseek.com/v1",
        console_url="https://platform.deepseek.com/api_keys",
        models=["deepseek-v3", "deepseek-r1", "deepseek-coder"],
        description="国产开源旗舰模型，编码和推理能力极强，性价比高", icon="🐋",
    ),
    Provider(
        id="voyage", name="Voyage AI", category="international",
        env_var="VOYAGE_API_KEY", key_prefix="",
        base_url="https://api.voyageai.com/v1",
        console_url="https://dash.voyageai.com/api-keys",
        models=["voyage-3-large", "voyage-3", "voyage-3-lite", "voyage-code-3"],
        description="专注 Embedding 和 Reranking 的向量模型", icon="🧭",
    ),
    Provider(
        id="jina", name="Jina AI", category="international",
        env_var="JINA_API_KEY", key_prefix="jina_",
        base_url="https://api.jina.ai/v1",
        console_url="https://jina.ai/embeddings",
        models=["jina-embeddings-v3", "jina-clip-v2", "jina-reranker-v2"],
        description="多模态 Embedding 和 Reranker，支持长文本", icon="🔴",
    ),
    Provider(
        id="ai21", name="AI21 Labs", category="international",
        env_var="AI21_API_KEY", key_prefix="",
        base_url="https://api.ai21.com/studio/v1",
        console_url="https://studio.ai21.com/account/api-keys",
        models=["jamba-1.6-large", "jamba-1.6-mini"],
        description="Jamba 系列 SSM-Transformer 混合架构模型", icon="🧪",
    ),
    Provider(
        id="nlpcloud", name="NLP Cloud", category="international",
        env_var="NLPCLOUD_API_KEY", key_prefix="",
        base_url="https://api.nlpcloud.io/v1",
        console_url="https://nlpcloud.com/home/token",
        models=["dolphin-mixtral", "llama-4", "chatdolphin"],
        description="欧洲 AI API 平台，支持多种开源模型微调", icon="☁️",
    ),

    # ── Chinese Providers ────────────────────────────────────────
    Provider(
        id="dashscope", name="阿里云百炼 (Qwen)", category="china",
        env_var="DASHSCOPE_API_KEY", key_prefix="sk-",
        base_url="https://dashscope.aliyuncs.com/api/v1",
        console_url="https://dashscope.console.aliyun.com/apiKey",
        models=["qwen3-235b", "qwen3-32b", "qwen3-8b", "qwen-coder-plus", "qwen-vl-max"],
        description="通义千问 Qwen3 系列，阿里自研旗舰开源模型", icon="🐲",
    ),
    Provider(
        id="qianfan", name="百度千帆", category="china",
        env_var="QIANFAN_API_KEY", key_prefix="",
        base_url="https://qianfan.baidubce.com/v2",
        console_url="https://console.bce.baidu.com/qianfan/overview",
        models=["ernie-4.5", "ernie-4.5-turbo", "ernie-speed", "ernie-char"],
        description="文心一言 ERNIE 系列，中文理解和生成能力突出", icon="🔵",
    ),
    Provider(
        id="zhipu", name="智谱 GLM", category="china",
        env_var="ZHIPUAI_API_KEY", key_prefix="",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        console_url="https://open.bigmodel.cn/usercenter/apikeys",
        models=["glm-5", "glm-5-flash", "glm-5-plus", "cogview-4"],
        description="GLM 系列，清华系团队，多模态和 Agent 能力强", icon="🎓",
    ),
    Provider(
        id="moonshot", name="月之暗面 Kimi", category="china",
        env_var="MOONSHOT_API_KEY", key_prefix="sk-",
        base_url="https://api.moonshot.cn/v1",
        console_url="https://platform.moonshot.cn/console/api-keys",
        models=["kimi-k2", "moonshot-v1-auto", "kimi-thinking"],
        description="Kimi K2，超长上下文（128K-1M tokens）和深度推理", icon="🌙",
    ),
    Provider(
        id="minimax", name="MiniMax", category="china",
        env_var="MINIMAX_API_KEY", key_prefix="",
        base_url="https://api.minimax.chat/v1",
        console_url="https://platform.minimax.io/user-center/basic-information",
        models=["abab7", "abab6.5s", "speech-02", "video-01"],
        description="ABAB 系列，语音合成和视频生成多模态能力", icon="🎵",
    ),
    Provider(
        id="yi", name="零一万物 Yi", category="china",
        env_var="YI_API_KEY", key_prefix="",
        base_url="https://api.lingyiwanwu.com/v1",
        console_url="https://platform.lingyiwanwu.com/apikeys",
        models=["yi-lightning", "yi-large", "yi-medium", "yi-vision"],
        description="Yi 系列开源模型，李开复团队，中英双语优化", icon="⚪",
    ),
    Provider(
        id="baichuan", name="百川 Baichuan", category="china",
        env_var="BAICHUAN_API_KEY", key_prefix="sk-",
        base_url="https://api.baichuan-ai.com/v1",
        console_url="https://platform.baichuan-ai.com/console/apikey",
        models=["baichuan4", "baichuan4-turbo", "baichuan4-air"],
        description="百川系列，王小川团队，中文医疗和法律领域见长", icon="💧",
    ),
    Provider(
        id="spark", name="讯飞星火 Spark", category="china",
        env_var="SPARK_API_KEY", key_prefix="",
        base_url="https://spark-api-open.xf-yun.com/v1",
        console_url="https://console.xfyun.cn/services/spark",
        models=["spark-4.0-ultra", "spark-4.0", "spark-lite"],
        description="星火认知大模型，讯飞语音 AI 技术积累", icon="✨",
    ),
    Provider(
        id="hunyuan", name="腾讯混元", category="china",
        env_var="HUNYUAN_API_KEY", key_prefix="",
        base_url="https://hunyuanapi.woa.com/openapi/v1",
        console_url="https://hunyuan.tencent.com",
        models=["hunyuan-turbos", "hunyuan-standard", "hunyuan-vision"],
        description="腾讯混元大模型，微信生态深度集成", icon="💬",
    ),
    Provider(
        id="doubao", name="字节豆包 Doubao", category="china",
        env_var="DOUBAO_API_KEY", key_prefix="",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        console_url="https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey",
        models=["doubao-pro-256k", "doubao-lite-128k", "doubao-vision-pro"],
        description="火山引擎豆包模型，超长上下文 256K", icon="🫘",
    ),
    Provider(
        id="sensenova", name="商汤日日新 SenseNova", category="china",
        env_var="SENSENOVA_API_KEY", key_prefix="",
        base_url="https://api.sensenova.cn/v1",
        console_url="https://platform.sensenova.cn",
        models=["sensechat-5", "sensechat-5-vision", "sensechat-turbo"],
        description="商汤日日新大模型，计算机视觉 + 多模态", icon="👁️",
    ),
    Provider(
        id="skywork", name="昆仑万维 Skywork", category="china",
        env_var="SKYWORK_API_KEY", key_prefix="",
        base_url="https://api.skywork.ai/v1",
        console_url="https://skywork.ai",
        models=["skywork-4.0", "skywork-4.0-mini", "skymusic-2.0"],
        description="Skywork 天工大模型，昆仑万维全模态 AI", icon="🌌",
    ),

    # ── Local / Open Source ──────────────────────────────────────
    Provider(
        id="ollama", name="Ollama", category="local",
        env_var="OLLAMA_HOST", key_prefix="",
        base_url="http://localhost:11434",
        console_url="https://ollama.com/search",
        models=["llama4", "qwen3", "deepseek-v3", "mistral", "gemma3", "phi-4"],
        description="本地运行大模型的最简单方式，一键下载运行开源模型", icon="🦙",
    ),
    Provider(
        id="lmstudio", name="LM Studio", category="local",
        env_var="LMSTUDIO_HOST", key_prefix="",
        base_url="http://localhost:1234/v1",
        console_url="https://lmstudio.ai",
        models=["llama-4", "qwen3", "deepseek-v3", "mistral", "phi-4"],
        description="桌面端本地模型运行器，GUI 管理模型，兼容 OpenAI API", icon="💻",
    ),
    Provider(
        id="vllm", name="vLLM", category="local",
        env_var="VLLM_HOST", key_prefix="",
        base_url="http://localhost:8000/v1",
        console_url="https://docs.vllm.ai",
        models=["任意开源模型 / Any open-source model"],
        description="高性能 LLM 推理引擎，PagedAttention 加速，生产级部署", icon="🏎️",
    ),
    Provider(
        id="localai", name="LocalAI", category="local",
        env_var="LOCALAI_HOST", key_prefix="",
        base_url="http://localhost:8080/v1",
        console_url="https://localai.io",
        models=["任意模型 / Any model (gguf format)"],
        description="一站式本地 AI 平台，支持 LLM/Image/Audio/Embedding", icon="🏠",
    ),
    Provider(
        id="textgen", name="Text Gen WebUI", category="local",
        env_var="TEXTGEN_HOST", key_prefix="",
        base_url="http://localhost:5000/v1",
        console_url="https://github.com/oobabooga/text-generation-webui",
        models=["任意模型 / Any HuggingFace model"],
        description="Oobabooga WebUI，社区流行的本地模型交互界面", icon="🖥️",
    ),
    Provider(
        id="openai_compat", name="OpenAI 兼容接口", category="local",
        env_var="OPENAI_API_KEY", key_prefix="",
        base_url="http://localhost:8000/v1",
        console_url="",
        models=["取决于自建服务 / Depends on your server"],
        description="兼容 OpenAI API 格式的任意自建服务，可自定义 Base URL", icon="🔌",
    ),
]

# ── Custom providers persistence ─────────────────────────────────

_CONFIG_DIR = Path.home() / ".ai-deploy"
_CUSTOM_FILE = _CONFIG_DIR / "custom_providers.json"

def _ensure_config_dir():
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_custom_providers() -> list[Provider]:
    """Load user-defined custom providers from disk."""
    if not _CUSTOM_FILE.exists():
        return []
    try:
        data = json.loads(_CUSTOM_FILE.read_text())
        return [Provider.from_dict(d) for d in data]
    except Exception:
        return []

def save_custom_provider(provider: Provider) -> bool:
    """Add or update a custom provider persistently."""
    _ensure_config_dir()
    custom = load_custom_providers()
    # Update if exists, else append
    for i, p in enumerate(custom):
        if p.id == provider.id:
            custom[i] = provider
            break
    else:
        custom.append(provider)
    try:
        _CUSTOM_FILE.write_text(
            json.dumps([p.to_dict() for p in custom], ensure_ascii=False, indent=2)
        )
        return True
    except Exception:
        return False

def delete_custom_provider(provider_id: str) -> bool:
    """Remove a custom provider."""
    custom = load_custom_providers()
    new_list = [p for p in custom if p.id != provider_id]
    if len(new_list) == len(custom):
        return False  # Nothing removed
    _ensure_config_dir()
    try:
        _CUSTOM_FILE.write_text(
            json.dumps([p.to_dict() for p in new_list], ensure_ascii=False, indent=2)
        )
        return True
    except Exception:
        return False

def get_all_providers() -> list[Provider]:
    """Get built-in + custom providers."""
    return PROVIDERS + load_custom_providers()

def get_provider(provider_id: str) -> Optional[Provider]:
    """Find a provider by ID."""
    for p in get_all_providers():
        if p.id == provider_id:
            return p
    return None

def get_providers_by_category(category: str) -> list[Provider]:
    """Filter providers by category."""
    return [p for p in get_all_providers() if p.category == category]

def scan_configured_providers() -> dict[str, bool]:
    """Return which providers have their env var set in current process."""
    result = {}
    for p in get_all_providers():
        result[p.id] = bool(os.environ.get(p.env_var, ""))
    return result

def get_configured_summary() -> dict:
    """Return summary of all providers and their config status."""
    configured = scan_configured_providers()
    cats = {}
    for p in get_all_providers():
        cat = p.category
        if cat not in cats:
            cats[cat] = {"total": 0, "configured": 0, "providers": []}
        cats[cat]["total"] += 1
        if configured.get(p.id):
            cats[cat]["configured"] += 1
        cats[cat]["providers"].append({
            "id": p.id, "name": p.name, "icon": p.icon,
            "configured": configured.get(p.id, False),
        })
    return {
        "categories": cats,
        "total": sum(c["total"] for c in cats.values()),
        "configured": sum(c["configured"] for c in cats.values()),
    }
