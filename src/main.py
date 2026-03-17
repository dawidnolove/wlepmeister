import io
import os
import sys
import tkinter as tk
import zlib
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from auth_ui import AuthUIMixin
from db import (
    list_user_cloud_projects,
    load_user_cloud_project,
    save_cloud_project,
)
from layers_mod import Layer, LayerUIMixin

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


class ImageObject:
    def __init__(self, image_path=None, x=0, y=0, pil_image=None):
        self.image_path = image_path
        self.x = x
        self.y = y
        if pil_image is not None:
            self.pil_image = pil_image.convert("RGBA").copy()
        else:
            if not image_path:
                raise ValueError("Image path is required for file import.")
            with Image.open(image_path) as source_image:
                if source_image.format != "PNG":
                    raise ValueError("Only PNG files are allowed.")
                self.pil_image = source_image.convert("RGBA").copy()
        self.photo_image = ImageTk.PhotoImage(self.pil_image)


class Wlepmeister(AuthUIMixin, LayerUIMixin):
    def __init__(self):
        self.okno = tk.Tk()
        icon_path = resource_path("../media/icon_py_128.ico")
        # Only set the icon if the file exists to avoid startup crash.
        if os.path.exists(icon_path):
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

    def _serialize_project_layers(self):
        layers_payload = []
        for layer in self.layers:
            layer_payload = {
                "name": layer.name,
                "visible": bool(layer.visible),
                "objects": [],
            }
            for image_obj in layer.objects:
                png_buffer = io.BytesIO()
                image_obj.pil_image.save(png_buffer, format="PNG", optimize=True)
                png_bytes = png_buffer.getvalue()
                compressed = zlib.compress(png_bytes, level=9)
                if len(compressed) < len(png_bytes):
                    payload_bytes = compressed
                    encoding = "zlib+png"
                else:
                    payload_bytes = png_bytes
                    encoding = "png"

                layer_payload["objects"].append(
                    {
                        "x": int(image_obj.x),
                        "y": int(image_obj.y),
                        "encoding": encoding,
                        "png_blob": payload_bytes,
                    }
                )
            layers_payload.append(layer_payload)
        return layers_payload

    def _create_cloud_dialog(self, title, width, height):
        dialog = tk.Toplevel(self.okno)
        dialog.title(title)
        dialog.transient(self.okno)
        dialog.grab_set()
        dialog.configure(bg="#fca9b8")
        self._center_child_window(dialog, width, height)
        return dialog

    def _ask_cloud_project_name(self):
        dialog = self._create_cloud_dialog("Save to cloud", 420, 200)
        result = {"name": None}

        container = tk.Frame(dialog, bg="#fca9b8", padx=16, pady=14)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="Save project to cloud",
            bg="#fca9b8",
            fg="#1f1f1f",
            font=("Arial", 13, "bold"),
        ).pack(anchor="w", pady=(0, 10))
        tk.Label(
            container,
            text="Project name:",
            bg="#fca9b8",
            fg="#1f1f1f",
            font=("Arial", 10),
        ).pack(anchor="w")

        name_var = tk.StringVar()
        entry = tk.Entry(container, textvariable=name_var, font=("Arial", 11), relief="flat")
        entry.pack(fill="x", pady=(6, 12), ipady=5)
        entry.focus_set()

        buttons = tk.Frame(container, bg="#fca9b8")
        buttons.pack(fill="x")

        def submit():
            value = name_var.get().strip()
            if not value:
                messagebox.showerror("Invalid name", "Project name cannot be empty.", parent=dialog)
                return
            result["name"] = value
            dialog.destroy()

        tk.Button(
            buttons,
            text="Cancel",
            width=10,
            bg="#f1f1f1",
            activebackground="#e7e7e7",
            command=dialog.destroy,
            relief="flat",
        ).pack(side="right")
        tk.Button(
            buttons,
            text="Save",
            width=10,
            bg="#ffffff",
            activebackground="#f2f2f2",
            command=submit,
            relief="flat",
        ).pack(side="right", padx=(0, 8))

        dialog.bind("<Return>", lambda _event: submit())
        dialog.wait_window()
        return result["name"]

    def save_project_to_cloud(self):
        if not self.current_user:
            messagebox.showwarning("Login required", "Log in first to save project in cloud.")
            return

        project_name = self._ask_cloud_project_name()
        if not project_name:
            return

        layers_payload = self._serialize_project_layers()
        saved = save_cloud_project(
            username=self.current_user,
            project_name=project_name,
            layers_payload=layers_payload,
        )
        if saved:
            self.show_message("Project saved to cloud", duration=2500)
            return
        messagebox.showerror("Cloud save failed", "Could not save project to cloud.")

    def _pick_cloud_project_name(self, project_names):
        picker = self._create_cloud_dialog("Open from cloud", 430, 340)

        selected_name = {"value": None}

        container = tk.Frame(picker, bg="#fca9b8", padx=14, pady=12)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="Open project from cloud",
            bg="#fca9b8",
            fg="#1f1f1f",
            font=("Arial", 13, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            container,
            text="Choose project:",
            bg="#fca9b8",
            fg="#1f1f1f",
            font=("Arial", 10),
        ).pack(anchor="w", pady=(0, 4))

        listbox = tk.Listbox(
            container,
            height=10,
            bg="#ffffff",
            fg="#1f1f1f",
            selectbackground="#f08093",
            relief="flat",
            highlightthickness=0,
        )
        listbox.pack(fill="both", expand=True, pady=(0, 10))
        for name in project_names:
            listbox.insert(tk.END, name)
        if project_names:
            listbox.selection_set(0)

        def choose_selected():
            selection = listbox.curselection()
            if not selection:
                return
            selected_name["value"] = listbox.get(selection[0])
            picker.destroy()

        buttons = tk.Frame(container, bg="#fca9b8")
        buttons.pack(fill="x")
        tk.Button(
            buttons,
            text="Cancel",
            width=10,
            bg="#f1f1f1",
            activebackground="#e7e7e7",
            command=picker.destroy,
            relief="flat",
        ).pack(side="right")
        tk.Button(
            buttons,
            text="Open",
            width=10,
            bg="#ffffff",
            activebackground="#f2f2f2",
            command=choose_selected,
            relief="flat",
        ).pack(side="right", padx=(0, 8))

        listbox.bind("<Double-Button-1>", lambda _event: choose_selected())
        picker.wait_window()
        return selected_name["value"]

    def _apply_cloud_project(self, project_doc):
        raw_layers = project_doc.get("layers", [])
        loaded_layers = []
        for raw_layer in raw_layers:
            layer = Layer(raw_layer.get("name", f"Layer {len(loaded_layers) + 1}"))
            layer.visible = bool(raw_layer.get("visible", True))
            for raw_obj in raw_layer.get("objects", []):
                raw_blob = raw_obj.get("png_blob")
                if raw_blob is None:
                    continue

                try:
                    blob_bytes = bytes(raw_blob)
                    encoding = raw_obj.get("encoding", "png")
                    if encoding == "zlib+png":
                        blob_bytes = zlib.decompress(blob_bytes)
                    elif encoding != "png":
                        raise ValueError(f"Unsupported image encoding: {encoding}")
                    pil_image = Image.open(io.BytesIO(blob_bytes)).convert("RGBA")
                except Exception as exc:
                    raise ValueError(f"Invalid object payload in cloud project: {exc}") from exc

                layer.objects.append(
                    ImageObject(
                        image_path=None,
                        x=int(raw_obj.get("x", 0)),
                        y=int(raw_obj.get("y", 0)),
                        pil_image=pil_image,
                    )
                )
            loaded_layers.append(layer)

        self.layers = loaded_layers
        if not self.layers:
            self.add_layer()
            return
        self.active_layer = self.layers[-1]
        self.refresh_layers_ui()
        self.redraw_canvas()

    def open_project_from_cloud(self):
        if not self.current_user:
            messagebox.showwarning("Login required", "Log in first to open project from cloud.")
            return

        project_names = list_user_cloud_projects(self.current_user)
        if not project_names:
            messagebox.showinfo("No projects", "No cloud projects for this account yet.")
            return

        selected_name = self._pick_cloud_project_name(project_names)
        if not selected_name:
            return

        project_doc = load_user_cloud_project(self.current_user, selected_name)
        if not project_doc:
            messagebox.showerror("Open failed", "Could not load selected project.")
            return

        try:
            self._apply_cloud_project(project_doc)
        except Exception as exc:
            messagebox.showerror("Open failed", f"Project data is invalid:\n{exc}")
            return

        self.show_message(f"Opened cloud project: {selected_name}", duration=2500)

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
        file_menu.add_command(label="Save project to cloud", command=self.save_project_to_cloud)
        file_menu.add_command(label="Open project from cloud", command=self.open_project_from_cloud)
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
