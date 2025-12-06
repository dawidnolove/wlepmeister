# instalacja: pip install pillow

import tkinter as tk
from tkinter import filedialog, Canvas
from PIL import Image, ImageTk

# ============================================
# KLASY - STRUKTURA DANYCH
# ============================================

class ImageObject:
    """Pojedynczy obrazek na płótnie"""
    def __init__(self, image_path, x=0, y=0):
        self.image_path = image_path
        self.pil_image = Image.open(image_path)
        self.x = x
        self.y = y
        self.canvas_id = None
        self.photo = None  # Przechowuje PhotoImage
        
class Layer:
    """Warstwa zawierająca wiele obrazków"""
    def __init__(self, name):
        self.name = name
        self.objects = []
        self.visible = True

# ============================================
# APLIKACJA GŁÓWNA
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
        
    def setup_ui(self):
        """Buduje interfejs"""
        
        # ===== GÓRNE MENU =====
        menu_bar = tk.Frame(self.okno, height=50, bg="#2d2d2d")
        menu_bar.pack(fill="x", padx=10, pady=10)
        
        tk.Label(menu_bar, text="Wlepmeister", font=("Arial", 16, "bold"), 
                bg="#2d2d2d", fg="white").pack(side="left", padx=10)
        
        tk.Button(menu_bar, text="Nowa Warstwa", command=self.dodaj_warstwe, 
                 bg="#4d4d4d", fg="white", relief="flat", padx=10).pack(side="left", padx=5)
        
        tk.Button(menu_bar, text="Dodaj Obraz (Ctrl+A)", command=self.dodaj_obraz, 
                 bg="#4d4d4d", fg="white", relief="flat", padx=10).pack(side="left", padx=5)
        
        tk.Button(menu_bar, text="Eksportuj PNG", command=self.eksportuj, 
                 bg="#4d4d4d", fg="white", relief="flat", padx=10).pack(side="left", padx=5)
        
        tk.Button(menu_bar, text="Zamknij", command=self.okno.destroy, 
                 bg="#ff4444", fg="white", relief="flat", padx=10).pack(side="right", padx=10)
        
        # ===== KONTENER GŁÓWNY =====
        main_container = tk.Frame(self.okno, bg="#1a1a1a")
        main_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # ===== PANEL WARSTW (LEWA STRONA) =====
        panel_warstw = tk.Frame(main_container, width=200, bg="#2d2d2d")
        panel_warstw.pack(side="left", fill="y", padx=(0, 10))
        panel_warstw.pack_propagate(False)
        
        tk.Label(panel_warstw, text="Warstwy", font=("Arial", 14, "bold"), 
                bg="#2d2d2d", fg="white").pack(pady=10)
        
        # Frame z scrollbarem dla warstw
        canvas_warstwy = Canvas(panel_warstw, bg="#1a1a1a", highlightthickness=0)
        scrollbar = tk.Scrollbar(panel_warstw, orient="vertical", command=canvas_warstwy.yview)
        self.warstwy_container = tk.Frame(canvas_warstwy, bg="#1a1a1a")
        
        self.warstwy_container.bind(
            "<Configure>",
            lambda e: canvas_warstwy.configure(scrollregion=canvas_warstwy.bbox("all"))
        )
        
        canvas_warstwy.create_window((0, 0), window=self.warstwy_container, anchor="nw")
        canvas_warstwy.configure(yscrollcommand=scrollbar.set)
        
        canvas_warstwy.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))
        scrollbar.pack(side="right", fill="y")
        
        # ===== CANVAS (PRAWA STRONA) =====
        canvas_container = tk.Frame(main_container, bg="#ffffff")
        canvas_container.pack(side="right", fill="both", expand=True)
        
        self.canvas = Canvas(canvas_container, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Bindowanie eventów myszy
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)
        
        # Skrót klawiszowy Ctrl+A
        self.okno.bind("<Control-a>", lambda e: self.dodaj_obraz())
        self.okno.bind("<Control-A>", lambda e: self.dodaj_obraz())
        
    def dodaj_warstwe(self):
        """Tworzy nową warstwę"""
        layer_num = len(self.layers) + 1
        new_layer = Layer(f"Warstwa {layer_num}")
        self.layers.append(new_layer)
        
        # Dodaj przycisk warstwy
        layer_btn = tk.Button(
            self.warstwy_container,
            text=new_layer.name,
            command=lambda l=new_layer: self.wybierz_warstwe(l),
            bg="#3d3d3d",
            fg="white",
            relief="flat",
            activebackground="#4d4d4d"
        )
        layer_btn.pack(fill="x", pady=2, padx=5)
        
        # Automatycznie wybierz nową warstwę
        self.wybierz_warstwe(new_layer)
        
    def wybierz_warstwe(self, layer):
        """Ustawia aktywną warstwę"""
        self.active_layer = layer
        print(f"Aktywna warstwa: {layer.name}")
        
    def dodaj_obraz(self):
        """Otwiera dialog wyboru pliku PNG i dodaje do aktywnej warstwy"""
        if not self.active_layer:
            print("Najpierw utwórz warstwę!")
            return
            
        filepath = filedialog.askopenfilename(
            title="Wybierz obraz PNG",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filepath:
            # Twórz obiekt obrazu
            img_obj = ImageObject(filepath, x=50, y=50)
            
            # Skaluj obraz do max 300px
            img_obj.pil_image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Dodaj do warstwy
            self.active_layer.objects.append(img_obj)
            
            # Wyświetl na canvas
            self.rysuj_canvas()
            
    def rysuj_canvas(self):
        """Odrysowuje wszystkie obiekty na canvas"""
        self.canvas.delete("all")
        
        # Iteruj przez wszystkie warstwy
        for layer in self.layers:
            if not layer.visible:
                continue
                
            # Iteruj przez obiekty w warstwie
            for obj in layer.objects:
                # Konwertuj PIL Image do PhotoImage
                obj.photo = ImageTk.PhotoImage(obj.pil_image)
                
                # Rysuj na canvas
                canvas_id = self.canvas.create_image(
                    obj.x, obj.y, 
                    image=obj.photo, 
                    anchor="nw"
                )
                obj.canvas_id = canvas_id
                
    def canvas_click(self, event):
        """Obsługa kliknięcia na canvas"""
        # Znajdź obiekt pod kursorem
        clicked_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        
        if not clicked_items:
            return
            
        clicked_id = clicked_items[-1]  # Ostatni = najwyższy
        
        # Znajdź ImageObject
        for layer in self.layers:
            for obj in layer.objects:
                if obj.canvas_id == clicked_id:
                    self.dragging_object = obj
                    self.drag_start_x = event.x - obj.x
                    self.drag_start_y = event.y - obj.y
                    return
                    
    def canvas_drag(self, event):
        """Obsługa przeciągania"""
        if self.dragging_object:
            self.dragging_object.x = event.x - self.drag_start_x
            self.dragging_object.y = event.y - self.drag_start_y
            self.rysuj_canvas()
            
    def canvas_release(self, event):
        """Obsługa puszczenia myszy"""
        self.dragging_object = None
        
    def eksportuj(self):
        """Zapisuje canvas jako PNG"""
        if not self.layers:
            print("Brak warstw do eksportu!")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        
        if filepath:
            # Znajdź wymiary canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Utwórz nowy obraz
            final_image = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 255))
            
            # Składaj warstwy
            for layer in self.layers:
                if not layer.visible:
                    continue
                for obj in layer.objects:
                    final_image.paste(obj.pil_image, (int(obj.x), int(obj.y)), obj.pil_image)
                    
            final_image.save(filepath)
            print(f"Zapisano: {filepath}")
            
    def run(self):
        """Uruchamia aplikację"""
        self.okno.mainloop()

# ============================================
# URUCHOMIENIE
# ============================================

if __name__ == "__main__":
    app = Wlepmeister()
    app.run()