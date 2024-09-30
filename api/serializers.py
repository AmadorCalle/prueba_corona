from rest_framework import serializers
from .models import ImageRequest

class PredictionSerializer(serializers.Serializer):
    request_id = serializers.CharField(max_length=100)
    image = serializers.CharField()  # Asumiendo que la imagen se envía como una cadena base64
    modelo = serializers.CharField(max_length=100)

class ImageRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageRequest
        fields = ['request_id', 'image', 'model_used']
