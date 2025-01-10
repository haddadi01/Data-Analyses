'''views.py'''
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import traceback
from io import StringIO, BytesIO
import pandas as pd
import base64
from .utils import CSVHandler, DataAnalyzer, DataVisualizer
from django.http import JsonResponse, HttpResponse
import base64
import matplotlib.pyplot as plt
import seaborn as sns


def upload_csv(request):
    context = {
        'data_html': None,
        'row_data': None,
        'column_data': None,
        'stats_data': None,
        'columns': [],
        'numeric_columns': [],
        'categorical_columns': [],
        'selected_variable': None,
        'visualization_options': {
            'scatter': 'Nuage de points',
            'line': 'Ligne',
            'bar': 'Barres',
            'histogram': 'Histogramme',
            'box': 'Boîte à moustaches',
            'pie': 'Secteurs'
        }
    }
    
    try:
        if 'data_csv' in request.session:
            data_df = pd.read_csv(StringIO(request.session['data_csv']))
            context.update({
                'data_html': CSVHandler.get_preview(data_df),
                'columns': data_df.columns.tolist(),
                'numeric_columns': data_df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
                'categorical_columns': data_df.select_dtypes(include=['object']).columns.tolist()
            })
    except Exception as e:
        messages.error(request, f"Erreur lors de la lecture des données: {str(e)}")
        if 'data_csv' in request.session:
            del request.session['data_csv']
    
    if request.method == "POST":
        if request.FILES.get('csv_file'):
            try:
                csv_file = request.FILES['csv_file']
                
                if not csv_file.name.lower().endswith('.csv'):
                    raise ValueError("Le fichier doit être au format CSV")
                
                if csv_file.size > 10 * 1024 * 1024:
                    raise ValueError("Le fichier est trop volumineux (limite: 10MB)")
                
                file_path = CSVHandler.process_uploaded_file(csv_file)
                data_df = CSVHandler.read_csv_file(file_path)
                data_df = CSVHandler.clean_data(data_df)
                
                if data_df.empty:
                    raise ValueError("Le fichier CSV ne contient pas de données valides")
                
                request.session['data_csv'] = data_df.to_csv(index=False)
                context.update({
                    'data_html': CSVHandler.get_preview(data_df),
                    'columns': data_df.columns.tolist(),
                    'numeric_columns': data_df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
                    'categorical_columns': data_df.select_dtypes(include=['object']).columns.tolist()
                })
                messages.success(request, "Fichier CSV chargé avec succès!")
            except Exception as e:
                messages.error(request, f"Erreur lors du chargement du fichier: {str(e)}")
        
        elif 'data_csv' in request.session:
            try:
                data_df = pd.read_csv(StringIO(request.session['data_csv']))
                
                if row_index := request.POST.get('row_index'):
                    try:
                        row_index = int(row_index)
                        if 0 <= row_index < len(data_df):
                            context['row_data'] = DataAnalyzer.get_row_data(data_df, row_index)
                        else:
                            messages.error(request, "Index de ligne invalide")
                    except ValueError:
                        messages.error(request, "Index de ligne invalide")
                
                if column_name := request.POST.get('column_name'):
                    if column_name in data_df.columns:
                        context['selected_variable'] = column_name
                        column_data = DataAnalyzer.get_column_data(data_df, column_name)
                        context['column_data'] = column_data
                        
                        if pd.api.types.is_numeric_dtype(data_df[column_name]):
                            context['column_stats'] = DataAnalyzer.get_column_statistics(data_df, column_name)
                            context['visualization_type'] = 'numeric'
                        else:
                            context['visualization_type'] = 'categorical'
                    else:
                        messages.error(request, "Colonne non trouvée")
                
                if num_rows := request.POST.get('num_rows'):
                    try:
                        num_rows = int(num_rows)
                        if num_rows > 0:
                            context['data_html'] = CSVHandler.get_preview(data_df, num_rows)
                        else:
                            messages.error(request, "Le nombre de lignes doit être positif")
                    except ValueError:
                        messages.error(request, "Nombre de lignes invalide")
                
                if request.POST.get('show_stats'):
                    stats_data = DataAnalyzer.get_statistics(data_df)
                    correlation_matrix = DataAnalyzer.get_correlation_matrix(data_df)
                    context.update({
                        'stats_data': stats_data,
                        'correlation_matrix': correlation_matrix
                    })
                
            except Exception as e:
                messages.error(request, f"Erreur lors de l'analyse des données: {str(e)}")
    
    return render(request, 'upload_csv.html', context)
@csrf_exempt
def generate_plot(request):
    if request.method == 'POST':
        try:
            if 'data_csv' not in request.session:
                return JsonResponse({'error': 'Aucune donnée disponible'}, status=400)

            data = json.loads(request.body)
            plot_type = data.get('plot_type')
            variable = data.get('variable')
            additional_params = data.get('params', {})

            if not plot_type or not variable:
                return JsonResponse({
                    'error': 'Type de graphique et variable requis'
                }, status=400)

            data_df = pd.read_csv(StringIO(request.session['data_csv']))
            
            if variable not in data_df.columns:
                return JsonResponse({
                    'error': f'Variable non trouvée: {variable}'
                }, status=400)

            # Génération du graphique
            chart_data = DataVisualizer.generate_plot(
                data_df, 
                plot_type, 
                variable, 
                additional_params
            )
            
            return JsonResponse(chart_data)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Format JSON invalide'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'error': 'Méthode non autorisée'
    }, status=405)

def download_plot(request):
    """Fonction pour télécharger le graphique en différents formats"""
    if request.method == 'POST':
        try:
            if 'data_csv' not in request.session:
                return JsonResponse({'error': 'Aucune donnée disponible'}, status=400)

            data = json.loads(request.body)
            plot_data = data.get('plot_data')
            format_type = data.get('format', 'png').lower()

            if not plot_data:
                return JsonResponse({'error': 'Données du graphique manquantes'}, status=400)

            if format_type not in ['png', 'svg']:
                return JsonResponse({
                    'error': 'Format non supporté. Formats acceptés: png, svg'
                }, status=400)

            # Créer une figure matplotlib
            plt.figure(figsize=(10, 6))
            
            # Créer le graphique selon le type
            if plot_data.get('type') == 'bar':
                plt.bar(plot_data['labels'], plot_data['datasets'][0]['data'])
            elif plot_data.get('type') == 'line':
                plt.plot(plot_data['labels'], plot_data['datasets'][0]['data'])
            elif plot_data.get('type') == 'scatter':
                plt.scatter(plot_data['labels'], plot_data['datasets'][0]['data'])
            elif plot_data.get('type') == 'pie':
                plt.pie(plot_data['datasets'][0]['data'], labels=plot_data['labels'])
            
            plt.title(plot_data.get('datasets', [{}])[0].get('label', ''))
            
            # Sauvegarder dans un buffer
            buffer = BytesIO()
            plt.savefig(buffer, format=format_type, bbox_inches='tight')
            plt.close()
            
            # Préparer la réponse
            response = HttpResponse(
                buffer.getvalue(),
                content_type=f'image/{format_type}'
            )
            response['Content-Disposition'] = f'attachment; filename="plot.{format_type}"'
            
            return response

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)