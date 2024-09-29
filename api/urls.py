from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.PredictionView.as_view(), name='predict'),
]