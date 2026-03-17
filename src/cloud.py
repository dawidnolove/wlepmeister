import io
import tkinter as tk
import zlib

from PIL import Image

from db import (
    delete_user_cloud_project,
    list_user_cloud_projects,
    load_user_cloud_project,
    save_cloud_project,
)
from image_object import ImageObject
from layers_mod import Layer
from ui_dialogs import ask_yes_no, show_error, show_info, show_warning


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
                show_error(dialog, "Invalid name", "Project name cannot be empty.")
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

    def _pick_cloud_project_name(self, project_names):
        picker = self._create_cloud_dialog("Open from cloud", 430, 360)

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

        def delete_selected():
            selection = listbox.curselection()
            if not selection:
                return
            name = listbox.get(selection[0])
            confirm = ask_yes_no(picker, "Confirmation", f"Delete project:\n\n{name}")
            if not confirm:
                return
            if not delete_user_cloud_project(self.current_user, name):
                show_error(picker, "Delete failed", "Could not delete project.")
                return
            listbox.delete(selection[0])
            if listbox.size() > 0:
                listbox.selection_set(0)

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
        tk.Button(
            buttons,
            text="Delete",
            width=10,
            bg="#ffffff",
            activebackground="#f2f2f2",
            command=delete_selected,
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
            show_warning(self.okno, "Login required", "Log in first to open project from cloud.")
            return

        project_names = list_user_cloud_projects(self.current_user)
        if not project_names:
            show_info(self.okno, "No projects", "No cloud projects for this account yet.")
            return

        selected_name = self._pick_cloud_project_name(project_names)
        if not selected_name:
            return

        project_doc = load_user_cloud_project(self.current_user, selected_name)
        if not project_doc:
            show_error(self.okno, "Open failed", "Could not load selected project.")
            return

        try:
            self._apply_cloud_project(project_doc)
        except Exception as exc:
            show_error(self.okno, "Open failed", f"Project data is invalid:\n{exc}")
            return

        self.show_message(f"Opened cloud project: {selected_name}", duration=2500)
