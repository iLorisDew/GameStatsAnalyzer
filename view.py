# view.py ← VERSION FINALE 100% FONCTIONNELLE (copie-colle intégral)
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class StatsView:
    def __init__(self, root, model):
        self.root = root
        self.model = model
        self.root.title("Game Stats Analyzer")
        self.root.configure(bg="#0d1117")
        self.root.minsize(1100, 700)

        self.root.geometry("1000x620")
        self.center_window()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background="#0d1117", foreground="#e6edf3")
        style.configure("Card.TFrame", background="#161b22")
        style.configure("TNotebook", background="#0d1117")
        style.configure("TNotebook.Tab", padding=[25, 12], font=("Segoe UI", 12, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", "#161b22"), ("active", "#21262d")],
                  foreground=[("selected", "#58a6ff"), ("active", "#e6edf3")])

        style.configure("Treeview", background="#161b22", foreground="#e6edf3", fieldbackground="#161b22", rowheight=40)
        style.configure("Treeview.Heading", background="#21262d", foreground="#58a6ff", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[('selected', '#1f6feb')])

        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), padding=14)
        style.configure("Success.TButton", padding=12, background="#238636")
        style.configure("Warning.TButton", padding=12, background="#daaa3f")

        self.main_frame = ttk.Frame(root, style="Card.TFrame", padding="80")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        ttk.Label(self.main_frame, text="Game Stats Analyzer", font=("Segoe UI", 36, "bold"),
                  foreground="#58a6ff").pack(pady=(0, 30))
        ttk.Label(self.main_frame, text="Analyse tes logs de jeu en un clic",
                  font=("Segoe UI", 13), foreground="#8b949e").pack(pady=(0, 80))

        self.load_button = ttk.Button(self.main_frame, text="Charger le fichier Excel", style="Accent.TButton")
        self.load_button.pack(ipadx=60, ipady=20)

        self.results_frame = None
        self.back_button = None
        self.export_button = None

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x, y = (self.root.winfo_screenwidth() // 2) - (w // 2), (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def show_results(self, tree_columns, formatted_data, duration, df):
        if self.results_frame:
            self.results_frame.destroy()

        self.root.geometry("1450x950")
        self.center_window()

        self.results_frame = ttk.Frame(self.root)
        self.results_frame.pack(fill="both", expand=True)

        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        notebook = ttk.Notebook(self.results_frame)
        notebook.grid(row=0, column=0, sticky="nsew", padx=25, pady=(25, 0))

        # === ONGLETS ===
        tab_stats = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(tab_stats, text="   Statistiques   ")

        ttk.Label(tab_stats, text="Résumé de la partie", font=("Segoe UI", 26, "bold"),
                  foreground="#58a6ff").pack(pady=(30, 10))
        h = int(duration.total_seconds()) // 3600
        m = (int(duration.total_seconds()) % 3600) // 60
        s = int(duration.total_seconds()) % 60
        ttk.Label(tab_stats, text=f"Durée : {h:02d}:{m:02d}:{s:02d}",
                  font=("Segoe UI", 16), foreground="#58a6ff").pack(pady=(0, 30))

        tree = ttk.Treeview(tab_stats, columns=tree_columns, show="headings")
        tree.pack(fill="both", expand=True, padx=40, pady=10)
        tree.heading("Stat", text="Statistique")
        tree.column("Stat", width=220, anchor="w")
        for col in tree_columns[1:]:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        for row in formatted_data:
            tree.insert("", "end", values=row)

        # Graphiques
        tab_graph = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(tab_graph, text="   Graphiques   ")

        fig = plt.Figure(figsize=(14, 8), dpi=100, facecolor='#0d1117')
        ax1 = fig.add_subplot(111, facecolor='#0d1117')

        total_minutes = len(df) / 60
        time_minutes = np.linspace(0, total_minutes, len(df))

        line1 = ax1.plot(time_minutes, df['Framerate'], color="#58a6ff", linewidth=3, label="Framerate (FPS)")[0]
        ax1.set_ylabel("FPS", color="#58a6ff", fontsize=14, fontweight="bold")
        ax1.tick_params(axis='y', labelcolor="#58a6ff")
        ax1.set_ylim(bottom=0)

        ax2 = ax1.twinx()
        line2 = ax2.plot(time_minutes, df['GPU temperature'], color="#ff5555", linewidth=3, label="GPU Temp (°C)")[0]
        ax2.set_ylabel("GPU °C", color="#ff5555", fontsize=14, fontweight="bold")
        ax2.tick_params(axis='y', labelcolor="#ff5555")

        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        line3 = ax3.plot(time_minutes, df['CPU usage'], color="#50fa7b", linewidth=3, label="CPU Usage (%)")[0]
        ax3.set_ylabel("CPU %", color="#50fa7b", fontsize=14, fontweight="bold")
        ax3.tick_params(axis='y', labelcolor="#50fa7b")
        ax3.set_ylim(0, 100)

        ax1.set_xlabel("Temps de jeu", color="white", fontsize=13)
        ax1.set_xticks(np.arange(0, total_minutes + 1, max(1, total_minutes // 15)))
        ax1.set_xticklabels([f"{int(m)}:{int((m%1)*60):02d}" for m in np.arange(0, total_minutes + 1, max(1, total_minutes // 15))],
                            color="white")

        ax1.grid(True, color="#30363d", linestyle="--", alpha=0.5)

        lines = [line1, line2, line3]
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc="upper right", frameon=True, facecolor="#161b22",
                   edgecolor="#30363d", labelcolor="white", fontsize=13)

        fig.suptitle("Évolution complète de la partie", color="white", fontsize=22, fontweight="bold")
        fig.tight_layout(rect=[0, 0.02, 1, 0.95])

        canvas = FigureCanvasTkAgg(fig, master=tab_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=40, pady=30)

        # === BOUTONS ===
        btn_frame = tk.Frame(self.results_frame, bg="#0d1117")
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(20, 30))
        btn_frame.grid_columnconfigure(0, weight=1)

        inner = tk.Frame(btn_frame, bg="#0d1117")
        inner.grid(row=0, column=0)

        self.back_button = ttk.Button(inner, text="Retour", style="Success.TButton")
        self.back_button.pack(side="left", padx=200)

        self.export_button = ttk.Button(inner, text="Exporter JSON", style="Warning.TButton")
        self.export_button.pack(side="right", padx=200)

    # === NAVIGATION & D'ACCUEIL ===
    def hide_main(self):
        self.main_frame.pack_forget()

    def show_main(self):
        if self.results_frame:
            self.results_frame.pack_forget()
        self.root.geometry("1000x620")
        self.center_window()
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=40)

    # === DIALOGUES FICHIERS ===
    def ask_open_filename(self, title="Ouvrir", filetypes=None):
        if filetypes is None:
            filetypes = [("Fichiers Excel", "*.xlsx *.xls"), ("Tous les fichiers", "*.*")]
        return filedialog.askopenfilename(title=title, filetypes=filetypes)

    def ask_save_filename(self, title="Enregistrer sous", filetypes=None, defaultextension=".json"):
        if filetypes is None:
            filetypes = [("Fichier JSON", "*.json"), ("Texte", "*.txt"), ("Tous", "*.*")]
        return filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            defaultextension=defaultextension,
            initialfile="game_stats.json"
        )

    # === BOUTONS ===
    def set_load_command(self, command):
        self.load_button.config(command=command)

    def set_back_command(self, command):
        if self.back_button:
            self.back_button.config(command=command)

    def set_export_command(self, command):
        if self.export_button:
            self.export_button.config(command=command)

    # === MESSAGES ===
    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self.root)

    def show_info(self, title, message):
        messagebox.showinfo(title, message, parent=self.root)