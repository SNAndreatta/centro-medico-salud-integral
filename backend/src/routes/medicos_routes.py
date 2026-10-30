from flask import Blueprint, request

from src.services.medicos_services import filtrar_medicos
from src.utils.auth import token_required, roles_required
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA, PACIENTE
from src.utils.http_errors import handle_unexpected_errors

medicos_bp = Blueprint('medicos_bp', __name__)


@medicos_bp.get('/medicos')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE)
def listar_medicos():
    respuesta, status_code = filtrar_medicos(request.args)
    return respuesta, status_code