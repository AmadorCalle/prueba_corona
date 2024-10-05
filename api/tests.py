from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
import base64
import io
from PIL import Image
from .models import ImageRequest
import numpy as np

class PredictionTestCase(APITestCase):

    def setUp(self):
        # Crear un usuario de prueba y obtener el token de autenticación
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)  # Establecer el token en el encabezado

        # Crear una imagen de prueba
        image = Image.new('L', (8, 8))  # Crear una imagen en escala de grises de 8x8
        buffer = io.BytesIO()  # Crear un buffer en memoria
        image.save(buffer, format="JPEG")  # Guardar la imagen en el buffer en formato JPEG
        self.image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')  # Codificar la imagen en base64

        # Decodificar la imagen base64
        image_data = base64.b64decode(self.image_base64)
        image = Image.open(io.BytesIO(image_data))  # Abrir la imagen desde el buffer

        # Convertir la imagen a un array de numpy y preprocesarla
        self.number = np.round((np.array(image) / 255) * 16)  # Normalizar y escalar la imagen

    def test_prediction(self):
        """
        Prueba que una predicción sea realizada correctamente y que la imagen
        y demás información se almacenen en la base de datos.
        """
        url = reverse('predict')  # Ruta para la predicción
        data = {
            'request_id': 'uuid',
            'image': self.image_base64,
            'modelo': 'clf.pickle'
        }

        response = self.client.post(url, data, format='json')  # Enviar la solicitud POST

        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('classification', response.data)
        self.assertIn('message', response.data)

        # Verificar que la imagen y la solicitud se almacenaron en la base de datos
        image_request = ImageRequest.objects.get(request_id='uuid')
        self.assertEqual(image_request.model_used, 'clf.pickle')
        self.assertIsNotNone(image_request.image)
        self.assertEqual(image_request.status, 'SUCCESS')

    def test_prediction_with_invalid_image_size(self):
        """
        Prueba que una imagen con tamaño incorrecto sea rechazada.
        """
        # Crear una imagen de tamaño incorrecto (10x10 en lugar de 8x8)
        image = Image.new('L', (10, 10), color=128)
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        url = reverse('predict')
        data = {
            'request_id': 'test_invalid_size',
            'image': image_base64,
            'modelo': 'test_model'
        }

        response = self.client.post(url, data, format='json')

        # Verificar que la respuesta sea un error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_prediction_without_image(self):
        """
        Prueba que una solicitud sin imagen sea rechazada.
        """
        url = reverse('predict')
        data = {
            'request_id': 'test_no_image',
            'image': '',
            'modelo': 'test_model'
        }

        response = self.client.post(url, data, format='json')

        # Verificar que el error está en el campo 'image'
        self.assertIn('image', response.data)
        self.assertEqual(response.data['image'][0].code, 'blank')

    def test_prediction_with_invalid_model(self):
        """
        Prueba que un modelo no válido sea rechazado.
        """
        url = reverse('predict')
        data = {
            'request_id': 'test_invalid_model',
            'image': self.image_base64,
            'modelo': 'invalid_model'
        }

        response = self.client.post(url, data, format='json')

        # Verificar que la respuesta sea un error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_prediction_without_authentication(self):
        """
        Prueba que un usuario no autenticado no pueda hacer predicciones.
        """
        self.client.credentials()  # Eliminar las credenciales para simular un usuario no autenticado

        url = reverse('predict')
        data = {
            'request_id': 'test_no_auth',
            'image': self.image_base64,
            'modelo': 'test_model'
        }

        response = self.client.post(url, data, format='json')

        # Verificar que la respuesta sea un error 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)