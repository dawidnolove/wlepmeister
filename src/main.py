import os 
import sys
import tkinter as tk
from tkinter import filedialog, Canvas
from PIL import Image, ImageTk


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
        self.okno = tk.Tk() # okno główne tkinter
        icon_path = resource_path("media/icon_py_128.ico") # ikona pliku
        self.okno.iconbitmap(icon_path) # ikona dla paska zadań oraz okna
        self.okno.title("WLEPMEISTER") # title
        self.okno.geometry("900x600")
        self.okno.configure(bg="#99ac9d")
        
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

        menu_bar = tk.Menu(self.okno)# menu pasek
        self.okno.config(menu=menu_bar)

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
        file_menu.add_command(label="Exit", command=self.okno.destroy)

        edit_menu = tk.Menu(menu_bar, tearoff=0)# edycja
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