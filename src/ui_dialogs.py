import tkinter as tk

from .theme_colors import COLORS, FONTS
from .ui_theme import apply_titlebar_color

TITLE_FONT = FONTS["section"]
BODY_FONT = FONTS["body"]


def _center_child_window(parent, window, width, height):
    parent.update_idletasks()
    main_x = parent.winfo_x()
    main_y = parent.winfo_y()
    main_width = max(parent.winfo_width(), width)
    main_height = max(parent.winfo_height(), height)
    center_x = main_x + (main_width // 2) - (width // 2)
    center_y = main_y + (main_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{center_x}+{center_y}")
    window.resizable(False, False)


def _build_dialog(parent, title, message, width, height, buttons, default=None):
    dialog_bg = COLORS["surface"]
    text_color = COLORS["text"]
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    dialog.configure(bg=dialog_bg)
    apply_titlebar_color(dialog)
    _center_child_window(parent, dialog, width, height)

    result = {"value": default}

    container = tk.Frame(dialog, bg=dialog_bg, padx=16, pady=14)
    container.pack(fill="both", expand=True)

    tk.Label(
        container,
        text=title,
        bg=dialog_bg,
        fg=text_color,
        font=TITLE_FONT,
    ).pack(anchor="w", pady=(0, 10))

    tk.Label(
        container,
        text=message,
        bg=dialog_bg,
        fg=text_color,
        font=BODY_FONT,
        wraplength=width - 32,
        justify="left",
    ).pack(anchor="w")

    buttons_frame = tk.Frame(container, bg=dialog_bg)
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
            fg = "#ffffff"
            active_bg = COLORS["accent_dark"]
        else:
            bg = COLORS["surface_alt"]
            fg = COLORS["text"]
            active_bg = COLORS["border"]
        tk.Button(
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
        ).pack(side="right", padx=(0, 8))

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
    dialog_bg = COLORS["surface"]
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    dialog.configure(bg=dialog_bg)
    apply_titlebar_color(dialog)
    _center_child_window(parent, dialog, 430, 210)

    result = {"value": None}

    container = tk.Frame(dialog, bg=dialog_bg, padx=16, pady=14)
    container.pack(fill="both", expand=True)

    tk.Label(
        container,
        text=title,
        bg=dialog_bg,
        fg=COLORS["text"],
        font=TITLE_FONT,
    ).pack(anchor="w", pady=(0, 10))

    tk.Label(
        container,
        text=message,
        bg=dialog_bg,
        fg=COLORS["text"],
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

    buttons = tk.Frame(container, bg=dialog_bg)
    buttons.pack(fill="x")

    def submit():
        value = value_var.get().strip()
        if not value:
            show_error(dialog, "Invalid name", "Value cannot be empty.")
            return
        result["value"] = value
        dialog.destroy()

    tk.Button(
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
    ).pack(side="right")
    tk.Button(
        buttons,
        text="Save",
        width=10,
        bg=COLORS["accent"],
        fg="#ffffff",
        activebackground=COLORS["accent_dark"],
        activeforeground="#ffffff",
        command=submit,
        relief="flat",
        bd=0,
        cursor="hand2",
        font=BODY_FONT,
    ).pack(side="right", padx=(0, 8))

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

    def destroy_message():
        try:
            message.destroy()
        except tk.TclError:
            pass

    parent.after(duration, destroy_message)
