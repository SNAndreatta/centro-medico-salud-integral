from flask import Blueprint, g, request

from src.services.agendas_services import filtrar_agendas
from src.utils.auth import token_required, roles_required
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA, MEDICO, PACIENTE
from src.utils.http_errors import handle_unexpected_errors

agendas_bp = Blueprint('agendas_bp', __name__)

@agendas_bp.get('/agendas')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, MEDICO, PACIENTE)
def listar_agendas():
    respuesta, status_code = filtrar_agendas(request.args, g.current_user)
    return respuesta, status_code