# CSV Data Analysis Web Application

Une application web Django pour l'analyse et la visualisation de données CSV, offrant une interface intuitive pour explorer et visualiser vos données.

## 🌟 Fonctionnalités

- **Upload de fichiers CSV**
  - Support des fichiers CSV jusqu'à 10MB
  - Validation automatique du format
  - Nettoyage automatique des données

- **Aperçu des données**
  - Affichage tabulaire interactif
  - Nombre de lignes personnalisable
  - Formatage automatique des nombres décimaux

- **Analyse statistique**
  - Statistiques descriptives complètes
  - Analyse par colonne
    - Valeurs minimales/maximales
    - Moyenne, médiane, écart-type
    - Skewness et Kurtosis
  - Matrice de corrélation interactive
  - Détection des valeurs manquantes

- **Visualisation des données**
  - Types de graphiques multiples :
    - Lignes
    - Barres
    - Nuage de points
    - Histogramme
    - Boîte à moustaches
    - Camembert
  - Fonctionnalités interactives :
    - Zoom in/out
    - Réinitialisation du zoom
    - Export en PNG/SVG

## 🛠 Prérequis

- Python 3.8+
- Django 3.2+
- Pandas
- NumPy
- Matplotlib
- Seaborn

## 📥 Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/csv-analysis-app.git
cd csv-analysis-app
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Effectuez les migrations :
```bash
python manage.py migrate
```

5. Lancez le serveur de développement :
```bash
python manage.py runserver
```

L'application sera accessible à l'adresse : http://127.0.0.1:8000

## 📊 Utilisation

1. **Upload de fichier**
   - Cliquez sur "Choisir un fichier CSV"
   - Sélectionnez votre fichier CSV
   - Cliquez sur "Télécharger"

2. **Aperçu des données**
   - Visualisez les premières lignes du fichier
   - Ajustez le nombre de lignes affichées

3. **Analyse des données**
   - Sélectionnez l'analyse par ligne ou par colonne
   - Consultez les statistiques descriptives
   - Explorez la matrice de corrélation

4. **Visualisation**
   - Choisissez le type de graphique
   - Sélectionnez la variable à visualiser
   - Utilisez les contrôles de zoom
   - Exportez les graphiques en PNG ou SVG

## 🔒 Sécurité

- Validation CSRF activée
- Limite de taille de fichier (10MB)
- Validation du format de fichier
- Nettoyage automatique des données

## 🛠 Structure du projet

```
DATA_visualization/
├── data_visualization/        # Répertoire principal du projet Django
│   ├── __pycache__/           # Cache Python pour des optimisations
│   ├── __init__.py            # Indique que ce dossier est un package Python
│   ├── asgi.py                # Configuration ASGI pour le déploiement asynchrone
│   ├── settings.py            # Paramètres globaux du projet (BDD, apps, etc.)
│   ├── urls.py                # Configuration des routes principales
│   └── wsgi.py                # Configuration WSGI pour le déploiement

├── myapp/                     # Application Django principale
│   ├── __pycache__/           # Cache Python
│   ├── migrations/            # Gestion des migrations de la base de données
│   ├── templates/             # Templates HTML pour l'affichage
│   │   └── upload_csv.html    # Interface pour uploader un fichier CSV
│   ├── __init__.py            # Package Python
│   ├── admin.py               # Configuration de l'admin Django
│   ├── apps.py                # Configuration de l'application
│   ├── models.py              # Modèles de la base de données
│   ├── tests.py               # Tests unitaires
│   ├── urls.py                # Routes spécifiques à l'application
│   ├── utils.py               # Fonctions utilitaires (traitement de données)
│   └── views.py               # Vues logiques de l'application

├── static/                    # Fichiers statiques (CSS, JS, images)
│   ├── css/
│   │   └── style.css          # Feuille de style pour le frontend
│   └── js/
│       ├── chart-config.js    # Configuration des graphiques
        ├── chart-utils.js    # Fonctions utilitaires pour les graphiques
        └── script.js         # les autres scripts js 
```



## 📝 License

Distribué sous la licence Hassan Haddadi pour plus d'informations hassanhaddadi@gmail.com .
