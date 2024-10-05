from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

# Rutas de la API
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', RedirectView.as_view(url='/api/predict/', permanent=False)),
]
