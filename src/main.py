import base64
import io
import math
import os
import sys
import tkinter as tk
from tkinter import filedialog

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "src"

from PIL import Image, ImageOps, ImageTk
from .auth_ui import AuthUIMixin
from .cloud import CloudUIMixin
from .db import get_user_profile
from .image_object import ImageObject
from .layers_mod import LayerUIMixin
from .theme_colors import COLORS, FONTS, set_theme
from .ui_dialogs import show_error, show_info, show_toast
from .ui_theme import apply_titlebar_color, build_button

APP_TITLE = "WLEPMEISTER"
APP_GEOMETRY = "900x600"
LAYERS_PANEL_MAX_WIDTH = 250
ALPHA_LEVELS = [0.5, 0.75, 1.0]
SELECTION_CORNER_HIT_RADIUS = 14
MIN_OBJECT_SIZE = 12
EXPORT_FILETYPES = [
    ("PNG image", "*.png"),
    ("SVG image", "*.svg"),
    ("JPEG image", "*.jpg"),
]
JPEG_QUALITY_BY_SIZE = (
    (8_000_000, 78),
    (4_000_000, 80),
    (2_000_000, 82),
    (0, 85),
)


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
        self.resize_state = None
        self.rotate_state = None
        self.rotation_mode = False
        self.canvas = None
        self.workspace_toolbar = None
        self.status_label = None
        self.workspace_frame = None
        self.current_user = None
        self.topbar = None
        self.user_badge_frame = None
        self.user_name_label = None
        self.user_avatar_label = None
        self.user_avatar_image = None
        self.current_theme = "dark"
        self.dark_mode_var = tk.BooleanVar(value=True)
        self.selected_object = None
        self.selected_object_layer = None

        self.init_layers_state()
        self.setup_ui()
        self.add_layer()

    def add_image(self):
        file_path = filedialog.askopenfilename(
            title="Import image",
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp;*.tif;*.tiff"),
                ("All files", "*.*"),
            ],
        )
        if not file_path:
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
        self.selected_object = image_obj
        self.selected_object_layer = self.active_layer
        self.refresh_layers_ui()
        self.redraw_canvas()
        self._update_status()

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

    def _iter_visible_image_objects(self):
        for layer in self.layers:
            if not layer.visible:
                continue
            for image_obj in layer.objects:
                yield image_obj

    def _resolve_export_target(self, save_path, selected_filetype):
        normalized_ext = os.path.splitext(save_path)[1].lower()
        if normalized_ext == ".png":
            return "png", save_path
        if normalized_ext == ".svg":
            return "svg", save_path
        if normalized_ext in (".jpg", ".jpeg"):
            return "jpg", save_path

        selected_filetype = (selected_filetype or "").lower()
        if "svg" in selected_filetype:
            return "svg", save_path + ".svg"
        if "jpeg" in selected_filetype or "jpg" in selected_filetype:
            return "jpg", save_path + ".jpg"
        return "png", save_path + ".png"

    def _choose_jpeg_quality(self, image):
        pixel_count = image.width * image.height
        for min_pixels, quality in JPEG_QUALITY_BY_SIZE:
            if pixel_count >= min_pixels:
                return quality
        return 85

    def _image_object_to_svg_data_uri(self, image_obj):
        source_path = getattr(image_obj, "image_path", None)
        if source_path and os.path.exists(source_path):
            extension = os.path.splitext(source_path)[1].lower()
            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".bmp": "image/bmp",
                ".webp": "image/webp",
                ".tif": "image/tiff",
                ".tiff": "image/tiff",
            }
            mime_type = mime_types.get(extension)
            if mime_type:
                with open(source_path, "rb") as source_file:
                    encoded = base64.b64encode(source_file.read()).decode("ascii")
                return f"data:{mime_type};base64,{encoded}"

        png_buffer = io.BytesIO()
        image_obj.pil_image.save(png_buffer, format="PNG", optimize=True)
        encoded = base64.b64encode(png_buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    def _export_png(self, save_path):
        rendered = self._build_visible_layers_image()
        rendered.save(save_path, format="PNG", optimize=True)

    def _export_jpg(self, save_path):
        rendered = self._build_visible_layers_image()
        background = Image.new("RGBA", rendered.size, COLORS["canvas"])
        flattened = Image.alpha_composite(background, rendered).convert("RGB")
        flattened.save(
            save_path,
            format="JPEG",
            quality=self._choose_jpeg_quality(flattened),
            optimize=True,
            progressive=True,
            subsampling=2,
        )

    def _export_svg(self, save_path):
        self.okno.update_idletasks()
        width = max(1, int(self.canvas.winfo_width()))
        height = max(1, int(self.canvas.winfo_height()))
        svg_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            ),
        ]

        for image_obj in self._iter_visible_image_objects():
            image_width, image_height = image_obj.pil_image.size
            href = self._image_object_to_svg_data_uri(image_obj)
            svg_lines.append(
                (
                    f'  <image x="{int(image_obj.x)}" y="{int(image_obj.y)}" '
                    f'width="{image_width}" height="{image_height}" href="{href}" />'
                )
            )

        svg_lines.append("</svg>")
        with open(save_path, "w", encoding="utf-8", newline="\n") as svg_file:
            svg_file.write("\n".join(svg_lines))

    def export(self):
        if self.canvas is None:
            return

        selected_filetype = tk.StringVar(value=EXPORT_FILETYPES[0][1])
        save_path = filedialog.asksaveasfilename(
            title="Export image",
            defaultextension="",
            filetypes=EXPORT_FILETYPES,
            typevariable=selected_filetype,
        )
        if not save_path:
            return

        export_format, save_path = self._resolve_export_target(save_path, selected_filetype.get())
        export_label = {"png": "PNG", "svg": "SVG", "jpg": "JPG"}[export_format]

        try:
            if export_format == "png":
                self._export_png(save_path)
            elif export_format == "svg":
                self._export_svg(save_path)
            else:
                self._export_jpg(save_path)
        except Exception as exc:
            show_error(self.okno, "Export failed", f"Could not export image:\n{exc}")
            return

        self.show_message(f"Exported {export_label}", duration=2000)

    def delete_selected_object(self):
        if self.selected_object is None or self.selected_object_layer is None:
            self.show_message("No image selected", duration=1200)
            return
        if self.selected_object_layer not in self.layers:
            self._clear_selected_object()
            return
        if self.selected_object in self.selected_object_layer.objects:
            self.selected_object_layer.objects.remove(self.selected_object)
        self._clear_selected_object()
        self.redraw_canvas()
        self.show_message("Image deleted", duration=1400)

    def print(self):
        show_info(
            self.okno,
            "Print",
            "Printing is not available yet. Export to PNG, JPG, or SVG first.",
        )

    def new_window(self):
        new = Wlepmeister()
        new.run()

    def toggle_alpha(self):
        current_alpha = self.okno.attributes("-alpha")
        closest_alpha = min(ALPHA_LEVELS, key=lambda alpha: abs(alpha - current_alpha))
        next_alpha_index = (ALPHA_LEVELS.index(closest_alpha) + 1) % len(ALPHA_LEVELS)
        self.okno.attributes("-alpha", ALPHA_LEVELS[next_alpha_index])

    def show_message(self, text, duration=2000):
        show_toast(self.okno, text, duration=duration)

    def on_login_state_changed(self):
        self.build_menus()
        self.update_user_badge()
        self._apply_user_theme()

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
        edit_menu.add_command(label="Undo", state="disabled")
        edit_menu.add_command(label="Redo", state="disabled")
        edit_menu.add_separator()
        edit_menu.add_command(label="New layer", command=self.add_layer)
        edit_menu.add_command(label="Merge selected layers", command=self.merge_selected_layers)

        view_menu = tk.Menu(menu_bar, **_submenu_kw)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Alpha", command=self.toggle_alpha)
        view_menu.add_separator()
        view_menu.add_checkbutton(
            label="Dark theme",
            variable=self.dark_mode_var,
            command=self._toggle_theme_from_menu,
        )

        account_menu = tk.Menu(menu_bar, **_submenu_kw)
        menu_bar.add_cascade(label="Account", menu=account_menu)
        account_menu.add_command(label="Login", command=self.open_login_window)
        account_menu.add_command(label="Register", command=self.open_register_window)
        if self.current_user:
            account_menu.add_command(label="Profile", command=self.open_profile_window)
            account_menu.add_separator()
            account_menu.add_command(label="Logout", command=self.logout)

    def setup_ui(self):
        self.build_menus()

        self.okno.configure(bg=COLORS["bg"])
        self._build_topbar(self.okno)
        self.setup_layers_panel(self.okno, max_layers_width=LAYERS_PANEL_MAX_WIDTH)
        self.setup_workspace_panel(self.okno)
        self.update_user_badge()

    def _build_topbar(self, parent):
        if self.topbar is not None:
            self.topbar.destroy()

        self.topbar = tk.Frame(parent, bg=COLORS["panel_header"])
        self.topbar.pack(side="top", fill="x")

        title = tk.Label(
            self.topbar,
            text=self.APP_TITLE,
            bg=COLORS["panel_header"],
            fg=COLORS["text"],
            font=FONTS["section"],
            padx=12,
            pady=6,
        )
        title.pack(side="left")

        self.user_badge_frame = tk.Frame(self.topbar, bg=COLORS["panel_header"])
        self.user_badge_frame.pack(side="right", padx=10, pady=4)

        self.user_avatar_label = tk.Label(
            self.user_badge_frame,
            bg=COLORS["panel_header"],
        )
        self.user_avatar_label.pack(side="right", padx=(6, 0))

        self.user_name_label = tk.Label(
            self.user_badge_frame,
            bg=COLORS["panel_header"],
            fg=COLORS["text"],
            font=FONTS["body_bold"],
        )
        self.user_name_label.pack(side="right")

        def open_profile(_event=None):
            if self.current_user:
                self.open_profile_window()

        self.user_badge_frame.bind("<Button-1>", open_profile)
        self.user_name_label.bind("<Button-1>", open_profile)
        self.user_avatar_label.bind("<Button-1>", open_profile)

    def update_user_badge(self):
        if self.user_name_label is None or self.user_avatar_label is None:
            return
        if not self.current_user:
            self.user_name_label.configure(text="Guest", fg=COLORS["muted"])
            self.user_avatar_label.configure(image="", text="")
            self.user_avatar_image = None
            return

        self.user_name_label.configure(text=self.current_user, fg=COLORS["text"])
        profile = get_user_profile(self.current_user) or {}
        avatar_b64 = profile.get("avatar_b64")
        if not avatar_b64:
            self.user_avatar_label.configure(image="", text="")
            self.user_avatar_image = None
            return
        try:
            raw = base64.b64decode(avatar_b64)
            image = Image.open(io.BytesIO(raw))
            image = ImageOps.exif_transpose(image).convert("RGBA")
            image = image.resize((24, 24), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
        except Exception:
            self.user_avatar_label.configure(image="", text="")
            self.user_avatar_image = None
            return
        self.user_avatar_image = photo
        self.user_avatar_label.configure(image=photo, text="")

    def apply_theme(self, name):
        if not set_theme(name):
            return
        self.current_theme = name
        self.dark_mode_var.set(name == "dark")
        apply_titlebar_color(self.okno)
        self._refresh_ui_theme()
        if self.current_user:
            profile = get_user_profile(self.current_user) or {}
            if profile.get("theme") != name:
                from .db import update_user_profile
                update_user_profile(self.current_user, theme=name)

    def _refresh_ui_theme(self):
        self.build_menus()
        self.okno.configure(bg=COLORS["bg"])
        self._build_topbar(self.okno)

        if getattr(self, "left_panel", None) is not None:
            self.left_panel.destroy()
        if self.workspace_frame is not None:
            self.workspace_frame.destroy()

        self.setup_layers_panel(self.okno, max_layers_width=LAYERS_PANEL_MAX_WIDTH)
        self.setup_workspace_panel(self.okno)
        self.refresh_layers_ui()
        self.redraw_canvas()
        self.update_user_badge()
        self._update_status()

    def _toggle_theme_from_menu(self):
        self.apply_theme("dark" if self.dark_mode_var.get() else "light")

    def _apply_user_theme(self):
        if not self.current_user:
            self.apply_theme("dark")
            return
        profile = get_user_profile(self.current_user) or {}
        theme = profile.get("theme") or "dark"
        self.apply_theme(theme if theme in ("light", "dark") else "dark")

    def _start_layer_drag(self, event):
        if self.active_layer is None:
            return
        self._clear_selected_object(redraw=False)
        self.layer_drag_anchor = (event.x, event.y)
        self._update_status("Moving selected layer")

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

        self.workspace_toolbar = tk.Frame(self.workspace_frame, bg=COLORS["bg"])
        self.workspace_toolbar.pack(fill="x", padx=10, pady=(10, 0))

        build_button(
            self.workspace_toolbar,
            text="Import",
            command=self.add_image,
            variant="primary",
            padx=10,
            pady=4,
        ).pack(side="left")
        build_button(
            self.workspace_toolbar,
            text="Export",
            command=self.export,
            variant="secondary",
            padx=10,
            pady=4,
        ).pack(side="left", padx=(6, 0))
        build_button(
            self.workspace_toolbar,
            text="Delete",
            command=self.delete_selected_object,
            variant="danger",
            padx=10,
            pady=4,
        ).pack(side="left", padx=(6, 0))

        self.canvas = tk.Canvas(
            self.workspace_frame,
            bg=COLORS["canvas"],
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.status_label = tk.Label(
            self.workspace_frame,
            text="",
            anchor="w",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=FONTS["small"],
            padx=10,
            pady=6,
        )
        self.status_label.pack(fill="x")

        self.canvas.bind("<Shift-ButtonPress-1>", self._start_layer_drag)
        self.canvas.bind("<Shift-B1-Motion>", self._drag_active_layer)
        self.canvas.bind("<Shift-ButtonRelease-1>", self._stop_layer_drag)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Double-Button-1>", self._start_rotation_interaction)
        self.canvas.bind("<ButtonPress-1>", self._start_object_interaction)
        self.canvas.bind("<B1-Motion>", self._drag_selected_object)
        self.canvas.bind("<ButtonRelease-1>", self._stop_object_interaction)
        self.canvas.bind("<Delete>", lambda _event: self.delete_selected_object())
        self.canvas.bind("<BackSpace>", lambda _event: self.delete_selected_object())
        self.okno.bind("<Delete>", lambda _event: self.delete_selected_object())
        self.okno.bind("<BackSpace>", lambda _event: self.delete_selected_object())
        for key, dx, dy in (
            ("<Left>", -1, 0),
            ("<Right>", 1, 0),
            ("<Up>", 0, -1),
            ("<Down>", 0, 1),
            ("<Shift-Left>", -10, 0),
            ("<Shift-Right>", 10, 0),
            ("<Shift-Up>", 0, -10),
            ("<Shift-Down>", 0, 10),
        ):
            self.okno.bind(key, lambda _event, x=dx, y=dy: self._nudge_selected_object(x, y))
        self.okno.after_idle(self.redraw_canvas)
        self._update_status()

    def _on_canvas_configure(self, _event):
        if not any(layer.visible and layer.objects for layer in self.layers):
            self.redraw_canvas()

    def _iter_visible_image_objects_with_layers(self):
        for layer in self.layers:
            if not layer.visible:
                continue
            for image_obj in layer.objects:
                yield layer, image_obj

    def _find_object_at(self, x, y):
        for layer, image_obj in reversed(list(self._iter_visible_image_objects_with_layers())):
            width, height = image_obj.pil_image.size
            if image_obj.x <= x <= image_obj.x + width and image_obj.y <= y <= image_obj.y + height:
                return layer, image_obj
        return None, None

    def _selected_object_bounds(self):
        if self.selected_object is None:
            return None
        width, height = self.selected_object.pil_image.size
        x = int(self.selected_object.x)
        y = int(self.selected_object.y)
        return x, y, width, height

    def _hit_selected_corner(self, x, y):
        bounds = self._selected_object_bounds()
        if bounds is None:
            return None
        obj_x, obj_y, width, height = bounds
        corners = {
            "nw": (obj_x, obj_y),
            "ne": (obj_x + width, obj_y),
            "sw": (obj_x, obj_y + height),
            "se": (obj_x + width, obj_y + height),
        }
        for corner, (corner_x, corner_y) in corners.items():
            if abs(x - corner_x) <= SELECTION_CORNER_HIT_RADIUS and abs(y - corner_y) <= SELECTION_CORNER_HIT_RADIUS:
                return corner
        return None

    def _replace_object_image(self, image_obj, pil_image):
        image_obj.pil_image = pil_image.convert("RGBA").copy()
        image_obj.photo_image = ImageTk.PhotoImage(image_obj.pil_image)

    def _start_resize_interaction(self, corner, event):
        bounds = self._selected_object_bounds()
        if bounds is None:
            return
        obj_x, obj_y, width, height = bounds
        anchors = {
            "nw": (obj_x + width, obj_y + height),
            "ne": (obj_x, obj_y + height),
            "sw": (obj_x + width, obj_y),
            "se": (obj_x, obj_y),
        }
        self.resize_state = {
            "corner": corner,
            "anchor": anchors[corner],
            "start_image": self.selected_object.pil_image.copy(),
            "start_width": width,
            "start_height": height,
        }
        self.dragging_object = self.selected_object
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self._update_status("Resizing image")

    def _resize_selected_object(self, event):
        if self.selected_object is None or self.resize_state is None:
            return
        state = self.resize_state
        anchor_x, anchor_y = state["anchor"]
        start_width = max(1, state["start_width"])
        start_height = max(1, state["start_height"])
        scale_x = abs(event.x - anchor_x) / start_width
        scale_y = abs(event.y - anchor_y) / start_height
        scale = max(scale_x, scale_y, MIN_OBJECT_SIZE / start_width, MIN_OBJECT_SIZE / start_height)
        new_width = max(MIN_OBJECT_SIZE, int(start_width * scale))
        new_height = max(MIN_OBJECT_SIZE, int(start_height * scale))
        resized = state["start_image"].resize((new_width, new_height), Image.LANCZOS)

        corner = state["corner"]
        if corner == "nw":
            self.selected_object.x = anchor_x - new_width
            self.selected_object.y = anchor_y - new_height
        elif corner == "ne":
            self.selected_object.x = anchor_x
            self.selected_object.y = anchor_y - new_height
        elif corner == "sw":
            self.selected_object.x = anchor_x - new_width
            self.selected_object.y = anchor_y
        else:
            self.selected_object.x = anchor_x
            self.selected_object.y = anchor_y

        self._replace_object_image(self.selected_object, resized)
        self.redraw_canvas()
        self._update_status("Resizing image")

    def _start_rotation_interaction(self, event):
        corner = self._hit_selected_corner(event.x, event.y)
        if corner is None or self.selected_object is None:
            return
        self.rotation_mode = True
        self.rotate_state = None
        self.resize_state = None
        self.dragging_object = None
        self._update_status("Rotation ready: drag the image")
        return "break"

    def _start_rotation_drag(self, event):
        if self.selected_object is None:
            return
        width, height = self.selected_object.pil_image.size
        center_x = self.selected_object.x + (width / 2)
        center_y = self.selected_object.y + (height / 2)
        self.rotate_state = {
            "center": (center_x, center_y),
            "start_angle": math.atan2(event.y - center_y, event.x - center_x),
            "start_image": self.selected_object.pil_image.copy(),
        }
        self.resize_state = None
        self.dragging_object = self.selected_object
        self._update_status("Rotate: drag around the image")

    def _rotate_selected_object(self, event):
        if self.selected_object is None or self.rotate_state is None:
            return
        center_x, center_y = self.rotate_state["center"]
        current_angle = math.atan2(event.y - center_y, event.x - center_x)
        delta_degrees = math.degrees(current_angle - self.rotate_state["start_angle"])
        rotated = self.rotate_state["start_image"].rotate(
            -delta_degrees,
            expand=True,
            resample=Image.BICUBIC,
        )
        self._replace_object_image(self.selected_object, rotated)
        self.selected_object.x = center_x - (rotated.width / 2)
        self.selected_object.y = center_y - (rotated.height / 2)
        self.redraw_canvas()
        self._update_status(f"Rotating image: {int(delta_degrees)} deg")

    def _clear_selected_object(self, redraw=True):
        self.selected_object = None
        self.selected_object_layer = None
        self.dragging_object = None
        self.resize_state = None
        self.rotate_state = None
        self.rotation_mode = False
        if redraw:
            self.redraw_canvas()
        self._update_status()

    def _select_object(self, layer, image_obj):
        self.selected_object = image_obj
        self.selected_object_layer = layer
        self.active_layer = layer
        self.active_layers = [layer]
        self.refresh_layers_ui()
        self.redraw_canvas()
        self._update_status()

    def _start_object_interaction(self, event):
        if event.state & 0x0001:
            return
        self.canvas.focus_set()
        if self.rotation_mode and self.selected_object is not None:
            self._start_rotation_drag(event)
            return "break"
        corner = self._hit_selected_corner(event.x, event.y)
        if corner is not None and self.selected_object is not None:
            self._start_resize_interaction(corner, event)
            return "break"
        layer, image_obj = self._find_object_at(event.x, event.y)
        if image_obj is None:
            self._clear_selected_object()
            return
        self._select_object(layer, image_obj)
        self.dragging_object = image_obj
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        return "break"

    def _drag_selected_object(self, event):
        if self.dragging_object is None:
            return
        if self.rotate_state is not None:
            self._rotate_selected_object(event)
            return "break"
        if self.resize_state is not None:
            self._resize_selected_object(event)
            return "break"
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        if dx == 0 and dy == 0:
            return "break"
        self.dragging_object.x += dx
        self.dragging_object.y += dy
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.redraw_canvas()
        self._update_status("Moving image")
        return "break"

    def _stop_object_interaction(self, _event):
        was_rotating = self.rotate_state is not None
        self.dragging_object = None
        self.resize_state = None
        self.rotate_state = None
        if was_rotating:
            self.rotation_mode = False
        self._update_status()

    def _nudge_selected_object(self, dx, dy):
        if self.selected_object is None:
            if self.move_active_layer(dx, dy):
                self._update_status("Layer moved")
                return "break"
            return None
        self.selected_object.x += dx
        self.selected_object.y += dy
        self.redraw_canvas()
        self._update_status("Image moved")
        return "break"

    def _update_status(self, prefix=None):
        if self.status_label is None:
            return
        layer_name = self.active_layer.name if self.active_layer is not None else "No layer"
        layer_count = len(self.layers)
        object_count = sum(len(layer.objects) for layer in self.layers)
        if self.selected_object is not None:
            x = int(self.selected_object.x)
            y = int(self.selected_object.y)
            width, height = self.selected_object.pil_image.size
            detail = f"Selected image: {width}x{height} at {x}, {y}"
        else:
            detail = "Click an image to select it. Drag or use arrow keys to move."
        message = f"{layer_name} | {layer_count} layers | {object_count} images | {detail}"
        if prefix:
            message = f"{prefix} | {message}"
        self.status_label.configure(text=message, bg=COLORS["bg"], fg=COLORS["muted"])

    def redraw_canvas(self):
        if self.canvas is None:
            return

        self.canvas.delete("all")
        visible_objects = list(self._iter_visible_image_objects_with_layers())
        if not visible_objects:
            width = max(1, int(self.canvas.winfo_width()))
            height = max(1, int(self.canvas.winfo_height()))
            self.canvas.create_text(
                width // 2,
                height // 2,
                text="Import an image to start composing",
                fill=COLORS["muted"],
                font=FONTS["section"],
            )
            self._update_status()
            return

        for _layer, image_obj in visible_objects:
            self.canvas.create_image(
                image_obj.x,
                image_obj.y,
                anchor="nw",
                image=image_obj.photo_image,
            )
            if image_obj is self.selected_object:
                width, height = image_obj.pil_image.size
                x1 = int(image_obj.x)
                y1 = int(image_obj.y)
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x1 + width,
                    y1 + height,
                    outline=COLORS["accent2"],
                    width=2,
                    dash=(6, 3),
                )
                self.canvas.create_rectangle(
                    x1 - 2,
                    y1 - 2,
                    x1 + width + 2,
                    y1 + height + 2,
                    outline=COLORS["accent"],
                    width=1,
                )
        self._update_status()

    def run(self):
        self.okno.mainloop()


def main():
    app = Wlepmeister()
    app.run()


if __name__ == "__main__":
    app = Wlepmeister()
    app.run()
