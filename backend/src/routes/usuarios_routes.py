from flask import Blueprint, g, request

from src.errores import error_respuesta
from src.repositories.auth_repository import obtener_usuario_por_id
from src.services.usuarios_services import crear_usuario_staff, listar_usuarios_staff
from src.utils.auth import roles_required, token_required
from src.utils.roles import ADMINISTRADOR, ROLES_VALIDOS
from src.utils.http_errors import handle_unexpected_errors

usuarios_bp = Blueprint('usuarios_bp', __name__)


@usuarios_bp.get('/usuarios/me')
@handle_unexpected_errors
@token_required
@roles_required(*ROLES_VALIDOS)
def usuario_actual():
    usuario = obtener_usuario_por_id(g.current_user['id_usuario'])
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
    if rol not in (None, 'admin', 'recepcionista'):
        return error_respuesta(
            'El filtro rol debe ser admin o recepcionista',
            'FILTRO_INVALIDO',
        ), 400

    usuarios = listar_usuarios_staff(rol)
    return {'usuarios': usuarios}, 200


@usuarios_bp.post('/usuarios')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def crear_usuario():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return error_respuesta('El cuerpo debe ser un objeto JSON', 'CUERPO_INVALIDO'), 400

    resultado, status_code = crear_usuario_staff(datos)
    return resultado, status_code