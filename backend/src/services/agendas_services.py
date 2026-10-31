from src.repositories.agendas_repositories import buscar_agendas
from src.utils.roles import MEDICO
from src.validators.agendas_validators import validar_filtros_agendas


def filtrar_agendas(parametros, usuario_actual):
    filtros, error = validar_filtros_agendas(parametros)
    if error:
        return error, 400

    id_usuario_medico = (
        usuario_actual['id_usuario']
        if usuario_actual['id_rol'] == MEDICO
        else None
    )

    agendas = buscar_agendas(
        **filtros,
        id_usuario_medico=id_usuario_medico,
    )
    return {'agendas': agendas}, 200