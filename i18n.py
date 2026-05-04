#!/usr/bin/env python3
"""
Internationalization module — 6 UN official languages.
Arabic, Chinese, English, French, Russian, Spanish.

Usage:
    from i18n import _, set_language, LANGUAGES
    set_language('zh')
    print(_('welcome_title'))
"""

import json
import os
from pathlib import Path

# ── Language definitions ─────────────────────────────────────────

LANGUAGES = {
    "en": {"name": "English",           "native": "English",            "flag": "🇬🇧", "dir": "ltr"},
    "zh": {"name": "Chinese",           "native": "中文",               "flag": "🇨🇳", "dir": "ltr"},
    "fr": {"name": "French",            "native": "Français",           "flag": "🇫🇷", "dir": "ltr"},
    "es": {"name": "Spanish",           "native": "Español",            "flag": "🇪🇸", "dir": "ltr"},
    "ru": {"name": "Russian",           "native": "Русский",           "flag": "🇷🇺", "dir": "ltr"},
    "ar": {"name": "Arabic",            "native": "العربية",           "flag": "🇸🇦", "dir": "rtl"},
}

_current_lang = "zh"
_config_dir = Path.home() / ".ai-deploy"
_config_file = _config_dir / "config.json"


def set_language(lang: str):
    global _current_lang
    if lang in LANGUAGES:
        _current_lang = lang
        _config_dir.mkdir(parents=True, exist_ok=True)
        try:
            cfg = json.loads(_config_file.read_text()) if _config_file.exists() else {}
        except Exception:
            cfg = {}
        cfg["language"] = lang
        _config_file.write_text(json.dumps(cfg, indent=2))


def get_language() -> str:
    return _current_lang


def get_dir() -> str:
    return LANGUAGES.get(_current_lang, {}).get("dir", "ltr")


def load_language():
    """Restore saved language preference."""
    global _current_lang
    try:
        if _config_file.exists():
            cfg = json.loads(_config_file.read_text())
            saved = cfg.get("language", "")
            if saved in LANGUAGES:
                _current_lang = saved
    except Exception:
        pass

# Load saved language on import
load_language()


# ── Translation strings ─────────────────────────────────────────
# Key format: lower_snake_case
# Each key maps to a dict with language codes.

STRINGS = {
    # ── App title & branding ────────────────────────────────────
    "app_title": {
        "en": "AI API One-Click Deploy Tool",
        "zh": "AI API 一键部署工具",
        "fr": "Outil de Déploiement API IA en Un Clic",
        "es": "Herramienta de Implementación API IA en Un Clic",
        "ru": "Инструмент Развертывания AI API в Один Клик",
        "ar": "أداة نشر API للذكاء الاصطناعي بنقرة واحدة",
    },
    "app_subtitle": {
        "en": "Visual API Key Management for 50+ AI Providers",
        "zh": "50+ AI 模型 API Key 可视化管理",
        "fr": "Gestion Visuelle des Clés API pour 50+ Fournisseurs IA",
        "es": "Gestión Visual de Claves API para 50+ Proveedores IA",
        "ru": "Визуальное Управление API Ключами для 50+ ИИ Провайдеров",
        "ar": "إدارة مرئية لمفاتيح API لأكثر من ٥٠ مزود ذكاء اصطناعي",
    },

    # ── Language selection ──────────────────────────────────────
    "lang_title": {
        "en": "Select Language / 选择语言",
        "zh": "选择语言 / Select Language",
        "fr": "Choisir la Langue / Select Language",
        "es": "Seleccionar Idioma / Select Language",
        "ru": "Выберите Язык / Select Language",
        "ar": "اختر اللغة / Select Language",
    },
    "lang_prompt": {
        "en": "Choose your preferred language to continue:",
        "zh": "选择您偏好的语言以继续：",
        "fr": "Choisissez votre langue préférée pour continuer:",
        "es": "Elija su idioma preferido para continuar:",
        "ru": "Выберите предпочитаемый язык для продолжения:",
        "ar": "اختر لغتك المفضلة للمتابعة:",
    },
    "lang_saved": {
        "en": "Language set to English ✓",
        "zh": "语言已设置为中文 ✓",
        "fr": "Langue définie sur Français ✓",
        "es": "Idioma establecido en Español ✓",
        "ru": "Язык установлен на Русский ✓",
        "ar": "تم تعيين اللغة إلى العربية ✓",
    },

    # ── Directory selection ─────────────────────────────────────
    "dir_title": {
        "en": "Select Installation Directory",
        "zh": "选择安装目录",
        "fr": "Choisir le Dossier d'Installation",
        "es": "Seleccionar Directorio de Instalación",
        "ru": "Выберите Директорию Установки",
        "ar": "اختر مجلد التثبيت",
    },
    "dir_default": {
        "en": "Default (system npm global)",
        "zh": "默认（系统 npm 全局）",
        "fr": "Par Défaut (npm global système)",
        "es": "Por Defecto (npm global del sistema)",
        "ru": "По Умолчанию (системный npm global)",
        "ar": "الافتراضي (npm عمومي النظام)",
    },
    "dir_custom": {
        "en": "Custom directory",
        "zh": "自定义目录",
        "fr": "Dossier personnalisé",
        "es": "Directorio personalizado",
        "ru": "Пользовательская директория",
        "ar": "مجلد مخصص",
    },
    "dir_browse": {
        "en": "Browse...",
        "zh": "浏览...",
        "fr": "Parcourir...",
        "es": "Examinar...",
        "ru": "Обзор...",
        "ar": "تصفح...",
    },
    "dir_label": {
        "en": "Installation path (npm prefix):",
        "zh": "安装路径（npm prefix）:",
        "fr": "Chemin d'installation (npm prefix):",
        "es": "Ruta de instalación (npm prefix):",
        "ru": "Путь установки (npm prefix):",
        "ar": "مسار التثبيت (npm prefix):",
    },
    "dir_hint": {
        "en": "Claude Code CLI will be installed here. Choose a writable location.",
        "zh": "Claude Code CLI 将安装到此位置。请选择可写入的目录。",
        "fr": "Claude Code CLI sera installé ici. Choisissez un emplacement accessible.",
        "es": "Claude Code CLI se instalará aquí. Elija una ubicación escribible.",
        "ru": "Claude Code CLI будет установлен сюда. Выберите доступное для записи место.",
        "ar": "سيتم تثبيت Claude Code CLI هنا. اختر موقعًا قابلاً للكتابة.",
    },

    # ── System check steps ──────────────────────────────────────
    "step_os": {
        "en": "System Detection",
        "zh": "系统检测",
        "fr": "Détection du Système",
        "es": "Detección del Sistema",
        "ru": "Определение Системы",
        "ar": "اكتشاف النظام",
    },
    "step_node": {
        "en": "Node.js Check",
        "zh": "Node.js 环境检查",
        "fr": "Vérification Node.js",
        "es": "Verificación Node.js",
        "ru": "Проверка Node.js",
        "ar": "فحص Node.js",
    },
    "step_npm": {
        "en": "npm Check",
        "zh": "npm 检查",
        "fr": "Vérification npm",
        "es": "Verificación npm",
        "ru": "Проверка npm",
        "ar": "فحص npm",
    },
    "step_install": {
        "en": "Install Claude Code",
        "zh": "安装 Claude Code CLI",
        "fr": "Installer Claude Code",
        "es": "Instalar Claude Code",
        "ru": "Установка Claude Code",
        "ar": "تثبيت Claude Code",
    },
    "step_apikey": {
        "en": "Configure API Keys",
        "zh": "配置 API Key",
        "fr": "Configurer les Clés API",
        "es": "Configurar Claves API",
        "ru": "Настройка API Ключей",
        "ar": "تكوين مفاتيح API",
    },
    "step_verify": {
        "en": "Verify Installation",
        "zh": "验证安装",
        "fr": "Vérifier l'Installation",
        "es": "Verificar Instalación",
        "ru": "Проверка Установки",
        "ar": "التحقق من التثبيت",
    },

    # ── Guidance text per step ──────────────────────────────────
    "guide_os_title": {
        "en": "What is this step?",
        "zh": "这一步做什么？",
        "fr": "Que fait cette étape?",
        "es": "¿Qué hace este paso?",
        "ru": "Что делает этот шаг?",
        "ar": "ماذا تفعل هذه الخطوة؟",
    },
    "guide_os_desc": {
        "en": "We detect your operating system (Windows/macOS/Linux) and architecture to choose the correct installation method.",
        "zh": "检测您的操作系统（Windows/macOS/Linux）和架构，以选择正确的安装方式。",
        "fr": "Nous détectons votre système d'exploitation (Windows/macOS/Linux) pour choisir la bonne méthode.",
        "es": "Detectamos su sistema operativo (Windows/macOS/Linux) para elegir el método correcto.",
        "ru": "Мы определяем вашу ОС (Windows/macOS/Linux) и архитектуру для выбора правильного метода.",
        "ar": "نكتشف نظام التشغيل الخاص بك (Windows/macOS/Linux) لاختيار طريقة التثبيت الصحيحة.",
    },
    "guide_node_title": {
        "en": "Why Node.js?",
        "zh": "为什么需要 Node.js？",
        "fr": "Pourquoi Node.js?",
        "es": "¿Por qué Node.js?",
        "ru": "Зачем нужен Node.js?",
        "ar": "لماذا Node.js؟",
    },
    "guide_node_desc": {
        "en": "Claude Code CLI is distributed via npm (Node Package Manager). Node.js >= 18 is required. If not installed, we'll guide you through the setup.",
        "zh": "Claude Code CLI 通过 npm 分发，需要 Node.js >= 18。如果未安装，将指导您完成安装。",
        "fr": "Claude Code CLI est distribué via npm. Node.js >= 18 est requis. Si absent, nous vous guiderons.",
        "es": "Claude Code CLI se distribuye via npm. Requiere Node.js >= 18. Si no está, le guiaremos.",
        "ru": "Claude Code CLI распространяется через npm. Требуется Node.js >= 18. Если нет — поможем установить.",
        "ar": "يتم توزيع Claude Code CLI عبر npm. يتطلب Node.js >= 18. إذا لم يكن مثبتًا، سنرشدك.",
    },
    "guide_install_title": {
        "en": "What's being installed?",
        "zh": "正在安装什么？",
        "fr": "Qu'est-ce qui est installé?",
        "es": "¿Qué se está instalando?",
        "ru": "Что устанавливается?",
        "ar": "ماذا يتم تثبيته؟",
    },
    "guide_install_desc": {
        "en": "We run: npm install -g @anthropic-ai/claude-code\nThis downloads the Claude Code CLI tool to your system so you can run 'claude' from any terminal.",
        "zh": "运行: npm install -g @anthropic-ai/claude-code\n将 Claude Code CLI 安装到系统中，之后可在任意终端运行 claude。",
        "fr": "Nous exécutons: npm install -g @anthropic-ai/claude-code\nInstalle l'outil CLI Claude Code pour l'utiliser dans n'importe quel terminal.",
        "es": "Ejecutamos: npm install -g @anthropic-ai/claude-code\nInstala Claude Code CLI en su sistema.",
        "ru": "Запускаем: npm install -g @anthropic-ai/claude-code\nУстанавливает Claude Code CLI для использования из любого терминала.",
        "ar": "نشغل: npm install -g @anthropic-ai/claude-code\nيثبت أداة Claude Code CLI على نظامك.",
    },
    "guide_apikey_title": {
        "en": "Setting up API Keys",
        "zh": "设置 API Key",
        "fr": "Configuration des Clés API",
        "es": "Configuración de Claves API",
        "ru": "Настройка API Ключей",
        "ar": "إعداد مفاتيح API",
    },
    "guide_apikey_desc": {
        "en": "Click any provider card to add its API key. Keys are saved to your shell profile and persist across restarts. You can configure multiple providers.",
        "zh": "点击任意提供商卡片添加 API Key。密钥保存在 shell profile 中，重启后仍然有效。可配置多个提供商。",
        "fr": "Cliquez sur une carte fournisseur pour ajouter sa clé API. Les clés sont enregistrées dans le profil shell.",
        "es": "Haga clic en cualquier tarjeta para agregar su clave API. Las claves se guardan en el perfil de shell.",
        "ru": "Нажмите на карточку провайдера чтобы добавить API ключ. Ключи сохраняются в профиле оболочки.",
        "ar": "انقر على بطاقة أي مزود لإضافة مفتاح API الخاص به. يتم حفظ المفاتيح في ملف تعريف الصدفة.",
    },

    # ── Buttons ──────────────────────────────────────────────────
    "btn_install": {
        "en": "Install All",
        "zh": "一键安装",
        "fr": "Tout Installer",
        "es": "Instalar Todo",
        "ru": "Установить Всё",
        "ar": "تثبيت الكل",
    },
    "btn_retry": {
        "en": "Retry",
        "zh": "重试",
        "fr": "Réessayer",
        "es": "Reintentar",
        "ru": "Повторить",
        "ar": "إعادة المحاولة",
    },
    "btn_cancel": {
        "en": "Cancel",
        "zh": "取消",
        "fr": "Annuler",
        "es": "Cancelar",
        "ru": "Отмена",
        "ar": "إلغاء",
    },
    "btn_exit": {
        "en": "Exit",
        "zh": "退出",
        "fr": "Quitter",
        "es": "Salir",
        "ru": "Выход",
        "ar": "خروج",
    },
    "btn_save": {
        "en": "Save",
        "zh": "保存",
        "fr": "Enregistrer",
        "es": "Guardar",
        "ru": "Сохранить",
        "ar": "حفظ",
    },
    "btn_skip": {
        "en": "Skip",
        "zh": "跳过",
        "fr": "Passer",
        "es": "Omitir",
        "ru": "Пропустить",
        "ar": "تخطي",
    },
    "btn_next": {
        "en": "Next →",
        "zh": "下一步 →",
        "fr": "Suivant →",
        "es": "Siguiente →",
        "ru": "Далее →",
        "ar": "→ التالي",
    },
    "btn_back": {
        "en": "← Back",
        "zh": "← 上一步",
        "fr": "← Retour",
        "es": "← Atrás",
        "ru": "← Назад",
        "ar": "→ رجوع",
    },
    "btn_configure": {
        "en": "Configure",
        "zh": "配置",
        "fr": "Configurer",
        "es": "Configurar",
        "ru": "Настроить",
        "ar": "تكوين",
    },
    "btn_reconfig": {
        "en": "Reconfig",
        "zh": "重配",
        "fr": "Reconfig.",
        "es": "Reconf.",
        "ru": "Перенастр.",
        "ar": "إعادة",
    },
    "btn_delete": {
        "en": "Delete",
        "zh": "删除",
        "fr": "Supprimer",
        "es": "Eliminar",
        "ru": "Удалить",
        "ar": "حذف",
    },
    "btn_test": {
        "en": "Test Connection",
        "zh": "测试连接",
        "fr": "Tester Connexion",
        "es": "Probar Conexión",
        "ru": "Проверить Связь",
        "ar": "اختبار الاتصال",
    },
    "btn_export": {
        "en": "Export .env",
        "zh": "导出 .env",
        "fr": "Exporter .env",
        "es": "Exportar .env",
        "ru": "Экспорт .env",
        "ar": "تصدير .env",
    },
    "btn_custom": {
        "en": "Add Custom",
        "zh": "添加自定义",
        "fr": "Ajouter Perso.",
        "es": "Añadir Pers.",
        "ru": "Добавить",
        "ar": "إضافة مخصص",
    },
    "btn_refresh": {
        "en": "Refresh",
        "zh": "刷新",
        "fr": "Actualiser",
        "es": "Actualizar",
        "ru": "Обновить",
        "ar": "تحديث",
    },
    "btn_console": {
        "en": "Show Console",
        "zh": "显示输出",
        "fr": "Afficher Console",
        "es": "Mostrar Consola",
        "ru": "Показать Консоль",
        "ar": "إظهار وحدة التحكم",
    },

    # ── Status ──────────────────────────────────────────────────
    "status_ready": {
        "en": "Ready — Click a provider card to configure API keys",
        "zh": "就绪 — 点击提供商卡片配置 API Key",
        "fr": "Prêt — Cliquez sur une carte pour configurer",
        "es": "Listo — Haga clic en tarjeta para configurar",
        "ru": "Готово — Нажмите на карточку для настройки",
        "ar": "جاهز — انقر على بطاقة مزود لتكوين مفاتيح API",
    },
    "status_scanning": {
        "en": "Scanning system environment...",
        "zh": "正在检测系统环境...",
        "fr": "Analyse de l'environnement système...",
        "es": "Analizando entorno del sistema...",
        "ru": "Сканирование системного окружения...",
        "ar": "جاري فحص بيئة النظام...",
    },
    "status_installing": {
        "en": "Installing Claude Code via npm...",
        "zh": "正在通过 npm 安装 Claude Code...",
        "fr": "Installation de Claude Code via npm...",
        "es": "Instalando Claude Code via npm...",
        "ru": "Установка Claude Code через npm...",
        "ar": "جاري تثبيت Claude Code عبر npm...",
    },
    "status_complete": {
        "en": "Installation complete! Restart terminal and run: claude",
        "zh": "安装完成！重启终端后运行: claude",
        "fr": "Installation terminée! Redémarrez le terminal: claude",
        "es": "¡Instalación completa! Reinicie terminal: claude",
        "ru": "Установка завершена! Перезапустите терминал: claude",
        "ar": "اكتمل التثبيت! أعد تشغيل الطرفية: claude",
    },
    "status_configured": {
        "en": "✓ Configured",
        "zh": "✓ 已配置",
        "fr": "✓ Configuré",
        "es": "✓ Configurado",
        "ru": "✓ Настроено",
        "ar": "✓ تم التكوين",
    },
    "status_not_configured": {
        "en": "Click to configure",
        "zh": "点击配置",
        "fr": "Cliquer pour configurer",
        "es": "Clic para configurar",
        "ru": "Нажмите для настройки",
        "ar": "انقر للتكوين",
    },

    # ── System bar ──────────────────────────────────────────────
    "sys_os": {
        "en": "System",
        "zh": "系统",
        "fr": "Système",
        "es": "Sistema",
        "ru": "Система",
        "ar": "النظام",
    },
    "sys_claude_not_installed": {
        "en": "Claude: Not installed",
        "zh": "Claude: 未安装",
        "fr": "Claude: Non installé",
        "es": "Claude: No instalado",
        "ru": "Claude: Не установлен",
        "ar": "Claude: غير مثبت",
    },

    # ── Errors ──────────────────────────────────────────────────
    "err_node_missing": {
        "en": "Node.js is not installed. Install Node.js >= 18.",
        "zh": "Node.js 未安装。请安装 Node.js >= 18。",
        "fr": "Node.js n'est pas installé. Installez Node.js >= 18.",
        "es": "Node.js no instalado. Instale Node.js >= 18.",
        "ru": "Node.js не установлен. Установите Node.js >= 18.",
        "ar": "Node.js غير مثبت. ثبت Node.js >= 18.",
    },
    "err_node_old": {
        "en": "Node.js version too old (< 18). Please upgrade.",
        "zh": "Node.js 版本过旧（< 18）。请升级。",
        "fr": "Version Node.js trop ancienne (< 18). Mettez à jour.",
        "es": "Versión Node.js demasiado antigua (< 18). Actualice.",
        "ru": "Версия Node.js устарела (< 18). Обновите.",
        "ar": "إصدار Node.js قديم جدًا (< 18). يرجى الترقية.",
    },
    "err_npm_missing": {
        "en": "npm not found. Reinstall Node.js.",
        "zh": "npm 未找到。请重新安装 Node.js。",
        "fr": "npm introuvable. Réinstallez Node.js.",
        "es": "npm no encontrado. Reinstale Node.js.",
        "ru": "npm не найден. Переустановите Node.js.",
        "ar": "npm غير موجود. أعد تثبيت Node.js.",
    },
    "err_permission": {
        "en": "Permission denied (EACCES). Run as admin or fix npm prefix.",
        "zh": "权限不足（EACCES）。请以管理员身份运行或修改 npm prefix。",
        "fr": "Permission refusée (EACCES). Exécutez en admin.",
        "es": "Permiso denegado (EACCES). Ejecute como admin.",
        "ru": "Доступ запрещен (EACCES). Запустите от администратора.",
        "ar": "تم رفض الإذن (EACCES). شغل كمسؤول.",
    },
    "err_network": {
        "en": "Network error. Check connection and proxy settings.",
        "zh": "网络错误。请检查网络连接和代理设置。",
        "fr": "Erreur réseau. Vérifiez la connexion et le proxy.",
        "es": "Error de red. Verifique conexión y proxy.",
        "ru": "Ошибка сети. Проверьте подключение и прокси.",
        "ar": "خطأ في الشبكة. تحقق من الاتصال وإعدادات الوكيل.",
    },
    "err_key_empty": {
        "en": "API Key is empty",
        "zh": "API Key 为空",
        "fr": "Clé API vide",
        "es": "Clave API vacía",
        "ru": "API ключ пуст",
        "ar": "مفتاح API فارغ",
    },
    "err_key_format": {
        "en": "API Key format incorrect",
        "zh": "API Key 格式不正确",
        "fr": "Format de clé API incorrect",
        "es": "Formato de clave API incorrecto",
        "ru": "Неверный формат API ключа",
        "ar": "تنسيق مفتاح API غير صحيح",
    },
    "err_key_short": {
        "en": "API Key too short — copy the full key",
        "zh": "API Key 太短 — 请完整复制",
        "fr": "Clé API trop courte — copiez la clé complète",
        "es": "Clave API demasiado corta — copie completa",
        "ru": "API ключ слишком короткий — скопируйте полностью",
        "ar": "مفتاح API قصير جدًا — انسخ المفتاح كاملاً",
    },
    "err_claude_path": {
        "en": "Claude CLI not found on PATH. Add npm global bin to PATH.",
        "zh": "Claude CLI 不在 PATH 中。请添加 npm 全局 bin 到 PATH。",
        "fr": "Claude CLI introuvable dans PATH. Ajoutez npm bin au PATH.",
        "es": "Claude CLI no en PATH. Agregue npm bin al PATH.",
        "ru": "Claude CLI не найден в PATH. Добавьте npm bin в PATH.",
        "ar": "Claude CLI غير موجود في PATH. أضف npm bin إلى PATH.",
    },
    "err_connection": {
        "en": "Cannot connect to provider API",
        "zh": "无法连接到提供商 API",
        "fr": "Impossible de se connecter à l'API",
        "es": "No se puede conectar a la API",
        "ru": "Не удается подключиться к API провайдера",
        "ar": "لا يمكن الاتصال بـ API المزود",
    },

    # ── Provider dialog ──────────────────────────────────────────
    "prov_configure": {
        "en": "Configure",
        "zh": "配置",
        "fr": "Configurer",
        "es": "Configurar",
        "ru": "Настроить",
        "ar": "تكوين",
    },
    "prov_env_var": {
        "en": "Environment Variable",
        "zh": "环境变量",
        "fr": "Variable d'Environnement",
        "es": "Variable de Entorno",
        "ru": "Переменная Окружения",
        "ar": "متغير البيئة",
    },
    "prov_key_format": {
        "en": "Key Format",
        "zh": "密钥格式",
        "fr": "Format de Clé",
        "es": "Formato de Clave",
        "ru": "Формат Ключа",
        "ar": "تنسيق المفتاح",
    },
    "prov_endpoint": {
        "en": "API Endpoint",
        "zh": "API 端点",
        "fr": "Point de Terminaison API",
        "es": "Endpoint API",
        "ru": "API Эндпоинт",
        "ar": "نقطة نهاية API",
    },
    "prov_models": {
        "en": "Supported Models",
        "zh": "支持模型",
        "fr": "Modèles Supportés",
        "es": "Modelos Soportados",
        "ru": "Поддерживаемые Модели",
        "ar": "النماذج المدعومة",
    },
    "prov_api_key": {
        "en": "API Key:",
        "zh": "API Key:",
        "fr": "Clé API:",
        "es": "Clave API:",
        "ru": "API Ключ:",
        "ar": "مفتاح API:",
    },
    "prov_get_key": {
        "en": "Get Key →",
        "zh": "获取 Key →",
        "fr": "Obtenir Clé →",
        "es": "Obtener Clave →",
        "ru": "Получить Ключ →",
        "ar": "→ الحصول على مفتاح",
    },
    "prov_show": {
        "en": "Show",
        "zh": "显示",
        "fr": "Afficher",
        "es": "Mostrar",
        "ru": "Показать",
        "ar": "إظهار",
    },

    # ── Export ───────────────────────────────────────────────────
    "export_title": {
        "en": "Export API Configuration",
        "zh": "导出 API 配置",
        "fr": "Exporter Configuration API",
        "es": "Exportar Configuración API",
        "ru": "Экспорт Конфигурации API",
        "ar": "تصدير تكوين API",
    },
    "export_success": {
        "en": "Config exported to:",
        "zh": "配置已导出到:",
        "fr": "Configuration exportée vers:",
        "es": "Configuración exportada a:",
        "ru": "Конфигурация экспортирована в:",
        "ar": "تم تصدير التكوين إلى:",
    },
    "export_warning": {
        "en": "Contains API keys — keep it safe!",
        "zh": "包含 API Key — 请妥善保管！",
        "fr": "Contient des clés API — gardez en sécurité!",
        "es": "Contiene claves API — ¡manténgalo seguro!",
        "ru": "Содержит API ключи — храните безопасно!",
        "ar": "يحتوي على مفاتيح API — احتفظ به بأمان!",
    },

    # ── Custom provider dialog ───────────────────────────────────
    "custom_title": {
        "en": "Add Custom AI Provider",
        "zh": "添加自定义 AI 提供商",
        "fr": "Ajouter Fournisseur IA Personnalisé",
        "es": "Añadir Proveedor IA Personalizado",
        "ru": "Добавить Пользовательского Провайдера",
        "ar": "إضافة مزود AI مخصص",
    },
    "custom_name": {
        "en": "Provider Name *",
        "zh": "提供商名称 *",
        "fr": "Nom du Fournisseur *",
        "es": "Nombre del Proveedor *",
        "ru": "Название Провайдера *",
        "ar": "اسم المزود *",
    },
    "custom_id": {
        "en": "ID (short slug) *",
        "zh": "ID (英文短名) *",
        "fr": "ID (slug court) *",
        "es": "ID (slug corto) *",
        "ru": "ID (короткий slug) *",
        "ar": "المعرف (slug قصير) *",
    },
    "custom_env": {
        "en": "Environment Variable *",
        "zh": "环境变量 *",
        "fr": "Variable d'Environnement *",
        "es": "Variable de Entorno *",
        "ru": "Переменная Окружения *",
        "ar": "متغير البيئة *",
    },
    "custom_prefix": {
        "en": "Key Prefix (optional)",
        "zh": "Key 前缀（可选）",
        "fr": "Préfixe de Clé (optionnel)",
        "es": "Prefijo de Clave (opcional)",
        "ru": "Префикс Ключа (опционально)",
        "ar": "بادئة المفتاح (اختياري)",
    },
    "custom_url": {
        "en": "API Base URL",
        "zh": "API Base URL",
        "fr": "URL de Base API",
        "es": "URL Base API",
        "ru": "Базовый URL API",
        "ar": "URL الأساسي لـ API",
    },
    "custom_console": {
        "en": "Console URL",
        "zh": "控制台地址",
        "fr": "URL Console",
        "es": "URL Consola",
        "ru": "URL Консоли",
        "ar": "رابط لوحة التحكم",
    },
    "custom_desc": {
        "en": "Description",
        "zh": "描述",
        "fr": "Description",
        "es": "Descripción",
        "ru": "Описание",
        "ar": "الوصف",
    },
    "custom_category": {
        "en": "Category",
        "zh": "分类",
        "fr": "Catégorie",
        "es": "Categoría",
        "ru": "Категория",
        "ar": "الفئة",
    },

    # ── Category names ──────────────────────────────────────────
    "cat_international": {
        "en": "🌍 International Cloud",
        "zh": "🌍 国际云平台",
        "fr": "🌍 Cloud International",
        "es": "🌍 Nube Internacional",
        "ru": "🌍 Международные",
        "ar": "🌍 السحابة الدولية",
    },
    "cat_china": {
        "en": "🇨🇳 Chinese Providers",
        "zh": "🇨🇳 国内模型",
        "fr": "🇨🇳 Fournisseurs Chinois",
        "es": "🇨🇳 Proveedores Chinos",
        "ru": "🇨🇳 Китайские Провайдеры",
        "ar": "🇨🇳 المزودون الصينيون",
    },
    "cat_local": {
        "en": "🏠 Local & Open Source",
        "zh": "🏠 本地/开源",
        "fr": "🏠 Local & Open Source",
        "es": "🏠 Local & Código Abierto",
        "ru": "🏠 Локальные и Open Source",
        "ar": "🏠 محلي ومفتوح المصدر",
    },
    "cat_custom": {
        "en": "⚡ Custom",
        "zh": "⚡ 自定义",
        "fr": "⚡ Personnalisé",
        "es": "⚡ Personalizado",
        "ru": "⚡ Пользовательские",
        "ar": "⚡ مخصص",
    },

    # ── Connection test ──────────────────────────────────────────
    "test_testing": {
        "en": "Testing connection...",
        "zh": "正在测试连接...",
        "fr": "Test de connexion...",
        "es": "Probando conexión...",
        "ru": "Проверка соединения...",
        "ar": "جاري اختبار الاتصال...",
    },
    "test_ok": {
        "en": "✓ Connected!",
        "zh": "✓ 连接成功！",
        "fr": "✓ Connecté!",
        "es": "✓ ¡Conectado!",
        "ru": "✓ Подключено!",
        "ar": "✓ تم الاتصال!",
    },
    "test_fail": {
        "en": "✗ Connection failed",
        "zh": "✗ 连接失败",
        "fr": "✗ Échec de connexion",
        "es": "✗ Conexión fallida",
        "ru": "✗ Ошибка подключения",
        "ar": "✗ فشل الاتصال",
    },

    # ── Confirm dialogs ──────────────────────────────────────────
    "confirm_delete": {
        "en": "Delete API Key configuration for",
        "zh": "确定删除以下提供商的 API Key 配置？",
        "fr": "Supprimer la configuration de clé API pour",
        "es": "¿Eliminar configuración de clave API para",
        "ru": "Удалить конфигурацию API ключа для",
        "ar": "حذف تكوين مفتاح API لـ",
    },
    "confirm_exit": {
        "en": "Exit the application?",
        "zh": "确定退出？",
        "fr": "Quitter l'application?",
        "es": "¿Salir de la aplicación?",
        "ru": "Выйти из приложения?",
        "ar": "الخروج من التطبيق؟",
    },

    # ── Setup/Launch ─────────────────────────────────────────────
    "setup_title": {
        "en": "Claude Code Deploy Setup",
        "zh": "Claude Code 部署安装向导",
        "fr": "Assistant d'Installation Claude Code",
        "es": "Asistente de Instalación Claude Code",
        "ru": "Мастер Установки Claude Code",
        "ar": "معالج تثبيت Claude Code",
    },
    "setup_check_python": {
        "en": "Checking Python...",
        "zh": "检查 Python...",
        "fr": "Vérification de Python...",
        "es": "Verificando Python...",
        "ru": "Проверка Python...",
        "ar": "جاري فحص Python...",
    },
    "setup_check_tk": {
        "en": "Checking tkinter...",
        "zh": "检查 tkinter...",
        "fr": "Vérification de tkinter...",
        "es": "Verificando tkinter...",
        "ru": "Проверка tkinter...",
        "ar": "جاري فحص tkinter...",
    },
    "setup_launching": {
        "en": "Launching GUI...",
        "zh": "启动图形界面...",
        "fr": "Lancement de l'interface...",
        "es": "Iniciando interfaz...",
        "ru": "Запуск интерфейса...",
        "ar": "جاري تشغيل الواجهة...",
    },
    "setup_no_python": {
        "en": "Python 3.8+ is required but not found.\nInstall from https://python.org",
        "zh": "需要 Python 3.8+，未找到。\n请从 https://python.org 安装",
        "fr": "Python 3.8+ requis mais introuvable.\nInstallez depuis https://python.org",
        "es": "Python 3.8+ requerido pero no encontrado.\nInstale desde https://python.org",
        "ru": "Требуется Python 3.8+, не найден.\nУстановите с https://python.org",
        "ar": "Python 3.8+ مطلوب لكنه غير موجود.\nثبته من https://python.org",
    },
    "setup_no_tk": {
        "en": "tkinter not found. Install python3-tk package.",
        "zh": "tkinter 未找到。请安装 python3-tk。",
        "fr": "tkinter introuvable. Installez python3-tk.",
        "es": "tkinter no encontrado. Instale python3-tk.",
        "ru": "tkinter не найден. Установите python3-tk.",
        "ar": "tkinter غير موجود. ثبت python3-tk.",
    },
    "setup_complete": {
        "en": "Setup complete! Starting the application...",
        "zh": "环境检查完成！正在启动应用...",
        "fr": "Configuration terminée! Démarrage de l'application...",
        "es": "¡Configuración completa! Iniciando aplicación...",
        "ru": "Настройка завершена! Запуск приложения...",
        "ar": "اكتمل الإعداد! جاري تشغيل التطبيق...",
    },

    # ── Provider descriptions (for tooltips) ────────────────────
    "desc_anthropic": {
        "en": "Claude models — long context, coding, complex reasoning",
        "zh": "Claude 系列 — 长文本分析、编程和复杂推理",
        "fr": "Modèles Claude — contexte long, programmation, raisonnement",
        "es": "Modelos Claude — contexto largo, programación, razonamiento",
        "ru": "Модели Claude — длинный контекст, программирование",
        "ar": "نماذج Claude — سياق طويل، برمجة، استدلال معقد",
    },
    "desc_openai": {
        "en": "GPT models — the most capable general-purpose LLM",
        "zh": "GPT 系列 — 综合能力最强的通用大模型",
        "fr": "Modèles GPT — le LLM généraliste le plus performant",
        "es": "Modelos GPT — el LLM general más capaz",
        "ru": "Модели GPT — самые мощные универсальные LLM",
        "ar": "نماذج GPT — أقوى نموذج لغة عام",
    },
    "desc_gemini": {
        "en": "Google multimodal — text, image, video, audio",
        "zh": "Google 多模态 — 支持文本/图片/视频/音频",
        "fr": "Multimodal Google — texte, image, vidéo, audio",
        "es": "Multimodal Google — texto, imagen, video, audio",
        "ru": "Мультимодальные Google — текст, изображения, видео, аудио",
        "ar": "Google متعدد الوسائط — نص، صورة، فيديو، صوت",
    },
    "desc_deepseek": {
        "en": "Chinese open-source flagship — coding & reasoning, great value",
        "zh": "国产开源旗舰 — 编码和推理能力极强，性价比高",
        "fr": "Fleuron open-source chinois — programmation, bon rapport qualité-prix",
        "es": "Estándar chino open-source — codificación, excelente relación calidad-precio",
        "ru": "Китайский open-source флагман — кодинг, рассуждение",
        "ar": "رائد صيني مفتوح المصدر — برمجة واستدلال، قيمة ممتازة",
    },
    "desc_ollama": {
        "en": "Run LLMs locally — one command to download and run",
        "zh": "本地运行大模型 — 一键下载运行开源模型",
        "fr": "Exécutez des LLM localement — un ordre pour télécharger et lancer",
        "es": "Ejecute LLMs localmente — descargue y ejecute en un comando",
        "ru": "Запуск LLM локально — одна команда для скачивания и запуска",
        "ar": "تشغيل نماذج اللغة محليًا — أمر واحد للتنزيل والتشغيل",
    },
    "desc_openai_compat": {
        "en": "Any OpenAI-compatible API with custom Base URL",
        "zh": "兼容 OpenAI API 格式的任意自建服务",
        "fr": "Toute API compatible OpenAI avec URL personnalisée",
        "es": "Cualquier API compatible OpenAI con URL personalizada",
        "ru": "Любой OpenAI-совместимый API с настраиваемым URL",
        "ar": "أي API متوافق مع OpenAI مع URL أساسي مخصص",
    },
}


# ── Translation function ────────────────────────────────────────

def _(key: str, **kwargs) -> str:
    """Get translated string for the current language."""
    if key not in STRINGS:
        return f"[[{key}]]"
    translations = STRINGS[key]
    text = translations.get(_current_lang, translations.get("en", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text

def translate(key: str, lang: str = None, **kwargs) -> str:
    """Get translated string for a specific language."""
    if lang is None:
        lang = _current_lang
    if key not in STRINGS:
        return f"[[{key}]]"
    text = STRINGS[key].get(lang, STRINGS[key].get("en", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text
