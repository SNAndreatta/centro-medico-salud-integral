from flask import Blueprint, g, request

from src.errores import error_respuesta
from src.repositories.pacientes_repositories import obtener_paciente_por_usuario
from src.services.turnos_services import (
    cancelar_turno,
    filtrar_turnos,
    filtrar_turnos_disponibles,
    generar_disponibilidad,
    registrar_checkin_por_qr,
    reservar_turno,
)
from src.utils.auth import roles_required, token_required
from src.utils.http_errors import handle_unexpected_errors
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA, PACIENTE, MEDICO
from src.utils.utils import validar_id_positivo, validar_objeto_json
from src.validators.turnos_validators import validar_cancelacion_turno

turnos_bp = Blueprint('turnos_bp', __name__)

@turnos_bp.get('/turnos/disponibles')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE, MEDICO)
def listar_turnos_disponibles():
    respuesta, status_code = filtrar_turnos_disponibles(request.args)
    return respuesta, status_code


@turnos_bp.get('/turnos')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE, MEDICO)
def listar_turnos():
    respuesta, status_code = filtrar_turnos(request.args, g.current_user)
    return respuesta, status_code

@turnos_bp.post('/turnos/generar')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def generar_turnos():
    respuesta, status_code = generar_disponibilidad()
    return respuesta, status_code


@turnos_bp.post('/turnos/<int:id_turno>/reservar')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE)
def reservar_turno_endpoint(id_turno):
    datos = request.get_json(silent=True)
    if datos is None:
        datos = {}
    if not isinstance(datos, dict):
        return error_respuesta('El cuerpo debe ser un objeto JSON', 'CUERPO_INVALIDO'), 400

    id_paciente = datos.get('id_paciente')
    if g.current_user['id_rol'] == PACIENTE:
        id_paciente = obtener_paciente_por_usuario(g.current_user['id_usuario'])
        if id_paciente is None:
            return error_respuesta('El paciente autenticado no existe', 'PACIENTE_INEXISTENTE'), 404

    if id_paciente is None:
        return error_respuesta('id_paciente es obligatorio', 'ID_PACIENTE_REQUERIDO'), 400

    id_paciente, error = validar_id_positivo(id_paciente, 'id_paciente')
    if error:
        return error, 400

    respuesta, status_code = reservar_turno(id_turno, id_paciente)
    return respuesta, status_code


@turnos_bp.post('/turnos/checkin')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def checkin_turno_endpoint():
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    token = datos.get('token')
    if not isinstance(token, str) or not token.strip():
        return error_respuesta('token es obligatorio', 'TOKEN_REQUERIDO'), 400

    respuesta, status_code = registrar_checkin_por_qr(token.strip())
    return respuesta, status_code


@turnos_bp.post('/turnos/cancelar')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE)
def cancelar_turno_endpoint():
    datos = request.get_json(silent=True)
    id_turno, error = validar_cancelacion_turno(datos)
    if error:
        return error

    respuesta, status_code = cancelar_turno(id_turno, g.current_user)
    return respuesta, status_code