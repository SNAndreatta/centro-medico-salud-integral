from flask import Blueprint, g, request

from src.errores import error_respuesta
from src.services.turnos_services import (
    actualizar_estado_turno,
    cancelar_turno,
    cancelar_turno_por_token,
    filtrar_turnos,
    filtrar_turnos_disponibles,
    generar_disponibilidad,
    obtener_detalle_turno,
    registrar_checkin_por_qr,
    resolver_estado_turno,
    reservar_turno_solicitado,
)
from src.utils.auth import roles_required, token_required
from src.utils.http_errors import handle_unexpected_errors
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA, PACIENTE, MEDICO
from src.validators.turnos_validators import (
    validar_cancelacion_turno,
    validar_checkin_turno,
    validar_estado_turno,
)

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


@turnos_bp.get('/turnos/<int:id_turno>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE, MEDICO)
def detalle_turno(id_turno):
    return obtener_detalle_turno(id_turno, g.current_user)


@turnos_bp.post('/turnos/generar')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def generar_turnos():
    respuesta, status_code = generar_disponibilidad()
    return respuesta, status_code


@turnos_bp.put('/turnos/<int:id_turno>/estado')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, MEDICO)
def modificar_estado_turno(id_turno):
    id_estado, nombre_estado, error = validar_estado_turno(request.get_json(silent=True))
    if error:
        return error

    id_estado, error = resolver_estado_turno(id_estado, nombre_estado)
    if error:
        return error

    return actualizar_estado_turno(id_turno, id_estado, g.current_user)


@turnos_bp.post('/turnos/<int:id_turno>/reservar')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE)
def reservar_turno_endpoint(id_turno):
    datos = request.get_json(silent=True)
    respuesta, status_code = reservar_turno_solicitado(id_turno, datos, g.current_user)
    return respuesta, status_code


@turnos_bp.post('/turnos/checkin')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def checkin_turno_endpoint():
    datos = request.get_json(silent=True)
    token, error = validar_checkin_turno(datos)
    if error:
        return error

    respuesta, status_code = registrar_checkin_por_qr(token)
    return respuesta, status_code


@turnos_bp.get('/turnos/<int:id_turno>/cancelar')
@handle_unexpected_errors
def cancelar_turno_por_email_endpoint(id_turno):
    token = request.args.get('token')
    if not token:
        return error_respuesta('El token de cancelación es obligatorio', 'TOKEN_REQUERIDO'), 400

    respuesta, status_code = cancelar_turno_por_token(id_turno, token)
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
