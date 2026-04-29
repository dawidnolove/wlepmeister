import tkinter as tk

from PIL import Image

from .image_object import ImageObject
from .theme_colors import COLORS, FONTS
from .ui_dialogs import ask_yes_no, prompt_string, show_info
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
        self._show_job = None

        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide)
        widget.bind("<ButtonPress>", self.hide)

    def schedule(self, _event=None):
        self.cancel()
        self._show_job = self.widget.after(550, self.show)

    def cancel(self):
        if self._show_job is None:
            return
        try:
            self.widget.after_cancel(self._show_job)
        except tk.TclError:
            pass
        self._show_job = None

    def show(self):
        self._show_job = None
        if self.tooltip:
            return

        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.tooltip.configure(bg=COLORS["border"])
        self.tooltip.attributes("-topmost", True)

        frame = tk.Frame(
            self.tooltip,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        frame.pack()

        label = tk.Label(
            frame,
            text=self.text,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=FONTS["small"],
            relief="flat",
            padx=9,
            pady=5,
        )
        label.pack()

    def hide(self, _event=None):
        self.cancel()
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class LayerUIMixin:
    def init_layers_state(self):
        self.layers = []
        self.active_layer = None
        self.active_layers = []
        self.layers_container = None
        self.layer_widgets = {}
        self._pending_layer_select_job = None

    def add_layer(self):
        name = f"Layer {len(self.layers) + 1}"
        layer = Layer(name)
        self.layers.append(layer)
        self.active_layer = layer
        self.active_layers = [layer]
        self.refresh_layers_ui()
        self._request_canvas_redraw()

    def set_active_layer(self, layer, extend=False):
        if layer not in self.layers:
            return
        if hasattr(self, "selected_object") and self.selected_object not in layer.objects:
            self.selected_object = None
            self.selected_object_layer = None
        if extend:
            selected = [item for item in self.active_layers if item in self.layers]
            if layer in selected:
                if len(selected) > 1:
                    selected.remove(layer)
            else:
                selected.append(layer)
            self.active_layers = selected or [layer]
            self.active_layer = self.active_layers[-1]
            self._refresh_layer_selection_styles()
            return
        self.active_layer = layer
        self.active_layers = [layer]
        self._refresh_layer_selection_styles()

    def _cancel_pending_layer_select(self):
        if self._pending_layer_select_job and self.layers_container is not None:
            try:
                self.layers_container.after_cancel(self._pending_layer_select_job)
            except tk.TclError:
                pass
        self._pending_layer_select_job = None

    def _handle_layer_single_click(self, layer, extend=False):
        self._cancel_pending_layer_select()
        self.set_active_layer(layer, extend=extend)

    def _apply_layer_single_click(self, layer, extend=False):
        self._pending_layer_select_job = None
        self.set_active_layer(layer, extend=extend)

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
            "Delete layer",
            f"You are about to delete current layer:\n\n'{layer.name}' ?",
            yes_text="Yes",
            no_text="No",
        )

        if not confirm:
            return

        if getattr(self, "selected_object_layer", None) == layer:
            self.selected_object = None
            self.selected_object_layer = None

        self.layers.remove(layer)

        if self.active_layer == layer:
            self.active_layer = self.layers[-1] if self.layers else None
        self.active_layers = [item for item in self.active_layers if item in self.layers]
        if self.active_layer and self.active_layer not in self.active_layers:
            self.active_layers = [self.active_layer]
        elif not self.active_layer:
            self.active_layers = []

        self.refresh_layers_ui()
        self._request_canvas_redraw()

    def toggle_layer_visibility(self, layer):
        layer.visible = not layer.visible
        if not layer.visible and getattr(self, "selected_object_layer", None) == layer:
            self.selected_object = None
            self.selected_object_layer = None
        self.refresh_layers_ui()
        self._request_canvas_redraw()

    def move_active_layer(self, dx, dy):
        layers_to_move = [layer for layer in self.active_layers if layer in self.layers]
        if not layers_to_move and self.active_layer is not None:
            layers_to_move = [self.active_layer]
        if not layers_to_move:
            return False

        moved_any = False
        for layer in layers_to_move:
            for obj in layer.objects:
                if hasattr(obj, "x") and hasattr(obj, "y"):
                    obj.x += dx
                    obj.y += dy
                    moved_any = True

        if moved_any:
            self._request_canvas_redraw()
        return moved_any

    def merge_selected_layers(self):
        selected_layers = [layer for layer in self.layers if layer in self.active_layers]
        if len(selected_layers) < 2:
            show_info(
                self.okno,
                "Merge layers",
                "Select two or more layers with Alt-click, then use Merge.",
            )
            return

        objects = []
        visible = False
        for layer in selected_layers:
            visible = visible or layer.visible
            for obj in layer.objects:
                objects.append(obj)

        first_index = min(self.layers.index(layer) for layer in selected_layers)
        if objects:
            min_x = min(int(obj.x) for obj in objects)
            min_y = min(int(obj.y) for obj in objects)
            max_x = max(int(obj.x) + obj.pil_image.width for obj in objects)
            max_y = max(int(obj.y) + obj.pil_image.height for obj in objects)
            merged_image = Image.new("RGBA", (max_x - min_x, max_y - min_y), (0, 0, 0, 0))

            for layer in self.layers:
                if layer not in selected_layers:
                    continue
                for obj in layer.objects:
                    merged_image.alpha_composite(
                        obj.pil_image,
                        (int(obj.x) - min_x, int(obj.y) - min_y),
                    )

            merged_layer = Layer("Merged layer")
            merged_layer.objects = [ImageObject(image_path=None, x=min_x, y=min_y, pil_image=merged_image)]
        else:
            merged_layer = Layer("Merged layer")

        merged_layer.visible = visible
        self.layers = [layer for layer in self.layers if layer not in selected_layers]
        self.layers.insert(first_index, merged_layer)
        self.active_layer = merged_layer
        self.active_layers = [merged_layer]
        self.selected_object = merged_layer.objects[0] if merged_layer.objects else None
        self.selected_object_layer = merged_layer if self.selected_object else None
        self.refresh_layers_ui()
        self._request_canvas_redraw()
        if hasattr(self, "show_message"):
            self.show_message("Layers merged", duration=1800)

    def refresh_layers_ui(self):
        if self.layers_container is None:
            return

        for widget in self.layers_container.winfo_children():
            widget.destroy()
        self.layer_widgets = {}
        for index, layer in reversed(list(enumerate(self.layers))):
            self.create_layer_widget(layer, index)

    def _refresh_layer_selection_styles(self):
        if not self.layer_widgets:
            self.refresh_layers_ui()
            return
        for layer, widgets in list(self.layer_widgets.items()):
            if layer not in self.layers:
                continue
            is_selected = layer in self.active_layers
            is_active = layer == self.active_layer
            row_bg = COLORS["layer_active"] if is_selected else COLORS["layer_inactive"]
            name_color = COLORS["text"] if is_selected else COLORS["muted"]
            for widget in widgets["row_widgets"]:
                widget.configure(bg=row_bg)
            widgets["name_label"].configure(
                fg=name_color,
                font=FONTS["body_bold"] if is_active else FONTS["body"],
            )

    def truncate_text(self, text, max_chars=MAX_LAYER_NAME_CHARS):
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 3] + "..."

    def create_layer_widget(self, layer, index):
        is_selected = layer in self.active_layers
        is_active = layer == self.active_layer
        row_bg = COLORS["layer_active"] if is_selected else COLORS["layer_inactive"]
        text_color = COLORS["text"]
        muted_color = COLORS["muted"]
        btn_bg = COLORS["surface_alt"]
        btn_fg = COLORS["text"]

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
            fg=text_color if is_selected else muted_color,
            font=FONTS["body_bold"] if is_active else FONTS["body"],
        )
        name_label.pack(side="left", fill="x", expand=True)

        Tooltip(name_label, layer.name)

        def handle_click(event, force_extend=False):
            extend = force_extend or self._event_has_alt(event)
            self._handle_layer_single_click(layer, extend)
            return "break"

        def bind_selection(widget):
            widget.bind("<Button-1>", handle_click)
            widget.bind("<Alt-Button-1>", lambda e: handle_click(e, True))
            widget.bind("<Mod1-Button-1>", lambda e: handle_click(e, True))

        bind_selection(frame)
        bind_selection(drag_label)
        bind_selection(name_label)

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
        self.layer_widgets[layer] = {
            "row_widgets": (frame, drag_label, name_label),
            "name_label": name_label,
        }

    def _event_has_alt(self, event):
        # Tk reports Alt as Mod1 on most platforms, but Windows builds can expose
        # an extended bit too. Accept both so Alt-click feels reliable.
        return bool(event.state & (0x0008 | 0x20000))

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

        merge_btn = tk.Button(
            header,
            text="Merge",
            width=6,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            activebackground=COLORS["accent"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=FONTS["small"],
            command=self.merge_selected_layers,
        )
        merge_btn.pack(side="right", padx=(0, 4), pady=3)
        Tooltip(merge_btn, "Merge selected layers")

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
        Tooltip(move_right_btn, "Move layer right by 10px")

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
        Tooltip(move_left_btn, "Move layer left by 10px")

        self.layers_container = tk.Frame(self.left_panel, bg=COLORS["panel"])
        self.layers_container.pack(fill="both", expand=True)

    def _request_canvas_redraw(self):
        redraw = getattr(self, "redraw_canvas", None)
        if callable(redraw):
            redraw()
