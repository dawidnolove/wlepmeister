import io
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from auth_ui import AuthUIMixin
from db import save_user_png_export
from layers_mod import LayerUIMixin

import subprocess, sys

#subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]) # bez potrzeby uruchamina osobno

APP_TITLE = "WLEPMEISTER"
APP_GEOMETRY = "900x600"
LAYERS_PANEL_MAX_WIDTH = 250
ALPHA_LEVELS = [0.5, 0.75, 1.0]


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ImageObject:
    def __init__(self, image_path, x=0, y=0):
        self.image_path = image_path
        self.x = x
        self.y = y
        with Image.open(image_path) as source_image:
            if source_image.format != "PNG":
                raise ValueError("Only PNG files are allowed.")
            self.pil_image = source_image.convert("RGBA").copy()
        self.photo_image = ImageTk.PhotoImage(self.pil_image)


class Wlepmeister(AuthUIMixin, LayerUIMixin):
    def __init__(self):
        self.okno = tk.Tk()
        icon_path = resource_path("../media/icon_py_128.ico")
        self.okno.iconbitmap(icon_path)
        self.okno.title(APP_TITLE)
        self.okno.geometry(APP_GEOMETRY)

        self.APP_TITLE = APP_TITLE
        self.dragging_object = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.layer_drag_anchor = None
        self.canvas = None
        self.workspace_frame = None
        self.current_user = None

        self.init_layers_state()
        self.setup_ui()
        self.add_layer()

    def add_image(self):
        if self.active_layer is None:
            messagebox.showwarning("No active layer", "Select or create a layer first.")
            return

        file_path = filedialog.askopenfilename(
            title="Import PNG image",
            filetypes=[("PNG image", "*.png")],
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".png"):
            messagebox.showerror("Invalid file", "Only PNG files are allowed.")
            return

        try:
            image_obj = ImageObject(file_path, x=30, y=30)
        except Exception as exc:
            messagebox.showerror("Import failed", f"Could not import image:\n{exc}")
            return

        self.active_layer.objects.append(image_obj)
        self.redraw_canvas()

    def _build_visible_layers_image(self):
        self.okno.update_idletasks()
        width = max(1, int(self.canvas.winfo_width()))
        height = max(1, int(self.canvas.winfo_height()))
        out_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        for layer in self.layers:
            if not layer.visible:
                continue
            for image_obj in layer.objects:
                out_image.paste(
                    image_obj.pil_image,
                    (int(image_obj.x), int(image_obj.y)),
                    image_obj.pil_image,
                )
        return out_image

    def export(self):
        if self.canvas is None:
            return

        save_path = filedialog.asksaveasfilename(
            title="Export PNG",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
        )
        if not save_path:
            return
        if not save_path.lower().endswith(".png"):
            save_path += ".png"

        rendered = self._build_visible_layers_image()
        png_buffer = io.BytesIO()
        rendered.save(png_buffer, format="PNG", optimize=True)
        png_bytes = png_buffer.getvalue()
        rendered.save(save_path, format="PNG", optimize=True)

        if self.current_user:
            saved_to_db = save_user_png_export(
                username=self.current_user,
                file_name=os.path.basename(save_path),
                png_bytes=png_bytes,
                image_size=rendered.size,
            )
            if saved_to_db:
                self.show_message("Exported PNG and saved to MongoDB", duration=2500)
            else:
                self.show_message("Exported PNG, MongoDB save failed", duration=3000)
        else:
            self.show_message("Exported PNG", duration=2000)

    def print(self):
        pass

    def new_window(self):
        new = Wlepmeister()
        new.run()

    def properties(self):
        pass

    def toggle_alpha(self):
        current_alpha = self.okno.attributes("-alpha")
        next_alpha_index = (ALPHA_LEVELS.index(current_alpha) + 1) % len(ALPHA_LEVELS)
        self.okno.attributes("-alpha", ALPHA_LEVELS[next_alpha_index])

    def show_message(self, text, duration=2000):
        message = tk.Label(self.okno, text=text, bg="#e3fca9", fg="#000000")
        message.place(relx=1.0, rely=1.0, anchor="se")
        self.okno.after(duration, message.destroy)

    def setup_ui(self):
        menu_bar = tk.Menu(self.okno)
        self.okno.configure(bg="#fca9b8")
        self.okno.configure(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New window", command=self.new_window)
        file_menu.add_command(label="Import image", command=self.add_image)
        file_menu.add_separator()
        file_menu.add_command(label="Export", command=self.export)
        file_menu.add_command(label="Print", command=self.print)
        file_menu.add_separator()
        file_menu.add_command(label="Properties", command=self.properties)
        file_menu.add_separator()
        file_menu.add_command(label="Close window", command=self.okno.destroy)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        edit_menu.add_separator()
        edit_menu.add_command(label="New layer", command=self.add_layer)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Alpha", command=self.toggle_alpha)

        account_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Account", menu=account_menu)
        account_menu.add_command(label="Login", command=self.open_login_window)
        account_menu.add_command(label="Register", command=self.open_register_window)
        account_menu.add_separator()
        account_menu.add_command(label="Logout", command=self.logout)

        self.setup_layers_panel(self.okno, max_layers_width=LAYERS_PANEL_MAX_WIDTH)
        self.setup_workspace_panel(self.okno)

    def _start_layer_drag(self, event):
        if self.active_layer is None:
            return
        self.layer_drag_anchor = (event.x, event.y)

    def _drag_active_layer(self, event):
        if self.layer_drag_anchor is None:
            return
        prev_x, prev_y = self.layer_drag_anchor
        dx = event.x - prev_x
        dy = event.y - prev_y
        if dx == 0 and dy == 0:
            return
        self.move_active_layer(dx, dy)
        self.layer_drag_anchor = (event.x, event.y)

    def _stop_layer_drag(self, _event):
        self.layer_drag_anchor = None

    def setup_workspace_panel(self, parent):
        self.workspace_frame = tk.Frame(parent, bg="#2b2b2b")
        self.workspace_frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.workspace_frame,
            bg="#f5f5f5",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.bind("<Shift-ButtonPress-1>", self._start_layer_drag)
        self.canvas.bind("<Shift-B1-Motion>", self._drag_active_layer)
        self.canvas.bind("<Shift-ButtonRelease-1>", self._stop_layer_drag)

    def redraw_canvas(self):
        if self.canvas is None:
            return

        self.canvas.delete("all")
        for layer in self.layers:
            if not layer.visible:
                continue
            for image_obj in layer.objects:
                self.canvas.create_image(
                    image_obj.x,
                    image_obj.y,
                    anchor="nw",
                    image=image_obj.photo_image,
                )

    def run(self):
        self.okno.mainloop()


if __name__ == "__main__":
    app = Wlepmeister()
    app.run()
