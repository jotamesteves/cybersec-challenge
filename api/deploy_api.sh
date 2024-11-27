#!/bin/bash

# Configuración del servicio API
IMAGE_NAME="api_image"
CONTAINER_NAME="api_container"

# Variables de entorno
DB_HOST="database-1.c7e0caq2ehy0.us-east-2.rds.amazonaws.com"
DB_PORT="3306"
DB_USER="admin"
DB_PASSWORD="Be2un1t#J*oD]y"
DB_NAME="system_info_db"

# Construir la imagen del API
echo "Construyendo la imagen del API..."
docker build -t $IMAGE_NAME .

# Verifica si el contenedor ya está corriendo
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
  echo "Deteniendo el contenedor existente..."
  docker stop $CONTAINER_NAME
  docker rm $CONTAINER_NAME
fi

# Correr el contenedor del API
echo "Corriendo el contenedor del API..."
docker run -d \
  --name $CONTAINER_NAME \
  --env DB_HOST=$DB_HOST \
  --env DB_PORT=$DB_PORT \
  --env DB_USER=$DB_USER \
  --env DB_PASSWORD=$DB_PASSWORD \
  --env DB_NAME=$DB_NAME \
  -p 5012:5012 \
  $IMAGE_NAME