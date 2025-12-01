# controller.py – VERSION FINALE CORRIGÉE
from model import StatsModel
from view import StatsView
import tkinter as tk
from tkinter import ttk, messagebox


class StatsController:
    def __init__(self, root):
        self.model = StatsModel()
        self.view = StatsView(root, self.model)
        self.view.set_load_command(self.load_excel_file)
        self.stats = None
        self.current_file = None

    def load_excel_file(self):
        file_path = self.view.ask_open_filename(
            "Choisis ton log MSI Afterburner",
            (("Fichiers Excel", "*.xlsx *.xls"), ("Tous", "*.*"))
        )
        if not file_path:
            return

        self.current_file = file_path
        result, error, extra = self.model.compute_stats(file_path)

        if error == "NEED_COLUMN_SELECTION":
            self.show_column_dialog(extra, file_path)
            return

        if error:
            self.view.show_error("Erreur", error)
            return

        self.display_results(result)

    def show_column_dialog(self, df_preview, file_path):
        dialog = tk.Toplevel(self.view.root)
        dialog.title("Sélectionne les colonnes à analyser")
        dialog.geometry("900x750")
        dialog.transient(self.view.root)
        dialog.grab_set()
        dialog.configure(bg="#0d1117")

        tk.Label(dialog, text="Quelles colonnes veux-tu analyser ?", bg="#0d1117",
                 fg="#58a6ff", font=("Segoe UI", 16, "bold")).pack(pady=20)

        frame = tk.Frame(dialog, bg="#0d1117")
        frame.pack(fill="both", expand=True, padx=30)

        canvas = tk.Canvas(frame, bg="#161b22")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="#161b22")

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        self.vars = {}
        for col in df_preview.columns:
            default = any(k in str(col).lower() for k in ["frame","temp","usage","clock","fps","mhz","°c","%"])
            v = tk.BooleanVar(value=default)
            self.vars[col] = v
            tk.Checkbutton(inner, text=str(col), variable=v, bg="#161b22", fg="white",
                           selectcolor="#21262d", font=("Segoe UI", 10)).pack(anchor="w", pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        btns = tk.Frame(dialog, bg="#0d1117")
        btns.pack(pady=30)
        tk.Button(btns, text="Annuler", command=dialog.destroy, bg="#444", fg="white").pack(side="right", padx=10)
        tk.Button(btns, text="Analyser →", command=lambda: self.validate_columns(dialog, file_path),
                  bg="#238636", fg="white", font=("Segoe UI", 11, "bold")).pack(side="right", padx=10)

    def validate_columns(self, dialog, file_path):
        selected = [col for col, var in self.vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("Attention", "Coche au moins une colonne !")
            return

        dialog.destroy()

        result, error, _ = self.model.compute_stats(file_path, selected_columns=selected)
        if error:
            self.view.show_error("Erreur", error)
            return
        self.display_results(result)

    def display_results(self, result):
        self.stats = result['stats']
        df = result['df']
        duration = result['duration']

        tree_columns, formatted_data = self.model.format_stats_for_display(self.stats)

        self.view.hide_main()
        self.view.show_results(tree_columns, formatted_data, duration, df)

        self.view.set_back_command(self.back_to_main)
        self.view.set_export_command(self.export_to_txt)

    def export_to_txt(self):
        if not self.stats:
            return

        file_path = self.view.ask_save_filename(
            title="Exporter les statistiques",
            filetypes=[("JSON", "*.json"), ("Texte", "*.txt"), ("Tous", "*.*")],
            defaultextension=".json"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.model.generate_export_text(self.stats))
            self.view.show_info("Succès", "Export terminé !")
        except Exception as e:
            self.view.show_error("Erreur", str(e))

    def back_to_main(self):
        self.view.show_main()
        self.stats = None
        self.current_file = None