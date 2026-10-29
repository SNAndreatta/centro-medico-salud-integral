from flask import Blueprint, request

from src.services.pacientes_services import filtrar_pacientes
from src.utils.auth import roles_required, token_required

pacientes_bp = Blueprint('pacientes_bp', __name__)


@pacientes_bp.get('/pacientes')
@token_required
@roles_required(1, 2)
def listar_pacientes():
    respuesta, status_code = filtrar_pacientes(request.args)
    return respuesta, status_code