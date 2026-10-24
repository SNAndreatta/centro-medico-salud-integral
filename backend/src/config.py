import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    # Base de datos MySQL
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_NAME = os.getenv('DB_NAME', 'centro_medico')
    DB_USER = os.getenv('DB_USER', 'app_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'app_password')
    DB_ROOT_PASSWORD = os.getenv('DB_ROOT_PASSWORD', 'root_password')

    # Servidor Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'

    # Seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-de-desarrollo')