from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PredictionSerializer, ImageRequestSerializer, PredictionResponseSerializer
from .models import ImageRequest
import base64
import io
from PIL import Image
import numpy as np
from .ml_model.model_loader import load_model
import time  # Para medir el tiempo de procesamiento

# Cargar el modelo de ML
model = load_model("clf.pickle")

class PredictionView(APIView):

    def get_view_name(self):
        return "API RESTful de clasificación de imágenes"

    def post(self, request):
        print("Datos recibidos:", request.data)  # Confirmar datos recibidos
        
        # Validar los datos con el PredictionSerializer
        serializer = PredictionSerializer(data=request.data)
        
        if serializer.is_valid():
            request_id = serializer.validated_data['request_id']
            base64_image = serializer.validated_data['image']
            model_used = serializer.validated_data['modelo']

            # Validar el modelo usado
            valid_models = ['clf.pickle']  # Agrega los modelos válidos que tengas
            if model_used not in valid_models:
                return Response({
                    'error': 'El modelo proporcionado no es válido.'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                start_time = time.time()  # Iniciar el temporizador de procesamiento
                image_data = base64.b64decode(base64_image)  # Decodificar la imagen base64
                image = Image.open(io.BytesIO(image_data))  # Crear un objeto de imagen PIL

                # Convertir la imagen a un array de numpy y preprocesarla
                number = np.round((np.array(image) / 255) * 16)

                if number.size != 64:  # Verificar si la imagen tiene las características correctas
                    return Response({
                        'error': 'La imagen debe tener exactamente 64 características (8x8 píxeles).'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Realizar la clasificación
                classification = model.predict(number.reshape(1, -1))
                print(f"Clasificación realizada: {classification}")

                end_time = time.time()  # Terminar el temporizador de procesamiento
                processing_time = end_time - start_time

                # Obtener la dirección IP del solicitante
                ip_address = request.META.get('REMOTE_ADDR', None)

                # Obtener el usuario autenticado, si lo hay
                user = request.user if request.user.is_authenticated else None

                # Guardar la solicitud de la imagen en el modelo ImageRequest. No es necesario serializar porque solo se serializan las respuestas/solicitudes al cliente, aquí solo guardamos en la base de datos
                ImageRequest.objects.create(
                    request_id=request_id,
                    image=base64_image,  # Almacenar la imagen en formato base64
                    model_used=model_used,
                    processing_time=processing_time,
                    prediction_result=classification.tolist(),  # Guardar la clasificación como JSON
                    ip_address=ip_address,
                    user=user,
                    status='SUCCESS'  # Suponemos que la solicitud fue exitosa
                )

                # Serializar la respuesta con PredictionResponseSerializer
                response_serializer = PredictionResponseSerializer(data={
                    'request_id': request_id,
                    'classification': classification.tolist(),  # Convertir a lista si es necesario
                    'message': 'Clasificación realizada con éxito.'
                })

                if response_serializer.is_valid():
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(response_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                error_message = f'Error al procesar la imagen: {str(e)}'
    
                # Guardar como solicitud fallida
                ImageRequest.objects.create(
                    request_id=request_id,
                    image=base64_image,
                    model_used=model_used,
                    ip_address=request.META.get('REMOTE_ADDR', None),
                    user=request.user if request.user.is_authenticated else None,
                    status='FAILED'  # Marca la solicitud como fallida
                )
                
                # Serializar el error y enviarlo en la respuesta
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
