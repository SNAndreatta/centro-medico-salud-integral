from functools import wraps

from flask import current_app

from src.errores import error_respuesta


def handle_unexpected_errors(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        try:
            return view(*args, **kwargs)
        except Exception:
            current_app.logger.exception('Unhandled error while processing API request')
            return error_respuesta(
                'Error interno del servidor',
                'ERROR_INTERNO',
            ), 500

    return wrapped