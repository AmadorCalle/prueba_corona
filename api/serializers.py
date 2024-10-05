from rest_framework import serializers
from .models import ImageRequest

# Serializador para la solicitud de clasificación
class PredictionSerializer(serializers.Serializer):
    request_id = serializers.CharField(max_length=100)
    image = serializers.CharField()
    modelo = serializers.CharField(max_length=100)

# Serializador para la respuesta de clasificación
class PredictionResponseSerializer(serializers.Serializer):
    request_id = serializers.CharField(max_length=100)
    classification = serializers.ListField()
    message = serializers.CharField(max_length=255)

# Serializador para la solicitud de imagen
class ImageRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageRequest
        fields = ['request_id', 'image', 'model_used']