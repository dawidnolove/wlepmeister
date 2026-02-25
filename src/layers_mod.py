import tkinter as tk
from tkinter import messagebox, simpledialog

MAX_LAYER_NAME_CHARS = 18
DEFAULT_MAX_LAYERS_WIDTH = 250
LAYER_NUDGE_STEP = 10


class Layer:
    def __init__(self, name):
        self.name = name
        self.objects = []
        self.visible = True


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None

        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tooltip:
            return

        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip,
            text=self.text,
            bg="#ffffe0",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=2,
        )
        label.pack()

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class LayerUIMixin:
    def init_layers_state(self):
        self.layers = []
        self.active_layer = None
        self.layers_container = None

    def add_layer(self):
        name = f"Layer {len(self.layers) + 1}"
        layer = Layer(name)
        self.layers.append(layer)
        self.active_layer = layer
        self.refresh_layers_ui()
        self._request_canvas_redraw()

    def set_active_layer(self, layer):
        self.active_layer = layer
        self.refresh_layers_ui()

    def rename_layer(self, layer):
        new_name = simpledialog.askstring(
            "Rename layer",
            "New layer name:",
            initialvalue=layer.name,
        )
        if new_name:
            layer.name = new_name
            self.refresh_layers_ui()

    def move_layer(self, index, direction):
        new_index = index + direction
        if 0 <= new_index < len(self.layers):
            self.layers[index], self.layers[new_index] = (
                self.layers[new_index],
                self.layers[index],
            )
            self.refresh_layers_ui()
            self._request_canvas_redraw()

    def delete_layer(self, layer):
        if layer not in self.layers:
            return

        confirm = messagebox.askyesno(
            "Potwierdzenie usuniecia",
            f"Czy na pewno chcesz usunac warstwe:\n\n'{layer.name}' ?",
        )

        if not confirm:
            return

        self.layers.remove(layer)

        if self.active_layer == layer:
            self.active_layer = self.layers[-1] if self.layers else None

        self.refresh_layers_ui()
        self._request_canvas_redraw()

    def toggle_layer_visibility(self, layer):
        layer.visible = not layer.visible
        self.refresh_layers_ui()
        self._request_canvas_redraw()

    def move_active_layer(self, dx, dy):
        if self.active_layer is None:
            return False

        moved_any = False
        for obj in self.active_layer.objects:
            if hasattr(obj, "x") and hasattr(obj, "y"):
                obj.x += dx
                obj.y += dy
                moved_any = True

        if moved_any:
            self._request_canvas_redraw()
        return moved_any

    def refresh_layers_ui(self):
        if self.layers_container is None:
            return

        for widget in self.layers_container.winfo_children():
            widget.destroy()
        for index, layer in reversed(list(enumerate(self.layers))):
            self.create_layer_widget(layer, index)

    def truncate_text(self, text, max_chars=MAX_LAYER_NAME_CHARS):
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 3] + "..."

    def create_layer_widget(self, layer, index):
        frame = tk.Frame(
            self.layers_container,
            bg="#ffffff" if layer == self.active_layer else "#cccccc",
            relief="raised",
            bd=1,
        )
        frame.pack(fill="x", padx=4, pady=2)

        drag_label = tk.Label(frame, text="\u2261")
        drag_label.pack(side="left", padx=4)

        eye_icon = "\U0001F441" if layer.visible else "\U0001F648"

        visibility_btn = tk.Button(
            frame,
            text=eye_icon,
            width=2,
            command=lambda l=layer: self.toggle_layer_visibility(l),
        )
        visibility_btn.pack(side="left", padx=2)

        tooltip_text = "Ukryj layer" if layer.visible else "Pokaz layer"
        Tooltip(visibility_btn, tooltip_text)

        display_name = self.truncate_text(layer.name)

        name_label = tk.Label(
            frame,
            text=display_name,
            anchor="w",
        )
        name_label.pack(side="left", fill="x", expand=True)

        Tooltip(name_label, layer.name)

        frame.bind("<Button-1>", lambda e: self.set_active_layer(layer))
        drag_label.bind("<Button-1>", lambda e: self.set_active_layer(layer))
        name_label.bind("<Button-1>", lambda e: self.set_active_layer(layer))

        name_label.bind("<Double-Button-1>", lambda e: self.rename_layer(layer))

        up_btn = tk.Button(
            frame,
            text="\u25B2",
            width=2,
            command=lambda: self.move_layer(index, 1),
        )
        up_btn.pack(side="right")
        Tooltip(up_btn, "Przesun layer w gore")

        down_btn = tk.Button(
            frame,
            text="\u25BC",
            width=2,
            command=lambda: self.move_layer(index, -1),
        )
        down_btn.pack(side="right")
        Tooltip(down_btn, "Przesun layer w dol")

        delete_btn = tk.Button(
            frame,
            text="\u2715",
            width=2,
            command=lambda l=layer: self.delete_layer(l),
        )
        delete_btn.pack(side="right", padx=2)

        Tooltip(delete_btn, "Usun layer")

    def setup_layers_panel(self, parent, max_layers_width=DEFAULT_MAX_LAYERS_WIDTH):
        self.left_panel = tk.Frame(
            parent,
            width=max_layers_width,
            bg="#dddddd",
        )
        self.left_panel.pack(side="left", fill="y")
        self.left_panel.pack_propagate(False)

        header = tk.Frame(self.left_panel, bg="#bbbbbb")
        header.pack(fill="x")
        tk.Label(header, text="Layers", bg="#bbbbbb").pack(side="left", padx=5)

        add_btn = tk.Button(header, text="+", command=self.add_layer)
        add_btn.pack(side="right", padx=5)
        Tooltip(add_btn, "Dodaj nowy layer")

        move_right_btn = tk.Button(
            header,
            text="→",
            width=2,
            command=lambda: self.move_active_layer(LAYER_NUDGE_STEP, 0),
        )
        move_right_btn.pack(side="right")
        Tooltip(move_right_btn, "Przesun aktywna warstwe w prawo")

        move_left_btn = tk.Button(
            header,
            text="←",
            width=2,
            command=lambda: self.move_active_layer(-LAYER_NUDGE_STEP, 0),
        )
        move_left_btn.pack(side="right")
        Tooltip(move_left_btn, "Przesun aktywna warstwe w lewo")

        self.layers_container = tk.Frame(self.left_panel, bg="#dddddd")
        self.layers_container.pack(fill="both", expand=True)

    def _request_canvas_redraw(self):
        redraw = getattr(self, "redraw_canvas", None)
        if callable(redraw):
            redraw()

