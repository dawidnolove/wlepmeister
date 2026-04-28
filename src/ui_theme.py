"""
ui_theme.py - Style helpers for WLEPMEISTER.

All colour / font / icon constants are centralised in theme_colors.py.
This module re-exports those constants and provides convenience helpers for
styling tkinter widgets.
"""

import os
import sys
from pathlib import Path
import tkinter as tk

from .theme_colors import COLORS, FONTS, ICON_FILES  # noqa: F401 – re-exported

APP_TITLE = "WLEPMEISTER"


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = Path(__file__).resolve().parent
    return os.path.normpath(os.path.join(base_path, relative_path))


def apply_root_style(root):
    root.configure(bg=COLORS["bg"])


def _hex_to_colorref(hex_color):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return None
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)
    return red | (green << 8) | (blue << 16)


def apply_titlebar_color(root):
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return
    try:
        root.update_idletasks()
        hwnd = wintypes.HWND(root.winfo_id())
    except Exception:
        return

    color = _hex_to_colorref(COLORS["title_bar_bg"])
    if color is None:
        return

    DWMWA_CAPTION_COLOR = 35
    value = ctypes.c_int(color)
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWA_CAPTION_COLOR,
        ctypes.byref(value),
        ctypes.sizeof(value),
    )


def center_child_window(parent, window, width, height):
    parent.update_idletasks()
    main_x = parent.winfo_x()
    main_y = parent.winfo_y()
    main_width = max(parent.winfo_width(), width)
    main_height = max(parent.winfo_height(), height)
    center_x = main_x + (main_width // 2) - (width // 2)
    center_y = main_y + (main_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{center_x}+{center_y}")
    window.resizable(False, False)


def style_button(button, variant="primary"):
    if variant == "primary":
        bg = COLORS["accent"]
        fg = "#ffffff"
        active = COLORS["accent_dark"]
    elif variant == "secondary":
        bg = COLORS["surface_alt"]
        fg = COLORS["text"]
        active = COLORS["surface"]
    elif variant == "ghost":
        bg = COLORS["surface"]
        fg = COLORS["text"]
        active = COLORS["surface_alt"]
    elif variant == "danger":
        bg = COLORS["danger"]
        fg = "#ffffff"
        active = COLORS["danger_dark"]
    else:
        bg = COLORS["surface_alt"]
        fg = COLORS["text"]
        active = COLORS["surface"]

    button.configure(
        bg=bg,
        fg=fg,
        activebackground=active,
        activeforeground=fg,
        relief="flat",
        bd=0,
        highlightthickness=0,
        cursor="hand2",
        font=FONTS["body_bold"],
    )


def build_button(parent, text, command, variant="primary", icon=None, **kwargs):
    button = tk.Button(parent, text=text, command=command, **kwargs)
    if icon is not None:
        button.configure(image=icon, compound="left")
    style_button(button, variant=variant)
    return button


def style_entry(entry):
    entry.configure(
        bg=COLORS["surface_alt"],
        fg=COLORS["text"],
        insertbackground=COLORS["accent"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["border_focus"],
    )


def load_icons(scale=1):
    icons = {}
    for key, filename in ICON_FILES.items():
        path = resource_path(os.path.join("..", "media", "icons", filename))
        if not os.path.exists(path):
            continue
        image = tk.PhotoImage(file=path)
        if scale > 1:
            image = image.subsample(scale, scale)
        icons[key] = image
    return icons
