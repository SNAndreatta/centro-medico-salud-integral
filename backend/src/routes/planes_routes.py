from flask import Blueprint, request

from src.services.planes_services import eliminar_plan, modificar_plan
from src.utils.auth import roles_required, token_required
from src.utils.http_errors import handle_unexpected_errors
from src.utils.roles import ADMINISTRADOR
from src.utils.utils import validar_objeto_json

planes_bp = Blueprint('planes_bp', __name__)

@planes_bp.put('/planes/<int:id_plan>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def editar_plan(id_plan):
    datos = request.get_json(silent=True)
    error = validar_objeto_json(datos)
    if error:
        return error

    respuesta, status_code = modificar_plan(id_plan, datos)
    return respuesta, status_code


@planes_bp.delete('/planes/<int:id_plan>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def baja_plan(id_plan):
    respuesta, status_code = eliminar_plan(id_plan)
    return respuesta, status_code