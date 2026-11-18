from flask import Blueprint, g, request

from src.errores import error_respuesta
from src.services.usuarios_services import (
    actualizar_password_usuario,
    actualizar_usuario as actualizar_usuario_service,
    crear_usuario_staff,
    eliminar_usuario as eliminar_usuario_service,
    listar_usuarios as listar_usuarios_service,
    obtener_perfil_usuario,
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
    perfil = obtener_perfil_usuario(g.current_user['id_usuario'])
    if perfil is None:
        return error_respuesta(
            'El usuario asociado al token ya no existe',
            'USUARIO_INEXISTENTE',
        ), 401

    return perfil, 200


@usuarios_bp.get('/usuarios')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def listar_usuarios():
    rol = request.args.get('rol')
    error = validar_filtro_rol(rol)
    if error:
        return error, 400

    usuarios = listar_usuarios_service(rol)
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


@usuarios_bp.put('/usuarios/<int:id_usuario>')
@handle_unexpected_errors
@token_required
@roles_required(*ROLES_VALIDOS)
def actualizar_usuario(id_usuario):
    # Cada usuario puede editar sus propios datos personales; el
    # administrador sigue pudiendo editar a cualquier otro usuario.
    es_propio = id_usuario == g.current_user['id_usuario']
    if not es_propio and g.current_user['id_rol'] != ADMINISTRADOR:
        return error_respuesta(
            'No tenés permiso para modificar otro usuario',
            'PERMISOS_INSUFICIENTES',
        ), 403

    datos = request.get_json(silent=True)
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    resultado, status_code = actualizar_usuario_service(id_usuario, datos)
    return resultado, status_code


@usuarios_bp.delete('/usuarios/<int:id_usuario>')
@handle_unexpected_errors
@token_required
@roles_required(ADMINISTRADOR)
def eliminar_usuario(id_usuario):
    resultado, status_code = eliminar_usuario_service(id_usuario, g.current_user)
    return resultado, status_code


@usuarios_bp.put('/usuarios/<int:id_usuario>/password')
@handle_unexpected_errors
@token_required
@roles_required(*ROLES_VALIDOS)
def cambiar_password(id_usuario):
    return actualizar_password_usuario(id_usuario, request.get_json(silent=True), g.current_user)
