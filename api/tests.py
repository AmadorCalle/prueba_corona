from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
import base64
import io
from PIL import Image
import time
from api.models import ImageRequest  # Importar el modelo para verificar la base de datos

class PredictionViewTests(APITestCase):
    def setUp(self):
        # Crear un usuario para autenticación
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Obtener el token de autenticación
        response = self.client.post('/api/token-auth/', {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertIn('token', response.data)  # Verificar que se obtiene el token
        self.token = response.data['token']

        # Añadir el token a los encabezados para autenticación en las solicitudes
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        
        # Crear una imagen de prueba en memoria con dimensiones correctas (8x8)
        self.image = Image.new('L', (8, 8), color='white')
        buffered = io.BytesIO()
        self.image.save(buffered, format="JPEG")
        self.image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        
        self.url = '/api/predict/'

    def test_prediction_invalid_data(self):
        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',
            'image': 'invalid_base64_data'
        }
        response = self.client.post(self.url, data, format='json')
        print(f"Respuesta (Invalid Data): {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_prediction_authentication_required(self):
        self.client.logout()
        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',
            'image': self.image_base64
        }
        response = self.client.post(self.url, data, format='json')
        print(f"Respuesta (Authentication Required): {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_prediction_large_image(self):
        
        large_image = Image.new('L', (32, 32), color='white')
        buffered = io.BytesIO()
        large_image.save(buffered, format="JPEG")
        large_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',
            'image': large_image_base64
        }
        response = self.client.post(self.url, data, format='json')
        print(f"Respuesta (Large Image): {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_prediction_load(self):
        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',
            'image': self.image_base64
        }
        for _ in range(10):
            response = self.client.post(self.url, data, format='json')
            print(f"Respuesta (Load Test): {response.data}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('prediction', response.data)

    def test_prediction_response_time(self):
        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',
            'image': self.image_base64
        }
        start_time = time.time()
        response = self.client.post(self.url, data, format='json')
        end_time = time.time()
        response_time = end_time - start_time
        print(f"Tiempo de respuesta: {response_time}s")
        self.assertLess(response_time, 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_prediction_success(self):
        data = {
            'request_id': '12345',
            'modelo': 'clf.pickle',
            'image': self.image_base64
        }
        response = self.client.post(self.url, data, format='json')
        print(f"Respuesta (Success): {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('prediction', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Datos guardados correctamente.')

        
        image_request = ImageRequest.objects.filter(request_id='12345').first()
        self.assertIsNotNone(image_request)
        self.assertEqual(image_request.request_id, '12345')
        self.assertEqual(image_request.model_used, 'clf.pickle')
        self.assertEqual(image_request.image, self.image_base64)
