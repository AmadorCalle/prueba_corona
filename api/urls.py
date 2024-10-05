from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('predict/', views.PredictionView.as_view(), name='predict'), # URL para la vista de clasificación
    path('token-auth/', obtain_auth_token, name='token_auth'), # URL para obtener el token de autenticación
]