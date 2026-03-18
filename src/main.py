import os
import sys
import tkinter as tk
from tkinter import filedialog

from PIL import Image

from auth_ui import AuthUIMixin
from cloud import CloudUIMixin
from image_object import ImageObject
from layers_mod import LayerUIMixin
from theme_colors import COLORS, FONTS
from ui_dialogs import show_error, show_toast
from ui_theme import apply_titlebar_color

APP_TITLE = "WLEPMEISTER"
APP_GEOMETRY = "900x600"
LAYERS_PANEL_MAX_WIDTH = 250
ALPHA_LEVELS = [0.5, 0.75, 1.0]


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(base_path, relative_path))


class Wlepmeister(AuthUIMixin, CloudUIMixin, LayerUIMixin):
    def __init__(self):
        self.okno = tk.Tk()
        icon_path = resource_path("../media/icon_py_128.ico")
        # Only set the icon if the file exists to avoid startup crash.
        if os.path.exists(icon_path):
            self.okno.iconbitmap(icon_path)
        self.okno.title(APP_TITLE)
        self.okno.geometry(APP_GEOMETRY)
        apply_titlebar_color(self.okno)

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
        file_path = filedialog.askopenfilename(
            title="Import PNG image",
            filetypes=[("PNG image", "*.png")],
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".png"):
            show_error(self.okno, "Invalid file", "Only PNG files are allowed.")
            return

        try:
            image_obj = ImageObject(file_path, x=30, y=30)
        except Exception as exc:
            show_error(self.okno, "Import failed", f"Could not import image:\n{exc}")
            return

        # Each imported image gets its own dedicated layer so it can be managed independently.
        layer_name = os.path.splitext(os.path.basename(file_path))[0]
        self.add_layer()
        self.active_layer.name = layer_name or self.active_layer.name
        self.active_layer.objects = [image_obj]
        self.refresh_layers_ui()
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
        rendered.save(save_path, format="PNG", optimize=True)
        self.show_message("Exported PNG", duration=2000)

    def print(self):
        pass

    def new_window(self):
        new = Wlepmeister()
        new.run()

    def toggle_alpha(self):
        current_alpha = self.okno.attributes("-alpha")
        next_alpha_index = (ALPHA_LEVELS.index(current_alpha) + 1) % len(ALPHA_LEVELS)
        self.okno.attributes("-alpha", ALPHA_LEVELS[next_alpha_index])

    def show_message(self, text, duration=2000):
        show_toast(self.okno, text, duration=duration)

    def on_login_state_changed(self):
        self.build_menus()

    def build_menus(self):
        _menu_kw = dict(
            bg=COLORS["menu_bg"],
            fg=COLORS["menu_fg"],
            activebackground=COLORS["menu_active_bg"],
            activeforeground=COLORS["menu_active_fg"],
            font=FONTS["body"],
        )
        _submenu_kw = dict(
            tearoff=0,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            activebackground=COLORS["accent"],
            activeforeground="#ffffff",
            font=FONTS["body"],
        )

        menu_bar = tk.Menu(self.okno, **_menu_kw)
        self.okno.configure(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, **_submenu_kw)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New window", command=self.new_window)
        file_menu.add_command(label="Import image", command=self.add_image)
        if self.current_user:
            file_menu.add_separator()
            file_menu.add_command(label="Save project to cloud", command=self.save_project_to_cloud)
            file_menu.add_command(label="Open project from cloud", command=self.open_project_from_cloud)
        file_menu.add_separator()
        file_menu.add_command(label="Export", command=self.export)
        file_menu.add_command(label="Print", command=self.print)
        file_menu.add_separator()
        file_menu.add_command(label="Close window", command=self.okno.destroy)

        edit_menu = tk.Menu(menu_bar, **_submenu_kw)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        edit_menu.add_separator()
        edit_menu.add_command(label="New layer", command=self.add_layer)

        view_menu = tk.Menu(menu_bar, **_submenu_kw)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Alpha", command=self.toggle_alpha)

        account_menu = tk.Menu(menu_bar, **_submenu_kw)
        menu_bar.add_cascade(label="Account", menu=account_menu)
        account_menu.add_command(label="Login", command=self.open_login_window)
        account_menu.add_command(label="Register", command=self.open_register_window)
        account_menu.add_separator()
        account_menu.add_command(label="Logout", command=self.logout)

    def setup_ui(self):
        self.build_menus()

        self.okno.configure(bg=COLORS["bg"])
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
        self.workspace_frame = tk.Frame(parent, bg=COLORS["bg"])
        self.workspace_frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.workspace_frame,
            bg=COLORS["canvas"],
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
