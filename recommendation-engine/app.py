"""
NexRec — AI Recommendation Engine
===================================
Premium dark-mode desktop application.
"""

import threading
import webbrowser
import tkinter as tk
import customtkinter as ctk
from recommender.search import search_stream
from recommender.filter import score_result, _keywords
from recommender.catalog_scraper import catalog_search_stream, CatalogItem, CATEGORY_CONFIG

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Colour palette ────────────────────────────────────────────────────────────
BG       = "#07070d"
BG_PANEL = "#0c0d18"
BG_CARD  = "#10121e"
BG_HOVER = "#161929"
BG_INPUT = "#181b2c"
BORDER   = "#1f2336"

TEXT_PRI = "#eef0ff"
TEXT_SEC = "#7080a0"
TEXT_MUT = "#363d58"

ACCENT   = "#6c63ff"
ACCENT_H = "#8b84ff"

SCORE_GREAT = "#10b981"
SCORE_OK    = "#f59e0b"
SCORE_LOW   = "#ef4444"

# Per-category accent colours
CAT_COLOR = {
    "All":    "#6c63ff",
    "Movies": "#e05c8a",
    "Music":  "#f59e0b",
    "Books":  "#10b981",
    "Tech":   "#38bdf8",
    "Food":   "#f97316",
    "Travel": "#06b6d4",
    "Sports": "#84cc16",
}
CAT_ICON = {
    "All":    "✦",
    "Movies": "🎬",
    "Music":  "🎵",
    "Books":  "📚",
    "Tech":   "⚙",
    "Food":   "🍜",
    "Travel": "✈",
    "Sports": "⚽",
}

CATEGORIES = list(CAT_COLOR.keys())


def score_color(pct: int) -> str:
    if pct >= 70: return SCORE_GREAT
    if pct >= 40: return SCORE_OK
    return SCORE_LOW


def blend(color: str, alpha: float, bg: str = BG_CARD) -> str:
    """Blend `color` over `bg` at `alpha` (0.0–1.0). Returns a valid 6-char hex."""
    def parse(h: str):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    cr, cg, cb = parse(color)
    br, bgr, bb = parse(bg)
    r = int(br + (cr - br) * alpha)
    g = int(bgr + (cg - bgr) * alpha)
    b = int(bb + (cb - bb) * alpha)
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Item Card ─────────────────────────────────────────────────────────────────

class ItemCard(ctk.CTkFrame):
    """Result card for catalogue categories (Movies, Music, Books, etc.)."""

    def __init__(self, parent, rank: int, item: CatalogItem,
                 cat: str = "all", **kwargs):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=14,
                         border_width=1, border_color=BORDER, **kwargs)

        self.url    = item.url
        self.accent = CAT_COLOR.get(cat.title(), ACCENT)
        self.columnconfigure(1, weight=1)

        # Hover glow
        self.bind("<Enter>", lambda _: self.configure(
            fg_color=BG_HOVER, border_color=self.accent))
        self.bind("<Leave>", lambda _: self.configure(
            fg_color=BG_CARD,  border_color=BORDER))

        # ── Left accent strip ─────────────────────────────────────────────────
        ctk.CTkFrame(self, width=5, corner_radius=3,
                     fg_color=self.accent).grid(
            row=0, column=0, rowspan=5, sticky="ns", padx=(12, 0), pady=14)

        # ── Header: rank · title · year+score chips ───────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=1, sticky="ew", padx=(14, 14), pady=(14, 0))
        hdr.columnconfigure(1, weight=1)

        # Rank pill
        rp = ctk.CTkFrame(hdr, fg_color=self.accent,
                          corner_radius=7, width=34, height=24)
        rp.grid(row=0, column=0, padx=(0, 10))
        rp.grid_propagate(False)
        ctk.CTkLabel(rp, text=str(rank),
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#fff").place(relx=.5, rely=.5, anchor="center")

        # Title
        ctk.CTkLabel(hdr, text=item.name,
                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                     text_color=TEXT_PRI, anchor="w").grid(
            row=0, column=1, sticky="ew")

        # Right chips
        chips = ctk.CTkFrame(hdr, fg_color="transparent")
        chips.grid(row=0, column=2, padx=(8, 0))

        if item.year:
            yf = ctk.CTkFrame(chips, fg_color=BG_INPUT, corner_radius=6)
            yf.pack(side="left", padx=(0, 6))
            ctk.CTkLabel(yf, text=f"  {item.year}  ",
                         font=ctk.CTkFont(size=10),
                         text_color=TEXT_SEC).pack()

        sc_c = score_color(item.score)
        sf = ctk.CTkFrame(chips, fg_color=blend(sc_c, 0.16),
                          corner_radius=6)
        sf.pack(side="left")
        ctk.CTkLabel(sf, text=f"  {item.score}%  ",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=sc_c).pack()

        # ── Metadata row ──────────────────────────────────────────────────────
        cfg = CATEGORY_CONFIG.get(cat.lower(), {})
        lbl = cfg.get("subtitle_label", "Info")
        meta = []
        if item.subtitle: meta.append(f"{lbl}: {item.subtitle}")
        if item.genre:    meta.append(item.genre)
        if meta:
            mr = ctk.CTkFrame(self, fg_color="transparent")
            mr.grid(row=1, column=1, sticky="ew", padx=(14, 14), pady=(5, 0))
            for i, part in enumerate(meta):
                if i:
                    ctk.CTkLabel(mr, text="  ·  ", font=ctk.CTkFont(size=11),
                                 text_color=TEXT_MUT).pack(side="left")
                ctk.CTkLabel(mr, text=part, font=ctk.CTkFont(size=11),
                             text_color=self.accent).pack(side="left")

        # ── Description ───────────────────────────────────────────────────────
        desc = (item.description or "").strip()
        if desc:
            if len(desc) > 200: desc = desc[:197] + "…"
            ctk.CTkLabel(self, text=desc,
                         font=ctk.CTkFont(family="Segoe UI", size=11),
                         text_color=TEXT_SEC, anchor="w",
                         justify="left", wraplength=610).grid(
                row=2, column=1, sticky="ew", padx=(14, 14), pady=(5, 0))

        # ── Thin divider ──────────────────────────────────────────────────────
        ctk.CTkFrame(self, fg_color=BORDER, height=1).grid(
            row=3, column=1, sticky="ew", padx=(14, 14), pady=(10, 0))

        # ── Footer: category chip + open button ───────────────────────────────
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=4, column=1, sticky="ew", padx=(14, 14), pady=(7, 12))

        icon = CAT_ICON.get(cat.title(), "•")
        cf = ctk.CTkFrame(foot, fg_color=blend(self.accent, 0.10),
                          corner_radius=8)
        cf.pack(side="left")
        ctk.CTkLabel(cf, text=f"  {icon}  {cat.title()}  ",
                     font=ctk.CTkFont(size=11),
                     text_color=self.accent).pack()

        if item.url:
            ctk.CTkButton(
                foot, text="Open  →", width=86, height=28,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=blend(self.accent, 0.10),
                hover_color=blend(self.accent, 0.20),
                border_width=1, border_color=self.accent,
                text_color=self.accent, corner_radius=8,
                command=lambda: webbrowser.open(self.url),
            ).pack(side="right")


# ── Web Result Card ───────────────────────────────────────────────────────────

class WebCard(ctk.CTkFrame):
    """Card for generic web search results (All category)."""

    def __init__(self, parent, rank: int, result, **kwargs):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=14,
                         border_width=1, border_color=BORDER, **kwargs)
        self.url = result.url
        pct      = result.match_pct
        col      = score_color(pct)
        self.columnconfigure(1, weight=1)

        self.bind("<Enter>", lambda _: self.configure(
            fg_color=BG_HOVER, border_color=ACCENT))
        self.bind("<Leave>", lambda _: self.configure(
            fg_color=BG_CARD,  border_color=BORDER))

        # Left bar
        ctk.CTkFrame(self, width=5, corner_radius=3, fg_color=ACCENT).grid(
            row=0, column=0, rowspan=4, sticky="ns", padx=(12, 0), pady=14)

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=1, sticky="ew", padx=(14, 14), pady=(14, 0))
        hdr.columnconfigure(1, weight=1)

        rp = ctk.CTkFrame(hdr, fg_color=ACCENT, corner_radius=7,
                          width=34, height=24)
        rp.grid(row=0, column=0, padx=(0, 10))
        rp.grid_propagate(False)
        ctk.CTkLabel(rp, text=str(rank),
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#fff").place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(hdr, text=result.title,
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     text_color=TEXT_PRI, anchor="w", wraplength=500).grid(
            row=0, column=1, sticky="ew")

        # Score chip
        sf = ctk.CTkFrame(hdr, fg_color=blend(col, 0.16), corner_radius=6)
        sf.grid(row=0, column=2, padx=(8, 0))
        ctk.CTkLabel(sf, text=f"  {pct}%  ",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=col).pack()

        # Snippet
        snip = (result.snippet or "").strip()
        if len(snip) > 200: snip = snip[:197] + "…"
        if snip:
            ctk.CTkLabel(self, text=snip,
                         font=ctk.CTkFont(family="Segoe UI", size=11),
                         text_color=TEXT_SEC, anchor="w",
                         justify="left", wraplength=610).grid(
                row=1, column=1, sticky="ew", padx=(14, 14), pady=(5, 0))

        # URL
        url_s = result.url[:60] + "…" if len(result.url) > 60 else result.url
        ctk.CTkLabel(self, text=url_s, font=ctk.CTkFont(size=10),
                     text_color=TEXT_MUT, anchor="w").grid(
            row=2, column=1, sticky="ew", padx=(14, 14), pady=(3, 0))

        # Divider
        ctk.CTkFrame(self, fg_color=BORDER, height=1).grid(
            row=3, column=1, sticky="ew", padx=14, pady=(10, 0))

        # Footer: progress bar + open
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=4, column=1, sticky="ew", padx=(14, 14), pady=(7, 12))
        foot.columnconfigure(1, weight=1)

        ctk.CTkLabel(foot, text=f"{pct}% match",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=col).grid(row=0, column=0)

        bar_bg = ctk.CTkFrame(foot, fg_color=BORDER, height=5,
                              corner_radius=3)
        bar_bg.grid(row=0, column=1, sticky="ew", padx=(10, 12))
        bar_bg.grid_propagate(False)
        ctk.CTkFrame(bar_bg, fg_color=col, height=5, corner_radius=3).place(
            relx=0, rely=0, relwidth=pct / 100, relheight=1.0)

        if result.url:
            ctk.CTkButton(
                foot, text="Open  →", width=86, height=28,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=blend(ACCENT, 0.10),
                hover_color=blend(ACCENT, 0.20),
                border_width=1, border_color=ACCENT,
                text_color=ACCENT, corner_radius=8,
                command=lambda: webbrowser.open(result.url),
            ).grid(row=0, column=2)


# ── Main Application ──────────────────────────────────────────────────────────

class NexRec(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Discover Anything · AI Recommendation Engine")
        self.geometry("860x740")
        self.minsize(680, 540)
        self.configure(fg_color=BG)

        self._cat      = "All"
        self._busy     = False
        self._n        = 0
        self._dot_job  = None

        self._build()
        self.bind("<Return>", lambda _: self._search())

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # ── Top header ────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=60)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(1, weight=1)
        hdr.grid_propagate(False)

        logo = ctk.CTkFrame(hdr, fg_color="transparent")
        logo.grid(row=0, column=0, padx=18, pady=8)

        # Blue diamond logo pill  
        BLUE = "#1a8cff"
        icon_pill = ctk.CTkFrame(logo, fg_color=blend(BLUE, 0.22, BG_PANEL),
                                 corner_radius=10, width=38, height=38)
        icon_pill.pack(side="left", padx=(0, 12))
        icon_pill.pack_propagate(False)
        ctk.CTkLabel(icon_pill, text="◆",
                     font=ctk.CTkFont(size=17), text_color=BLUE).place(
            relx=0.5, rely=0.5, anchor="center")

        # App name
        ctk.CTkLabel(logo, text="Discover Anything",
                     font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                     text_color=TEXT_PRI).pack(side="left")
        ctk.CTkLabel(logo, text="  ·  AI Powered",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUT).pack(side="left")

        self._status = ctk.CTkLabel(
            hdr, text="Ready",
            font=ctk.CTkFont(size=11), text_color=TEXT_MUT)
        self._status.grid(row=0, column=2, padx=22)

        ctk.CTkFrame(self, fg_color=BORDER, height=1).grid(
            row=1, column=0, sticky="ew")

        # ── Search panel ──────────────────────────────────────────────────────
        sp = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0)
        sp.grid(row=2, column=0, sticky="ew")
        sp.columnconfigure(0, weight=1)

        # Input row
        ir = ctk.CTkFrame(sp, fg_color="transparent")
        ir.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 10))
        ir.columnconfigure(0, weight=1)

        self._qvar = tk.StringVar()
        self._entry = ctk.CTkEntry(
            ir,
            placeholder_text="   🔍   Search movies, music, books, travel, food…",
            textvariable=self._qvar,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=BG_INPUT, border_color=ACCENT, border_width=1,
            text_color=TEXT_PRI, height=44, corner_radius=12,
        )
        self._entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        btns = ctk.CTkFrame(ir, fg_color="transparent")
        btns.grid(row=0, column=1)

        self._sbtn = ctk.CTkButton(
            btns, text="Search", width=100, height=44,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_H,
            text_color="#fff", corner_radius=12,
            command=self._search,
        )
        self._sbtn.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btns, text="✕", width=44, height=44,
            font=ctk.CTkFont(size=15),
            fg_color=BG_INPUT, hover_color=BG_HOVER,
            text_color=TEXT_SEC, border_width=1, border_color=BORDER,
            corner_radius=12, command=self._clear,
        ).pack(side="left")

        # Category pills
        pr = ctk.CTkFrame(sp, fg_color="transparent")
        pr.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 16))

        self._cbts: dict[str, ctk.CTkButton] = {}
        for cat in CATEGORIES:
            icon  = CAT_ICON.get(cat, "")
            label = f"{icon} {cat}"
            active = cat == "All"
            c = CAT_COLOR[cat]
            b = ctk.CTkButton(
                pr, text=label, width=86, height=30,
                font=ctk.CTkFont(family="Segoe UI", size=11,
                                 weight="bold" if active else "normal"),
                corner_radius=15,
                fg_color=c if active else BG_INPUT,
                text_color="#fff" if active else TEXT_SEC,
                hover_color=c,
                border_width=0,
                command=lambda c=cat: self._pick(c),
            )
            b.pack(side="left", padx=(0, 7))
            self._cbts[cat] = b

        ctk.CTkFrame(self, fg_color=BORDER, height=1).grid(
            row=2, column=0, sticky="sew")

        # ── Results area ──────────────────────────────────────────────────────
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color=BG, corner_radius=0,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color="#2a2f47",
        )
        self._scroll.grid(row=3, column=0, sticky="nsew", padx=18, pady=(14, 0))
        self._scroll.columnconfigure(0, weight=1)

        # ── Footer ────────────────────────────────────────────────────────────
        ftr = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=34)
        ftr.grid(row=4, column=0, sticky="ew")
        ftr.grid_propagate(False)
        ctk.CTkLabel(ftr,
                     text="NexRec  ·  AI-Powered Recommendations  ·  v1.0",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUT).pack(
            side="left", padx=18, pady=7)
        self._cnt = ctk.CTkLabel(ftr, text="",
                                 font=ctk.CTkFont(size=10), text_color=TEXT_MUT)
        self._cnt.pack(side="right", padx=18, pady=7)

        self._welcome()

    # ── Welcome screen ────────────────────────────────────────────────────────

    def _welcome(self):
        wrap = ctk.CTkFrame(self._scroll, fg_color="transparent")
        wrap.grid(row=0, column=0, pady=(40, 20), padx=40)

        # Big icon — blue diamond matching header logo
        BLUE = "#1a8cff"
        icon_bg = ctk.CTkFrame(wrap, fg_color=blend(BLUE, 0.18, BG),
                               corner_radius=22, width=76, height=76)
        icon_bg.pack()
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="◆",
                     font=ctk.CTkFont(size=36), text_color=BLUE).place(
            relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(wrap, text="Discover Anything",
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                     text_color=TEXT_PRI).pack(pady=(14, 0))

        ctk.CTkLabel(wrap,
                     text="Search movies, music, books, travel destinations, food & more — powered by AI",
                     font=ctk.CTkFont(size=12), text_color=TEXT_SEC).pack(pady=(4, 24))

        # ── Category showcase row ─────────────────────────────────────────────
        cats_row = ctk.CTkFrame(wrap, fg_color="transparent")
        cats_row.pack(pady=(0, 24))

        for cat, color in CAT_COLOR.items():
            if cat == "All":
                continue
            tile = ctk.CTkFrame(cats_row,
                                fg_color=blend(color, 0.10),
                                corner_radius=12, width=82, height=70,
                                border_width=1, border_color=blend(color, 0.20))
            tile.pack(side="left", padx=5)
            tile.pack_propagate(False)
            ctk.CTkLabel(tile, text=CAT_ICON[cat],
                         font=ctk.CTkFont(size=22)).pack(pady=(14, 0))
            ctk.CTkLabel(tile, text=cat,
                         font=ctk.CTkFont(size=10),
                         text_color=color).pack()

        # ── Suggestion chips ──────────────────────────────────────────────────
        ctk.CTkLabel(wrap, text="Try searching for:",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUT).pack()

        suggestions = [
            ("🎬  Telugu movies 2026",   "Movies"),
            ("🎵  AR Rahman songs",      "Music"),
            ("📚  Mystery thrillers",    "Books"),
            ("✈  Paris tourist places", "Travel"),
            ("🍜  Indian street food",   "Food"),
            ("⚽  IPL cricket players",  "Sports"),
        ]

        row1 = ctk.CTkFrame(wrap, fg_color="transparent")
        row1.pack(pady=(8, 0))
        row2 = ctk.CTkFrame(wrap, fg_color="transparent")
        row2.pack(pady=(6, 0))

        for i, (q, cat) in enumerate(suggestions):
            parent = row1 if i < 3 else row2
            c = CAT_COLOR.get(cat, ACCENT)
            ctk.CTkButton(
                parent, text=q,
                font=ctk.CTkFont(size=12),
                fg_color=blend(c, 0.09),
                border_width=1, border_color=blend(c, 0.27),
                text_color=TEXT_SEC,
                hover_color=blend(c, 0.20),
                corner_radius=20, height=34,
                command=lambda q=q, c=cat: self._quick(q, c),
            ).pack(side="left", padx=4)

    def _quick(self, query: str, cat: str):
        import re
        clean = re.sub(r"^[\U0001F300-\U0001FFFF\s✈⚽⚙]+", "", query).strip()
        self._qvar.set(clean)
        self._pick(cat)
        self._search()

    # ── Category picker ───────────────────────────────────────────────────────

    def _pick(self, cat: str):
        self._cat = cat
        c = CAT_COLOR[cat]
        for name, btn in self._cbts.items():
            if name == cat:
                btn.configure(fg_color=c, text_color="#fff",
                              font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
            else:
                btn.configure(fg_color=BG_INPUT, text_color=TEXT_SEC,
                              font=ctk.CTkFont(family="Segoe UI", size=11))

    # ── Loading dots ──────────────────────────────────────────────────────────

    def _dots_start(self):
        self._dot_i = 0
        self._dots_tick()

    def _dots_tick(self):
        frames = ["Searching  ·", "Searching  · ·", "Searching  · · ·"]
        self._status.configure(text=frames[self._dot_i % 3])
        self._dot_i += 1
        self._dot_job = self.after(400, self._dots_tick)

    def _dots_stop(self):
        if self._dot_job:
            self.after_cancel(self._dot_job)
            self._dot_job = None

    # ── Actions ───────────────────────────────────────────────────────────────

    def _clear(self):
        self._qvar.set("")
        self._wipe()
        self._status.configure(text="Ready")
        self._cnt.configure(text="")
        self._entry.focus()
        self._welcome()

    def _wipe(self):
        for w in self._scroll.winfo_children():
            w.destroy()
        self._n = 0

    def _set_status(self, t: str):
        self.after(0, lambda: self._status.configure(text=t))

    def _search(self):
        if self._busy:
            return
        q = self._qvar.get().strip()
        if not q:
            self._entry.focus()
            return

        self._wipe()
        self._busy = True
        self._n    = 0

        self._sbtn.configure(state="disabled", text="…")
        self._dots_start()

        is_cat = self._cat != "All"
        fq = f"{q} {self._cat.lower()}" if is_cat else q

        threading.Thread(
            target=self._cat_worker if is_cat else self._web_worker,
            args=(fq,), daemon=True,
        ).start()

    # ── Workers ───────────────────────────────────────────────────────────────

    def _cat_worker(self, fq: str):
        cat = self._cat.lower()
        for item in catalog_search_stream(fq, category=cat, max_items=12):
            self._n += 1
            n = self._n
            self.after(0, lambda m=item, k=n: self._add_item(m, k))
        self.after(0, self._done)

    def _web_worker(self, fq: str):
        kws = _keywords(fq)
        pos = 0
        for raw in search_stream(fq, max_results=12):
            sc = score_result(raw, kws, fq, pos)
            pos += 1
            if sc.match_pct >= 5:
                self._n += 1
                n = self._n
                self.after(0, lambda r=sc, k=n: self._add_web(r, k))
        self.after(0, self._done)

    def _add_item(self, item: CatalogItem, n: int):
        ItemCard(self._scroll, n, item, cat=self._cat).grid(
            row=n - 1, column=0, sticky="ew", pady=(0, 10))
        self._cnt.configure(text=f"{n} result{'s' if n > 1 else ''}")

    def _add_web(self, result, n: int):
        WebCard(self._scroll, n, result).grid(
            row=n - 1, column=0, sticky="ew", pady=(0, 10))
        self._cnt.configure(text=f"{n} result{'s' if n > 1 else ''}")

    def _done(self):
        self._busy = False
        self._dots_stop()
        self._sbtn.configure(state="normal", text="Search")

        if self._n == 0:
            ctk.CTkLabel(
                self._scroll,
                text="No results found — try a different query.",
                font=ctk.CTkFont(size=13), text_color=TEXT_MUT,
            ).grid(row=0, column=0, pady=60)
            self._status.configure(text="No results.")
        else:
            self._status.configure(text=f"✓  {self._n} results found")


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    NexRec().mainloop()
