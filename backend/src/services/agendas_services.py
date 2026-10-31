from src.repositories.agendas_repositories import buscar_agendas, verificar_referencias_agenda, buscar_conflicto_agenda, guardar_agenda
from src.utils.roles import MEDICO
from src.validators.agendas_validators import validar_filtros_agendas, validar_datos_agenda
from src.errores import error_respuesta

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

def crear_agenda(datos):
    agenda, error = validar_datos_agenda(datos)

    if error:
        return error, 400

    referencias = verificar_referencias_agenda(
        agenda['id_medico'],
        agenda['id_consultorio'],
    )
    if not referencias['medico_existe']:
        return error_respuesta('El medico indicado no existe', 'MEDICO_INEXISTENTE'), 404

    if not referencias['consultorio_existe']:
        return error_respuesta('El consultorio indicado no existe', 'CONSULTORIO_INEXISTENTE'), 404

    conflicto = buscar_conflicto_agenda(agenda)

    if conflicto is not None:
        if conflicto['tipo'] == 'MEDICO':
            return error_respuesta('El medico ya tiene otra agenda en ese dia y horario', 'AGENDA_MEDICO_SUPERPUESTA'), 409

        return error_respuesta('El consultorio ya esta ocupado en ese dia y horario', 'AGENDA_CONSULTORIO_SUPERPUESTA'), 409

    id_agenda = guardar_agenda(agenda)

    agenda_creada = {
        'id_agenda': id_agenda,
        'id_medico': agenda['id_medico'],
        'id_consultorio': agenda['id_consultorio'],
        'duracion_turno': agenda['duracion_turno'],
        'fecha_inicio': agenda['fecha_inicio'],
        'fecha_hasta': agenda['fecha_hasta'],
        'dias': [
            {
                'dia_semana': dia['dia_semana'],
                'horario_inicio_jornada': dia['horario_inicio_jornada'],
                'horario_final_jornada': dia['horario_final_jornada'],
            }
            for dia in agenda['dias']
        ],
    }

    return {'agenda': agenda_creada}, 201
