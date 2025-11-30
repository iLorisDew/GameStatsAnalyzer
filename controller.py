# controller.py
from model import StatsModel
from view import StatsView
import pandas as pd


class StatsController:
    def __init__(self, root):
        self.model = StatsModel()
        self.view = StatsView(root, self.model)  # Passer self.model à StatsView
        self.view.set_load_command(self.load_excel_file)
        self.stats = None  # To store stats for export

    def load_excel_file(self):
        file_path = self.view.ask_open_filename(
            "Select Excel File",
            (("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if not file_path:
            return

        result, error = self.model.compute_stats( file_path )
        if error:
            self.view.show_error( "Error", error )
            return
        if result is None:
            self.view.show_info( "No Data", "No data to display." )
            return

        # On récupère tout proprement
        stats = result['stats']
        df = result['df']
        duration = result['duration']

        self.stats = stats

        tree_columns, formatted_data = self.model.format_stats_for_display( stats )

        self.view.hide_main()
        self.view.show_results( tree_columns, formatted_data, duration, df )  # df bien passé !

        self.view.set_back_command( self.back_to_main )
        self.view.set_export_command( self.export_to_txt )

    def export_to_txt(self):
        if not self.stats:
            return

        file_path = self.view.ask_save_filename(
            "Save Stats as TXT",
            (("Text files", "*.txt"), ("All files", "*.*")),
            ".txt"
        )
        if not file_path:
            return  # User canceled

        try:
            export_text = self.model.generate_export_text(self.stats)
            with open(file_path, 'w') as f:
                f.write(export_text)
            self.view.show_info("Success", "Stats exported successfully!")
        except Exception as e:
            self.view.show_error("Error", f"Failed to export: {str(e)}")

    def back_to_main(self):
        self.view.show_main()