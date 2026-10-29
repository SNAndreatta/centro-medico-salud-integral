from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import check_password_hash

from src.config import Config
from src.repositories.auth_repository import obtener_usuario_por_email


def crear_access_token(usuario):
    ahora = datetime.now(timezone.utc)
    payload = {
        'sub': str(usuario['id_usuario']),
        'id_rol': int(usuario['id_rol']),
        'iat': ahora,
        'exp': ahora + timedelta(minutes=Config.JWT_ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')


def autenticar_usuario(correo_electronico, password):
    usuario = obtener_usuario_por_email(correo_electronico.strip())
    if usuario is None or not check_password_hash(usuario['contrasenia'], password):
        return None

    perfil = {
        'id_usuario': int(usuario['id_usuario']),
        'nombre': usuario['nombre'],
        'apellido': usuario['apellido'],
        'id_rol': int(usuario['id_rol']),
    }
    return {
        'access_token': crear_access_token(perfil),
        'usuario': perfil,
    }