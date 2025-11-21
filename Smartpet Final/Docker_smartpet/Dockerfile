FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Carpeta raíz en el contenedor
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    musl-dev \
    && apt-get clean

# Copiar archivo requirements
COPY SmartPet/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO SmartPet dentro del contenedor
COPY SmartPet /app/SmartPet

# AQUÍ está tu manage.py REAL
WORKDIR /app/SmartPet/SmartPet

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
