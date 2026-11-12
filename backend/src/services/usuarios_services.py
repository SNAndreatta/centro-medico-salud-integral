from src.repositories.auth_repository import obtener_usuario_por_id
from src.repositories.usuarios_repositories import (
    actualizar_hash_password,
    guardar_usuario_staff,
    obtener_usuario_para_cambio_password,
    obtener_usuarios_staff,
)
from src.errores import error_respuesta
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA
from src.utils.security import hash_password, verify_password
from src.validators.usuarios_validators import validar_cambio_password, validar_datos_usuario_staff

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


def actualizar_password_usuario(id_usuario, datos, usuario_actual):
    es_cambio_propio = id_usuario == usuario_actual['id_usuario']
    sin_permiso = error_respuesta(
        'No tenés permiso para cambiar esta contraseña',
        'PERMISOS_INSUFICIENTES',
    ), 403
    if not es_cambio_propio:
        if usuario_actual['id_rol'] != ADMINISTRADOR:
            return sin_permiso
        administrador = obtener_usuario_por_id(usuario_actual['id_usuario'])
        if administrador is None or administrador['id_rol'] != ADMINISTRADOR:
            return sin_permiso

    error = validar_cambio_password(datos, es_cambio_propio)
    if error:
        return error

    usuario = obtener_usuario_para_cambio_password(id_usuario)
    if usuario is None:
        return error_respuesta('El usuario no existe', 'USUARIO_INEXISTENTE'), 404

    if es_cambio_propio:
        if not verify_password(usuario['contrasenia'], datos['password_actual']):
            return error_respuesta('La contraseña actual es incorrecta', 'PASSWORD_ACTUAL_INVALIDA'), 403
    elif usuario['id_rol'] not in ROLES_STAFF.values():
        return error_respuesta(
            'El administrador solo puede restablecer contraseñas del personal administrativo y de recepción',
            'PERMISOS_INSUFICIENTES',
        ), 403

    nuevo_hash = hash_password(datos['nueva_password'])
    if not actualizar_hash_password(usuario, nuevo_hash):
        return error_respuesta(
            'La cuenta cambió durante la operación. Volvé a intentar el cambio',
            'USUARIO_MODIFICADO',
        ), 409

    return {'mensaje': 'Contraseña actualizada correctamente'}, 200
