from flask import Blueprint, request

from src.utils.auth import roles_required, token_required
from src.utils.http_errors import handle_unexpected_errors
from src.errores import error_respuesta
from src.services.especialiades_services import (
    listar_especialidades,
    crear_especialidad
    )
from src.utils.roles import ADMINISTRADOR

especialidades_bp = Blueprint('especialidades_bp', __name__)

@especialidades_bp.get('/especialidades')
@handle_unexpected_errors
def obtener_especialidades():
    respuesta, status_code = listar_especialidades()
    return respuesta, status_code

@especialidades_bp.post('/especialidades')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def alta_especialidad():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return error_respuesta('El cuerpo debe ser un objeto JSON', 'CUERPO_INVALIDO'), 400
 
    respuesta, status_code = crear_especialidad(datos)
    return respuesta, status_code