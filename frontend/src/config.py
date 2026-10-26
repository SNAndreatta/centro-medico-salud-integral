import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    # Servidor Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'

    # Seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-de-desarrollo')