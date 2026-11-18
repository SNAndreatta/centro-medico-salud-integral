from flask import Blueprint, g, request

from src.repositories.medicos_repositories import obtener_medico_por_usuario
from src.services.medicos_services import (
    agregar_cobertura_medico,
    crear_medico,
    eliminar_medico,
    filtrar_medicos,
    listar_coberturas_medico,
    modificar_medico,
    obtener_medico,
    quitar_cobertura_medico,
)
from src.utils.auth import token_required, roles_required
from src.utils.roles import ADMINISTRADOR, MEDICO, RECEPCIONISTA, PACIENTE
from src.utils.http_errors import handle_unexpected_errors
from src.validators.common import validar_objeto_json
from src.validators.medicos_validators import validar_datos_cobertura_medico

medicos_bp = Blueprint('medicos_bp', __name__)


def _es_medico_propio(id_medico):
    """Indica si el médico indicado pertenece al usuario autenticado."""
    medico = obtener_medico_por_usuario(g.current_user['id_usuario'])
    return medico is not None and int(medico['id_medico']) == id_medico


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


@medicos_bp.get('/medicos/<int:id_medico>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE)
def consultar_medico(id_medico):
    respuesta, status_code = obtener_medico(id_medico)
    return respuesta, status_code


@medicos_bp.put('/medicos/<int:id_medico>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, MEDICO)
def editar_medico(id_medico):
    if g.current_user['id_rol'] != ADMINISTRADOR and not _es_medico_propio(id_medico):
        return error_respuesta(
            'No tenés permiso para modificar este médico',
            'PERMISOS_INSUFICIENTES',
        ), 403

    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    respuesta, status_code = modificar_medico(id_medico, datos)
    return respuesta, status_code


@medicos_bp.delete('/medicos/<int:id_medico>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def borrar_medico(id_medico):
    respuesta, status_code = eliminar_medico(id_medico)
    return respuesta, status_code


@medicos_bp.get('/medicos/<int:id_medico>/coberturas')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, RECEPCIONISTA, PACIENTE, MEDICO)
def consultar_coberturas_medico(id_medico):
    respuesta, status_code = listar_coberturas_medico(id_medico)
    return respuesta, status_code


@medicos_bp.post('/medicos/<int:id_medico>/coberturas')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR, MEDICO)
def agregar_cobertura_a_medico(id_medico):
    if g.current_user['id_rol'] != ADMINISTRADOR and not _es_medico_propio(id_medico):
        return error_respuesta(
            'No tenés permiso para modificar este médico',
            'PERMISOS_INSUFICIENTES',
        ), 403

    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    id_cobertura, error = validar_datos_cobertura_medico(datos)
    if error:
        return error, 400

    respuesta, status_code = agregar_cobertura_medico(id_medico, id_cobertura)
    return respuesta, status_code


@medicos_bp.delete('/medicos/<int:id_medico>/coberturas/<int:id_cobertura>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def quitar_cobertura_de_medico(id_medico, id_cobertura):
    respuesta, status_code = quitar_cobertura_medico(id_medico, id_cobertura)
    return respuesta, status_code