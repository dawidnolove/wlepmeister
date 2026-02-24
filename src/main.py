import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from layers_mod import LayerUIMixin


def resource_path(relative_path):
    """absolute path for build"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ============================================
# KLASY
# ============================================
class ImageObject:
    """Single imported image bound to one layer."""

    def __init__(self, image_path, x=0, y=0):
        self.image_path = image_path
        self.x = x
        self.y = y
        with Image.open(image_path) as source_image:
            if source_image.format != "PNG":
                raise ValueError("Only PNG files are allowed.")
            self.pil_image = source_image.convert("RGBA").copy()
        self.photo_image = ImageTk.PhotoImage(self.pil_image)


# ============================================
# MAIN
# ============================================
class Wlepmeister(LayerUIMixin):
    def __init__(self):
        self.okno = tk.Tk()
        icon_path = resource_path("../media/icon_py_128.ico")
        self.okno.iconbitmap(icon_path)
        self.okno.title("WLEPMEISTER")
        self.okno.geometry("900x600")

        self.init_layers_state()

        self.dragging_object = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.canvas = None
        self.workspace_frame = None

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

    def export(self):
        pass

    def print(self):
        pass

    def new_window(self):
        new = Wlepmeister()
        new.run()

    def properties(self):
        pass

    def toggle_alpha(self):
        alpha_levels = [0.5, 0.75, 1]
        current_alpha_levels = self.okno.attributes("-alpha")
        next_alpha_level = (alpha_levels.index(current_alpha_levels) + 1) % len(alpha_levels)
        self.okno.attributes("-alpha", alpha_levels[next_alpha_level])

    def show_message(self, text, duration=2000):
        message = tk.Label(self.okno, text=text, bg="#e3fca9", fg="#000000")
        message.place(relx=1.0, rely=1.0, anchor="se")
        self.okno.after(duration, message.destroy)

    def setup_ui(self):
        """UI building"""

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

        self.setup_layers_panel(self.okno, max_layers_width=250)
        self.setup_workspace_panel(self.okno)

    def setup_workspace_panel(self, parent):
        self.workspace_frame = tk.Frame(parent, bg="#2b2b2b")
        self.workspace_frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.workspace_frame,
            bg="#f5f5f5",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

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


app = Wlepmeister()
app.run()
