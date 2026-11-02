from flask import Blueprint, g, request

from src.services.turnos_services import filtrar_turnos, filtrar_turnos_disponibles, generar_disponibilidad
from src.utils.auth import roles_required, token_required
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA, PACIENTE, MEDICO
from src.utils.http_errors import handle_unexpected_errors

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