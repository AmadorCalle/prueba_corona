from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import service_account
from google.cloud import bigquery
import time
import logging  # Para agregar logs adicionales

# Configuración de la autenticación con Google Cloud
credentials = service_account.Credentials.from_service_account_file('prueba-tecnica-corona-013e0a2a5035.json')

# Inicializar cliente de BigQuery
bigquery_client = bigquery.Client(credentials=credentials)

# Nombre del dataset y tabla en BigQuery
dataset_id = 'predictions_data'  # Dataset existente
table_id = 'inputs'              # Tabla a la que guardaremos los datos

# Configurar logging
logging.basicConfig(level=logging.INFO)

class PredictionView(APIView):

    def get_view_name(self):
        return "API RESTful para almacenar predicciones en BigQuery"

    def store_data_in_bigquery(self, instances):
        """Función para almacenar los datos de las instancias en BigQuery"""
        logging.info(f"Insertando datos en BigQuery: {instances}")
        table_ref = bigquery_client.dataset(dataset_id).table(table_id)
        table = bigquery_client.get_table(table_ref)

        # Preparar los datos para la inserción
        rows_to_insert = [
            {
                "image": "Hola"  # Almacenar las instancias en formato de cadena (JSON)
            }
        ]
        
        # Insertar los datos en BigQuery
        logging.info(f"Datos a insertar: {rows_to_insert}")
        errors = bigquery_client.insert_rows_json(table, rows_to_insert)
        if errors:
            logging.error(f"Error al insertar datos en BigQuery: {errors}")
            return False
        logging.info(f"Datos insertados correctamente en BigQuery.")
        return True

    def post(self, request):
        logging.info("Datos recibidos en la solicitud")
        print("Datos recibidos:", request.data)

        try:
            # Extraer las instancias del cuerpo de la solicitud
            instances = request.data.get("instances", None)

            if instances:
                # Almacenar las instancias en BigQuery
                store_success = self.store_data_in_bigquery(instances)
                if store_success:
                    return Response({"message": "Datos almacenados correctamente en BigQuery."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Error al almacenar datos en BigQuery."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                logging.error("No se proporcionaron instancias en la solicitud.")
                return Response({"error": "No se proporcionaron instancias en la solicitud."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            error_message = f'Error al procesar la solicitud: {str(e)}'
            logging.error(error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
