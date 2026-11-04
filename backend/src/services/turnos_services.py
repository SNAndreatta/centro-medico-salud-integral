from src.repositories.turnos_repositories import (
    buscar_turnos,
    buscar_turnos_disponibles,
    insertar_turnos_disponibles,
    cancelar_turno as cancelar_turno_repositorio,
)
from src.errores import error_respuesta
from src.utils.roles import PACIENTE, MEDICO
from src.validators.turnos_validators import (
    validar_filtros_turnos,
    validar_filtros_turnos_disponibles,
)
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from src.repositories.agendas_repositories import buscar_agendas


def cancelar_turno(id_turno, usuario_actual):
    resultado = cancelar_turno_repositorio(
        id_turno,
        usuario_actual['id_usuario'],
        usuario_actual['id_rol'],
    )
    if resultado is None:
        return error_respuesta('El turno no existe', 'TURNO_INEXISTENTE'), 404
    if resultado['resultado'] == 'NO_AUTORIZADO':
        return error_respuesta(
            'El turno no pertenece al paciente autenticado',
            'TURNO_NO_AUTORIZADO',
        ), 403
    if resultado['resultado'] == 'NO_CANCELABLE':
        return error_respuesta(
            'El turno no se encuentra reservado',
            'TURNO_NO_CANCELABLE',
        ), 409
    return {
        'mensaje': 'Turno cancelado correctamente',
        'id_turno': resultado['id_turno'],
        'estado': 'cancelado',
        'disponible': True,
    }, 200

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

def _obtener_periodo_proximo_mes():
    hoy = datetime.now(ZoneInfo('America/Argentina/Buenos_Aires')).date()

    fecha_desde = (hoy.replace(day=28) + timedelta(days=4)).replace(day=1)
    primer_dia_mes_siguiente = (fecha_desde.replace(day=28) + timedelta(days=4)).replace(day=1)

    fecha_hasta = primer_dia_mes_siguiente - timedelta(days=1)

    return fecha_desde, fecha_hasta

def generar_disponibilidad():
    fecha_desde, fecha_hasta = _obtener_periodo_proximo_mes()

    agendas = buscar_agendas()
    turnos_a_generar = []
    agendas_procesadas = 0

    for agenda in agendas:
        inicio_agenda = date.fromisoformat(agenda['fecha_inicio'])
        fin_agenda = date.fromisoformat(agenda['fecha_hasta'])
        inicio_periodo = max(fecha_desde, inicio_agenda)
        fin_periodo = min(fecha_hasta, fin_agenda)

        if inicio_periodo > fin_periodo:
            continue

        agendas_procesadas += 1
        duracion_turno = agenda['duracion_turno']

        for dia in agenda['dias']:
            dia_semana = dia['dia_semana']

            hora_inicio = time.fromisoformat(dia['horario_inicio_jornada'])
            hora_fin = time.fromisoformat(dia['horario_final_jornada'])

            fecha_actual = inicio_periodo

            while fecha_actual <= fin_periodo:
                if fecha_actual.isoweekday() == dia_semana:
                    inicio_turno = datetime.combine(fecha_actual, hora_inicio)

                    fin_jornada = datetime.combine(fecha_actual, hora_fin)
                    while(inicio_turno + timedelta(minutes=duracion_turno) <= fin_jornada):
                        turnos_a_generar.append({
                            'id_agenda': agenda['id_agenda'],
                            'fecha_horario_inicial': inicio_turno,
                        })

                        inicio_turno += timedelta(minutes=duracion_turno)
                fecha_actual += timedelta(days=1)

    cantidad_generada = insertar_turnos_disponibles(turnos_a_generar)

    return{
        'mensaje': 'Disponibilidad generada correctamente',
        'periodo': {
            'fecha_desde': fecha_desde.isoformat(),
            'fecha_hasta': fecha_hasta.isoformat(),
        },
        'agendas_procesadas': agendas_procesadas,
        'turnos_generados': cantidad_generada,
        'turnos_omitidos': len(turnos_a_generar) - cantidad_generada,
    }, 200
