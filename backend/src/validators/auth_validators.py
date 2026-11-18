from src.errores import error_respuesta
from src.validators.common import texto_obligatorio


def validar_credenciales_login(datos):
    correo_electronico = datos.get('correo_electronico')
    password = datos.get('password')
    if not texto_obligatorio(correo_electronico) or not isinstance(password, str) or not password:
        return None, None, error_respuesta(
            'correo_electronico y password son obligatorios',
            'CREDENCIALES_REQUERIDAS',
        )
    return correo_electronico.strip(), password, None