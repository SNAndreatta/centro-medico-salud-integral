from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.pacientes_services import filtrar_pacientes
from src.services.pacientes_registro_services import procesar_registro_paciente
from src.utils.auth import roles_required, token_required
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA
from src.utils.http_errors import handle_unexpected_errors

pacientes_bp = Blueprint('pacientes_bp', __name__)


@pacientes_bp.post('/pacientes/registro')
@handle_unexpected_errors
def registrar_paciente():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return error_respuesta('El cuerpo debe ser un objeto JSON', 'CUERPO_INVALIDO'), 400

    respuesta, status_code = procesar_registro_paciente(datos)
    return respuesta, status_code


@pacientes_bp.get('/pacientes')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA)
def listar_pacientes():
    respuesta, status_code = filtrar_pacientes(request.args)
    return respuesta, status_code