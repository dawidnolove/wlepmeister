import tkinter as tk
from tkinter import filedialog, Canvas
from PIL import Image, ImageTk

# ============================================
# KLASY
# ============================================

class ImageObject:
    """single image"""
    def __init__(self, image_path, x=0, y=0):
        {} # przechowywanie photo image
        
class Layer:
    """layer with images"""
    def __init__(self, name):
        self.name = name
        self.objects = []
        self.visible = True

# ============================================
# MAIN
# ============================================

class Wlepmeister:
    def __init__(self):
        # Okno główne
        self.okno = tk.Tk()
        self.okno.title("WLEPMEISTER")
        self.okno.geometry("900x600")
        self.okno.configure(bg="#1a1a1a")
        
        # Dane aplikacji
        self.layers = []
        self.active_layer = None
        self.dragging_object = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.setup_ui()
        
    def add_layer(self): pass  # na pozniejszy rozwoj
    def add_image(self): pass    # na pozniejszy rozwoj
    def export(self): pass      # na pozniejszy rozwoj
    def print(self): pass      # na pozniejszy rozwoj
    def new_window(self): pass      # na pozniejszy rozwoj
    def properties(self): pass      # na pozniejszy rozwoj (black theme, grid autoskalowalny)


    def setup_ui(self):
        """UI build up"""

        # ===== menu =====
        menu_bar = tk.Menu(self.okno)
        self.okno.config(menu=menu_bar)

        # Plik
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
        file_menu.add_command(label="Exit", command=self.okno.destroy)

        # Edit
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        edit_menu.add_separator()
        edit_menu.add_command(label="New layer", command=self.add_layer)

    def run(self):
        """execution"""
        self.okno.mainloop()

# ============================================
# EXEKUCJA
# ============================================

if __name__ == "__main__":
    app = Wlepmeister()
    app.run()
