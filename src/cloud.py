import io
import tkinter as tk
import zlib

from PIL import Image

from .db import (
    add_favorite_project,
    delete_user_cloud_project,
    list_user_cloud_projects,
    load_user_cloud_project,
    remove_favorite_project,
    save_cloud_project,
    share_cloud_project,
)
from .image_object import ImageObject
from .layers_mod import Layer
from .theme_colors import COLORS, FONTS
from .ui_dialogs import ask_yes_no, prompt_string, show_error, show_info, show_warning
from .ui_theme import apply_titlebar_color

_TITLE_FONT = FONTS["section"]
_BODY_FONT = FONTS["body"]


class CloudUIMixin:
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
        dialog.configure(bg=COLORS["surface"])
        apply_titlebar_color(dialog)
        self._center_child_window(dialog, width, height)
        return dialog

    def _ask_cloud_project_name(self):
        dialog = self._create_cloud_dialog("Save to cloud", 420, 200)
        result = {"name": None}

        bg = COLORS["surface"]
        container = tk.Frame(dialog, bg=bg, padx=16, pady=14)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="Save project to cloud",
            bg=bg,
            fg=COLORS["text"],
            font=_TITLE_FONT,
        ).pack(anchor="w", pady=(0, 10))
        tk.Label(
            container,
            text="Project name:",
            bg=bg,
            fg=COLORS["muted"],
            font=_BODY_FONT,
        ).pack(anchor="w")

        name_var = tk.StringVar()
        entry = tk.Entry(
            container,
            textvariable=name_var,
            font=_BODY_FONT,
            relief="flat",
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        entry.pack(fill="x", pady=(6, 12), ipady=5)
        entry.focus_set()

        buttons = tk.Frame(container, bg=bg)
        buttons.pack(fill="x")

        def submit():
            value = name_var.get().strip()
            if not value:
                show_error(dialog, "Invalid name", "Project name cannot be empty.")
                return
            result["name"] = value
            dialog.destroy()

        tk.Button(
            buttons,
            text="Cancel",
            width=10,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            command=dialog.destroy,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=_BODY_FONT,
        ).pack(side="right")
        tk.Button(
            buttons,
            text="Save",
            width=10,
            bg=COLORS["accent"],
            fg="#ffffff",
            activebackground=COLORS["accent_dark"],
            activeforeground="#ffffff",
            command=submit,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=_BODY_FONT,
        ).pack(side="right", padx=(0, 8))

        dialog.bind("<Return>", lambda _event: submit())
        dialog.wait_window()
        return result["name"]

    def save_project_to_cloud(self):
        if not self.current_user:
            show_warning(self.okno, "Login required", "Log in first to save project in cloud.")
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
        show_error(self.okno, "Cloud save failed", "Could not save project to cloud.")

    def _format_project_label(self, project):
        prefix = "[*] " if project.get("is_favorite") else "[ ] "
        name = project.get("project_name", "")
        owner = project.get("owner", "")
        if project.get("is_shared"):
            return f"{prefix}{name} (shared from {owner})"
        return f"{prefix}{name}"

    def _pick_cloud_project_name(self, projects_loader):
        picker = self._create_cloud_dialog("Open from cloud", 520, 430)
        selected_project = {"value": None}

        bg = COLORS["surface"]
        container = tk.Frame(picker, bg=bg, padx=14, pady=12)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="Open project from cloud",
            bg=bg,
            fg=COLORS["text"],
            font=_TITLE_FONT,
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            container,
            text="Search:",
            bg=bg,
            fg=COLORS["muted"],
            font=_BODY_FONT,
        ).pack(anchor="w")

        search_var = tk.StringVar()
        search_entry = tk.Entry(
            container,
            textvariable=search_var,
            font=_BODY_FONT,
            relief="flat",
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        search_entry.pack(fill="x", pady=(4, 10), ipady=4)

        tk.Label(
            container,
            text="Choose project:",
            bg=bg,
            fg=COLORS["muted"],
            font=_BODY_FONT,
        ).pack(anchor="w", pady=(0, 4))

        listbox = tk.Listbox(
            container,
            height=11,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            selectbackground=COLORS["select_bg"],
            selectforeground=COLORS["select_fg"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
            font=_BODY_FONT,
        )
        listbox.pack(fill="both", expand=True, pady=(0, 10))

        button_row = tk.Frame(container, bg=bg)
        button_row.pack(fill="x")
        favorite_btn = tk.Button(
            button_row,
            text="Star",
            width=10,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=_BODY_FONT,
        )
        favorite_btn.pack(side="left")

        share_btn = tk.Button(
            button_row,
            text="Share",
            width=10,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=_BODY_FONT,
        )
        share_btn.pack(side="left", padx=(8, 0))

        delete_btn = tk.Button(
            button_row,
            text="Delete",
            width=10,
            bg=COLORS["danger"],
            fg="#ffffff",
            activebackground=COLORS["danger_dark"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=_BODY_FONT,
        )
        delete_btn.pack(side="left", padx=(8, 0))

        cancel_btn = tk.Button(
            button_row,
            text="Cancel",
            width=10,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            command=picker.destroy,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=_BODY_FONT,
        )
        cancel_btn.pack(side="right")

        open_btn = tk.Button(
            button_row,
            text="Open",
            width=10,
            bg=COLORS["accent"],
            fg="#ffffff",
            activebackground=COLORS["accent_dark"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=_BODY_FONT,
        )
        open_btn.pack(side="right", padx=(0, 8))

        projects = []
        visible_projects = []

        def refresh_projects():
            nonlocal projects
            projects = projects_loader() or []
            apply_filter()

        def apply_filter():
            nonlocal visible_projects
            term = search_var.get().strip().lower()
            listbox.delete(0, tk.END)
            visible_projects = []
            for project in projects:
                name = project.get("project_name", "")
                owner = project.get("owner", "")
                if term and term not in name.lower() and term not in owner.lower():
                    continue
                listbox.insert(tk.END, self._format_project_label(project))
                visible_projects.append(project)
            if visible_projects:
                listbox.selection_set(0)
            update_buttons()

        def get_selected_project():
            selection = listbox.curselection()
            if not selection:
                return None
            idx = selection[0]
            if idx < 0 or idx >= len(visible_projects):
                return None
            return visible_projects[idx]

        def update_buttons(_event=None):
            project = get_selected_project()
            if not project:
                favorite_btn.configure(state="disabled")
                share_btn.configure(state="disabled")
                delete_btn.configure(state="disabled")
                open_btn.configure(state="disabled")
                return
            open_btn.configure(state="normal")
            favorite_btn.configure(state="normal")
            delete_btn.configure(state="normal")
            share_btn.configure(state="normal" if not project.get("is_shared") else "disabled")
            favorite_btn.configure(text="Unstar" if project.get("is_favorite") else "Star")

        def choose_selected():
            project = get_selected_project()
            if not project:
                return
            selected_project["value"] = project
            picker.destroy()

        def delete_selected():
            project = get_selected_project()
            if not project:
                return
            if project.get("is_shared"):
                show_error(picker, "Not allowed", "You can only delete your own projects.")
                return
            name = project.get("project_name")
            confirm = ask_yes_no(picker, "Confirmation", f"Delete project:\n\n{name}")
            if not confirm:
                return
            if not delete_user_cloud_project(self.current_user, name):
                show_error(picker, "Delete failed", "Could not delete project.")
                return
            refresh_projects()

        def toggle_favorite():
            project = get_selected_project()
            if not project:
                return
            owner = project.get("owner")
            name = project.get("project_name")
            if project.get("is_favorite"):
                remove_favorite_project(self.current_user, owner, name)
            else:
                add_favorite_project(self.current_user, owner, name)
            refresh_projects()

        def share_selected():
            project = get_selected_project()
            if not project:
                return
            if project.get("is_shared"):
                return
            target = prompt_string(picker, "Share project", "Share with username:")
            if not target:
                return
            if share_cloud_project(self.current_user, project.get("project_name"), target):
                show_info(picker, "Shared", f"Project shared with {target}.")
                refresh_projects()
                return
            show_error(picker, "Share failed", "Could not share project.")

        search_entry.bind("<KeyRelease>", lambda _event: apply_filter())
        listbox.bind("<<ListboxSelect>>", update_buttons)
        listbox.bind("<Double-Button-1>", lambda _event: choose_selected())

        open_btn.configure(command=choose_selected)
        delete_btn.configure(command=delete_selected)
        favorite_btn.configure(command=toggle_favorite)
        share_btn.configure(command=share_selected)

        refresh_projects()
        picker.wait_window()
        return selected_project["value"]

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
        self.active_layers = [self.active_layer]
        self.refresh_layers_ui()
        self.redraw_canvas()

    def open_project_from_cloud(self):
        if not self.current_user:
            show_warning(self.okno, "Login required", "Log in first to open project from cloud.")
            return

        def load_projects():
            return list_user_cloud_projects(self.current_user, include_shared=True)

        project_info = load_projects()
        if not project_info:
            show_info(self.okno, "No projects", "No cloud projects for this account yet.")
            return

        selected = self._pick_cloud_project_name(load_projects)
        if not selected:
            return

        project_doc = load_user_cloud_project(
            self.current_user,
            selected.get("project_name"),
            owner_username=selected.get("owner"),
        )
        if not project_doc:
            show_error(self.okno, "Open failed", "Could not load selected project.")
            return

        try:
            self._apply_cloud_project(project_doc)
        except Exception as exc:
            show_error(self.okno, "Open failed", f"Project data is invalid:\n{exc}")
            return

        self.show_message(
            f"Opened cloud project: {selected.get('project_name')}",
            duration=2500,
        )
