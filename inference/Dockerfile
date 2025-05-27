FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY ./inference/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./inference/app /app

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "80"]