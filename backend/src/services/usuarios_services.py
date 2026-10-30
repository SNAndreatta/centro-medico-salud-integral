import re

from werkzeug.security import generate_password_hash

from src.repositories.usuarios_repositories import (
    guardar_usuario_staff,
    obtener_usuarios_staff,
)
from src.errores import error_respuesta
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA

ROLES_STAFF = {'admin': ADMINISTRADOR, 'recepcionista': RECEPCIONISTA}
CAMPOS_USUARIO_STAFF = {
    'nombre',
    'apellido',
    'dni',
    'correo_electronico',
    'password',
    'id_rol',
}


def listar_usuarios_staff(rol=None):
    id_rol = ROLES_STAFF.get(rol) if rol is not None else None
    return obtener_usuarios_staff(id_rol)


def crear_usuario_staff(datos):
    if set(datos) != CAMPOS_USUARIO_STAFF:
        return error_respuesta(
            'El cuerpo debe incluir nombre, apellido, dni, correo_electronico, password e id_rol',
            'CUERPO_INVALIDO',
        ), 400

    texto = ('nombre', 'apellido', 'dni', 'correo_electronico', 'password')
    if any(not isinstance(datos[campo], str) or not datos[campo].strip() for campo in texto):
        return error_respuesta(
            'Todos los campos de texto son obligatorios',
            'DATOS_INVALIDOS',
        ), 400

    limites = {
        'nombre': 100,
        'apellido': 100,
        'dni': 20,
        'correo_electronico': 150,
    }
    if any(len(datos[campo].strip()) > limite for campo, limite in limites.items()):
        return error_respuesta(
            'Uno o más campos exceden la longitud permitida',
            'DATOS_INVALIDOS',
        ), 400

    correo = datos['correo_electronico'].strip().lower()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', correo):
        return error_respuesta('El correo electrónico no es válido', 'EMAIL_INVALIDO'), 400

    id_rol = datos['id_rol']
    if isinstance(id_rol, bool) or not isinstance(id_rol, int) or id_rol not in (ADMINISTRADOR, RECEPCIONISTA):
        return error_respuesta(
            'id_rol debe ser 1 (Administrador) o 2 (Recepcionista)',
            'ROL_INVALIDO',
        ), 400

    usuario = {
        'id_rol': id_rol,
        'nombre': datos['nombre'].strip(),
        'apellido': datos['apellido'].strip(),
        'dni': datos['dni'].strip(),
        'correo_electronico': correo,
        'contrasenia': generate_password_hash(datos['password']),
    }
    usuario_guardado = guardar_usuario_staff(usuario)
    if usuario_guardado is None:
        return error_respuesta(
            'Ya existe un usuario con ese correo electrónico o DNI',
            'USUARIO_DUPLICADO',
        ), 400

    return {'usuario': usuario_guardado}, 201