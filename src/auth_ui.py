import base64
import io
import re
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageOps, ImageTk

from .db import create_user, get_user_profile, login_user, update_user_profile, user_exists
from .theme_colors import COLORS, FONTS
from .ui_dialogs import show_error, show_info
from .ui_theme import build_button

LOGIN_WINDOW_WIDTH = 350
LOGIN_WINDOW_HEIGHT = 260
REGISTER_WINDOW_WIDTH = 350
REGISTER_WINDOW_HEIGHT = 260
PROFILE_WINDOW_WIDTH = 520
PROFILE_WINDOW_HEIGHT = 420

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9][0-9\s()\-]{5,}$")

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
            text="Login",
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

        build_button(
            main_frame,
            text="Login",
            command=attempt_login,
            width=15,
            pady=5,
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
            text="Register",
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

        build_button(
            main_frame,
            text="Register",
            command=attempt_register,
            width=15,
            pady=5,
        ).pack()

        register_window.bind("<Return>", lambda _event: attempt_register())

    def open_profile_window(self):
        if not self.current_user:
            show_info(self.okno, "Info", "No user logged in")
            return

        profile = get_user_profile(self.current_user) or {}
        avatar_b64 = profile.get("avatar_b64")

        profile_window = tk.Toplevel(self.okno)
        profile_window.title("User profile")
        profile_window.transient(self.okno)
        profile_window.grab_set()
        profile_window.configure(bg=_DIALOG_BG)
        self._center_child_window(profile_window, PROFILE_WINDOW_WIDTH, PROFILE_WINDOW_HEIGHT)

        outer = tk.Frame(profile_window, bg=_DIALOG_BG)
        outer.pack(expand=True, fill="both")

        canvas = tk.Canvas(outer, bg=_DIALOG_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        main_frame = tk.Frame(canvas, padx=24, pady=18, bg=_DIALOG_BG)
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def _on_frame_configure(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        main_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        tk.Label(
            main_frame,
            text="Profile",
            font=_TITLE_FONT,
            bg=_DIALOG_BG,
            fg=_TEXT,
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            main_frame,
            text=f"Username: {self.current_user}",
            font=_BODY_FONT,
            bg=_DIALOG_BG,
            fg=_MUTED,
        ).pack(anchor="w", pady=(0, 10))

        content = tk.Frame(main_frame, bg=_DIALOG_BG)
        content.pack(fill="both", expand=True)

        left = tk.Frame(content, bg=_DIALOG_BG)
        left.pack(side="left", fill="y", padx=(0, 18))

        avatar_label = tk.Label(left, bg=_DIALOG_BG)
        avatar_label.pack(pady=(0, 8))

        avatar_image_ref = {"image": None}
        avatar_data_ref = {"value": avatar_b64}

        def render_avatar(b64_value):
            if not b64_value:
                avatar_label.configure(text="No photo", fg=_MUTED, font=_BODY_FONT, image="")
                avatar_image_ref["image"] = None
                return
            try:
                raw = base64.b64decode(b64_value)
                image = Image.open(io.BytesIO(raw)).convert("RGBA")
                image = image.resize((128, 128), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
            except Exception:
                avatar_label.configure(text="Invalid photo", fg=_MUTED, font=_BODY_FONT, image="")
                avatar_image_ref["image"] = None
                return
            avatar_image_ref["image"] = photo
            avatar_label.configure(image=photo, text="")

        def change_avatar():
            file_path = filedialog.askopenfilename(
                parent=profile_window,
                title="Select profile image",
                filetypes=[
                    ("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp;*.tif;*.tiff"),
                    ("All files", "*.*"),
                ],
            )
            if not file_path:
                return
            try:
                image = Image.open(file_path)
                image = ImageOps.exif_transpose(image).convert("RGBA")
                image = image.resize((128, 128), Image.LANCZOS)
                buffer = io.BytesIO()
                image.save(buffer, format="PNG", optimize=True)
                b64_value = base64.b64encode(buffer.getvalue()).decode("utf-8")
            except Exception as exc:
                show_error(profile_window, "Error", f"Could not load image:\n{exc}")
                return
            avatar_data_ref["value"] = b64_value
            render_avatar(b64_value)

        render_avatar(avatar_b64)

        build_button(
            left,
            text="Change photo",
            command=change_avatar,
            width=15,
            pady=4,
            variant="secondary",
        ).pack(pady=(4, 0))

        right = tk.Frame(content, bg=_DIALOG_BG)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(
            right,
            text="Email:",
            anchor="w",
            bg=_DIALOG_BG,
            fg=_MUTED,
            font=_BODY_FONT,
        ).pack(fill="x")
        email_var = tk.StringVar(value=profile.get("email") or "")
        email_entry = tk.Entry(
            right,
            textvariable=email_var,
            font=_BODY_FONT,
            relief="flat",
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        email_entry.pack(fill="x", pady=(4, 12), ipady=4)

        tk.Label(
            right,
            text="First name:",
            anchor="w",
            bg=_DIALOG_BG,
            fg=_MUTED,
            font=_BODY_FONT,
        ).pack(fill="x")
        first_name_var = tk.StringVar(value=profile.get("first_name") or "")
        first_name_entry = tk.Entry(
            right,
            textvariable=first_name_var,
            font=_BODY_FONT,
            relief="flat",
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        first_name_entry.pack(fill="x", pady=(4, 12), ipady=4)

        tk.Label(
            right,
            text="Last name:",
            anchor="w",
            bg=_DIALOG_BG,
            fg=_MUTED,
            font=_BODY_FONT,
        ).pack(fill="x")
        last_name_var = tk.StringVar(value=profile.get("last_name") or "")
        last_name_entry = tk.Entry(
            right,
            textvariable=last_name_var,
            font=_BODY_FONT,
            relief="flat",
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        last_name_entry.pack(fill="x", pady=(4, 12), ipady=4)

        tk.Label(
            right,
            text="Phone number:",
            anchor="w",
            bg=_DIALOG_BG,
            fg=_MUTED,
            font=_BODY_FONT,
        ).pack(fill="x")
        phone_var = tk.StringVar(value=profile.get("phone") or "")
        phone_entry = tk.Entry(
            right,
            textvariable=phone_var,
            font=_BODY_FONT,
            relief="flat",
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        phone_entry.pack(fill="x", pady=(4, 12), ipady=4)

        tk.Label(
            right,
            text="Bio:",
            anchor="w",
            bg=_DIALOG_BG,
            fg=_MUTED,
            font=_BODY_FONT,
        ).pack(fill="x")
        bio_text = tk.Text(
            right,
            height=6,
            font=_BODY_FONT,
            relief="flat",
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
            wrap="word",
        )
        bio_text.pack(fill="both", expand=True, pady=(4, 12))
        bio_text.insert("1.0", profile.get("bio") or "")

        buttons = tk.Frame(main_frame, bg=_DIALOG_BG)
        buttons.pack(fill="x", pady=(6, 0))

        def save_profile():
            email_value = email_var.get().strip()
            first_name_value = first_name_var.get().strip()
            last_name_value = last_name_var.get().strip()
            phone_value = phone_var.get().strip()
            bio_value = bio_text.get("1.0", "end").strip()
            if email_value and not EMAIL_RE.match(email_value):
                show_error(profile_window, "Error", "Invalid email address.")
                return
            if phone_value and not PHONE_RE.match(phone_value):
                show_error(profile_window, "Error", "Invalid phone number.")
                return
            if not update_user_profile(
                self.current_user,
                email=email_value or None,
                first_name=first_name_value,
                last_name=last_name_value,
                phone=phone_value,
                bio=bio_value,
                avatar_b64=avatar_data_ref["value"],
            ):
                show_error(profile_window, "Error", "Could not update profile.")
                return
            if hasattr(self, "update_user_badge"):
                self.update_user_badge()
            show_info(profile_window, "Saved", "Profile updated.")

        build_button(
            buttons,
            text="Save",
            command=save_profile,
            width=12,
            pady=5,
        ).pack(side="right")
        build_button(
            buttons,
            text="Close",
            command=profile_window.destroy,
            width=12,
            pady=5,
            variant="secondary",
        ).pack(side="right", padx=(0, 8))

    def logout(self):
        if self.current_user:
            self.current_user = None
            self.okno.title(self.APP_TITLE)
            show_info(self.okno, "Logout", "Logged out")
            if hasattr(self, "on_login_state_changed"):
                self.on_login_state_changed()
            return
        show_info(self.okno, "Info", "No user logged in")
