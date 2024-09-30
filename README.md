# API de clasificación de imágenes
Este proyecto es una API desarrollada con Django y Django REST Framework que permite realizar clasificación de imágenes utilizando un modelo de Machine Learning. Los usuarios pueden enviar imágenes codificadas en base64 y la API procesa las imágenes, ejecuta una clasificación y almacena los resultados en una base de datos. Está diseñado para facilitar la integración de servicios de clasificación de imágenes en aplicaciones empresariales.

## Lo que aprenderás siguendo esta guía
Esta guía te permitirá usar la API en su despliegue en la dirección http://34.174.155.71/api/predict/. Tenemos 3 secciones sobre el uso de la API. En la primera sección aprenderás a usarla y en las dos siguientes tendrás una breve descripción de parámetros técnicos.
1. Primer contacto: autenticación
2. Endpoints
3. Latencia

## 1. Primer contacto: autenticación
Cuando ingreses a la dirección proporcionada anteriormente te encontrarás con la interfaz de usuario de Django REST framework.

Esta interfaz está pensada para uso interno y tiene autenticación, por lo que para usarla se requiere generar un token único asignado a cada usuario ya registrado en la base de datos. Esto lo podemos notar en el siguiente mensaje.
```
{
    "detail": "Authentication credentials were not provided."
}
```

Para comunicarnos con la API podemos usar diversas herramientas como Insomnia, Thunder Client o Postman. En este caso usaremos la última opción, Postman.

Si ya tienes token puedes ignorar la sección "1.1. Generación de token" e ir directamente a la sección "1.2. Uso de la API"

### 1.1. Generación de token.

Si no tenemos descargado Postman, lo primero es descargar Postman desde su web https://www.postman.com/downloads/.

Una vez descargado lo abriremos y en su interfaz presionaremos en agregar un nuevo request; botón con un símbolo "+" en la barra superior de la interfaz inmediatamente abajo del recuadro de búsqueda "Search Postman".

Allí configuraremos la solicitud de la siguiente manera:
* Método HTTP: POST
* URL: http://34.174.155.71/api/predict/

En el menú Headers haremos lo siguiente:
* Key: Content-Type
* Value: application/json

En el menú Body seleccionamos "raw" y "JSON" y en el recuadro pegaremos el siguiente JSON con las credenciales del usuario registrado en la base de datos:
```
{
  "username": "usuario_1",
  "password": "contra_987@"
}
```

Cliqueamos en "Send" y en el recuadro inferior (zona de resultados) obtendremos el resultado que se verá similar al siguiente JSON:

```
{
    "token": "a7b5c2d9f3e1g8h6i4j0k5l2m9n8o7p6q5r4s3t2"
}
```
Este es el token asignado al usuario "usuario_1" y "contra_987@".

### 1.2. Clasificación de imágenes mediante la API

Ahora que conocemos el token asociado a un usuario (username: usuario_1, password: contra_987@, token: a7b5c2d9f3e1g8h6i4j0k5l2m9n8o7p6q5r4s3t2), entonces procedemos a hacer la solicitud a la API con la que obtendremos el resultado del modelo, es decir, la clasificación de nuestra imagen.

La solicitud por Postman será la siguiente:
* Método HTTP: POST
* URL: http://34.174.155.71/api/predict/

Ahora tendremos dos Headers:
* Key: Content-Type
* Value: application/json
* Key: Authorization
* Value: Token a7b5c2d9f3e1g8h6i4j0k5l2m9n8o7p6q5r4s3t2

Cambia el contenido del recuadro de Body:
* raw
* JSON
* Recuadro del Body:
```
{
    "request_id": "uuid",
    "modelo": "clf.pickle",
    "image": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAAIAAgBAREA/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oACAEBAAA/AOYitTJ8BgJYkn8tZJ4maMLFEpnC5EhXJnBVh5YYZR884Ar/2Q=="
}
```
Ten presente que:
* El request_id es el id de la solicitud. No se genera automáticamente porque se asume que es generado por un proceso externo, por lo que no se debe cambiar para mantener trazabilidad.
* El modelo siempre será "clf.pickle" debido a que es el modelo entrenado para la clasificación de imágenes.
*  image: es la cadena codificada en base64 que representa la imagen que recibirá el modelo. Aquí ingresas la cadena que representa la imagen que quieres clasificar.

### 1.3. Resultado
¡Listo! Tendrás como resultado en el recuadro inferior la clasificación de tu imagen. El resultado debe ser similar al siguiente:

```
{"request_id":"uuid","prediction":[8]}
```

Esto significa que tu imagen contiene un 8.

## 2.Endpoints
### 2.1. **/api/predict/**
- **Método:** POST
- **Descripción:** este endpoint recibe una solicitud POST con una imagen codificada en base64 y realiza una predicción utilizando un modelo de Machine Learning. Los datos de la predicción se almacenan en la base de datos.
- **Parámetros requeridos:**
  - `request_id`: identificador único (UUID).
  - `modelo`: nombre del modelo a utilizar (por ejemplo, `clf.pickle`).
  - `image`: imagen codificada en base64.

### 2.2. **/api/token-auth/**
- **Método:** POST
- **Descripción:** este endpoint recibe credenciales de usuario (username y password) y devuelve un token de autenticación si las credenciales son correctas. Este token se utilizará para acceder a los demás endpoints protegidos por autenticación.
- **Parámetros requeridos:**
  - `username`: nombre del usuario.
  - `password`: contraseña del usuario.
  - `image`: La imagen codificada en base64.

### 2.3. **/**
- **Método:** GET
- **Descripción:** redirige al endpoint /api/predict/ de manera predeterminada.


## 3. Latencia
Aquí se presenta una tabla de latencia de los servicios de Google Cloud asociados al desplegue de la API. Estos valores son entre las 11:09am y las 12:09pm del lunes 30 de septiembre de 2024.

| Nombre                    | Solicitudes | Latencia mediana (ms) | 95% de latencia (ms) |
|---------------------------|-------------|-----------------------|----------------------|
| Cloud Monitoring API       | 6,924       | 53                    | 115                  |
| Compute Engine API         | 1,393       | 85                    | 199                  |
| Cloud Logging API          | 657         | 81                    | 126                  |
| Kubernetes Engine API      | 72          | 29                    | 61                   |


## Autor
* Amador Calle Loaiza.
* Economista, Magíster en Ingeniería Analítica y entusiasta de la tecnología.