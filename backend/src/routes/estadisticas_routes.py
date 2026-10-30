from flask import Blueprint, g, request

from src.services.estadisticas_services import obtener_sala_espera, obtener_estadisticas_turnos, obtener_estadisticas_ocupacion
from src.utils.auth import roles_required, token_required
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA, MEDICO
from src.utils.http_errors import handle_unexpected_errors

estadisticas_bp = Blueprint('estadisticas_bp', __name__)

@estadisticas_bp.get('/estadisticas/sala_espera')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, MEDICO)
def consultar_sala_espera():
    respuesta, status_code = obtener_sala_espera(g.current_user)
    return respuesta, status_code

@estadisticas_bp.get('/estadisticas/turnos')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def consultar_estadisticas_turnos():
    respuesta, status_code = obtener_estadisticas_turnos(request.args)
    return respuesta, status_code

@estadisticas_bp.get('/estadisticas/ocupacion_consultorios')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def consultar_ocupacion_consultorios():
    respuesta, status_code = obtener_estadisticas_ocupacion(request.args)
    return respuesta, status_code