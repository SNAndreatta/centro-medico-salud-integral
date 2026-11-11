from src.repositories.pacientes_repositories import (
    buscar_pacientes,
    obtener_paciente_por_usuario,
    obtener_usuario_por_paciente,
)
from src.validators.pacientes_validators import validar_filtros_pacientes


def obtener_id_paciente_por_usuario(id_usuario):
    return obtener_paciente_por_usuario(id_usuario)


def obtener_id_usuario_por_paciente(id_paciente):
    return obtener_usuario_por_paciente(id_paciente)


def filtrar_pacientes(parametros):
    filtros, error = validar_filtros_pacientes(parametros)
    if error:
        return error, 400

    return {'pacientes': buscar_pacientes(**filtros)}, 200