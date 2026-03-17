import tkinter as tk
from tkinter import messagebox

from db import create_user, login_user, user_exists

LOGIN_WINDOW_WIDTH = 350
LOGIN_WINDOW_HEIGHT = 240
REGISTER_WINDOW_WIDTH = 350
REGISTER_WINDOW_HEIGHT = 220


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
        self._center_child_window(login_window, LOGIN_WINDOW_WIDTH, LOGIN_WINDOW_HEIGHT)

        main_frame = tk.Frame(login_window, padx=30, pady=20)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="đź” Logowanie", font=("Arial", 16, "bold")).pack(pady=(0, 12))
        tk.Label(main_frame, text="Username:", anchor="w").pack(fill="x")
        username_entry = tk.Entry(main_frame, font=("Arial", 12))
        username_entry.pack(fill="x", pady=(2, 8), ipady=4)
        username_entry.focus()

        tk.Label(main_frame, text="Password:", anchor="w").pack(fill="x")
        password_entry = tk.Entry(main_frame, show="*", font=("Arial", 12))
        password_entry.pack(fill="x", pady=(2, 12), ipady=4)

        def attempt_login():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                messagebox.showerror("Error", "All fields required")
                return
            if login_user(username, password):
                self.current_user = username
                self.okno.title(f"{self.APP_TITLE} - {username}")
                messagebox.showinfo("Success", f"Logged in as {username}")
                login_window.destroy()
                if hasattr(self, "on_login_state_changed"):
                    self.on_login_state_changed()
                return
            messagebox.showerror("Error", "Wrong username or password")

        tk.Button(
            main_frame,
            text="Login",
            command=attempt_login,
            font=("Arial", 11),
            width=15,
            pady=5,
        ).pack()

        login_window.bind("<Return>", lambda _event: attempt_login())

    def open_register_window(self):
        register_window = tk.Toplevel(self.okno)
        register_window.title("Register")
        self._center_child_window(register_window, REGISTER_WINDOW_WIDTH, REGISTER_WINDOW_HEIGHT)

        main_frame = tk.Frame(register_window, padx=30, pady=20)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="đź“ť Rejestracja", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        tk.Label(main_frame, text="Username:", anchor="w").pack(fill="x")
        username_entry = tk.Entry(main_frame, font=("Arial", 12))
        username_entry.pack(fill="x", pady=(2, 10), ipady=5)
        username_entry.focus()

        tk.Label(main_frame, text="Password:", anchor="w").pack(fill="x")
        password_entry = tk.Entry(main_frame, show="*", font=("Arial", 12))
        password_entry.pack(fill="x", pady=(2, 20), ipady=5)

        def attempt_register():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                messagebox.showerror("Error", "All fields required")
                return
            if user_exists(username):
                messagebox.showerror("Error", "Username already exists")
                return
            if create_user(username, password):
                messagebox.showinfo("Success", "Account created!")
                register_window.destroy()
                return
            messagebox.showerror("Error", "Could not create account")

        tk.Button(
            main_frame,
            text="Register",
            command=attempt_register,
            font=("Arial", 11),
            width=15,
            pady=5,
        ).pack()

        register_window.bind("<Return>", lambda _event: attempt_register())

    def logout(self):
        if self.current_user:
            self.current_user = None
            self.okno.title(self.APP_TITLE)
            messagebox.showinfo("Logout", "Logged out")
            if hasattr(self, "on_login_state_changed"):
                self.on_login_state_changed()
            return
        messagebox.showinfo("Info", "No user logged in")
