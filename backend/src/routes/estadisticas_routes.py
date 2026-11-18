from flask import Blueprint, g, request

from src.services.estadisticas_services import (
    obtener_estadisticas_ausentismo,
    obtener_estadisticas_ocupacion,
    obtener_estadisticas_tiempo_espera,
    obtener_estadisticas_turnos,
    obtener_estadisticas_turnos_especialidad,
    obtener_sala_espera,
)
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


@estadisticas_bp.get('/estadisticas/ausentismo')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def consultar_ausentismo():
    respuesta, status_code = obtener_estadisticas_ausentismo(request.args)
    return respuesta, status_code


@estadisticas_bp.get('/estadisticas/tiempo_espera')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def consultar_tiempo_espera():
    respuesta, status_code = obtener_estadisticas_tiempo_espera(request.args)
    return respuesta, status_code


@estadisticas_bp.get('/estadisticas/turnos-especialidad')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def consultar_turnos_por_especialidad():
    respuesta, status_code = obtener_estadisticas_turnos_especialidad(request.args)
    return respuesta, status_code