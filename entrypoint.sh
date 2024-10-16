#!/bin/sh

# Esperar hasta que la base de datos esté disponible
while ! nc -z $DB_HOST $DB_PORT; do
  echo "Esperando a la base de datos..."
  sleep 1
done

# Ejecutar las migraciones solo si hay cambios
if python manage.py showmigrations | grep '\[ \]'; then
  python manage.py makemigrations
  python manage.py migrate
else
  echo "No hay migraciones pendientes."
fi

# Recoger archivos estáticos solo si hay cambios
python manage.py collectstatic --noinput --clear

# Ejecutar el servidor de Django
exec python manage.py runserver 0.0.0.0:80