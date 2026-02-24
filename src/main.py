import os 
import sys
import tkinter as tk
from tkinter import filedialog, Canvas
from PIL import Image, ImageTk
from layers_mod import Layer
from tkinter import simpledialog
from tkinter import messagebox


def resource_path(relative_path):
    """ absolute path for build"""
    try:
        base_path = sys._MEIPASS 
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path) # ścieżka ikony dla paska zadań oraz okna

# ============================================
# KLASY
# ============================================

class ImageObject:
    """single image"""
    def __init__(self, image_path, x=0, y=0):
        {} # przechowywanie photo image potem
        
# ============================================
# MAIN
# ============================================
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
            pady=2
        )
        label.pack()

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class Wlepmeister:
    def __init__(self): # metoda kontruktota init
        self.okno = tk.Tk() # okno główne tkinter tworzymy
        icon_path = resource_path("../media/icon_py_128.ico") # ikona pliku
        self.okno.iconbitmap(icon_path) # ikona dla paska zadań oraz okna
        self.okno.title("WLEPMEISTER") # title
        self.okno.geometry("900x600")
        self.layers = []
        self.active_layer = None # jedna domyślnie musi być
        self.dragging_object = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.setup_ui()
        
    def add_layer(self):
        name = f"Layer {len(self.layers) + 1}"
        layer = Layer(name)
        self.layers.append(layer)
        self.active_layer = layer
        self.refresh_layers_ui()

    def set_active_layer(self, layer):
        self.active_layer = layer
        self.refresh_layers_ui()

    def rename_layer(self, layer):
        new_name = simpledialog.askstring(
            "Rename layer",
            "New layer name:",
            initialvalue=layer.name
        )
        if new_name:
            layer.name = new_name
            self.refresh_layers_ui()

    def move_layer(self, index, direction):
        new_index = index + direction
        if 0 <= new_index < len(self.layers):
            self.layers[index], self.layers[new_index] = (
                self.layers[new_index],
                self.layers[index]
            )
            self.refresh_layers_ui()
    
    def delete_layer(self, layer):
        if layer not in self.layers:
            return

        confirm = messagebox.askyesno(
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć warstwę:\n\n'{layer.name}' ?"
        )

        if not confirm:
            return

        self.layers.remove(layer)

        # jeśli usunięto aktywną warstwę
        if self.active_layer == layer:
            self.active_layer = self.layers[-1] if self.layers else None

        self.refresh_layers_ui()


    def toggle_layer_visibility(self, layer):
        layer.visible = not layer.visible
        self.refresh_layers_ui()
    
    def refresh_layers_ui(self):
        for widget in self.layers_container.winfo_children():
            widget.destroy()
        for index, layer in reversed(list(enumerate(self.layers))):
            self.create_layer_widget(layer, index)

    def truncate_text(self, text, max_chars=18):
        if len(text) <= max_chars:
            return text
        return text[:max_chars - 3] + "..."

    def create_layer_widget(self, layer, index):
        frame = tk.Frame(
            self.layers_container,
            bg="#ffffff" if layer == self.active_layer else "#cccccc",
            relief="raised",
            bd=1 
        )
        frame.pack(fill="x", padx=4, pady=2)

        drag_label = tk.Label(frame, text="≡")
        drag_label.pack(side="left", padx=4)

        ## 👁 / 🙈 widac albo nie widac to mozna se potem zmienic
        eye_icon = "👁" if layer.visible else "🙈"

        visibility_btn = tk.Button(
            frame,
            text=eye_icon,
            width=2,
            command=lambda l=layer: self.toggle_layer_visibility(layer)
        )
        visibility_btn.pack(side="left", padx=2)

        #tooltip zalezy od tego czy visible czy nie
        tooltip_text = "Ukryj layer" if layer.visible else "Pokaż layer"
        Tooltip(visibility_btn, tooltip_text)

        display_name = self.truncate_text(layer.name)

        name_label = tk.Label(
            frame,
            text=display_name,
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)

        # tooltip z pełną nazwą
        Tooltip(name_label, layer.name)

        drag_label.bind("<Button-1>", lambda e: self.set_active_layer(layer))

        name_label.bind("<Double-Button-1>",
           lambda e: self.rename_layer(layer))

        
        up_btn = tk.Button(
            frame,
            text="▲",
            width=2,
            command=lambda: self.move_layer(index, 1)
        )
        up_btn.pack(side="right")
        Tooltip(up_btn, "Przesuń layer w górę")

        down_btn = tk.Button(
            frame,
            text="▼",
            width=2,
            command=lambda: self.move_layer(index, -1)
        )
        down_btn.pack(side="right")
        Tooltip(down_btn, "Przesuń layer w dół")

        delete_btn = tk.Button(
            frame,
            text="❌",
            width=2,
            command=lambda l=layer: self.delete_layer(l)
        )
        delete_btn.pack(side="right", padx=2)

        Tooltip(delete_btn, "Usuń layer")


    def add_image(self): pass    # na pozniejszy rozwoj
    def export(self): pass      # na pozniejszy rozwoj
    def print(self): pass      # na pozniejszy rozwoj
    def new_window(self): 
        new = Wlepmeister()
        new.run()
    def properties(self): pass      # na pozniejszy rozwoj (black theme, grid autoskalowalny)
    def toggle_alpha(self):
        # alpha = self.okno.attributes("-alpha")
        # if alpha == 1:
        #     self.okno.attributes("-alpha", 0.5) # przezroczystość okna i menu
        # if alpha == 0.5:
        #     self.okno.attributes("-alpha", 0.75)
        # if alpha == 0.75:
        #     self.okno.attributes("-alpha", 1)
        alpha_levels = [0.5,0.75,1]
        current_alpha_levels = self.okno.attributes("-alpha")
        next_alpha_level = (alpha_levels.index(current_alpha_levels) + 1) % len(alpha_levels)
        self.okno.attributes("-alpha", alpha_levels[next_alpha_level])
    def show_message(self,text,duration=2000): # 
        message = tk.Label(self.okno, text=text, bg="#e3fca9", fg="#000000")
        message.place(relx=1.0,rely=1.0,anchor="se")
        self.okno.after(duration,message.destroy) # znika po czasie

    def setup_ui(self):
        """UI building"""

        menu_bar = tk.Menu(self.okno)# menu pasek
        self.okno.configure(bg="#fca9b8")
        self.okno.configure(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0) # file_menu czyli plik
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

        edit_menu = tk.Menu(menu_bar, tearoff=0)# edycja
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        edit_menu.add_separator()
        edit_menu.add_command(label="New layer", command=self.add_layer)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Alpha", command=self.toggle_alpha)

        # === LEFT PANEL ===

        MAX_LAYERS_WIDTH = 250  # ← tu ustawiasz max szerokość

        self.left_panel = tk.Frame(
            self.okno,
            width=MAX_LAYERS_WIDTH,
            bg="#dddddd"
        )

        self.left_panel.pack(side="left", fill="y")

        # 🔒 blokuje automatyczne zmiany rozmiaru
        self.left_panel.pack_propagate(False)
        header = tk.Frame(self.left_panel, bg="#bbbbbb")
        header.pack(fill="x")
        tk.Label(header, text="Layers", bg="#bbbbbb").pack(side="left", padx=5)
        add_btn = tk.Button(header, text="+", command=self.add_layer)
        add_btn.pack(side="right", padx=5)
        Tooltip(add_btn, "Dodaj nowy layer")
        self.layers_container = tk.Frame(self.left_panel, bg="#dddddd")
        self.layers_container.pack(fill="both", expand=True)

    def run(self):
        """execution"""
        self.okno.mainloop()

# ============================================
# EXEKUCJA
# ============================================

# if __name__ == "__main__":
app = Wlepmeister()
app.run()