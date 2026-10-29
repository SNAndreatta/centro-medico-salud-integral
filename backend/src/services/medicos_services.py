from src.errores import error_respuesta
from src.repositories.medicos_repositories import buscar_medicos


def _id_positivo(valor, nombre):
    if valor is None:
        return None, None
    try:
        id_numerico = int(valor)
    except (TypeError, ValueError):
        return None, error_respuesta(f'{nombre} debe ser un entero positivo', 'FILTRO_INVALIDO')
    if id_numerico <= 0 or str(id_numerico) != str(valor).strip():
        return None, error_respuesta(f'{nombre} debe ser un entero positivo', 'FILTRO_INVALIDO')
    return id_numerico, None


def filtrar_medicos(parametros):
    id_especialidad, error = _id_positivo(parametros.get('id_especialidad'), 'id_especialidad')
    if error:
        return error, 400
    id_cobertura, error = _id_positivo(parametros.get('id_cobertura'), 'id_cobertura')
    if error:
        return error, 400

    nombre = parametros.get('nombre', '').strip()
    if len(nombre) > 100:
        return error_respuesta('nombre no puede superar 100 caracteres', 'FILTRO_INVALIDO'), 400

    return {'medicos': buscar_medicos(id_especialidad, id_cobertura, nombre or None)}, 200