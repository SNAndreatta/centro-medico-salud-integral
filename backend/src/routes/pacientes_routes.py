from flask import Blueprint, request

from src.services.pacientes_services import (
    filtrar_pacientes,
    obtener_paciente_por_id,
    modificar_paciente,
    listar_turnos_paciente
)
from src.services.pacientes_registro_services import procesar_registro_paciente
from src.utils.auth import roles_required, token_required
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA, PACIENTE
from src.utils.http_errors import handle_unexpected_errors
from src.validators.common import validar_objeto_json

pacientes_bp = Blueprint('pacientes_bp', __name__)


@pacientes_bp.post('/pacientes')
@handle_unexpected_errors
def registrar_paciente():
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    respuesta, status_code = procesar_registro_paciente(datos)
    return respuesta, status_code

@pacientes_bp.get('/pacientes')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def listar_pacientes():
    respuesta, status_code = filtrar_pacientes(request.args)
    return respuesta, status_code

@pacientes_bp.get('/pacientes/<int:id_paciente>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def consultar_paciente(id_paciente):
    respuesta, status_code = obtener_paciente_por_id(id_paciente)
    return respuesta, status_code

@pacientes_bp.put('/pacientes/<int:id_paciente>')
@handle_unexpected_errors
@token_required
@roles_required(RECEPCIONISTA, ADMINISTRADOR)
def editar_paciente(id_paciente):
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    respuesta, status_code = modificar_paciente(id_paciente, datos)
    return respuesta, status_code

@pacientes_bp.get('/pacientes/<int:id_paciente>/turnos')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE)
def consultar_turnos_paciente(id_paciente):
    respuesta, status_code = listar_turnos_paciente(id_paciente)
    return respuesta, status_code