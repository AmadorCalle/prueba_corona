# Usar una imagen base oficial de Python slim para reducir el tamaño de la imagen
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar netcat-openbsd para el healthcheck de la base de datos
RUN apt-get update && apt-get install -y netcat-openbsd postgresql-client

# Copiar solo los archivos necesarios para la instalación de dependencias
COPY requirements.txt .

# Actualizar pip a la última versión
RUN pip install --upgrade pip

# Instalar las dependencias usando pip y limpiar caché después de la instalación
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto al contenedor
COPY . .

# Establecer las variables de entorno para la configuración de Django
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# Crear un directorio para archivos estáticos
RUN mkdir -p /app/static

# Dar permisos de ejecución al script de entrypoint
RUN chmod +x /app/entrypoint.sh

# Exponer el puerto 80 para el servidor de desarrollo de Django
EXPOSE 80

# Definir el entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto para ejecutar el servidor de Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]