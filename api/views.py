from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PredictionSerializer, PredictionResponseSerializer
from .models import ImageRequest
import base64
import io
from PIL import Image
import numpy as np
import time  # Para medir el tiempo de procesamiento
from google.cloud import aiplatform
from google.oauth2 import service_account

# Configuración de la autenticación con Vertex AI
credentials = service_account.Credentials.from_service_account_file('service_account.json')

# Inicializar el cliente Vertex AI
aiplatform.init(credentials=credentials)

# Conectar con el endpoint de Vertex AI
endpoint = aiplatform.Endpoint(endpoint_name="projects/prueba-tecnica-corona/locations/southamerica-east1/endpoints/9046034005434040320")

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

            try:
                start_time = time.time()  # Iniciar el temporizador de procesamiento

                # Decodificar la imagen base64
                image_data = base64.b64decode(base64_image)  
                image = Image.open(io.BytesIO(image_data))  # Crear un objeto de imagen PIL

                # Convertir la imagen a un array de numpy y preprocesarla (esto depende del tamaño esperado por el modelo)
                image_array = np.array(image)

                # Enviar el array de la imagen preprocesado a Vertex AI
                response = endpoint.predict(instances=[image_array.tolist()])
                classification = response.predictions[0]

                print(f"Clasificación realizada: {classification}")

                end_time = time.time()  # Terminar el temporizador de procesamiento
                processing_time = end_time - start_time

                # Obtener la dirección IP del solicitante
                ip_address = request.META.get('REMOTE_ADDR', None)

                # Obtener el usuario autenticado, si lo hay
                user = request.user if request.user.is_authenticated else None

                # Guardar la solicitud de la imagen en el modelo ImageRequest
                ImageRequest.objects.create(
                    request_id=request_id,
                    image=base64_image,
                    model_used=model_used,
                    processing_time=processing_time,
                    prediction_result=classification,
                    ip_address=ip_address,
                    user=user,
                    status='SUCCESS'
                )

                # Serializar la respuesta con PredictionResponseSerializer
                response_serializer = PredictionResponseSerializer(data={
                    'request_id': request_id,
                    'classification': classification,
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
                    status='FAILED'
                )

                # Serializar el error y enviarlo en la respuesta
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)