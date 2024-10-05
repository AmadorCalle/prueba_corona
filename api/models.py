from django.db import models
from django.contrib.auth.models import User

class ImageRequest(models.Model):
    request_id = models.CharField(max_length=100) # Identificador de la solicitud
    image = models.TextField() # Imagen en formato base64
    model_used = models.CharField(max_length=100) # Modelo utilizado para la clasificación
    created_at = models.DateTimeField(auto_now_add=True) # Fecha de creación de la solicitud
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Dirección IP del solicitante
    processing_time = models.FloatField(null=True, blank=True)  # Tiempo de procesamiento de la imagen
    prediction_result = models.JSONField(null=True, blank=True)  # Resultado de la clasificación
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Usuario autenticado
    status = models.CharField(
        max_length=20, 
        choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')], 
        default='SUCCESS'
    )  # Estado de la solicitud
