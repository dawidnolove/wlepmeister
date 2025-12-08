import tkinter as tk
from tkinter import filedialog, Canvas
from PIL import Image, ImageTk

# ============================================
# KLASY
# ============================================

class ImageObject:
    """single image"""
    def __init__(self, image_path, x=0, y=0):
        self.image_path = image_path
        self.pil_image = Image.open(image_path)
        self.x = x
        self.y = y
        self.canvas_id = None
        self.photo = None  # Przechowuje PhotoImage
        
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
        self.okno.title("Wlepmeister MVP")
        self.okno.geometry("900x600")
        self.okno.configure(bg="#1a1a1a")
        
        # Dane aplikacji
        self.layers = []
        self.active_layer = None
        self.dragging_object = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.setup_ui()
        
    def dodaj_warstwe(self): pass  # na pozniejszy rozwoj
    def dodaj_obraz(self): pass    # na pozniejszy rozwoj
    def eksportuj(self): pass      # na pozniejszy rozwoj

    def setup_ui(self):
        """UI build up"""

        # ===== menu =====
        menu_bar = tk.Menu(self.okno)
        self.okno.config(menu=menu_bar)

        # Plik
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New layer", command=self.dodaj_warstwe)
        file_menu.add_command(label="Add image", command=self.dodaj_obraz)
        file_menu.add_separator()
        file_menu.add_command(label="Export as PNG", command=self.eksportuj)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.okno.destroy)

        menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

    def run(self):
        """execution"""
        self.okno.mainloop()

# ============================================
# EXEKUCJA
# ============================================

if __name__ == "__main__":
    app = Wlepmeister()
    app.run()
