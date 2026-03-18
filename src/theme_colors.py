"""
theme_colors.py – Unified dark space theme constants for WLEPMEISTER.

Inspired by the deep-space aesthetic of planetono.space:
  * Near-black / midnight-navy backgrounds
  * Electric violet / cyan accent palette
  * Crisp white-on-dark typography
"""

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
COLORS = {
    # ── backgrounds ──────────────────────────────────────────────────────────
    "bg":             "#0d1117",   # root window – near black / deep space
    "panel":          "#161b27",   # left/right side panels
    "panel_header":   "#1c2236",   # panel header strips
    "surface":        "#1e2435",   # dialog / card surfaces
    "surface_alt":    "#252c3d",   # slightly lighter surface (hover, stripe)
    "canvas":         "#111520",   # canvas drawing area
    "title_bar_bg":   "#000000",   # OS title bar (Windows)
    "menu_bg":        "#000000",   # top menu bar background (File/Edit/etc.)
    "menu_fg":        "#ffffff",   # top menu bar text
    "menu_active_bg": "#000000",   # top menu bar hover/active background
    "menu_active_fg": "#ffffff",   # top menu bar hover/active text

    # ── typography ───────────────────────────────────────────────────────────
    "text":           "#e8eaf6",   # primary text
    "muted":          "#7986cb",   # secondary / placeholder text
    "text_inverse":   "#0d1117",   # text on bright buttons

    # ── accent – electric violet ──────────────────────────────────────────
    "accent":         "#7c4dff",   # primary accent (violet)
    "accent_dark":    "#5e35b1",   # pressed / darker accent
    "accent_soft":    "#2a1f4f",   # subtle tinted background

    # ── secondary accent – cyan ───────────────────────────────────────────
    "accent2":        "#00e5ff",   # secondary accent (cyan)
    "accent2_dark":   "#00b2cc",   # pressed cyan

    # ── borders & dividers ───────────────────────────────────────────────────
    "border":         "#2d3550",   # default border / separator
    "border_focus":   "#7c4dff",   # focused / active border

    # ── status & feedback ────────────────────────────────────────────────────
    "success":        "#00e676",   # green confirmation
    "warning":        "#ffab40",   # orange warning
    "danger":         "#ff1744",   # destructive / error red
    "danger_dark":    "#b71c1c",   # pressed danger

    # ── toast notification ───────────────────────────────────────────────────
    "toast_bg":       "#1c2236",
    "toast_text":     "#00e5ff",

    # ── list selection ───────────────────────────────────────────────────────
    "select_bg":      "#5e35b1",
    "select_fg":      "#ffffff",

    # ── layer panel item states ──────────────────────────────────────────────
    "layer_active":   "#2a1f4f",   # active/selected layer row
    "layer_inactive": "#1c2236",   # inactive layer row
}

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
FONTS = {
    "title":      ("Segoe UI Semibold", 16),
    "section":    ("Segoe UI Semibold", 13),
    "body":       ("Segoe UI", 10),
    "body_bold":  ("Segoe UI Semibold", 10),
    "small":      ("Segoe UI", 9),
    "mono":       ("Consolas", 10),
}

# ---------------------------------------------------------------------------
# Icon filenames  (relative to media/icons/)
# ---------------------------------------------------------------------------
ICON_FILES = {
    "add":              "add.png",
    "delete":           "delete.png",
    "visibility":       "visibility.png",
    "visibility_off":   "visibility_off.png",
    "arrow_up":         "arrow_up.png",
    "arrow_down":       "arrow_down.png",
    "arrow_left":       "arrow_left.png",
    "arrow_right":      "arrow_right.png",
    "drag":             "drag.png",
    "cloud_upload":     "cloud_upload.png",
    "cloud_download":   "cloud_download.png",
    "save":             "save.png",
    "login":            "login.png",
    "logout":           "logout.png",
    "person_add":       "person_add.png",
}
