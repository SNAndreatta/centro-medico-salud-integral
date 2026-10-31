from src.errores import error_respuesta
from src.utils.utils import validar_id_positivo


def _booleano_opcional(valor, nombre):
    if valor is None:
        return None, None
    normalizado = str(valor).strip().lower()
    if normalizado == 'true':
        return True, None
    if normalizado == 'false':
        return False, None
    return None, error_respuesta(f'{nombre} debe ser true o false', 'FILTRO_INVALIDO')


def validar_filtros_agendas(parametros):
    filtros = {}
    for nombre in ('id_medico', 'id_consultorio'):
        valor, error = validar_id_positivo(parametros.get(nombre), nombre)
        if error:
            return None, error
        filtros[nombre] = valor

    vigente, error = _booleano_opcional(parametros.get('vigente'), 'vigente')
    if error:
        return None, error
    filtros['vigente'] = vigente
    return filtros, None