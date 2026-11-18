import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-de-desarrollo')

    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 8000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Zona horaria del centro médico. El backend usa la misma, así que los
    # horarios de los turnos se interpretan siempre en hora local.
    TIMEZONE = os.getenv('TIMEZONE', 'America/Argentina/Buenos_Aires')

    BACKEND_URL = os.getenv(
        'BACKEND_URL',
        'http://api:5000/api'
    )
