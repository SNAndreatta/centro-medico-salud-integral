from src.repositories.estadisticas_repositories import listar_sala_espera, obtener_turnos_por_estado, obtener_ocupacion_consultorios
from src.utils.roles import MEDICO
from src.validators.estadisticas_validators import validar_fechas_estadisticas

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
        return error,400

    ocupacion = obtener_ocupacion_consultorios(fecha_desde, fecha_hasta)
    return {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'consultorios': ocupacion,
    }, 200