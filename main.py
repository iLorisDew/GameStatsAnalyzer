import tkinter as tk
import os
import sys
from controller import StatsController

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

# ========================================
root = tk.Tk()
root.title("Game Stats Analyzer")
root.geometry("1200x800")
root.configure(bg="#0d1117")

# Icône (marche en dev ET en .exe)
try:
    root.iconbitmap(resource_path("assets/fox.ico"))
except:
    pass

StatsController(root)
root.mainloop()