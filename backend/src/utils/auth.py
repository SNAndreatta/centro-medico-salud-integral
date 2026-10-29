from functools import wraps

import jwt
from flask import g, request

from src.config import Config
from src.errores import error_respuesta


def token_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        authorization = request.headers.get('Authorization', '')
        scheme, separator, token = authorization.partition(' ')
        if scheme.lower() != 'bearer' or not separator or not token.strip():
            return error_respuesta(
                'Se requiere un token Bearer válido',
                'TOKEN_REQUERIDO',
            ), 401

        try:
            claims = jwt.decode(
                token.strip(),
                Config.SECRET_KEY,
                algorithms=['HS256'],
                options={'require': ['exp', 'iat', 'sub', 'id_rol']},
            )
            current_user = {
                'id_usuario': int(claims['sub']),
                'id_rol': int(claims['id_rol']),
            }
            if current_user['id_usuario'] <= 0 or current_user['id_rol'] <= 0:
                raise ValueError('Invalid token identity')
        except (jwt.InvalidTokenError, TypeError, ValueError, KeyError):
            return error_respuesta(
                'El token es inválido o expiró',
                'TOKEN_INVALIDO',
            ), 401

        g.current_user = current_user
        return view(*args, **kwargs)

    return wrapped


def roles_required(*role_ids):
    allowed_roles = {int(role_id) for role_id in role_ids}

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            current_user = getattr(g, 'current_user', None)
            if current_user is None:
                return error_respuesta(
                    'Se requiere autenticación',
                    'TOKEN_REQUERIDO',
                ), 401
            if current_user['id_rol'] not in allowed_roles:
                return error_respuesta(
                    'No tiene permisos para acceder a este recurso',
                    'PERMISOS_INSUFICIENTES',
                ), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator