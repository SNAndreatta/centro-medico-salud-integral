from flask import Blueprint, request

from src.utils.http_errors import handle_unexpected_errors
from src.errores import error_respuesta
from src.services.especialiades_services import listar_especialidades

especialidades_bp = Blueprint('especialidades_bp', __name__)

@especialidades_bp.get('/especialidades')
@handle_unexpected_errors
def obtener_especialidades():
    respuesta, status_code = listar_especialidades()
    return respuesta, status_code
