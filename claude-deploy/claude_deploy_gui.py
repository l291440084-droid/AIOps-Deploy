#!/usr/bin/env python3
"""
AI API One-Click Deploy — GUI Application (Wizard Edition)
Features: Language selection (6 UN languages), directory chooser,
          per-step visual guidance, 50+ provider management.
"""

import sys
import os
import queue
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deploy_core as core
from providers import (
    get_all_providers, get_providers_by_category, get_provider,
    scan_configured_providers, get_configured_summary,
    save_custom_provider, delete_custom_provider,
    CATEGORIES, Provider,
)
from i18n import _, set_language, get_language, get_dir, LANGUAGES, translate

# ── Constants ───────────────────────────────────────────────────

WIN_W, WIN_H = 900, 740

COLOR_BG       = "#F5F5F5"
COLOR_CARD     = "#FFFFFF"
COLOR_TEXT     = "#212121"
COLOR_MUTED    = "#757575"
COLOR_BANNER   = "#1A1A2E"
COLOR_DONE     = "#4CAF50"
COLOR_RUNNING  = "#2196F3"
COLOR_ERROR    = "#F44336"
COLOR_CONFIGURED = "#E8F5E9"
COLOR_GUIDE    = "#E3F2FD"
COLOR_PENDING  = "#888888"

STATUS_PENDING = "○"
STATUS_RUNNING = "●"
STATUS_DONE    = "✓"
STATUS_ERROR   = "✗"

CARD_W, CARD_H = 170, 130


# ── Main Application ────────────────────────────────────────────

class DeployApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(_("app_title"))
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.minsize(750, 600)
        self.root.configure(bg=COLOR_BG)
        self._center_window()

        self.queue = queue.Queue()
        self.current_step = 0
        self.total_steps = 5  # lang, dir, system(install), apikey, done
        self.provider_cards = {}
        self.configured = {}
        self.os_info = None
        self.install_dir = None
        self.lang_selected = get_language()

        # Wizard pages
        self.pages = {}
        self.page_order = ["lang", "dir", "system", "apikey", "done"]

        self._build_ui()
        self._poll_queue()
        self._show_page("lang")

    # ── UI Construction ──────────────────────────────────────────

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        # ── Banner ───────────────────────────────────────────────
        banner = tk.Frame(main, bg=COLOR_BANNER, height=50)
        banner.pack(fill=tk.X, pady=(0, 6))
        banner.pack_propagate(False)
        self.banner_label = tk.Label(
            banner, text=_("app_title"), fg="white", bg=COLOR_BANNER,
            font=("Microsoft YaHei", 13, "bold"),
        )
        self.banner_label.pack(side=tk.LEFT, padx=14, expand=True)

        # Step indicator dots
        self.step_dots_frame = tk.Frame(banner, bg=COLOR_BANNER)
        self.step_dots_frame.pack(side=tk.RIGHT, padx=14)
        self.step_dots = []
        for i in range(self.total_steps):
            dot = tk.Label(self.step_dots_frame, text="○", fg="#555",
                           bg=COLOR_BANNER, font=("Consolas", 11))
            dot.pack(side=tk.LEFT, padx=3)
            self.step_dots.append(dot)

        # ── Page container ───────────────────────────────────────
        self.page_container = tk.Frame(main, bg=COLOR_BG)
        self.page_container.pack(fill=tk.BOTH, expand=True)

        for page_id in self.page_order:
            page = tk.Frame(self.page_container, bg=COLOR_BG)
            self.pages[page_id] = page

        # ── Bottom bar ───────────────────────────────────────────
        bottom = ttk.Frame(main)
        bottom.pack(fill=tk.X, pady=(6, 0))

        self.progress = ttk.Progressbar(bottom, mode="indeterminate")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.status_label = tk.Label(
            bottom, text="", fg=COLOR_MUTED, bg=COLOR_BG,
            font=("Microsoft YaHei", 9), anchor=tk.W,
        )
        self.status_label.pack(side=tk.LEFT)

        self.btn_frame = tk.Frame(bottom, bg=COLOR_BG)
        self.btn_frame.pack(side=tk.RIGHT)

        self.btn_back = ttk.Button(self.btn_frame, text=_("btn_back"), command=self._go_back)
        self.btn_next = ttk.Button(self.btn_frame, text=_("btn_next"), command=self._go_next)
        self.btn_skip = ttk.Button(self.btn_frame, text=_("btn_skip"), command=self._go_next)
        self.btn_install = ttk.Button(self.btn_frame, text=_("btn_install"), command=self._start_install)
        self.btn_cancel = ttk.Button(self.btn_frame, text=_("btn_cancel"))
        self.btn_exit = ttk.Button(self.btn_frame, text=_("btn_exit"), command=self._on_exit)

    # ── Window helpers ───────────────────────────────────────────

    def _center_window(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - WIN_W) // 2
        y = (sh - WIN_H) // 2
        self.root.geometry(f"+{x}+{y}")

    # ── Queue system ─────────────────────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                self._handle_msg(msg)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _handle_msg(self, msg):
        kind = msg[0]
        if kind == "status":
            self.status_label.config(text=msg[1])
        elif kind == "log":
            pass  # Console output handled per page
        elif kind == "progress":
            if msg[1]: self.progress.start(10)
            else: self.progress.stop()

    def _set_status(self, text):
        self.queue.put(("status", text))

    # ── Page navigation ──────────────────────────────────────────

    def _show_page(self, page_id):
        for p in self.pages.values():
            p.pack_forget()

        page = self.pages[page_id]
        page.pack(fill=tk.BOTH, expand=True)
        self.current_step = self.page_order.index(page_id)

        # Build page content if empty
        if not page.winfo_children():
            build_method = getattr(self, f"_build_page_{page_id}", None)
            if build_method:
                build_method(page)

        # Update step dots
        for i, dot in enumerate(self.step_dots):
            if i < self.current_step:
                dot.config(text="●", fg=COLOR_DONE)
            elif i == self.current_step:
                dot.config(text="●", fg=COLOR_RUNNING)
            else:
                dot.config(text="○", fg="#555")

        # Update buttons
        self._update_buttons(page_id)
        self._update_banner(page_id)

    def _update_buttons(self, page_id):
        for b in [self.btn_back, self.btn_next, self.btn_skip, self.btn_install,
                  self.btn_cancel, self.btn_exit]:
            b.pack_forget()

        if page_id == "lang":
            # No buttons needed — language selection auto-advances
            pass
        elif page_id == "dir":
            self.btn_back.pack(side=tk.RIGHT, padx=(4, 0))
            self.btn_next.pack(side=tk.RIGHT, padx=(4, 0))
        elif page_id == "system":
            self.btn_back.pack(side=tk.RIGHT, padx=(4, 0))
            self.btn_install.pack(side=tk.RIGHT, padx=(4, 0))
        elif page_id == "apikey":
            self.btn_back.pack(side=tk.RIGHT, padx=(4, 0))
            self.btn_next.pack(side=tk.RIGHT, padx=(4, 0))
            # Extra buttons in the page itself
        elif page_id == "done":
            self.btn_exit.pack(side=tk.RIGHT, padx=(4, 0))

    def _update_banner(self, page_id):
        titles = {
            "lang": "app_title", "dir": "dir_title", "system": "app_title",
            "system": "step_install", "apikey": "step_apikey", "done": "app_title",
        }
        self.banner_label.config(text=_(titles.get(page_id, "app_title")))

    def _go_back(self):
        idx = self.page_order.index(self.page_order[self.current_step])
        if idx > 0:
            self._show_page(self.page_order[idx - 1])

    def _go_next(self):
        idx = self.page_order.index(self.page_order[self.current_step])
        if idx < len(self.page_order) - 1:
            nxt = self.page_order[idx + 1]
            # System page: trigger install (which auto-advances to apikey on completion)
            if self.page_order[idx] == "system" and nxt == "apikey":
                self._start_install()
                return  # Don't navigate yet — _finish_install handles it
            self._show_page(nxt)

    # ══════════════════════════════════════════════════════════════
    # PAGE 1: Language Selection
    # ══════════════════════════════════════════════════════════════

    def _build_page_lang(self, page):
        page.configure(bg=COLOR_BG)

        center = tk.Frame(page, bg=COLOR_BG)
        center.pack(expand=True)

        tk.Label(center, text="🌐", font=("Segoe UI Emoji", 48), bg=COLOR_BG).pack(pady=(0, 10))
        tk.Label(center, text=_("lang_title"), font=("Microsoft YaHei", 18, "bold"),
                 bg=COLOR_BG, fg=COLOR_TEXT).pack()
        tk.Label(center, text=_("lang_prompt"), font=("Microsoft YaHei", 10),
                 bg=COLOR_BG, fg=COLOR_MUTED).pack(pady=(6, 20))

        # Language buttons grid — 2 rows × 3 cols
        grid = tk.Frame(center, bg=COLOR_BG)
        grid.pack()

        row_frame = None
        for i, (code, info) in enumerate(LANGUAGES.items()):
            if i % 3 == 0:
                row_frame = tk.Frame(grid, bg=COLOR_BG)
                row_frame.pack(pady=4)
            self._create_lang_button(row_frame, code, info)

        tk.Label(center, text="You can change language anytime via Settings",
                 font=("Microsoft YaHei", 8), bg=COLOR_BG, fg=COLOR_MUTED).pack(pady=(20, 0))

    def _create_lang_button(self, parent, code, info):
        is_rtl = info.get("dir") == "rtl"
        btn = tk.Frame(parent, bg=COLOR_CARD, highlightbackground="#E0E0E0",
                        highlightthickness=1, cursor="hand2")
        btn.pack(side=tk.LEFT, padx=8, ipadx=14, ipady=10)
        btn.pack_propagate(False)

        tk.Label(btn, text=f"{info['flag']}  {info['native']}",
                 font=("Microsoft YaHei", 12) if not is_rtl else ("Segoe UI", 12),
                 bg=COLOR_CARD, fg=COLOR_TEXT).pack(padx=10, pady=8)
        tk.Label(btn, text=info['name'],
                 font=("Microsoft YaHei", 8), bg=COLOR_CARD, fg=COLOR_MUTED).pack(pady=(0, 6))

        btn.bind("<Button-1>", lambda e, c=code: self._on_lang_select(c))
        for child in btn.winfo_children():
            child.bind("<Button-1>", lambda e, c=code: self._on_lang_select(c))

    def _on_lang_select(self, code):
        set_language(code)
        self.lang_selected = code
        self._set_status(_("lang_saved"))
        # Rebuild all pages with new language
        for page_id in self.page_order:
            page = self.pages[page_id]
            for w in page.winfo_children():
                w.destroy()
        self.root.after(400, lambda: self._show_page("dir"))

    # ══════════════════════════════════════════════════════════════
    # PAGE 2: Directory Selection
    # ══════════════════════════════════════════════════════════════

    def _build_page_dir(self, page):
        page.configure(bg=COLOR_BG)

        center = tk.Frame(page, bg=COLOR_BG)
        center.pack(expand=True, fill=tk.X, padx=60)

        tk.Label(center, text="📁", font=("Segoe UI Emoji", 40), bg=COLOR_BG).pack(pady=(0, 8))
        tk.Label(center, text=_("dir_title"), font=("Microsoft YaHei", 16, "bold"),
                 bg=COLOR_BG, fg=COLOR_TEXT).pack()
        tk.Label(center, text=_("dir_hint"), font=("Microsoft YaHei", 9),
                 bg=COLOR_BG, fg=COLOR_MUTED, wraplength=600).pack(pady=(6, 20))

        # Default option
        self.dir_var = tk.StringVar(value="default")
        default_frame = tk.Frame(center, bg=COLOR_CARD, highlightbackground="#E0E0E0",
                                  highlightthickness=1, cursor="hand2")
        default_frame.pack(fill=tk.X, pady=4)
        tk.Radiobutton(default_frame, text=_("dir_default"), variable=self.dir_var,
                       value="default", font=("Microsoft YaHei", 11), bg=COLOR_CARD,
                       command=self._on_dir_option).pack(side=tk.LEFT, padx=14, pady=12)
        tk.Label(default_frame, text=f"({self._get_default_dir()})",
                 font=("Consolas", 8), bg=COLOR_CARD, fg=COLOR_MUTED).pack(side=tk.RIGHT, padx=14)

        # Custom option
        custom_frame = tk.Frame(center, bg=COLOR_CARD, highlightbackground="#E0E0E0",
                                 highlightthickness=1, cursor="hand2")
        custom_frame.pack(fill=tk.X, pady=4)
        tk.Radiobutton(custom_frame, text=_("dir_custom"), variable=self.dir_var,
                       value="custom", font=("Microsoft YaHei", 11), bg=COLOR_CARD,
                       command=self._on_dir_option).pack(side=tk.LEFT, padx=14, pady=12)

        self.dir_custom_frame = tk.Frame(custom_frame, bg=COLOR_CARD)
        self.dir_path_var = tk.StringVar()
        self.dir_entry = ttk.Entry(self.dir_custom_frame, textvariable=self.dir_path_var,
                                    font=("Consolas", 10), width=40)
        self.dir_entry.pack(side=tk.LEFT, padx=(0, 6), pady=8)
        ttk.Button(self.dir_custom_frame, text=_("dir_browse"),
                   command=self._browse_dir).pack(side=tk.LEFT)
        self.dir_custom_frame.pack_forget()

    def _get_default_dir(self):
        import subprocess
        try:
            return subprocess.check_output(["npm", "config", "get", "prefix"], text=True).strip()
        except Exception:
            return str(Path.home() / ".npm-global")

    def _on_dir_option(self):
        if self.dir_var.get() == "custom":
            self.dir_custom_frame.pack(fill=tk.X, padx=14, pady=(0, 8))
        else:
            self.dir_custom_frame.pack_forget()
            self.install_dir = None

    def _browse_dir(self):
        path = filedialog.askdirectory(title=_("dir_title"))
        if path:
            self.dir_path_var.set(path)
            self.install_dir = path

    # ══════════════════════════════════════════════════════════════
    # PAGE 3: System Check
    # ══════════════════════════════════════════════════════════════

    def _build_page_system(self, page):
        page.configure(bg=COLOR_BG)
        self._add_guidance_header(page, "guide_os")

        # Step list frame
        self.sys_step_frame = tk.Frame(page, bg=COLOR_CARD, highlightbackground="#E0E0E0",
                                        highlightthickness=1)
        self.sys_step_frame.pack(fill=tk.X, padx=20, pady=(12, 8))

        self.sys_labels = {}
        steps = [
            ("os", _("step_os"), "detect"),
            ("node", _("step_node"), "check"),
            ("npm", _("step_npm"), "check"),
            ("claude", _("step_install"), "install"),
        ]
        for sid, label, action in steps:
            self._create_sys_step_row(sid, label, action)

        # Auto-install button area (shown when Node is missing)
        self.auto_fix_frame = tk.Frame(page, bg="#FFF3E0", highlightbackground="#FFCC80",
                                        highlightthickness=1)
        self.auto_fix_label = tk.Label(self.auto_fix_frame, text="", bg="#FFF3E0",
                                        fg="#E65100", font=("Microsoft YaHei", 10),
                                        wraplength=800, justify=tk.LEFT)
        self.auto_fix_label.pack(side=tk.LEFT, padx=12, pady=10)
        self.auto_fix_btn = ttk.Button(self.auto_fix_frame, text="🔧 自动修复 / Auto-Fix",
                                        command=self._auto_fix_node)
        self.auto_fix_btn.pack(side=tk.RIGHT, padx=12, pady=10)

        # Console
        self._add_console(page)

    def _create_sys_step_row(self, sid, label, action):
        row = tk.Frame(self.sys_step_frame, bg=COLOR_CARD)
        row.pack(fill=tk.X, pady=3, padx=14)

        sl = tk.Label(row, text=STATUS_PENDING, fg=COLOR_PENDING, bg=COLOR_CARD,
                      font=("Consolas", 14, "bold"), width=2)
        sl.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(row, text=label, font=("Microsoft YaHei", 10), bg=COLOR_CARD,
                 fg=COLOR_TEXT).pack(side=tk.LEFT)
        dl = tk.Label(row, text="", font=("Microsoft YaHei", 9), bg=COLOR_CARD, fg=COLOR_MUTED)
        dl.pack(side=tk.RIGHT)

        self.sys_labels[sid] = (sl, dl, action)

    def _update_sys_step(self, sid, status, detail=""):
        colors = {STATUS_PENDING: COLOR_PENDING, STATUS_RUNNING: COLOR_RUNNING,
                  STATUS_DONE: COLOR_DONE, STATUS_ERROR: COLOR_ERROR}
        if sid in self.sys_labels:
            sl, dl, _ = self.sys_labels[sid]
            sl.config(text=status, fg=colors.get(status, COLOR_PENDING))
            dl.config(text=detail)

    def _start_install(self):
        """Run full auto-deploy: check → install missing → install Claude Code."""
        self.btn_install.config(state=tk.DISABLED)
        self.btn_back.config(state=tk.DISABLED)
        self.btn_skip.config(state=tk.DISABLED)
        self.auto_fix_frame.pack_forget()
        self.progress.start(10)
        self._set_status(_("status_scanning"))
        threading.Thread(target=self._run_auto_deploy, daemon=True).start()

    def _run_auto_deploy(self):
        """Use deploy_core.auto_deploy() — handles missing Node.js automatically."""
        # Step 1: OS
        self.root.after(0, lambda: self._update_sys_step("os", STATUS_RUNNING))
        os_info = core.detect_os()
        self.os_info = os_info
        if os_info["success"]:
            self.root.after(0, lambda: self._update_sys_step("os", STATUS_DONE, os_info["name"]))
        else:
            self.root.after(0, lambda: self._update_sys_step("os", STATUS_ERROR, "Unknown"))
            self._finish_install(False)
            return

        # Step 2: Node.js — auto-install if missing
        self.root.after(0, lambda: self._update_sys_step("node", STATUS_RUNNING))
        nr = core.check_node()
        if nr["success"]:
            self.root.after(0, lambda: self._update_sys_step("node", STATUS_DONE, f"v{nr['version']}"))
        else:
            self.root.after(0, lambda: self._update_sys_step("node", STATUS_RUNNING, "自动安装中..."))
            self.root.after(0, lambda: self._log(f"[Auto] Node.js 缺失，自动安装...\n"))
            ni = core.install_nodejs(
                lambda msg, pct: self.root.after(0, lambda m=msg, p=pct:
                    self._update_sys_step("node", STATUS_RUNNING, f"{int(pct*100)}% {m}"))
            )
            if ni["success"]:
                nr2 = core.check_node()
                if nr2["success"]:
                    self.root.after(0, lambda: self._update_sys_step("node", STATUS_DONE, f"v{nr2['version']} ✓"))
                else:
                    self.root.after(0, lambda: self._update_sys_step("node", STATUS_ERROR, "安装后仍不可用"))
                    self._show_auto_fix("Node.js 自动安装失败，请手动安装后重试。",
                                        "https://nodejs.org")
                    self._finish_install(False)
                    return
            else:
                self.root.after(0, lambda: self._update_sys_step("node", STATUS_ERROR, "自动安装失败"))
                self._show_auto_fix(ni.get("error", "Node.js 安装失败"),
                                    ni.get("fix", "https://nodejs.org"))
                self._finish_install(False)
                return

        # Step 3: npm
        self.root.after(0, lambda: self._update_sys_step("npm", STATUS_RUNNING))
        npmr = core.check_npm()
        if npmr["success"]:
            self.root.after(0, lambda: self._update_sys_step("npm", STATUS_DONE, f"v{npmr['version']}"))
        else:
            self.root.after(0, lambda: self._update_sys_step("npm", STATUS_ERROR, _("err_npm_missing")[:35]))
            self._finish_install(False)
            return

        # Step 4: Install Claude Code
        self.root.after(0, lambda: self._update_sys_step("claude", STATUS_RUNNING, "安装中..."))

        def install_progress(line, pct):
            self.root.after(0, lambda l=line, p=pct:
                self._update_sys_step("claude", STATUS_RUNNING, f"{int(p*100)}%"))
            if line and len(line) < 120:
                self.root.after(0, lambda l=line: self._log(l))

        if self.install_dir:
            os.makedirs(self.install_dir, exist_ok=True)
            import subprocess
            subprocess.run(["npm", "config", "set", "prefix", self.install_dir], capture_output=True)

        result = core.install_claude(install_progress)
        if result["success"]:
            ver = result.get("version", "OK")
            self.root.after(0, lambda v=ver: self._update_sys_step("claude", STATUS_DONE, v or "Installed"))
        else:
            self.root.after(0, lambda: self._update_sys_step("claude", STATUS_ERROR, "安装失败"))
            if result.get("output"):
                self.root.after(0, lambda o=result["output"]: self._log("\n".join(o[-15:])))
            self._finish_install(False)
            return

        self._finish_install(True)

    def _show_auto_fix(self, error_msg, fix_url=""):
        """Show the auto-fix panel below the step list."""
        self.auto_fix_label.config(text=f"⚠  {error_msg}")
        self.auto_fix_frame.pack(fill=tk.X, padx=20, pady=(0, 8), before=self.console if hasattr(self, 'console') else None)
        if fix_url:
            self._current_auto_fix_url = fix_url
            self.auto_fix_btn.config(text="📖 手动安装指南 / Manual Install Guide",
                                      command=lambda: webbrowser.open(fix_url),
                                      state=tk.NORMAL)
        else:
            self.auto_fix_btn.config(state=tk.DISABLED)

    def _auto_fix_node(self):
        """Handle auto-fix button click — retry auto-install."""
        self.auto_fix_frame.pack_forget()
        self._start_install()

    def _finish_install(self, success):
        self.root.after(0, lambda: self.progress.stop())
        self.root.after(0, lambda: self.btn_back.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.btn_skip.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.btn_install.config(state=tk.NORMAL))
        if success:
            self.root.after(0, lambda: self._set_status(_("status_complete")))
            self.root.after(600, lambda: self._show_page("apikey"))
        else:
            self.root.after(0, lambda: self._set_status("⚠ 部署未完成，请查看上方错误 / Fix errors above"))

    # ══════════════════════════════════════════════════════════════
    # PAGE 4: API Key Configuration (Provider Grid)
    # ══════════════════════════════════════════════════════════════

    def _build_page_apikey(self, page):
        page.configure(bg=COLOR_BG)
        self._add_guidance_header(page, "guide_apikey")

        # Notebook tabs
        self.notebook = ttk.Notebook(page)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(6, 0))

        self.tab_frames = {}
        for cat_id, cat_info in sorted(CATEGORIES.items(), key=lambda x: x[1]["order"]):
            cat_name = _(f"cat_{cat_id}", default=cat_info["name"])
            tab_frame = tk.Frame(self.notebook, bg=COLOR_BG)
            self.notebook.add(tab_frame, text=f"  {cat_name}  ")

            canvas = tk.Canvas(tab_frame, bg=COLOR_BG, highlightthickness=0)
            scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=canvas.yview)
            card_frame = tk.Frame(canvas, bg=COLOR_BG, padx=6, pady=6)
            card_frame.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.create_window((0, 0), window=card_frame, anchor="nw", tags="cf")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.bind("<Configure>", lambda e, c=canvas, cf=card_frame: c.itemconfig("cf", width=e.width))
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.tab_frames[cat_id] = (canvas, card_frame)

        # Bottom action bar for API page
        apikey_bar = tk.Frame(page, bg=COLOR_BG)
        apikey_bar.pack(fill=tk.X, padx=8, pady=(6, 0))

        ttk.Button(apikey_bar, text=_("btn_export"), command=self._export_env).pack(side=tk.RIGHT, padx=(4, 0))
        ttk.Button(apikey_bar, text=_("btn_custom"), command=self._add_custom).pack(side=tk.RIGHT, padx=(4, 0))
        ttk.Button(apikey_bar, text=_("btn_refresh"), command=self._refresh_cards).pack(side=tk.RIGHT, padx=(4, 0))

        self._refresh_cards()

    def _refresh_cards(self):
        self.configured = scan_configured_providers()

        for cat_id in CATEGORIES:
            if cat_id not in self.tab_frames:
                continue
            canvas, card_frame = self.tab_frames[cat_id]
            for w in card_frame.winfo_children():
                w.destroy()

            providers = get_providers_by_category(cat_id)
            if not providers:
                tk.Label(card_frame, text=_("status_not_configured"),
                         bg=COLOR_BG, fg=COLOR_MUTED, font=("Microsoft YaHei", 11)).pack(pady=20)
                continue

            cols = max(1, (WIN_W - 100) // (CARD_W + 10))
            row_frame = None
            for i, p in enumerate(providers):
                if i % cols == 0:
                    row_frame = tk.Frame(card_frame, bg=COLOR_BG)
                    row_frame.pack(fill=tk.X, pady=2)
                self._create_provider_card(row_frame, p)

            if cat_id == "custom":
                tk.Button(card_frame, text="+ " + _("btn_custom"),
                          font=("Microsoft YaHei", 10), bg="#E3F2FD", fg="#1565C0",
                          relief=tk.FLAT, cursor="hand2", padx=14, pady=6,
                          command=self._add_custom).pack(pady=8)

    def _create_provider_card(self, parent, provider):
        is_configured = self.configured.get(provider.id, False)
        bg = COLOR_CONFIGURED if is_configured else COLOR_CARD
        border = "#A5D6A7" if is_configured else "#E0E0E0"

        card = tk.Frame(parent, bg=bg, highlightbackground=border, highlightthickness=1,
                        width=CARD_W, height=CARD_H)
        card.pack(side=tk.LEFT, padx=3, pady=2)
        card.pack_propagate(False)

        header = tk.Frame(card, bg=bg)
        header.pack(fill=tk.X, padx=7, pady=(6, 2))
        tk.Label(header, text=provider.icon, font=("Segoe UI Emoji", 16), bg=bg).pack(side=tk.LEFT)
        if is_configured:
            tk.Label(header, text=" ✓", fg=COLOR_DONE, bg=bg, font=("Microsoft YaHei", 10, "bold")).pack(side=tk.RIGHT)

        tk.Label(card, text=provider.name, bg=bg, fg=COLOR_TEXT,
                 font=("Microsoft YaHei", 9, "bold"), anchor=tk.W, wraplength=CARD_W-14).pack(fill=tk.X, padx=7)

        st = _("status_configured") if is_configured else _("status_not_configured")
        tk.Label(card, text=st, bg=bg, fg=COLOR_DONE if is_configured else COLOR_MUTED,
                 font=("Microsoft YaHei", 7)).pack(fill=tk.X, padx=7, pady=(1, 4))

        if is_configured:
            bf = tk.Frame(card, bg=bg)
            bf.pack(fill=tk.X, padx=5, pady=(0, 4))
            tk.Button(bf, text=_("btn_reconfig"), font=("Microsoft YaHei", 7),
                      bg="#E3F2FD", relief=tk.FLAT, cursor="hand2",
                      command=lambda p=provider: self._open_provider_dialog(p)).pack(side=tk.LEFT, padx=(0, 3))
            tk.Button(bf, text=_("btn_delete"), font=("Microsoft YaHei", 7),
                      bg="#FFEBEE", relief=tk.FLAT, cursor="hand2",
                      command=lambda p=provider: self._forget_provider(p)).pack(side=tk.LEFT)
        else:
            tk.Button(card, text=_("btn_configure"), font=("Microsoft YaHei", 7),
                      bg="#E3F2FD", fg="#1565C0", relief=tk.FLAT, cursor="hand2",
                      command=lambda p=provider: self._open_provider_dialog(p)).pack(pady=(0, 4))

        card.bind("<Button-1>", lambda e, p=provider: self._open_provider_dialog(p))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, p=provider: self._open_provider_dialog(p))
            for c2 in child.winfo_children():
                c2.bind("<Button-1>", lambda e, p=provider: self._open_provider_dialog(p))

        self.provider_cards[provider.id] = card

    def _open_provider_dialog(self, provider):
        ProviderConfigDialog(self.root, provider, self._on_provider_saved)

    def _on_provider_saved(self, provider_id):
        self._refresh_cards()
        self._set_status(f"✓ {provider_id} " + _("status_configured"))

    def _forget_provider(self, provider):
        if not messagebox.askyesno("Confirm", f"{_('confirm_delete')} {provider.name}?"):
            return
        result = core.delete_provider_key(provider.id)
        if result["success"]:
            self._refresh_cards()

    def _add_custom(self):
        CustomProviderDialog(self.root, self._refresh_cards)

    def _export_env(self):
        content = core.export_env_file()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".env",
            filetypes=[("Env files", "*.env"), ("All files", "*.*")],
            initialfile="ai_providers.env",
            title=_("export_title"),
        )
        if filepath:
            with open(filepath, "w") as f:
                f.write(content)
            self._set_status(f"{_('export_success')} {filepath}")
            messagebox.showinfo("Export", f"{_('export_success')}\n{filepath}\n\n{_('export_warning')}")

    # ══════════════════════════════════════════════════════════════
    # PAGE 5: Done / Summary
    # ══════════════════════════════════════════════════════════════

    def _build_page_done(self, page):
        page.configure(bg=COLOR_BG)

        center = tk.Frame(page, bg=COLOR_BG)
        center.pack(expand=True)

        tk.Label(center, text="🎉", font=("Segoe UI Emoji", 56), bg=COLOR_BG).pack(pady=(0, 12))
        tk.Label(center, text=_("status_complete"), font=("Microsoft YaHei", 16, "bold"),
                 bg=COLOR_BG, fg=COLOR_DONE, wraplength=600).pack()

        # Summary
        summary = get_configured_summary()
        summary_text = f"{summary['configured']}/{summary['total']} providers configured"
        tk.Label(center, text=summary_text, font=("Microsoft YaHei", 10),
                 bg=COLOR_BG, fg=COLOR_MUTED).pack(pady=(8, 20))

        # Quick start instructions
        guide = tk.Frame(center, bg="#E8F5E9", highlightbackground="#A5D6A7", highlightthickness=1)
        guide.pack(fill=tk.X, padx=40)
        tips = [
            "✓  Run 'claude' in any terminal to start",
            "✓  Configure more providers on the API Keys tab",
            "✓  Use 'claude --cwd /path/to/project' for project mode",
            "✓  Get help: 'claude --help' or https://docs.anthropic.com",
        ]
        for tip in tips:
            tk.Label(guide, text=tip, font=("Microsoft YaHei", 10), bg="#E8F5E9",
                     fg=COLOR_TEXT, anchor=tk.W).pack(fill=tk.X, padx=16, pady=4)

        tk.Label(center, text="\nSettings saved to ~/.ai-deploy/",
                 font=("Microsoft YaHei", 8), bg=COLOR_BG, fg=COLOR_MUTED).pack()

    # ── Shared UI components ─────────────────────────────────────

    def _add_guidance_header(self, page, i18n_key):
        """Add a visual guidance panel at the top of a page."""
        guide = tk.Frame(page, bg=COLOR_GUIDE, highlightbackground="#90CAF9", highlightthickness=1)
        guide.pack(fill=tk.X, padx=10, pady=(4, 6))

        title_key = i18n_key + "_title"
        desc_key = i18n_key + "_desc"

        title_text = _(title_key) if title_key else "?"
        desc_text = _(desc_key) if desc_key else "?"

        tk.Label(guide, text=f"💡  {title_text}", font=("Microsoft YaHei", 10, "bold"),
                 bg=COLOR_GUIDE, fg="#1565C0", anchor=tk.W).pack(fill=tk.X, padx=12, pady=(8, 2))
        tk.Label(guide, text=desc_text, font=("Microsoft YaHei", 9),
                 bg=COLOR_GUIDE, fg=COLOR_TEXT, anchor=tk.W, wraplength=850, justify=tk.LEFT).pack(
            fill=tk.X, padx=12, pady=(0, 8))

    def _add_console(self, page):
        """Add a collapsible console output to a page."""
        cf = tk.Frame(page, bg=COLOR_BG)
        cf.pack(fill=tk.BOTH, expand=True, padx=14, pady=(4, 0))

        self.console_visible = tk.BooleanVar(value=True)
        ch = tk.Frame(cf, bg=COLOR_BG)
        ch.pack(fill=tk.X)
        ttk.Checkbutton(ch, text=_("btn_console"), variable=self.console_visible,
                        command=self._toggle_console_el).pack(side=tk.LEFT)

        self.console = scrolledtext.ScrolledText(
            cf, height=6, font=("Consolas", 9),
            bg="#263238", fg="#ECEFF1", insertbackground="white",
            state=tk.DISABLED, wrap=tk.WORD,
        )
        self.console.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

    def _toggle_console_el(self):
        if self.console_visible.get():
            self.console.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        else:
            self.console.pack_forget()

    def _on_exit(self):
        if messagebox.askyesno("Exit", _("confirm_exit")):
            self.root.destroy()


# ── Provider Config Dialog ──────────────────────────────────────

class ProviderConfigDialog:
    def __init__(self, parent, provider, callback):
        self.provider = provider
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{_('prov_configure')} — {provider.name}")
        self.dialog.geometry("530x440")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self._center(parent)
        self.dialog.configure(bg=COLOR_BG)

        content = ttk.Frame(self.dialog, padding=18)
        content.pack(fill=tk.BOTH, expand=True)

        # Header
        hdr = tk.Frame(content, bg=COLOR_BG)
        hdr.pack(fill=tk.X, pady=(0, 10))
        tk.Label(hdr, text=f"{provider.icon}  {provider.name}", font=("Microsoft YaHei", 13, "bold"),
                 bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor=tk.W)
        tk.Label(hdr, text=provider.description, font=("Microsoft YaHei", 8),
                 bg=COLOR_BG, fg=COLOR_MUTED, wraplength=460, justify=tk.LEFT).pack(anchor=tk.W, pady=(2, 0))

        # Info
        info_frame = tk.Frame(content, bg="#F5F5F5", highlightbackground="#E0E0E0", highlightthickness=1)
        info_frame.pack(fill=tk.X, pady=(0, 8))
        info = f"{_('prov_env_var')}:  {provider.env_var}"
        if provider.key_prefix:
            info += f"\n{_('prov_key_format')}:  {provider.key_prefix}..."
        if provider.base_url:
            info += f"\n{_('prov_endpoint')}:  {provider.base_url}"
        tk.Label(info_frame, text=info, font=("Consolas", 9), bg="#F5F5F5", fg=COLOR_TEXT,
                 justify=tk.LEFT).pack(padx=10, pady=7, anchor=tk.W)

        # Entry
        tk.Label(content, text=_("prov_api_key"), font=("Microsoft YaHei", 10, "bold"),
                 bg=COLOR_BG).pack(anchor=tk.W)

        ef = tk.Frame(content, bg=COLOR_BG)
        ef.pack(fill=tk.X, pady=(4, 6))
        self.show_key = tk.BooleanVar(value=False)
        self.entry = ttk.Entry(ef, font=("Consolas", 11), show="*")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.focus_set()
        ttk.Checkbutton(ef, text=_("prov_show"), variable=self.show_key,
                        command=lambda: self.entry.config(show="" if self.show_key.get() else "*")).pack(side=tk.RIGHT, padx=(6, 0))

        existing = os.environ.get(provider.env_var, "")
        if existing:
            self.entry.insert(0, existing)

        self.error_lbl = tk.Label(content, text="", fg=COLOR_ERROR, bg=COLOR_BG, font=("Microsoft YaHei", 8))
        self.error_lbl.pack(anchor=tk.W, pady=(0, 4))

        # Models
        if provider.models:
            tk.Label(content, text=_("prov_models") + ":", font=("Microsoft YaHei", 9, "bold"),
                     bg=COLOR_BG).pack(anchor=tk.W)
            mt = ", ".join(provider.models[:6])
            if len(provider.models) > 6:
                mt += f" ... (+{len(provider.models)-6})"
            tk.Label(content, text=mt, font=("Microsoft YaHei", 7), bg=COLOR_BG, fg=COLOR_MUTED,
                     wraplength=480, justify=tk.LEFT).pack(anchor=tk.W, pady=(1, 8))

        # Buttons
        bf = tk.Frame(content, bg=COLOR_BG)
        bf.pack(fill=tk.X, pady=(4, 0))
        ttk.Button(bf, text=_("btn_skip"), command=self._cancel).pack(side=tk.LEFT)
        if provider.console_url:
            ttk.Button(bf, text=_("prov_get_key"),
                       command=lambda: webbrowser.open(f"https://{provider.console_url}")).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(bf, text=_("btn_test"), command=self._test).pack(side=tk.RIGHT, padx=(0, 6))
        ttk.Button(bf, text="✓ " + _("btn_save"), command=self._save).pack(side=tk.RIGHT)

        self.dialog.protocol("WM_DELETE_WINDOW", self._cancel)
        self.entry.bind("<Return>", lambda e: self._save())
        self.dialog.wait_window()

    def _center(self, parent):
        parent.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        x = px + (pw - 530) // 2
        y = py + (ph - 440) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _save(self):
        key = self.entry.get().strip()
        pd = self.provider.to_dict()

        if not key and self.provider.category != "local":
            self.error_lbl.config(text=_("err_key_empty"))
            return
        if key:
            v = core.validate_key_for_provider(key, pd)
            if not v["success"]:
                self.error_lbl.config(text=v["error"])
                return

        result = core.save_provider_key(self.provider.id, key) if key else core.delete_provider_key(self.provider.id)
        if result["success"]:
            self.callback(self.provider.id)
            self.dialog.destroy()
        else:
            self.error_lbl.config(text=result["error"])

    def _cancel(self):
        self.dialog.destroy()

    def _test(self):
        key = self.entry.get().strip()
        if key:
            os.environ[self.provider.env_var] = key
        self.error_lbl.config(text=_("test_testing"), fg=COLOR_RUNNING)
        self.dialog.update()

        def _run():
            r = core.test_api_connection(self.provider.id)
            if r["success"]:
                self.error_lbl.config(text=f"{_('test_ok')} {r.get('endpoint','')}", fg=COLOR_DONE)
            else:
                self.error_lbl.config(text=f"{_('test_fail')}: {r.get('detail','')[:80]}", fg=COLOR_ERROR)
        threading.Thread(target=_run, daemon=True).start()


# ── Custom Provider Dialog ──────────────────────────────────────

class CustomProviderDialog:
    def __init__(self, parent, callback):
        self.callback = callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(_("custom_title"))
        self.dialog.geometry("480x520")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self._center(parent)
        self.dialog.configure(bg=COLOR_BG)

        content = ttk.Frame(self.dialog, padding=18)
        content.pack(fill=tk.BOTH, expand=True)

        tk.Label(content, text=_("custom_title"), font=("Microsoft YaHei", 13, "bold"),
                 bg=COLOR_BG).pack(anchor=tk.W)
        tk.Label(content, text="", font=("Microsoft YaHei", 8), bg=COLOR_BG,
                 fg=COLOR_MUTED).pack(anchor=tk.W, pady=(1, 10))

        self.fields = {}
        for field, label_key, placeholder in [
            ("name", "custom_name", "My LLM Service"),
            ("id", "custom_id", "myllm"),
            ("env_var", "custom_env", "MYLLM_API_KEY"),
            ("key_prefix", "custom_prefix", "sk- (optional)"),
            ("base_url", "custom_url", "https://api.example.com/v1"),
            ("console_url", "custom_console", "console.example.com"),
            ("desc", "custom_desc", ""),
        ]:
            tk.Label(content, text=_(label_key), font=("Microsoft YaHei", 9), bg=COLOR_BG).pack(anchor=tk.W, pady=(6, 1))
            e = ttk.Entry(content, font=("Microsoft YaHei", 10))
            e.pack(fill=tk.X)
            self.fields[field] = e

        # Category
        tk.Label(content, text=_("custom_category"), font=("Microsoft YaHei", 9), bg=COLOR_BG).pack(anchor=tk.W, pady=(6, 1))
        self.cat_var = tk.StringVar(value="custom")
        cf = tk.Frame(content, bg=COLOR_BG)
        cf.pack(fill=tk.X)
        for cid, cinfo in CATEGORIES.items():
            ttk.Radiobutton(cf, text=_(f"cat_{cid}"), variable=self.cat_var, value=cid).pack(side=tk.LEFT, padx=(0, 10))

        self.error_lbl = tk.Label(content, text="", fg=COLOR_ERROR, bg=COLOR_BG, font=("Microsoft YaHei", 8))
        self.error_lbl.pack(anchor=tk.W, pady=(8, 0))

        bf = tk.Frame(content, bg=COLOR_BG)
        bf.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(bf, text=_("btn_skip"), command=self.dialog.destroy).pack(side=tk.LEFT)
        ttk.Button(bf, text="✓ " + _("btn_save"), command=self._save).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def _center(self, parent):
        parent.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        x = px + (pw - 480) // 2
        y = py + (ph - 520) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _save(self):
        name = self.fields["name"].get().strip()
        pid = self.fields["id"].get().strip()
        env_var = self.fields["env_var"].get().strip()
        if not name or not pid or not env_var:
            self.error_lbl.config(text="Name, ID, Env Var are required")
            return

        provider = Provider(
            id=pid, name=name, category=self.cat_var.get(),
            env_var=env_var,
            key_prefix=self.fields["key_prefix"].get().strip(),
            base_url=self.fields["base_url"].get().strip(),
            console_url=self.fields["console_url"].get().strip(),
            description=self.fields["desc"].get().strip(),
            models=[], icon="⚡",
        )
        if save_custom_provider(provider):
            self.callback()
            self.dialog.destroy()
        else:
            self.error_lbl.config(text="Save failed")


# ── Entry ───────────────────────────────────────────────────────

def main():
    app = DeployApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
