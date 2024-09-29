from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('predict/', views.PredictionView.as_view(), name='predict'),
    path('token-auth/', obtain_auth_token, name='token_auth'),
]