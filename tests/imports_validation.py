print("1. Import tkinter...")
import tkinter as tk
print("✓ tkinter OK")

print("2. Import filedialog...")
from tkinter import filedialog, Canvas
print("✓ filedialog OK")

print("3. Import PIL...")
from PIL import Image, ImageTk
print("✓ PIL OK")

print("4. Tworzenie okna...")
okno = tk.Tk()
print("✓ Okno OK")

print("5. Ustawienia okna...")
okno.title("Test")
okno.geometry("400x300")
print("✓ Ustawienia OK")

print("6. Mainloop...")
okno.mainloop()