from flask import Blueprint, g, request

from src.services.agendas_services import filtrar_agendas, crear_agenda, obtener_agenda, actualizar_agenda, eliminar_agenda
from src.utils.auth import token_required, roles_required
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA, MEDICO, PACIENTE
from src.utils.http_errors import handle_unexpected_errors
from src.utils.utils import validar_objeto_json
agendas_bp = Blueprint('agendas_bp', __name__)

@agendas_bp.get('/agendas')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, MEDICO, PACIENTE)
def listar_agendas():
    respuesta, status_code = filtrar_agendas(request.args, g.current_user)
    return respuesta, status_code

@agendas_bp.get('/agendas/<int:id_agenda>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, MEDICO, PACIENTE)
def consultar_agenda(id_agenda):
    respuesta, status_code = obtener_agenda(id_agenda, g.current_user)
    return respuesta, status_code


@agendas_bp.post('/agendas')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def agregar_agenda():
    datos = request.get_json(silent=True)

    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    respuesta, status_code = crear_agenda(datos)
    return respuesta, status_code

@agendas_bp.put('/agendas/<int:id_agenda>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def modificar_agenda(id_agenda):
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json
    respuesta, status_code = actualizar_agenda(id_agenda, datos)
    return respuesta, status_code

@agendas_bp.delete('/agendas/<int:id_agenda>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def borrar_agenda(id_agenda):
    respuesta, status_code = eliminar_agenda(id_agenda)
    return respuesta, status_code