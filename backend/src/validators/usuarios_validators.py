from src.errores import error_respuesta
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA
from src.validators.common import texto_obligatorio, validar_correo_electronico, validar_objeto_json


CAMPOS_USUARIO_STAFF = {
    'nombre',
    'apellido',
    'dni',
    'correo_electronico',
    'password',
    'id_rol',
}


def validar_filtro_rol(rol):
    if rol not in (None, 'admin', 'recepcionista'):
        return error_respuesta(
            'El filtro rol debe ser admin o recepcionista',
            'FILTRO_INVALIDO',
        )
    return None


def validar_cambio_password(datos, es_cambio_propio):
    error_json = validar_objeto_json(datos)
    if error_json:
        return error_json

    if set(datos) - {'nueva_password', 'password_actual'}:
        return error_respuesta(
            'El cuerpo solo admite nueva_password y password_actual',
            'CUERPO_INVALIDO',
        ), 400

    nueva_password = datos.get('nueva_password')
    if not texto_obligatorio(nueva_password) or not 8 <= len(nueva_password) <= 128:
        return error_respuesta(
            'nueva_password debe tener entre 8 y 128 caracteres',
            'PASSWORD_INVALIDA',
        ), 400

    if (es_cambio_propio or 'password_actual' in datos) and not texto_obligatorio(datos.get('password_actual')):
        return error_respuesta(
            'password_actual debe ser texto y es obligatoria para un cambio propio',
            'PASSWORD_ACTUAL_REQUERIDA',
        ), 400
    return None


def validar_datos_usuario_staff(datos):
    if set(datos) != CAMPOS_USUARIO_STAFF:
        return None, error_respuesta(
            'El cuerpo debe incluir nombre, apellido, dni, correo_electronico, password e id_rol',
            'CUERPO_INVALIDO',
        )

    texto = ('nombre', 'apellido', 'dni', 'correo_electronico', 'password')
    if any(not texto_obligatorio(datos[campo]) for campo in texto):
        return None, error_respuesta(
            'Todos los campos de texto son obligatorios',
            'DATOS_INVALIDOS',
        )

    limites = {
        'nombre': 100,
        'apellido': 100,
        'dni': 20,
        'correo_electronico': 150,
    }
    if any(len(datos[campo].strip()) > limite for campo, limite in limites.items()):
        return None, error_respuesta(
            'Uno o más campos exceden la longitud permitida',
            'DATOS_INVALIDOS',
        )

    correo, error = validar_correo_electronico(datos['correo_electronico'])
    if error:
        return None, error

    id_rol = datos['id_rol']
    if isinstance(id_rol, bool) or not isinstance(id_rol, int) or id_rol not in (
        ADMINISTRADOR,
        RECEPCIONISTA,
    ):
        return None, error_respuesta(
            'id_rol debe ser 1 (Administrador) o 2 (Recepcionista)',
            'ROL_INVALIDO',
        )

    return {
        'id_rol': id_rol,
        'nombre': datos['nombre'].strip(),
        'apellido': datos['apellido'].strip(),
        'dni': datos['dni'].strip(),
        'correo_electronico': correo,
        'password': datos['password'],
    }, None
