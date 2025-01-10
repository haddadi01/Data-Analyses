# urls.py dans votre projet principal (data_visualization/urls.py)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),  # Utiliser 'myapp' au lieu de 'votre_app'
]

# urls.py dans votre application (myapp/urls.py)
from django.urls import path
from . import views

app_name = 'myapp'  # Utiliser 'myapp' comme nom d'application

urlpatterns = [
    path('', views.upload_csv, name='upload_csv'),
    path('generate-plot/', views.generate_plot, name='generate_plot'),
    path('download-plot/', views.download_plot, name='download_plot'),
]