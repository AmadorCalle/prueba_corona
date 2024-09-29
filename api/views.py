from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PredictionSerializer
from .ml_model.model_loader import load_model
from django.contrib.auth import logout
from django.http import JsonResponse
import base64
import io
import numpy as np
from PIL import Image

# Cargar el modelo entrenado una vez usando la función load_model
model = load_model("clf.pickle")

class PredictionView(APIView):
    def post(self, request):
        serializer = PredictionSerializer(data=request.data)
        if serializer.is_valid():
            # Decodificar la imagen en base64
            image_data = base64.b64decode(serializer.validated_data['image'])
            image = Image.open(io.BytesIO(image_data))
            
            # Convertir la imagen a un array de numpy y preprocesarla
            number = np.round((np.array(image) / 255) * 16)
            
            # Realizar la predicción
            prediction = model.predict(number.reshape(1, -1))
            
            return Response({
                'request_id': serializer.validated_data['request_id'],
                'prediction': prediction.tolist()  # Convertir la predicción a lista para que sea serializable
            }, status=status.HTTP_200_OK)
        
        # Si los datos no son válidos, devolver errores de validación
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)