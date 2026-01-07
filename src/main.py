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
        
    def add_layer(self): pass  # na pozniejszy rozwoj
    def add_image(self): pass    # na pozniejszy rozwoj
    def export(self): pass      # na pozniejszy rozwoj
    def print(self): pass      # na pozniejszy rozwoj
    def new_window(self): 
        self.__init__()
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
        next_alpha_level = (alpha_levels.index(current) + 1) % len(alpha_levels)
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

    def run(self):
        """execution"""
        self.okno.mainloop()

# ============================================
# EXEKUCJA
# ============================================

# if __name__ == "__main__":
app = Wlepmeister()
app.run()