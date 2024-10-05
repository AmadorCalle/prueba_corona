from django.apps import AppConfig

# Define una configuración de aplicación llamada ApiConfig
class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Establece el campo auto incrementable predeterminado
    name = 'api'  # Nombre de la aplicación