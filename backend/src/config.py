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
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        if FLASK_DEBUG:
            SECRET_KEY = 'development-only-secret-change-before-deploying'
        else:
            raise RuntimeError('SECRET_KEY must be configured when debug mode is disabled')
    elif not FLASK_DEBUG and len(SECRET_KEY) < 32:
        raise RuntimeError('SECRET_KEY must contain at least 32 characters when debug mode is disabled')

    JWT_ACCESS_TOKEN_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_MINUTES', '60'))
    if JWT_ACCESS_TOKEN_MINUTES <= 0:
        raise ValueError('JWT_ACCESS_TOKEN_MINUTES must be greater than zero')

    # SMTP para comprobantes por correo
    SMTP_ENABLED = os.getenv('SMTP_ENABLED', 'false').lower() == 'true'
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'
    SMTP_TIMEOUT = int(os.getenv('SMTP_TIMEOUT', '15'))
    SMTP_DEFAULT_SENDER = os.getenv('SMTP_DEFAULT_SENDER', 'no-reply@saludintegral.local')
    PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', 'http://localhost:5000')
    CANCELACION_TTL_MINUTES = int(os.getenv('CANCELACION_TTL_MINUTES', '60'))