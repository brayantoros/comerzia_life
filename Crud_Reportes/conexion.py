import os
import mysql.connector

# Configuración de la base de datos con valores por defecto y soporte para variables de entorno
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'crud_db'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Función para conectar con la base de datos
def connect(custom_config=None):
    config = custom_config or DB_CONFIG.copy()
    try:
        connection = mysql.connector.connect(**config)
        return connection
    except mysql.connector.Error as err:
        # Fallback al puerto 3307 si el puerto 3306 fue denegado y no se especificó un puerto personalizado
        if config.get('port') == 3306 and err.errno in (2003, 1061):
            try:
                fallback = config.copy()
                fallback['port'] = 3307
                return mysql.connector.connect(**fallback)
            except mysql.connector.Error:
                pass
        print(f"[ERROR BD] No se pudo conectar a la base de datos: {err}")
        raise err