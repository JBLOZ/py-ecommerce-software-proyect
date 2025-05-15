FROM python:3.9

WORKDIR /code

RUN apt-get update && apt-get install -y dos2unix netcat-openbsd iputils-ping dnsutils

COPY ./backend/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Solo copiamos el script wait-for-it.sh
COPY ./backend/scripts/wait-for-it.sh /code/scripts/wait-for-it.sh
RUN dos2unix /code/scripts/wait-for-it.sh && chmod +x /code/scripts/wait-for-it.sh

# Copiar el código fuente para producción
COPY ./backend/app /code/src
COPY ./data/ /code/data/

# Establecer PYTHONPATH para que apunte a la carpeta src
ENV PYTHONPATH=src
ENV ENVIRONMENT=prod

# Ejecutar el servidor y buscar el módulo main (main.py) dentro de /code/src
CMD ["/code/scripts/wait-for-it.sh", "db:3306", "-t", "60", "--", "fastapi", "run", "src/main.py", "--proxy-headers", "--port", "80"]