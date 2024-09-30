from django.db import models

class ImageRequest(models.Model):
    request_id = models.CharField(max_length=100)
    image = models.TextField()  # Cambia de ImageField a TextField para almacenar la cadena base64
    model_used = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
