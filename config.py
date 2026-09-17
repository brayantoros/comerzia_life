import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'tienda_db3'),
    'port': int(os.getenv('DB_PORT', 3306))
}

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'img')
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
SECRET_KEY = os.getenv('SECRET_KEY', 'cambia_esto_por_una_clave_segura')
