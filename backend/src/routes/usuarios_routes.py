from flask import Blueprint, g, request

from src.errores import error_respuesta
from src.services.usuarios_services import (
    crear_usuario_staff,
    listar_usuarios_staff,
    obtener_usuario_actual,
)
from src.utils.auth import roles_required, token_required
from src.utils.roles import ADMINISTRADOR, ROLES_VALIDOS
from src.utils.http_errors import handle_unexpected_errors
from src.validators.common import validar_objeto_json
from src.validators.usuarios_validators import validar_filtro_rol

usuarios_bp = Blueprint('usuarios_bp', __name__)


@usuarios_bp.get('/usuarios/me')
@handle_unexpected_errors
@token_required
@roles_required(*ROLES_VALIDOS)
def usuario_actual():
    usuario = obtener_usuario_actual(g.current_user['id_usuario'])
    if usuario is None:
        return error_respuesta(
            'El usuario asociado al token ya no existe',
            'USUARIO_INEXISTENTE',
        ), 401

    return {
        'id_usuario': int(usuario['id_usuario']),
        'nombre': usuario['nombre'],
        'apellido': usuario['apellido'],
        'id_rol': int(usuario['id_rol']),
    }, 200


@usuarios_bp.get('/usuarios')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def listar_usuarios():
    rol = request.args.get('rol')
    error = validar_filtro_rol(rol)
    if error:
        return error, 400

    usuarios = listar_usuarios_staff(rol)
    return {'usuarios': usuarios}, 200


@usuarios_bp.post('/usuarios')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def crear_usuario():
    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    resultado, status_code = crear_usuario_staff(datos)
    return resultado, status_code