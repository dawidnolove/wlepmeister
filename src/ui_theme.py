import os
import sys
from pathlib import Path
import tkinter as tk

APP_TITLE = "WLEPMEISTER"

COLORS = {
    "bg": "#f6f4f0",
    "panel": "#ece6de",
    "panel_header": "#e0d7cd",
    "surface": "#ffffff",
    "surface_alt": "#f7f2ec",
    "text": "#1f2328",
    "muted": "#6a645d",
    "accent": "#e4572e",
    "accent_dark": "#c44722",
    "accent_soft": "#fde5dc",
    "border": "#d6cec4",
    "canvas": "#fbfbfb",
    "toast_bg": "#e7f3de",
    "toast_text": "#1d3b1d",
}

FONTS = {
    "title": ("Segoe UI Semibold", 16),
    "section": ("Segoe UI Semibold", 13),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI Semibold", 10),
    "small": ("Segoe UI", 9),
}

ICON_FILES = {
    "add": "add.png",
    "delete": "delete.png",
    "visibility": "visibility.png",
    "visibility_off": "visibility_off.png",
    "arrow_up": "arrow_up.png",
    "arrow_down": "arrow_down.png",
    "arrow_left": "arrow_left.png",
    "arrow_right": "arrow_right.png",
    "drag": "drag.png",
    "cloud_upload": "cloud_upload.png",
    "cloud_download": "cloud_download.png",
    "save": "save.png",
    "login": "login.png",
    "logout": "logout.png",
    "person_add": "person_add.png",
}


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = Path(__file__).resolve().parent
    return os.path.normpath(os.path.join(base_path, relative_path))


def apply_root_style(root):
    root.configure(bg=COLORS["bg"])


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
    elif variant == "ghost":
        bg = COLORS["surface"]
        fg = COLORS["text"]
        active = COLORS["surface_alt"]
    elif variant == "danger":
        bg = "#c0392b"
        fg = "#ffffff"
        active = "#a93226"
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
