"""
theme_colors.py - Theme constants for WLEPMEISTER.
"""

# ---------------------------------------------------------------------------
# Color palettes
# ---------------------------------------------------------------------------
DARK_COLORS = {
    # backgrounds
    "bg":             "#0d1117",
    "panel":          "#161b27",
    "panel_header":   "#1c2236",
    "surface":        "#1e2435",
    "surface_alt":    "#252c3d",
    "canvas":         "#111520",
    "title_bar_bg":   "#0b0f14",
    "menu_bg":        "#0b0f14",
    "menu_fg":        "#ffffff",
    "menu_active_bg": "#151a22",
    "menu_active_fg": "#ffffff",

    # typography
    "text":           "#e8eaf6",
    "muted":          "#9aa4d1",
    "text_inverse":   "#0d1117",

    # accent
    "accent":         "#7c4dff",
    "accent_dark":    "#5e35b1",
    "accent_soft":    "#2a1f4f",

    # secondary accent
    "accent2":        "#00e5ff",
    "accent2_dark":   "#00b2cc",

    # borders
    "border":         "#2d3550",
    "border_focus":   "#7c4dff",

    # status
    "success":        "#00e676",
    "warning":        "#ffab40",
    "danger":         "#ff1744",
    "danger_dark":    "#b71c1c",

    # toast
    "toast_bg":       "#1c2236",
    "toast_text":     "#00e5ff",

    # list selection
    "select_bg":      "#5e35b1",
    "select_fg":      "#ffffff",

    # layer panel states
    "layer_active":   "#2a1f4f",
    "layer_inactive": "#1c2236",
}

LIGHT_COLORS = {
    # backgrounds
    "bg":             "#f7f8fb",
    "panel":          "#eef1f6",
    "panel_header":   "#e2e7f0",
    "surface":        "#ffffff",
    "surface_alt":    "#f1f4fa",
    "canvas":         "#f5f7fc",
    "title_bar_bg":   "#f7f8fb",
    "menu_bg":        "#f7f8fb",
    "menu_fg":        "#1e2432",
    "menu_active_bg": "#e7edf7",
    "menu_active_fg": "#1e2432",

    # typography
    "text":           "#1e2432",
    "muted":          "#5b677f",
    "text_inverse":   "#ffffff",

    # accent
    "accent":         "#2563eb",
    "accent_dark":    "#1e40af",
    "accent_soft":    "#dbe7ff",

    # secondary accent
    "accent2":        "#06b6d4",
    "accent2_dark":   "#0891b2",

    # borders
    "border":         "#d3d9e6",
    "border_focus":   "#2563eb",

    # status
    "success":        "#16a34a",
    "warning":        "#f59e0b",
    "danger":         "#ef4444",
    "danger_dark":    "#b91c1c",

    # toast
    "toast_bg":       "#1f2a44",
    "toast_text":     "#ffffff",

    # list selection
    "select_bg":      "#c7dbff",
    "select_fg":      "#1e2432",

    # layer panel states
    "layer_active":   "#dbe7ff",
    "layer_inactive": "#eef1f6",
}

THEMES = {
    "dark": DARK_COLORS,
    "light": LIGHT_COLORS,
}

CURRENT_THEME = "dark"
COLORS = DARK_COLORS.copy()


def set_theme(name):
    global CURRENT_THEME
    if name not in THEMES:
        return False
    COLORS.clear()
    COLORS.update(THEMES[name])
    CURRENT_THEME = name
    return True


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
# Icon filenames (relative to media/icons/)
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
