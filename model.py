# model.py
import pandas as pd
import numpy as np


class StatsModel:
    def __init__(self):
        pass

    def compute_stats(self, file_path):
        try:
            df = pd.read_excel( file_path, engine='openpyxl' )

            # === TOUS TES TRAITEMENTS EXISTANTS (drops, colonnes, scaling, etc.) ===
            # (je les laisse exactement comme tu les avais, je touche rien)
            df = df.drop( columns=df.columns[[8, 9, 10, 11, 12]] )
            indices_a_supprimer = df[df.iloc[:, 0].isin( [0, 1, 2, 3] )].index
            df = df.drop( indices_a_supprimer )

            df.columns = ['Action type', 'Timestamp', 'GPU temperature', 'GPU usage', 'Core clock ',
                          'Temp over limit', 'CPU usage', 'Framerate']

            columns_to_scale = ['GPU temperature', 'GPU usage', 'Core clock ', 'Temp over limit',
                                'CPU usage', 'Framerate']
            for col in columns_to_scale:
                if col in df.columns:
                    df[col] = pd.to_numeric( df[col], errors='coerce' ) / 1000

            tooHighFramerateIndexes = df[df['Framerate'] >= 1000].index
            df = df.drop( tooHighFramerateIndexes )

            df, duration = self.process_timestamp_column( df, col_index=1 )

            if df.empty:
                return None, "DataFrame vide après nettoyage."

            columns_for_calcs = ['Framerate', 'GPU temperature', 'GPU usage',
                                 'Core clock ', 'Temp over limit', 'CPU usage']

            custom_stats = {}

            # Moyenne / Min / Max
            for col in columns_for_calcs:
                if col in df.columns and pd.api.types.is_numeric_dtype( df[col] ):
                    custom_stats[f'Moyenne {col}'] = {'moyenne': df[col].mean()}
                    custom_stats[f'Min {col}'] = {'min': df[col].min()}
                    custom_stats[f'Max {col}'] = {'max': df[col].max()}
                else:
                    custom_stats[f'Moyenne {col}'] = {'moyenne': 'N/A'}
                    custom_stats[f'Min {col}'] = {'min': 'N/A'}
                    custom_stats[f'Max {col}'] = {'max': 'N/A'}

            custom_stats['Durée Partie'] = {'duration': duration}

            one_percent_lows = self.calculateOnePercentLow( df, columns=columns_for_calcs )
            custom_stats['1% Lows'] = one_percent_lows

            # === NOUVELLE RETOUR (tout ce qu’il faut pour les graphs) ===
            return {
                'stats': custom_stats,
                'df': df.copy(),  # on renvoie une copie propre
                'duration': duration
            }, None

        except Exception as e:
            return None, f"Erreur lors du chargement : {str( e )}"

    def format_stats_for_display(self, stats):
        # Colonnes pour la table
        columns = ['Framerate', 'GPU temperature', 'GPU usage', 'Core clock ', 'Temp over limit', 'CPU usage']

        # Types de stats
        stat_types = ['Moyenne', 'Min', 'Max', '1% Low']

        # Build formatted_data
        formatted_data = []
        for stat in stat_types:
            row = [stat]
            for col in columns:
                if stat == '1% Low':
                    # Extract from the dict '1% Lows'
                    one_low_dict = stats.get('1% Lows', {})
                    val = one_low_dict.get(col, 'N/A')
                else:
                    key = f"{stat} {col}"
                    val = stats.get(key, {}).get(stat.lower(), 'N/A')

                if isinstance(val, float):
                    row.append(f"{val:.1f}")
                else:
                    row.append(str(val))
            formatted_data.append(tuple(row))

        tree_columns = ("Stat",) + tuple(columns)

        return tree_columns, formatted_data

    def generate_export_text(self, stats):
        import json

        # Restructure par colonne
        restructured = {}
        stat_types = ['moyenne', 'min', 'max', '1% low', 'duration']

        for key, s in stats.items():
            if key.startswith(('Moyenne', 'Min', 'Max')):
                parts = key.split(' ', 1)
                stat = parts[0].lower()
                col = parts[1]
                if col not in restructured:
                    restructured[col] = {}
                restructured[col][stat] = s.get(stat, 'N/A')
            elif key == '1% Lows':  # Changé ici
                for sub_col, val in s.items():  # Directement s.items()
                    if sub_col not in restructured:
                        restructured[sub_col] = {}
                    restructured[sub_col]['1% low'] = val
            elif key == 'Durée Partie':
                restructured['Durée Partie'] = s.get('duration', 'N/A')
            else:
                restructured[key] = s

        # Handler pour JSON (Timedelta -> HH:MM:SS, floats -> 1 decimal)
        def default_handler(o):
            if isinstance(o, pd.Timedelta):
                total_seconds = int(o.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            elif isinstance(o, float):
                return round(o, 1)
            return str(o)

        return json.dumps(restructured, indent=4, default=default_handler)

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

        return df, duration

    def calculateOnePercentLow(self, df, columns=None):
        results = {}
        if columns is None:
            columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

        for col_name in columns:
            if col_name in df.columns:
                series = pd.to_numeric(df[col_name], errors='coerce')
                sorted_series = series.sort_values(ascending=True).dropna()
                if len(sorted_series) >= 5:  # Baissé à 5 pour petits datasets
                    one_percent_low = sorted_series.quantile(0.01)
                else:
                    one_percent_low = 'N/A (pas assez de données)'
            else:
                one_percent_low = 'N/A (colonne absente)'
            results[col_name] = one_percent_low

        return results