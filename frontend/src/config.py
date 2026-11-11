import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-de-desarrollo')

    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 8000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    BACKEND_URL = os.getenv(
        'BACKEND_URL',
        'http://api:5000/api'
    )
