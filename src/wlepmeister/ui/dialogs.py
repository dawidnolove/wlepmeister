import tkinter as tk

from .palette import COLORS, FONTS
from .theme import apply_macos_button_style

DIALOG_BG = COLORS["surface"]
TEXT_COLOR = COLORS["text"]
BUTTON_BG = COLORS["accent"]
BUTTON_BG_ALT = COLORS["surface_alt"]
BUTTON_ACTIVE = COLORS["accent_dark"]
TITLE_FONT = FONTS["section"]
BODY_FONT = FONTS["body"]


def _center_child_window(parent, window, width, height):
    parent.update_idletasks()
    main_x = parent.winfo_x()
    main_y = parent.winfo_y()
    main_width = parent.winfo_width()
    main_height = parent.winfo_height()
    center_x = main_x + (main_width // 2) - (width // 2)
    center_y = main_y + (main_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{center_x}+{center_y}")
    window.resizable(False, False)


def _build_dialog(parent, title, message, width, height, buttons, default=None):
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    dialog.configure(bg=DIALOG_BG)
    _center_child_window(parent, dialog, width, height)

    result = {"value": default}

    container = tk.Frame(dialog, bg=DIALOG_BG, padx=16, pady=14)
    container.pack(fill="both", expand=True)

    tk.Label(
        container,
        text=title,
        bg=DIALOG_BG,
        fg=TEXT_COLOR,
        font=TITLE_FONT,
    ).pack(anchor="w", pady=(0, 10))

    tk.Label(
        container,
        text=message,
        bg=DIALOG_BG,
        fg=TEXT_COLOR,
        font=BODY_FONT,
        wraplength=width - 32,
        justify="left",
    ).pack(anchor="w")

    buttons_frame = tk.Frame(container, bg=DIALOG_BG)
    buttons_frame.pack(fill="x", pady=(14, 0))

    def make_cmd(value, cmd=None):
        def _inner():
            result["value"] = value
            if callable(cmd):
                cmd()
            dialog.destroy()

        return _inner

    for label, value, style in buttons:
        if style == "primary":
            bg = COLORS["accent"]
            fg = COLORS["text_on_accent"]
            active_bg = COLORS["accent_dark"]
        else:
            bg = COLORS["surface_alt"]
            fg = COLORS["text"]
            active_bg = COLORS["border"]
        button = tk.Button(
            buttons_frame,
            text=label,
            width=10,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            command=make_cmd(value),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=BODY_FONT,
        )
        apply_macos_button_style(button, variant=style)
        button.pack(side="right", padx=(0, 8))

    dialog.protocol("WM_DELETE_WINDOW", make_cmd(default))
    dialog.wait_window()
    return result["value"]


def show_info(parent, title, message):
    _build_dialog(
        parent,
        title,
        message,
        width=420,
        height=190,
        buttons=[("OK", True, "primary")],
        default=True,
    )


def show_warning(parent, title, message):
    _build_dialog(
        parent,
        title,
        message,
        width=420,
        height=190,
        buttons=[("OK", True, "primary")],
        default=True,
    )


def show_error(parent, title, message):
    _build_dialog(
        parent,
        title,
        message,
        width=430,
        height=200,
        buttons=[("OK", True, "primary")],
        default=True,
    )


def ask_yes_no(parent, title, message, yes_text="Yes", no_text="No"):
    return bool(
        _build_dialog(
            parent,
            title,
            message,
            width=430,
            height=200,
            buttons=[
                (no_text, False, "secondary"),
                (yes_text, True, "primary"),
            ],
            default=False,
        )
    )


def prompt_string(parent, title, message, initial_value=""):
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    dialog.configure(bg=DIALOG_BG)
    _center_child_window(parent, dialog, 430, 210)

    result = {"value": None}

    container = tk.Frame(dialog, bg=DIALOG_BG, padx=16, pady=14)
    container.pack(fill="both", expand=True)

    tk.Label(
        container,
        text=title,
        bg=DIALOG_BG,
        fg=TEXT_COLOR,
        font=TITLE_FONT,
    ).pack(anchor="w", pady=(0, 10))

    tk.Label(
        container,
        text=message,
        bg=DIALOG_BG,
        fg=TEXT_COLOR,
        font=BODY_FONT,
    ).pack(anchor="w")

    value_var = tk.StringVar(value=initial_value)
    entry = tk.Entry(
        container,
        textvariable=value_var,
        font=FONTS["body"],
        relief="flat",
        bg=COLORS["surface_alt"],
        fg=COLORS["text"],
        insertbackground=COLORS["accent"],
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["border_focus"],
    )
    entry.pack(fill="x", pady=(6, 12), ipady=5)
    entry.focus_set()

    buttons = tk.Frame(container, bg=DIALOG_BG)
    buttons.pack(fill="x")

    def submit():
        value = value_var.get().strip()
        if not value:
            show_error(dialog, "Invalid name", "Value cannot be empty.")
            return
        result["value"] = value
        dialog.destroy()

    cancel_btn = tk.Button(
        buttons,
        text="Cancel",
        width=10,
        bg=COLORS["surface_alt"],
        fg=COLORS["text"],
        activebackground=COLORS["border"],
        activeforeground=COLORS["text"],
        command=dialog.destroy,
        relief="flat",
        bd=0,
        cursor="hand2",
        font=BODY_FONT,
    )
    apply_macos_button_style(cancel_btn, variant="secondary")
    cancel_btn.pack(side="right")
    save_btn = tk.Button(
        buttons,
        text="Save",
        width=10,
        bg=COLORS["accent"],
        fg=COLORS["text_on_accent"],
        activebackground=COLORS["accent_dark"],
        activeforeground=COLORS["text_on_accent"],
        command=submit,
        relief="flat",
        bd=0,
        cursor="hand2",
        font=BODY_FONT,
    )
    apply_macos_button_style(save_btn, variant="primary")
    save_btn.pack(side="right", padx=(0, 8))

    dialog.bind("<Return>", lambda _event: submit())
    dialog.wait_window()
    return result["value"]


def show_toast(parent, text, duration=2000):
    message = tk.Label(
        parent,
        text=text,
        bg=COLORS["toast_bg"],
        fg=COLORS["toast_text"],
        font=BODY_FONT,
        padx=12,
        pady=6,
    )
    message.place(relx=1.0, rely=1.0, anchor="se")
    parent.after(duration, message.destroy)
