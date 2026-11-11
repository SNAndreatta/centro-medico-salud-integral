from src.errores import error_respuesta
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA
from src.validators.common import texto_obligatorio, validar_correo_electronico


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