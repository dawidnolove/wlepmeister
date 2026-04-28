import tkinter as tk

from theme_colors import COLORS, FONTS
from ui_dialogs import ask_yes_no, prompt_string
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
            bg=COLORS["panel_header"],
            fg=COLORS["accent2"],
            font=FONTS["small"],
            relief="flat",
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
        self._pending_layer_select_job = None

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

    def _cancel_pending_layer_select(self):
        if self._pending_layer_select_job and self.layers_container is not None:
            try:
                self.layers_container.after_cancel(self._pending_layer_select_job)
            except tk.TclError:
                pass
        self._pending_layer_select_job = None

    def _handle_layer_single_click(self, layer):
        self._cancel_pending_layer_select()
        if self.layers_container is None:
            self.set_active_layer(layer)
            return
        # Delay single-click action so double-click can trigger rename first.
        self._pending_layer_select_job = self.layers_container.after(
            200,
            lambda l=layer: self._apply_layer_single_click(l),
        )

    def _apply_layer_single_click(self, layer):
        self._pending_layer_select_job = None
        self.set_active_layer(layer)

    def _handle_layer_double_click(self, layer):
        self._cancel_pending_layer_select()
        self.set_active_layer(layer)
        self.rename_layer(layer)

    def rename_layer(self, layer):
        new_name = prompt_string(self.okno, "Rename layer", "New layer name:", initial_value=layer.name)
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

        confirm = ask_yes_no(
            self.okno,
            "Potwierdzenie usuniecia",
            f"You are about to delete current layer:\n\n'{layer.name}' ?",
            yes_text="Yes",
            no_text="No",
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
        is_active = layer == self.active_layer
        row_bg = COLORS["layer_active"] if is_active else COLORS["layer_inactive"]
        text_color = COLORS["text"]
        muted_color = COLORS["muted"]
        btn_bg = COLORS["surface_alt"]
        btn_fg = COLORS["text"]
        btn_active = COLORS["border"]

        frame = tk.Frame(
            self.layers_container,
            bg=row_bg,
            relief="flat",
            bd=0,
        )
        frame.pack(fill="x", padx=4, pady=2)

        drag_label = tk.Label(
            frame,
            text="\u2261",
            bg=row_bg,
            fg=muted_color,
            font=FONTS["body"],
            cursor="fleur",
        )
        drag_label.pack(side="left", padx=4)

        eye_icon = "\U0001F441" if layer.visible else "\U0001F648"

        visibility_btn = tk.Button(
            frame,
            text=eye_icon,
            width=2,
            bg=btn_bg,
            fg=btn_fg,
            activebackground=COLORS["accent_soft"],
            activeforeground=btn_fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=FONTS["body"],
            command=lambda l=layer: self.toggle_layer_visibility(l),
        )
        visibility_btn.pack(side="left", padx=2)

        tooltip_text = "Hide layer" if layer.visible else "Show layer"
        Tooltip(visibility_btn, tooltip_text)

        display_name = self.truncate_text(layer.name)

        name_label = tk.Label(
            frame,
            text=display_name,
            anchor="w",
            bg=row_bg,
            fg=text_color if is_active else muted_color,
            font=FONTS["body_bold"] if is_active else FONTS["body"],
        )
        name_label.pack(side="left", fill="x", expand=True)

        Tooltip(name_label, layer.name)

        frame.bind("<Button-1>", lambda e, l=layer: self._handle_layer_single_click(l))
        drag_label.bind("<Button-1>", lambda e, l=layer: self._handle_layer_single_click(l))
        name_label.bind("<Button-1>", lambda e, l=layer: self._handle_layer_single_click(l))

        frame.bind("<Double-Button-1>", lambda e, l=layer: self._handle_layer_double_click(l))
        drag_label.bind("<Double-Button-1>", lambda e, l=layer: self._handle_layer_double_click(l))
        name_label.bind("<Double-Button-1>", lambda e, l=layer: self._handle_layer_double_click(l))

        up_btn = tk.Button(
            frame,
            text="\u25B2",
            width=2,
            bg=btn_bg,
            fg=btn_fg,
            activebackground=COLORS["accent"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=FONTS["small"],
            command=lambda: self.move_layer(index, 1),
        )
        up_btn.pack(side="right")
        Tooltip(up_btn, "Move layer up")

        down_btn = tk.Button(
            frame,
            text="\u25BC",
            width=2,
            bg=btn_bg,
            fg=btn_fg,
            activebackground=COLORS["accent"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=FONTS["small"],
            command=lambda: self.move_layer(index, -1),
        )
        down_btn.pack(side="right")
        Tooltip(down_btn, "Move layer down")

        delete_btn = tk.Button(
            frame,
            text="\u2715",
            width=2,
            bg=btn_bg,
            fg=COLORS["danger"],
            activebackground=COLORS["danger"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=FONTS["body_bold"],
            command=lambda l=layer: self.delete_layer(l),
        )
        delete_btn.pack(side="right", padx=2)

        Tooltip(delete_btn, "Delete layer")

    def setup_layers_panel(self, parent, max_layers_width=DEFAULT_MAX_LAYERS_WIDTH):
        self.left_panel = tk.Frame(
            parent,
            width=max_layers_width,
            bg=COLORS["panel"],
        )
        self.left_panel.pack(side="left", fill="y")
        self.left_panel.pack_propagate(False)

        header = tk.Frame(self.left_panel, bg=COLORS["panel_header"])
        header.pack(fill="x")
        tk.Label(
            header,
            text="Layers",
            bg=COLORS["panel_header"],
            fg=COLORS["text"],
            font=FONTS["body_bold"],
        ).pack(side="left", padx=5, pady=4)

        add_btn = tk.Button(
            header,
            text="+",
            width=2,
            bg=COLORS["accent"],
            fg="#ffffff",
            activebackground=COLORS["accent_dark"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=FONTS["body_bold"],
            command=self.add_layer,
        )
        add_btn.pack(side="right", padx=5, pady=3)
        Tooltip(add_btn, "Add new layer")

        move_right_btn = tk.Button(
            header,
            text="\u2192",
            width=2,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            activebackground=COLORS["accent"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=FONTS["body"],
            command=lambda: self.move_active_layer(LAYER_NUDGE_STEP, 0),
        )
        move_right_btn.pack(side="right")
        Tooltip(move_right_btn, "To the right by 1px")

        move_left_btn = tk.Button(
            header,
            text="\u2190",
            width=2,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            activebackground=COLORS["accent"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=FONTS["body"],
            command=lambda: self.move_active_layer(-LAYER_NUDGE_STEP, 0),
        )
        move_left_btn.pack(side="right")
        Tooltip(move_left_btn, "To the right by 1px")

        self.layers_container = tk.Frame(self.left_panel, bg=COLORS["panel"])
        self.layers_container.pack(fill="both", expand=True)

    def _request_canvas_redraw(self):
        redraw = getattr(self, "redraw_canvas", None)
        if callable(redraw):
            redraw()
