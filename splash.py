# splash.py
import tkinter as tk
from tkinter import ttk
import time
import threading

def show_splash(root, on_finish):
    splash = tk.Toplevel(root)
    splash.configure(bg="#0d1117")
    splash.overrideredirect(True)  # sans bordure
    splash.geometry(f"500x300+{root.winfo_screenwidth()//2-250}+{root.winfo_screenheight()//2-150}")
    splash.lift()
    splash.attributes("-topmost", True)

    # Titre
    tk.Label(splash, text="Game Stats Analyzer", font=("Segoe UI", 28, "bold"),
             fg="#58a6ff", bg="#0d1117").pack(pady=60)

    # Sous-titre
    tk.Label(splash, text="Chargement des modules...", font=("Segoe UI", 12),
             fg="#8b949e", bg="#0d1117").pack(pady=10)

    # Barre de progression
    progress = ttk.Progressbar(splash, length=300, mode="determinate")
    progress.pack(pady=30)

    # Animation
    def animate():
        for i in range(101):
            progress['value'] = i
            splash.update()
            time.sleep(0.03)
        splash.destroy()
        on_finish()  # lance l’app principale

    threading.Thread(target=animate, daemon=True).start()