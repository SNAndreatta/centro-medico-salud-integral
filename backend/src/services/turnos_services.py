from src.repositories.turnos_repositories import buscar_turnos, buscar_turnos_disponibles
from src.utils.roles import PACIENTE, MEDICO
from src.validators.turnos_validators import (
    validar_filtros_turnos,
    validar_filtros_turnos_disponibles,
)


def filtrar_turnos_disponibles(parametros):
    filtros, error = validar_filtros_turnos_disponibles(parametros)
    if error:
        return error, 400
    return {'turnos': buscar_turnos_disponibles(**filtros)}, 200


def filtrar_turnos(parametros, usuario_actual):
    filtros, error = validar_filtros_turnos(parametros)
    if error:
        return error, 400

    id_usuario_paciente = None
    id_usuario_medico = None
    if usuario_actual['id_rol'] == PACIENTE:
        id_usuario_paciente = usuario_actual['id_usuario']
    elif usuario_actual['id_rol'] == MEDICO:
        id_usuario_medico = usuario_actual['id_usuario']

    turnos = buscar_turnos(
        **filtros,
        id_usuario_paciente=id_usuario_paciente,
        id_usuario_medico=id_usuario_medico,
    )
    return {'turnos': turnos}, 200