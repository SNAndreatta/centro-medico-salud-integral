from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.auth_service import autenticar_usuario

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.post('/auth/login')
def login():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return error_respuesta('El cuerpo debe ser un objeto JSON', 'CUERPO_INVALIDO'), 400

    correo_electronico = datos.get('correo_electronico')
    password = datos.get('password')
    if (
        not isinstance(correo_electronico, str)
        or not correo_electronico.strip()
        or not isinstance(password, str)
        or not password
    ):
        return error_respuesta(
            'correo_electronico y password son obligatorios',
            'CREDENCIALES_REQUERIDAS',
        ), 400

    resultado = autenticar_usuario(correo_electronico, password)
    if resultado is None:
        return error_respuesta(
            'Correo electrónico o contraseña incorrectos',
            'CREDENCIALES_INVALIDAS',
        ), 401

    return resultado, 200