from src.repositories.pacientes_repositories import buscar_pacientes
from src.validators.pacientes_validators import validar_filtros_pacientes


def filtrar_pacientes(parametros):
    filtros, error = validar_filtros_pacientes(parametros)
    if error:
        return error, 400

    return {'pacientes': buscar_pacientes(**filtros)}, 200