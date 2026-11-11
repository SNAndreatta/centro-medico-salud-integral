from flask import Blueprint, request

from src.services.consultorios_services import (
    listar_consultorios,
    crear_consultorio,
    modificar_consultorio,
    eliminar_consultorio,
)
from src.utils.auth import roles_required, token_required
from src.utils.roles import ADMINISTRADOR, ROLES_VALIDOS
from src.utils.http_errors import handle_unexpected_errors
from src.validators.common import validar_objeto_json

consultorios_bp = Blueprint('consultorios_bp', __name__)

@consultorios_bp.get('/consultorios')
@handle_unexpected_errors
@token_required
@roles_required(*ROLES_VALIDOS)
def obtener_consultorios():
    respuesta, status_code = listar_consultorios()
    return respuesta, status_code

@consultorios_bp.post('/consultorios')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def alta_consultorio():
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    respuesta, status_code = crear_consultorio(datos)
    return respuesta, status_code


@consultorios_bp.put('/consultorios/<int:id_consultorio>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def editar_consultorio(id_consultorio):
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    respuesta, status_code = modificar_consultorio(id_consultorio, datos)
    return respuesta, status_code

@consultorios_bp.delete('/consultorios/<int:id_consultorio>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def baja_consultorio(id_consultorio):
    respuesta, status_code = eliminar_consultorio(id_consultorio)
    return respuesta, status_code