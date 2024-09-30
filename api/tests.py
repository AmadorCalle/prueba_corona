from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
import base64
import io
from PIL import Image
import time


class PredictionViewTests(APITestCase):
    def setUp(self):
        # Crear un usuario para autenticación
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Obtener el token de autenticación
        response = self.client.post('/api/token-auth/', {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.token = response.data['token']

        # Añadir el token a los encabezados para autenticación en las solicitudes
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        
        # Crear una imagen de prueba en memoria con dimensiones correctas (8x8)
        self.image = Image.new('RGB', (8, 8), color='white')
        buffered = io.BytesIO()
        self.image.save(buffered, format="JPEG")
        self.image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # URL correcta para predicción
        self.url = '/api/predict/'

    def test_prediction_invalid_data(self):
        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',  # Incluimos el modelo
            'image': 'invalid_base64_data'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_prediction_authentication_required(self):
        self.client.logout()  # Cierra la sesión actual
        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',  # Incluimos el modelo
            'image': self.image_base64
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_prediction_large_image(self):
        # Crear una imagen más grande (por ejemplo, 32x32 píxeles)
        large_image = Image.new('RGB', (32, 32), color='white')
        buffered = io.BytesIO()
        large_image.save(buffered, format="JPEG")
        large_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',  # Incluimos el modelo
            'image': large_image_base64
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)  # Verificar que devuelve un error sobre las características

    def test_prediction_load(self):
        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',  # Incluimos el modelo
            'image': self.image_base64
        }
        for _ in range(10):  # Simula 10 solicitudes consecutivas
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('prediction', response.data)

    def test_prediction_response_time(self):
        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',  # Incluimos el modelo
            'image': self.image_base64
        }
        start_time = time.time()
        response = self.client.post(self.url, data, format='json')
        end_time = time.time()
        response_time = end_time - start_time
        self.assertLess(response_time, 2)  # Verifica que el tiempo de respuesta sea menor a 2 segundos
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_prediction_success(self):
        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',  # Incluimos el modelo
            'image': self.image_base64
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('prediction', response.data)