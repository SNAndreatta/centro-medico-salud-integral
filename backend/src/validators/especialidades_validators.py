from src.errores import error_respuesta
from src.utils.utils import texto_obligatorio

CAMPOS_ESPECIALIDAD = {'nombre'}
LONGITUD_MAXIMA_NOMBRE = 100


def validar_datos_especialidad(datos):
    if not isinstance(datos, dict) or set(datos) != CAMPOS_ESPECIALIDAD:
        return None, error_respuesta(
            'El cuerpo debe incluir únicamente el campo nombre',
            'CUERPO_INVALIDO',
        )

    if not texto_obligatorio(datos['nombre']):
        return None, error_respuesta(
            'El nombre es obligatorio',
            'DATOS_INVALIDOS',
        )

    nombre = datos['nombre'].strip()
    if len(nombre) > LONGITUD_MAXIMA_NOMBRE:
        return None, error_respuesta(
            f'El nombre no puede superar {LONGITUD_MAXIMA_NOMBRE} caracteres',
            'DATOS_INVALIDOS',
        )

    return nombre, None