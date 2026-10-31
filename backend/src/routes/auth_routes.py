from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.auth_service import autenticar_usuario
from src.utils.http_errors import handle_unexpected_errors
from src.utils.utils import validar_objeto_json
from src.validators.auth_validators import validar_credenciales_login

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.post('/auth/login')
@handle_unexpected_errors
def login():
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    correo_electronico, password, error = validar_credenciales_login(datos)
    if error:
        return error, 400

    resultado = autenticar_usuario(correo_electronico, password)
    if resultado is None:
        return error_respuesta(
            'Correo electrónico o contraseña incorrectos',
            'CREDENCIALES_INVALIDAS',
        ), 401

    return resultado, 200