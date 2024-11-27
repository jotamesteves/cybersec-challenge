#!/bin/bash

# Configuración del servicio Agent
IMAGE_NAME="agent_image"
CONTAINER_NAME="agent_container"

# Variables de entorno
API_HOST=${API_HOST:-"http://172.31.20.158:5012"}  # Cambiar por la IP privada de la instancia EC2

# Construir la imagen del Agent
echo "Construyendo la imagen del Agent..."
docker build -t $IMAGE_NAME .

# Verifica si el contenedor ya está corriendo
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
  echo "Deteniendo el contenedor existente..."
  docker stop $CONTAINER_NAME
  docker rm $CONTAINER_NAME
fi

# Correr el contenedor del Agent
echo "Corriendo el contenedor del Agent..."
docker run -d \
  --name $CONTAINER_NAME \
  --env API_HOST=$API_HOST \
  $IMAGE_NAME