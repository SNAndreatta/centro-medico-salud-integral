from flask import Blueprint, request

from src.services.coberturas_services import (
    crear_cobertura,
    eliminar_cobertura,
    listar_coberturas,
    modificar_cobertura,
)
from src.utils.auth import roles_required, token_required
from src.utils.http_errors import handle_unexpected_errors
from src.utils.roles import ADMINISTRADOR
from src.validators.common import validar_objeto_json

coberturas_bp = Blueprint('coberturas_bp', __name__)

@coberturas_bp.get('/coberturas')
@handle_unexpected_errors
def obtener_coberturas():
    """Listado de coberturas.

    Es público porque el formulario de registro necesita mostrar todas las
    coberturas de la base de datos antes de que el paciente tenga cuenta.
    """
    respuesta, status_code = listar_coberturas()
    return respuesta, status_code

@coberturas_bp.post('/coberturas')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def alta_cobertura():
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    respuesta, status_code = crear_cobertura(datos)
    return respuesta, status_code

@coberturas_bp.put('/coberturas/<int:id_cobertura>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def editar_cobertura(id_cobertura):
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    respuesta, status_code = modificar_cobertura(id_cobertura, datos)
    return respuesta, status_code

@coberturas_bp.delete('/coberturas/<int:id_cobertura>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def baja_cobertura(id_cobertura):
    respuesta, status_code = eliminar_cobertura(id_cobertura)
    return respuesta, status_code
