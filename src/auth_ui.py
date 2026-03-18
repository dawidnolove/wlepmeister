import tkinter as tk

from db import create_user, login_user, user_exists
from theme_colors import COLORS, FONTS
from ui_dialogs import show_error, show_info

LOGIN_WINDOW_WIDTH = 350
LOGIN_WINDOW_HEIGHT = 260
REGISTER_WINDOW_WIDTH = 350
REGISTER_WINDOW_HEIGHT = 240

_DIALOG_BG = COLORS["surface"]
_TEXT = COLORS["text"]
_MUTED = COLORS["muted"]
_ENTRY_BG = COLORS["surface_alt"]
_BTN_BG = COLORS["accent"]
_BTN_ACTIVE = COLORS["accent_dark"]
_TITLE_FONT = FONTS["section"]
_BODY_FONT = FONTS["body"]


class AuthUIMixin:
    def _center_child_window(self, window, width, height):
        main_x = self.okno.winfo_x()
        main_y = self.okno.winfo_y()
        main_width = self.okno.winfo_width()
        main_height = self.okno.winfo_height()
        center_x = main_x + (main_width // 2) - (width // 2)
        center_y = main_y + (main_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{center_x}+{center_y}")
        window.resizable(False, False)

    def open_login_window(self):
        login_window = tk.Toplevel(self.okno)
        login_window.title("Login")
        login_window.configure(bg=_DIALOG_BG)
        self._center_child_window(login_window, LOGIN_WINDOW_WIDTH, LOGIN_WINDOW_HEIGHT)

        main_frame = tk.Frame(login_window, padx=30, pady=20, bg=_DIALOG_BG)
        main_frame.pack(expand=True, fill="both")

        tk.Label(
            main_frame,
            text="Logowanie",
            font=_TITLE_FONT,
            bg=_DIALOG_BG,
            fg=_TEXT,
        ).pack(pady=(0, 12))
        tk.Label(
            main_frame,
            text="Username:",
            anchor="w",
            bg=_DIALOG_BG,
            fg=_MUTED,
            font=_BODY_FONT,
        ).pack(fill="x")
        username_entry = tk.Entry(
            main_frame,
            font=FONTS["body"],
            relief="flat",
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        username_entry.pack(fill="x", pady=(2, 8), ipady=4)
        username_entry.focus()

        tk.Label(
            main_frame,
            text="Password:",
            anchor="w",
            bg=_DIALOG_BG,
            fg=_MUTED,
            font=_BODY_FONT,
        ).pack(fill="x")
        password_entry = tk.Entry(
            main_frame,
            show="*",
            font=FONTS["body"],
            relief="flat",
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        password_entry.pack(fill="x", pady=(2, 12), ipady=4)

        def attempt_login():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                show_error(self.okno, "Error", "All fields required")
                return
            if login_user(username, password):
                self.current_user = username
                self.okno.title(f"{self.APP_TITLE} - {username}")
                show_info(self.okno, "Success", f"Logged in as {username}")
                login_window.destroy()
                if hasattr(self, "on_login_state_changed"):
                    self.on_login_state_changed()
                return
            show_error(self.okno, "Error", "Wrong username or password")

        tk.Button(
            main_frame,
            text="Login",
            command=attempt_login,
            font=_BODY_FONT,
            width=15,
            pady=5,
            bg=_BTN_BG,
            fg="#ffffff",
            activebackground=_BTN_ACTIVE,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack()

        login_window.bind("<Return>", lambda _event: attempt_login())

    def open_register_window(self):
        register_window = tk.Toplevel(self.okno)
        register_window.title("Register")
        register_window.configure(bg=_DIALOG_BG)
        self._center_child_window(register_window, REGISTER_WINDOW_WIDTH, REGISTER_WINDOW_HEIGHT)

        main_frame = tk.Frame(register_window, padx=30, pady=20, bg=_DIALOG_BG)
        main_frame.pack(expand=True, fill="both")

        tk.Label(
            main_frame,
            text="Rejestracja",
            font=_TITLE_FONT,
            bg=_DIALOG_BG,
            fg=_TEXT,
        ).pack(pady=(0, 20))
        tk.Label(
            main_frame,
            text="Username:",
            anchor="w",
            bg=_DIALOG_BG,
            fg=_MUTED,
            font=_BODY_FONT,
        ).pack(fill="x")
        username_entry = tk.Entry(
            main_frame,
            font=FONTS["body"],
            relief="flat",
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        username_entry.pack(fill="x", pady=(2, 10), ipady=5)
        username_entry.focus()

        tk.Label(
            main_frame,
            text="Password:",
            anchor="w",
            bg=_DIALOG_BG,
            fg=_MUTED,
            font=_BODY_FONT,
        ).pack(fill="x")
        password_entry = tk.Entry(
            main_frame,
            show="*",
            font=FONTS["body"],
            relief="flat",
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        password_entry.pack(fill="x", pady=(2, 20), ipady=5)

        def attempt_register():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                show_error(self.okno, "Error", "All fields required")
                return
            if user_exists(username):
                show_error(self.okno, "Error", "Username already exists")
                return
            if create_user(username, password):
                show_info(self.okno, "Success", "Account created!")
                register_window.destroy()
                return
            show_error(self.okno, "Error", "Could not create account")

        tk.Button(
            main_frame,
            text="Register",
            command=attempt_register,
            font=_BODY_FONT,
            width=15,
            pady=5,
            bg=_BTN_BG,
            fg="#ffffff",
            activebackground=_BTN_ACTIVE,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack()

        register_window.bind("<Return>", lambda _event: attempt_register())

    def logout(self):
        if self.current_user:
            self.current_user = None
            self.okno.title(self.APP_TITLE)
            show_info(self.okno, "Logout", "Logged out")
            if hasattr(self, "on_login_state_changed"):
                self.on_login_state_changed()
            return
        show_info(self.okno, "Info", "No user logged in")
