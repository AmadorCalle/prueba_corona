from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PredictionSerializer, ImageRequestSerializer
from .models import ImageRequest
import base64
import io
from PIL import Image
import numpy as np
from .ml_model.model_loader import load_model
import uuid

# Cargar el modelo de ML
model = load_model("clf.pickle")

class PredictionView(APIView):
    def post(self, request):
        print("Datos recibidos:", request.data)  # Confirmar datos recibidos
        
        # Validar los datos con el PredictionSerializer
        serializer = PredictionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                print("Datos validados:", serializer.validated_data)  # Confirmar datos validados
                
                # Obtener la cadena base64 sin decodificar
                base64_image = serializer.validated_data['image']

                # Preparar los datos para el serializador de ImageRequest
                image_request_data = {
                    'request_id': serializer.validated_data['request_id'],
                    'image': base64_image,
                    'model_used': serializer.validated_data['modelo']
                }

                # Usar el ImageRequestSerializer para guardar el registro en la base de datos
                image_request_serializer = ImageRequestSerializer(data=image_request_data)
                
                if image_request_serializer.is_valid():
                    saved_image_request = image_request_serializer.save()
                    print(f"Registro guardado: {saved_image_request}")

                else:
                    print(f"Errores al intentar guardar: {image_request_serializer.errors}")
                    return Response(image_request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # Decodificar la imagen base64 para hacer predicciones
                try:
                    image_data = base64.b64decode(base64_image)
                except Exception as decode_error:
                    print(f"Error al decodificar la imagen base64: {str(decode_error)}")
                    return Response({
                        'error': f'Error al decodificar la imagen: {str(decode_error)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                image = Image.open(io.BytesIO(image_data))

                # Convertir la imagen a un array de numpy y preprocesarla
                number = np.round((np.array(image) / 255) * 16)

                if number.size != 64:
                    print(f"Error: la imagen tiene {number.size} características, se esperaban 64.")
                    return Response({
                        'error': 'La imagen debe tener exactamente 64 características (8x8 píxeles).'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Realizar la predicción
                prediction = model.predict(number.reshape(1, -1))
                print(f"Predicción realizada: {prediction}")

                return Response({
                    'request_id': serializer.validated_data['request_id'],
                    'prediction': prediction.tolist(),
                    'message': 'Datos guardados correctamente.'
                }, status=status.HTTP_200_OK)

            except Exception as e:
                print(f"Error al procesar la solicitud: {str(e)}")  # Mostrar cualquier excepción
                return Response({
                    'error': f'Error al procesar la imagen: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)

        
        print(f"Errores de validación: {serializer.errors}")  # Mostrar errores de validación en el serializador
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
