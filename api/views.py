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
from google.cloud import bigquery  # Cliente de BigQuery
import datetime

# Configuración de la autenticación con Vertex AI
credentials = service_account.Credentials.from_service_account_file('prueba-tecnica-corona-013e0a2a5035.json')

# Inicializar el cliente Vertex AI
aiplatform.init(credentials=credentials)

# Conectar con el endpoint de Vertex AI
endpoint = aiplatform.Endpoint(endpoint_name="projects/prueba-tecnica-corona/locations/southamerica-east1/endpoints/9046034005434040320")

# Inicializar cliente de BigQuery
bigquery_client = bigquery.Client(credentials=credentials)

# Nombre del dataset y tabla en BigQuery
dataset_id = 'predictions_data'  # Dataset existente
table_id = 'inputs'              # Tabla a la que guardaremos los datos

class PredictionView(APIView):

    def get_view_name(self):
        return "API RESTful de clasificación de imágenes"

    def store_data_in_bigquery(self, request_id, model_used, base64_image, ip_address, user):
        """Función para almacenar los datos en BigQuery"""
        table_ref = bigquery_client.dataset(dataset_id).table(table_id)
        table = bigquery_client.get_table(table_ref)
        
        # Obtener el timestamp actual
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        # Preparar los datos para la inserción
        rows_to_insert = [
            {
                "request_id": request_id,
                "modelo": model_used,
                "image": base64_image,  # Almacenar el base64 de la imagen
                "ip_address": ip_address,
                "user": user if user else 'anonymous',
                "timestamp": timestamp
            }
        ]
        
        # Insertar los datos en BigQuery
        errors = bigquery_client.insert_rows_json(table, rows_to_insert)
        if errors:
            print(f"Error al insertar datos en BigQuery: {errors}")
            return Response({'error': f"Error al insertar datos en BigQuery: {errors}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

                # Convertir la imagen a un array de numpy y preprocesarla
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

                # Guardar los datos de entrada en BigQuery
                store_result = self.store_data_in_bigquery(request_id, model_used, base64_image, ip_address, user)
                if isinstance(store_result, Response):
                    return store_result

                # Guardar la solicitud de la imagen en el modelo ImageRequest (opcional)
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
                print(error_message)  # Mostrar el error en la consola

                # Guardar como solicitud fallida en BigQuery
                self.store_data_in_bigquery(request_id, model_used, base64_image, ip_address, user)

                # Guardar como solicitud fallida en ImageRequest (opcional)
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

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
