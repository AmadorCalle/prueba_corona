# Usar una imagen base oficial de Python slim para reducir el tamaño de la imagen
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar solo los archivos necesarios para la instalación de dependencias
COPY requirements.txt .

# Instalar las dependencias usando pip y limpiar caché después de la instalación
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto al contenedor
COPY . .

# Establecer las variables de entorno para la configuración de Django
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# Crear un directorio para archivos estáticos
RUN mkdir -p /app/static

# Ejecutar el comando collectstatic durante la construcción del contenedor
RUN python manage.py collectstatic --noinput

# Exponer el puerto 8000 para el servidor de desarrollo de Django
EXPOSE 8000

# Ejecutar las migraciones y levantar el servidor de Django
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]