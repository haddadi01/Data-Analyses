"""utils.py """
import pandas as pd
import numpy as np
from django.core.files.storage import FileSystemStorage
from io import StringIO, BytesIO
import json
import seaborn as sns
import matplotlib.pyplot as plt
import base64

class CSVHandler:
    @staticmethod
    def process_uploaded_file(file):
        fs = FileSystemStorage()
        file_path = fs.save(file.name, file)
        return fs.path(file_path)
    
    @staticmethod
    def read_csv_file(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier CSV : {str(e)}")
    
    @staticmethod
    def clean_data(df):
        df = df.copy()
        df = df.drop_duplicates()
        
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            mean_value = df[col].mean()
            df[col] = df[col].fillna(mean_value)
        
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            df[col] = df[col].fillna('Non spécifié')
        
        return df
    
    @staticmethod
    def get_preview(df, num_rows=10):
        try:
            preview_df = df.head(num_rows)
            return preview_df.to_html(
                classes=['table', 'table-striped', 'table-hover', 'table-responsive'],
                index=False,
                float_format=lambda x: '{:.2f}'.format(x) if isinstance(x, float) else x
            )
        except Exception as e:
            raise ValueError(f"Erreur lors de la génération de l'aperçu : {str(e)}")

# utils.py
import pandas as pd
import numpy as np

class DataAnalyzer:
    @staticmethod
    def get_statistics(df):
        try:
            numeric_df = df.select_dtypes(include=['int64', 'float64'])
            if numeric_df.empty:
                return {"error": "Aucune colonne numérique trouvée"}
            
            # Création du DataFrame de statistiques de base
            stats = numeric_df.describe()
            
            # Calcul des statistiques supplémentaires pour toutes les colonnes d'un coup
            stats.loc['skewness'] = numeric_df.skew()
            stats.loc['kurtosis'] = numeric_df.kurtosis()
            stats.loc['missing_values'] = numeric_df.isnull().sum()
            stats.loc['unique_values'] = numeric_df.nunique()
            
            # Conversion en HTML avec les classes CSS appropriées
            html = '<div class="modern-table"><table>'
            
            # En-tête
            html += '<tr><th>Statistique</th>'
            for col in stats.columns:
                html += f'<th>{col}</th>'
            html += '</tr>'
            
            # Lignes de données
            for idx in stats.index:
                html += f'<tr><td>{idx}</td>'
                for col in stats.columns:
                    value = stats.loc[idx, col]
                    if isinstance(value, (int, np.integer)):
                        formatted_value = f'{value:,}'
                    else:
                        formatted_value = f'{value:.2f}'
                    html += f'<td>{formatted_value}</td>'
                html += '</tr>'
            
            html += '</table></div>'
            
            return html
            
        except Exception as e:
            raise ValueError(f"Erreur lors du calcul des statistiques : {str(e)}")

    @staticmethod
    def get_column_statistics(df, column_name):
        try:
            if column_name not in df.columns:
                raise ValueError(f"Colonne '{column_name}' non trouvée")
            
            series = df[column_name]
            
            if not pd.api.types.is_numeric_dtype(series):
                raise ValueError("La colonne doit être numérique")
            
            stats = {
                'count': len(series),
                'missing': series.isnull().sum(),
                'unique': series.nunique(),
                'min': series.min(),
                'max': series.max(),
                'mean': series.mean(),
                'median': series.median(),
                'std': series.std(),
                'skew': series.skew(),
                'kurtosis': series.kurtosis(),
                'quartiles': {
                    'Q1': series.quantile(0.25),
                    'Q2': series.quantile(0.50),
                    'Q3': series.quantile(0.75)
                }
            }
            
            # Format all numeric values to 2 decimal places
            for key, value in stats.items():
                if isinstance(value, (float, np.floating)):
                    stats[key] = round(value, 2)
                elif isinstance(value, dict):
                    stats[key] = {k: round(v, 2) for k, v in value.items()}
            
            return stats
            
        except Exception as e:
            raise ValueError(f"Erreur lors du calcul des statistiques de colonne : {str(e)}")

    @staticmethod
    def get_row_data(df, row_index):
        try:
            if not 0 <= row_index < len(df):
                raise ValueError("Index de ligne invalide")
            
            row = df.iloc[row_index]
            return row.to_dict()
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la récupération des données de ligne : {str(e)}")

    @staticmethod
    def get_column_data(df, column_name):
        try:
            if column_name not in df.columns:
                raise ValueError(f"Colonne '{column_name}' non trouvée")
            
            column = df[column_name]
            
            if pd.api.types.is_numeric_dtype(column):
                return {
                    'type': 'numeric',
                    'data': column.tolist(),
                    'stats': DataAnalyzer.get_column_statistics(df, column_name)
                }
            else:
                value_counts = column.value_counts()
                return {
                    'type': 'categorical',
                    'data': column.tolist(),
                    'distribution': value_counts.to_dict(),
                    'unique_count': len(value_counts)
                }
                
        except Exception as e:
            raise ValueError(f"Erreur lors de la récupération des données de colonne : {str(e)}")

    @staticmethod
    def get_correlation_matrix(df):
        try:
            numeric_df = df.select_dtypes(include=['int64', 'float64'])
            if numeric_df.empty:
                return None
            
            corr_matrix = numeric_df.corr()
            
            # Conversion en HTML
            html = '<div class="correlation-matrix"><table>'
            
            # En-tête
            html += '<tr><th></th>'
            for col in corr_matrix.columns:
                html += f'<th>{col}</th>'
            html += '</tr>'
            
            # Données
            for idx in corr_matrix.index:
                html += f'<tr><td>{idx}</td>'
                for col in corr_matrix.columns:
                    value = corr_matrix.loc[idx, col]
                    # Ajouter une classe CSS basée sur la valeur de corrélation
                    css_class = 'correlation-'
                    if abs(value) > 0.7:
                        css_class += 'high'
                    elif abs(value) > 0.4:
                        css_class += 'medium'
                    else:
                        css_class += 'low'
                    html += f'<td class="{css_class}">{value:.2f}</td>'
                html += '</tr>'
            
            html += '</table></div>'
            
            return html
            
        except Exception as e:
            raise ValueError(f"Erreur lors du calcul de la matrice de corrélation : {str(e)}")
class DataVisualizer:
    @staticmethod
    def prepare_plot_data(df, variable, plot_type):
        """Prépare les données pour le graphique"""
        try:
            if variable not in df.columns:
                raise ValueError(f"Variable {variable} non trouvée dans les données")
            
            data = df[variable].dropna()
            
            if plot_type == 'pie':
                value_counts = data.value_counts()
                return {
                    'labels': value_counts.index.tolist(),
                    'values': value_counts.values.tolist()
                }
            elif plot_type in ['line', 'scatter', 'bar']:
                return {
                    'labels': list(range(len(data))),
                    'values': data.tolist()
                }
            elif plot_type == 'histogram':
                return {
                    'labels': None,  # Sera généré plus tard
                    'values': data.tolist()
                }
            elif plot_type == 'box':
                return {
                    'labels': [variable],
                    'values': data.tolist()
                }
            else:
                raise ValueError(f"Type de graphique non supporté: {plot_type}")
        except Exception as e:
            raise ValueError(f"Erreur lors de la préparation des données: {str(e)}")

    @staticmethod
    def generate_plot(df, plot_type, variable, options=None):
        """Génère les données pour le graphique dans un format compatible avec Chart.js"""
        try:
            options = options or {}
            data = DataVisualizer.prepare_plot_data(df, variable, plot_type)
            
            chart_data = {
                'type': plot_type,
                'data': {
                    'datasets': [{
                        'label': variable,
                        'data': []
                    }]
                }
            }
            
            if plot_type == 'pie':
                chart_data['data']['labels'] = data['labels']
                chart_data['data']['datasets'][0]['data'] = data['values']
                chart_data['data']['datasets'][0]['backgroundColor'] = [
                    f'hsl({(i * 360) / len(data["labels"])}, 70%, 50%)'
                    for i in range(len(data['labels']))
                ]
            
            elif plot_type == 'histogram':
                hist, bins = np.histogram(data['values'], bins=options.get('bins', 30))
                chart_data['data']['labels'] = [f"{bins[i]:.2f}-{bins[i+1]:.2f}" for i in range(len(bins)-1)]
                chart_data['data']['datasets'][0]['data'] = hist.tolist()
            
            elif plot_type == 'box':
                values = np.array(data['values'])
                stats = {
                    'q1': float(np.percentile(values, 25)),
                    'median': float(np.median(values)),
                    'q3': float(np.percentile(values, 75)),
                    'whiskers': [
                        float(np.min(values)),
                        float(np.max(values))
                    ]
                }
                chart_data['data']['labels'] = data['labels']
                chart_data['data']['datasets'][0]['stats'] = stats
            
            else:  # line, scatter, bar
                chart_data['data']['labels'] = data['labels']
                chart_data['data']['datasets'][0]['data'] = data['values']
                chart_data['data']['datasets'][0]['backgroundColor'] = 'rgba(74, 144, 226, 0.5)'
                chart_data['data']['datasets'][0]['borderColor'] = 'rgba(74, 144, 226, 1)'
                chart_data['data']['datasets'][0]['borderWidth'] = 1
            
            return chart_data
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la génération du graphique: {str(e)}")