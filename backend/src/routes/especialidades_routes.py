from flask import Blueprint, request

from src.utils.auth import roles_required, token_required
from src.utils.http_errors import handle_unexpected_errors
from src.errores import error_respuesta
from src.services.especialiades_services import (
    listar_especialidades,
    crear_especialidad,
    modificar_especialidad,
    eliminar_especialidad,
    )
from src.utils.roles import ADMINISTRADOR, ROLES_VALIDOS
from src.utils.utils import validar_cuerpo_json, validar_objeto_json

especialidades_bp = Blueprint('especialidades_bp', __name__)

@especialidades_bp.get('/especialidades')
@handle_unexpected_errors
@token_required
@roles_required(*ROLES_VALIDOS)
def obtener_especialidades():
    respuesta, status_code = listar_especialidades()
    return respuesta, status_code

@especialidades_bp.post('/especialidades')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def alta_especialidad():
    datos = request.get_json(silent=True)
    error_json = validar_cuerpo_json(datos)
    if error_json:
        return error_json

    respuesta, status_code = crear_especialidad(datos)
    return respuesta, status_code

@especialidades_bp.put('/especialidades/<int:id_especialidad>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def editar_especialidad(id_especialidad):
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json
    
    respuesta, status_code = modificar_especialidad(id_especialidad, datos)
    return respuesta, status_code
 
 
@especialidades_bp.delete('/especialidades/<int:id_especialidad>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def baja_especialidad(id_especialidad):
    respuesta, status_code = eliminar_especialidad(id_especialidad)
    return respuesta, status_code
 