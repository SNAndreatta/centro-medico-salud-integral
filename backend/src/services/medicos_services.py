from src.repositories.medicos_repositories import buscar_medicos
from src.validators.medicos_validators import validar_filtros_medicos


def filtrar_medicos(parametros):
    filtros, error = validar_filtros_medicos(parametros)
    if error:
        return error, 400

    return {'medicos': buscar_medicos(**filtros)}, 200