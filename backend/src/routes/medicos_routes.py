from flask import Blueprint, request

from src.services.medicos_services import crear_medico, filtrar_medicos
from src.utils.auth import token_required, roles_required
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA, PACIENTE
from src.utils.http_errors import handle_unexpected_errors
from src.utils.utils import validar_objeto_json

medicos_bp = Blueprint('medicos_bp', __name__)


@medicos_bp.post('/medicos')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def alta_medico():
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    respuesta, status_code = crear_medico(datos)
    return respuesta, status_code


@medicos_bp.get('/medicos')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE)
def listar_medicos():
    respuesta, status_code = filtrar_medicos(request.args)
    return respuesta, status_code