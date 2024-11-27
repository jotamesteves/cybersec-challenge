from flask import Flask, request, jsonify
import logging
import mysql.connector
from datetime import datetime
import os
import json
import time

app = Flask(__name__)

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

# Configuración de la base de datos
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')), 
    'database': os.getenv('DB_NAME'), 
    'collation': "utf8mb4_unicode_ci", 
    'charset': "utf8mb4"
}

# Función para obtener la conexión a la base de datos con más detalles en los logs
def get_db_connection():
    try:
        logging.info(f"Intentando conectar a la base de datos: {db_config['host']}:{db_config['port']} (usuario: {db_config['user']})")
        conn = mysql.connector.connect(**db_config)
        logging.info("Conexión a la base de datos exitosa.")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Error al conectar a la base de datos: {err}")
        raise

# Inicializar la base de datos y crear tablas si no existen
def initialize_database():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        logging.info(f"Creando la base de datos {db_config['database']} si no existe...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        conn.database = db_config['database']
        logging.info("Base de datos seleccionada correctamente.")
        
        logging.info("Creando tabla system_info si no existe...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip VARCHAR(255),
            date DATE,
            data JSON
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
        """)

        conn.commit()
        logging.info("Tabla 'system_info' creada o verificada con éxito.")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        logging.error(f"Error en la inicialización de la base de datos: {err}")
        raise

# Ruta para recolectar datos
@app.route('/collect', methods=['POST'])
def collect_data():
    data = request.json
    ip = request.remote_addr
    date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        logging.info(f"Recibiendo datos desde {ip} para la fecha {date}")
        conn = get_db_connection()
        cursor = conn.cursor()
        logging.info(f"Ejecutando la consulta INSERT para los datos: {data}")
        cursor.execute("INSERT INTO system_info (ip, date, data) VALUES (%s, %s, %s)", (ip, date, json.dumps(data)))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Datos recibidos y almacenados exitosamente desde {ip}")
        return jsonify({"message": "Data collected successfully"}), 201
    except Exception as e:
        logging.error(f"Error al procesar los datos de {ip}: {e}")
        return jsonify({"error": str(e)}), 500

# Ruta para consultar datos
@app.route('/query', methods=['GET'])
def query_data():
    ip = request.args.get('ip')
    try:
        logging.info(f"Consultando datos para la IP: {ip}")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM system_info WHERE ip = %s", (ip,))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        logging.info(f"Consulta realizada exitosamente para {ip}")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error al realizar la consulta para la IP {ip}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Espera para asegurar que la base de datos esté lista
    logging.info("Esperando a que la base de datos esté lista...")
    time.sleep(12)
    initialize_database()
    logging.info("Inicialización de la base de datos completada. Iniciando la aplicación Flask.")
    app.run(host='0.0.0.0', port=5012)