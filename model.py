# model.py – VERSION FINALE DYNAMIQUE (tableau et stats adaptables aux colonnes sélectionnées)
import pandas as pd
import numpy as np
import json
from pathlib import Path


class StatsModel:
    def __init__(self):
        self.config_file = Path("config.json")
        self.presets = self.load_presets()

    def load_presets(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_preset(self, file_path, selected):
        self.presets[str(file_path)] = selected
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.presets, f, indent=2)

    def compute_stats(self, file_path, selected_columns=None):
        try:
            df = pd.read_excel(file_path, header=None)

            # Détection code 2 et 80
            header_row = df[df.iloc[:, 0] == 2].index
            if header_row.empty:
                return None, "NEED_COLUMN_SELECTION", df.head(50)
            header_row = header_row[0]

            data_start = df[df.iloc[:, 0] == 80].index
            if data_start.empty:
                return None, "Aucune donnée", None
            data_start = data_start[0]

            headers = df.iloc[header_row].astype(str).str.strip()
            data = df.iloc[data_start:].copy()
            data.columns = headers
            data = data.reset_index(drop=True)

            data = data.iloc[:, 1:].reset_index(drop=True)

            if selected_columns is None:
                return None, "NEED_COLUMN_SELECTION", data

            df_final = data[selected_columns].copy()

            # Scaling /1000
            scale_cols = ['GPU temperature', 'GPU usage', 'Core clock ', 'Temp over limit', 'CPU usage', 'Framerate']
            for col in selected_columns:
                if col in df_final.columns:
                    df_final[col] = pd.to_numeric(df_final[col], errors='coerce') / 1000

            # if 'Framerate' in df_final.columns:
            #     df_final = df_final[df_final['Framerate'] < 1000]

            tooHighFramerateIndexes = (df_final.columns['Framerate'] >= 1000).index
            df_final = df_final.drop( tooHighFramerateIndexes )

            # Durée
            #time_col = df[1]
            #df[1] = pd.to_datetime(df_final[time_col], errors='coerce')
            #df = df.dropna(subset=[time_col])
            #duration = df[time_col].iloc[-1] - df[time_col].iloc[0] if len(df) > 1 else pd.Timedelta(0)
            duration = self.process_timestamp_column(df)

            # df_with_time = df_final.copy()
            df_stats = df_final.copy()

            # Calculs stats
            calc_cols = [c for c in selected_columns if c in df_stats.columns and pd.api.types.is_numeric_dtype(df_stats[c])]

            stats = {}
            for col in calc_cols:
                s = df_stats[col].dropna()
                if len(s) > 0:
                    stats[f'Moyenne {col}'] = {'moyenne': round(s.mean(), 1)}
                    stats[f'Min {col}'] = {'min': round(s.min(), 1)}
                    stats[f'Max {col}'] = {'max': round(s.max(), 1)}
                else:
                    stats[f'Moyenne {col}'] = {'moyenne': 'N/A'}
                    stats[f'Min {col}'] = {'min': 'N/A'}
                    stats[f'Max {col}'] = {'max': 'N/A'}

            stats['Durée Partie'] = {'duration': duration}
            stats['1% Lows'] = self.calculateOnePercentLow(df_stats, calc_cols)

            self.save_preset(file_path, selected_columns)

            return {
                'stats': stats,
                'df': df_with_time,
                'duration': duration
            }, None, None

        except Exception as e:
            return None, f"Erreur : {str(e)}", None

    def calculateOnePercentLow(self, df, columns):
        res = {}
        for col in columns:
            if col in df.columns:
                s = pd.to_numeric(df[col], errors='coerce').dropna()
                res[col] = round(s.quantile(0.01), 1) if len(s) >= 5 else 'N/A'
        return res

    def format_stats_for_display(self, stats):
        # === DYNAMIQUE : ON EXTRAIT LES COLONNES DES CLÉS DE STATS ===
        cols = []
        for key in stats.keys():
            if key.startswith(('Moyenne', 'Min', 'Max')):
                col = key.split(' ', 1)[1]
                if col not in cols:
                    cols.append(col)
        types = ['Moyenne', 'Min', 'Max', '1% Low']
        data = []
        for t in types:
            row = [t]
            for c in cols:
                if t == '1% Low':
                    v = stats.get('1% Lows', {}).get(c, 'N/A')
                else:
                    v = stats.get(f'{t} {c}', {}).get(t.lower(), 'N/A')
                row.append(f"{v:.1f}" if isinstance(v, (int, float)) and v != 'N/A' else str(v))
            data.append(tuple(row))
        return ("Stat",) + tuple(cols), data

    def generate_export_text(self, stats):
        import json
        def handler(o):
            if isinstance(o, pd.Timedelta):
                t = int(o.total_seconds())
                return f"{t//3600:02d}:{(t%3600)//60:02d}:{t%60:02d}"
            return str(o)
        return json.dumps(stats, indent=4, default=handler, ensure_ascii=False)

    def process_timestamp_column(self, df, col_index=1):
        # Nettoyage : str, strip, normalize spaces
        df.iloc[:, col_index] = df.iloc[:, col_index].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)

        # Conversion to datetime
        df.iloc[:, col_index] = pd.to_datetime(df.iloc[:, col_index], format='%d-%m-%Y %H:%M:%S', errors='coerce')

        # Drop NaT
        df = df[df.iloc[:, col_index].notna()]

        # Extract time as string 'HH:MM:SS'
        df.iloc[:, col_index] = df.iloc[:, col_index].apply(
            lambda x: x.strftime('%H:%M:%S') if isinstance(x, pd.Timestamp) else None)

        # Drop None
        df = df[df.iloc[:, col_index].notna()]

        # Sort ascending on time string
        df = df.sort_values(by=df.columns[col_index], ascending=True).reset_index(drop=True)

        # Calcul durée
        if not df.empty:
            min_time = pd.to_timedelta(df.iloc[:, col_index].min())
            max_time = pd.to_timedelta(df.iloc[:, col_index].max())
            duration = max_time - min_time
        else:
            duration = pd.Timedelta(0)

        return duration

    if __name__ == "__main__":
        import pandas as pd  # Test import
        print( "Test: Pandas imported successfully" )
        # Ajoute un test réel, ex. si tu as une fonction :
        # df = pd.read_excel('chemin/vers/test.xlsx')
        # results = ta_fonction(df)
        # print(results)