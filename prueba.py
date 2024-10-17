import os
import requests
import json
import base64
import numpy as np
from PIL import Image
import io
import subprocess

# Ruta completa al ejecutable de gcloud
GCLOUD_PATH = r"C:\Users\htoca\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

# Obtener el Access Token de Google Cloud usando gcloud
def get_access_token():
    result = subprocess.run([GCLOUD_PATH, 'auth', 'print-access-token'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Error al obtener el access token: {result.stderr}")
    return result.stdout.strip()

# URL del endpoint en Vertex AI
url = "https://southamerica-east1-aiplatform.googleapis.com/v1/projects/prueba-tecnica-corona/locations/southamerica-east1/endpoints/9046034005434040320:predict"

# La imagen en formato base64
base64_image = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAAIAAgBAREA/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oACAEBAAA/AOAW9sYPgoun6hqF2Li61BrixtVtkKL5Y2s27IOGMmMnPKYA45//2Q=="

# Decodificar la imagen base64
image_data = base64.b64decode(base64_image)
image = Image.open(io.BytesIO(image_data))

# Convertir la imagen a un array NumPy (valores de píxeles)
image_array = np.array(image)

# Normalizar los valores de los píxeles (valores entre 0 y 1)
normalized_image_array = image_array / 255.0

# Aplanar el array (convertirlo en un vector de 64 valores)
image_flat = normalized_image_array.flatten()

# Convertir el array NumPy a lista para el JSON
image_flat_list = image_flat.tolist()

# Crear los datos que se enviarán al modelo (sin envolver con 'image')
data = {
    "instances": [
        image_flat_list
    ]
}

# Obtener el access token
access_token = get_access_token()

# Encabezados de la solicitud
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Hacer la solicitud POST al modelo
response = requests.post(url, headers=headers, data=json.dumps(data))

# Imprimir la respuesta
print(response.status_code)
print(response.json())