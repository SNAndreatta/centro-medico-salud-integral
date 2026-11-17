from src.repositories.estadisticas_repositories import (
    listar_sala_espera,
    obtener_ausentismo_especialidades,
    obtener_ausentismo_medicos,
    obtener_ocupacion_consultorios,
    obtener_tiempos_espera_especialidades,
    obtener_tiempos_espera_medicos,
    obtener_turnos_por_estado,
)
from src.repositories.turnos_repositories import buscar_turnos
from src.utils.roles import MEDICO
from src.validators.estadisticas_validators import validar_fechas_estadisticas


def _porcentaje(parcial, total):
    return round(parcial * 100 / total, 1) if total else 0.0


def obtener_sala_espera(usuario_actual):
    id_usuario_medico = (
        usuario_actual['id_usuario']
        if usuario_actual['id_rol'] == MEDICO
        else None
    )
    pacientes = listar_sala_espera(id_usuario_medico)
    return {'sala_espera': pacientes, 'total': len(pacientes)}, 200


def obtener_estadisticas_turnos(parametros):
    fecha_desde, fecha_hasta, error = validar_fechas_estadisticas(parametros)
    if error:
        return error, 400

    estadisticas = obtener_turnos_por_estado(fecha_desde, fecha_hasta)
    total = sum(item['cantidad'] for item in estadisticas)
    return {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_turnos': total,
        'turnos_por_estado': estadisticas,
    }, 200


def obtener_estadisticas_ocupacion(parametros):
    fecha_desde, fecha_hasta, error = validar_fechas_estadisticas(parametros)
    if error:
        return error, 400

    ocupacion = obtener_ocupacion_consultorios(fecha_desde, fecha_hasta)
    return {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'consultorios': ocupacion,
    }, 200


def obtener_estadisticas_ausentismo(parametros):
    fecha_desde, fecha_hasta, error = validar_fechas_estadisticas(parametros)
    if error:
        return error, 400

    conteos = {
        fila['estado'].lower(): fila['cantidad']
        for fila in obtener_turnos_por_estado(fecha_desde, fecha_hasta)
    }
    resumen = {
        'total': sum(conteos.values()),
        'atendidos': conteos.get('atendido', 0),
        'ausentes': conteos.get('ausente', 0),
        'cancelados': conteos.get('cancelado', 0),
    }

    medicos = [
        {**fila, 'porcentaje': _porcentaje(fila['ausentes'], fila['considerados'])}
        for fila in obtener_ausentismo_medicos(fecha_desde, fecha_hasta)
    ]
    medicos.sort(key=lambda fila: (-fila['porcentaje'], fila['nombre'], fila['apellido']))

    especialidades = [
        {**fila, 'porcentaje': _porcentaje(fila['ausentes'], fila['considerados'])}
        for fila in obtener_ausentismo_especialidades(fecha_desde, fecha_hasta)
    ]
    especialidades.sort(key=lambda fila: (-fila['porcentaje'], fila['nombre']))

    return {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'resumen': resumen,
        'medicos': medicos,
        'especialidades': especialidades,
    }, 200


def obtener_estadisticas_tiempo_espera(parametros):
    fecha_desde, fecha_hasta, error = validar_fechas_estadisticas(parametros)
    if error:
        return error, 400

    medicos = [
        {
            **fila,
            'espera': round(fila['minutos_totales'] / fila['turnos']) if fila['turnos'] else 0,
        }
        for fila in obtener_tiempos_espera_medicos(fecha_desde, fecha_hasta)
    ]
    medicos.sort(key=lambda fila: (-fila['espera'], fila['nombre'], fila['apellido']))

    especialidades = [
        {
            **fila,
            'espera': round(fila['minutos_totales'] / fila['turnos']) if fila['turnos'] else 0,
        }
        for fila in obtener_tiempos_espera_especialidades(fecha_desde, fecha_hasta)
    ]
    especialidades.sort(key=lambda fila: (-fila['espera'], fila['nombre']))

    return {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'turnos_considerados': sum(fila['turnos'] for fila in medicos),
        'medicos': medicos,
        'especialidades': especialidades,
    }, 200


def obtener_estadisticas_turnos_especialidad(parametros):
    fecha_desde, fecha_hasta, error = validar_fechas_estadisticas(parametros)
    if error:
        return error, 400

    turnos = buscar_turnos(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    agrupados = {}
    for turno in turnos:
        medico = turno.get('medico') or {}
        nombre = medico.get('especialidad') or 'Sin especialidad'
        grupo = agrupados.setdefault(nombre, {
            'id_especialidad': medico.get('id_especialidad'),
            'nombre': nombre,
            'total_turnos': 0,
            'turnos': [],
        })
        grupo['total_turnos'] += 1
        grupo['turnos'].append(turno)

    return {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_turnos': len(turnos),
        'especialidades': list(agrupados.values()),
    }, 200
