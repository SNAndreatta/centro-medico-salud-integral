from src.errores import error_respuesta
from src.repositories.pacientes_repositories import buscar_pacientes


def filtrar_pacientes(parametros):
    dni = parametros.get('dni', '').strip()
    apellido = parametros.get('apellido', '').strip()
    if len(dni) > 20 or len(apellido) > 100:
        return error_respuesta('Los filtros exceden la longitud permitida', 'FILTRO_INVALIDO'), 400

    return {'pacientes': buscar_pacientes(dni or None, apellido or None)}, 200