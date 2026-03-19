"""
palette.py – Unified dark graphite theme constants for WLEPMEISTER.

Palette direction:
  * Graphite / slate neutrals
  * Deep blue primary accent
  * Warm brass secondary accent
  * Clear, accessible contrast on dark UI
"""

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
COLORS = {
    # ── backgrounds ──────────────────────────────────────────────────────────
    "bg":             "#0f1112",   # root window – charcoal
    "panel":          "#15181b",   # left/right side panels
    "panel_header":   "#1c2024",   # panel header strips
    "surface":        "#181c20",   # dialog / card surfaces
    "surface_alt":    "#222830",   # slightly lighter surface (hover, stripe)
    "canvas":         "#0d0f11",   # canvas drawing area
    "title_bar_bg":   "#0f1112",   # OS title bar (Windows)
    "menu_bg":        "#0f1112",   # top menu bar background (File/Edit/etc.)
    "menu_fg":        "#e9edf1",   # top menu bar text
    "menu_active_bg": "#181c20",   # top menu bar hover/active background
    "menu_active_fg": "#e9edf1",   # top menu bar hover/active text

    # ── typography ───────────────────────────────────────────────────────────
    "text":           "#e9edf1",   # primary text
    "muted":          "#b0bac4",   # secondary / placeholder text
    "text_inverse":   "#0f1112",   # text on bright buttons
    "text_on_accent": "#ffffff",   # text on accent buttons

    # ── accent – deep blue ────────────────────────────────────────────────
    "accent":         "#2f7a8f",   # primary accent (deep teal)
    "accent_dark":    "#245f6f",   # pressed / darker accent
    "accent_soft":    "#172c33",   # subtle tinted background

    # ── secondary accent – warm brass ─────────────────────────────────────
    "accent2":        "#c58b5a",   # secondary accent (copper)
    "accent2_dark":   "#a36f45",   # pressed copper

    # ── borders & dividers ───────────────────────────────────────────────────
    "border":         "#2a3137",   # default border / separator
    "border_focus":   "#2f7a8f",   # focused / active border

    # ── status & feedback ────────────────────────────────────────────────────
    "success":        "#4c9a7c",   # green confirmation
    "warning":        "#d7a458",   # orange warning
    "danger":         "#c85b57",   # destructive / error red
    "danger_dark":    "#a04845",   # pressed danger

    # ── toast notification ───────────────────────────────────────────────────
    "toast_bg":       "#1c2024",
    "toast_text":     "#c58b5a",

    # ── list selection ───────────────────────────────────────────────────────
    "select_bg":      "#245f6f",
    "select_fg":      "#ffffff",

    # ── layer panel item states ──────────────────────────────────────────────
    "layer_active":   "#172c33",   # active/selected layer row
    "layer_inactive": "#1c2024",   # inactive layer row
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
# Icon filenames  (relative to assets/icons/)
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
