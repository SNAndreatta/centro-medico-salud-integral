from src.errores import error_respuesta
from src.utils.utils import validar_id_positivo


def validar_filtros_medicos(parametros):
    filtros = {}
    for nombre in ('id_especialidad', 'id_cobertura'):
        valor, error = validar_id_positivo(parametros.get(nombre), nombre)
        if error:
            return None, error
        filtros[nombre] = valor

    nombre = parametros.get('nombre', '')
    if not isinstance(nombre, str):
        return None, error_respuesta('nombre debe ser texto', 'FILTRO_INVALIDO')
    nombre = nombre.strip()
    if len(nombre) > 100:
        return None, error_respuesta('nombre no puede superar 100 caracteres', 'FILTRO_INVALIDO')
    filtros['nombre'] = nombre or None
    return filtros, None