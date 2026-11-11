from src.repositories.auth_repository import obtener_usuario_por_id
from src.repositories.usuarios_repositories import (
    guardar_usuario_staff,
    obtener_usuarios_staff,
)
from src.errores import error_respuesta
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA
from src.utils.security import hash_password
from src.validators.usuarios_validators import validar_datos_usuario_staff

ROLES_STAFF = {'admin': ADMINISTRADOR, 'recepcionista': RECEPCIONISTA}


def obtener_usuario_actual(id_usuario):
    return obtener_usuario_por_id(id_usuario)


def listar_usuarios_staff(rol=None):
    id_rol = ROLES_STAFF.get(rol) if rol is not None else None
    return obtener_usuarios_staff(id_rol)


def crear_usuario_staff(datos):
    usuario, error = validar_datos_usuario_staff(datos)
    if error:
        return error, 400

    usuario['contrasenia'] = hash_password(usuario.pop('password'))
    usuario_guardado = guardar_usuario_staff(usuario)
    if usuario_guardado is None:
        return error_respuesta(
            'Ya existe un usuario con ese correo electrónico o DNI',
            'USUARIO_DUPLICADO',
        ), 400

    return {'usuario': usuario_guardado}, 201