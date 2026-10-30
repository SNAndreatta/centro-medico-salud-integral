from datetime import date

from src.errores import error_respuesta
from src.repositories.estadisticas_repositories import listar_sala_espera, obtener_turnos_por_estado, obtener_ocupacion_consultorios
from src.utils.roles import MEDICO

def _fecha_opcional(valor, nombre):
    if valor is None or not str(valor).strip():
        return None, None
    try:
        fecha = date.fromisoformat(str(valor).strip())
    except ValueError:
        return None, error_respuesta(f'{nombre} debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA')
    if fecha.isoformat() != str(valor).strip():
        return None, error_respuesta(f'{nombre} debe tener formato YYYY-MMM-DD', 'FECHA_INVALIDA')
    return fecha.isoformat(), None


def _validar_fechas(parametros):
    fecha_desde, error = _fecha_opcional(parametros.get('fecha_desde'), 'fecha_desde')
    if error:
        return None, None, error

    fecha_hasta, error = _fecha_opcional(parametros.get('fecha_hasta'), 'fecha_hasta')
    if error:
        return None, None, error

    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        return None, None, error_respuesta(
            'fecha_desde no puede ser posterior a fecha_hasta',
            'RANGO_FECHAS_INVALIDO',
        )
    return fecha_desde, fecha_hasta, None

def obtener_sala_espera(usuario_actual):
    id_usuario_medico = (
        usuario_actual['id_usuario']
        if usuario_actual['id_rol'] == MEDICO
        else None
    )
    pacientes = listar_sala_espera(id_usuario_medico)
    return {'sala_espera': pacientes, 'total': len(pacientes)}, 200

def obtener_estadisticas_turnos(parametros):
    fecha_desde, fecha_hasta, error = _validar_fechas(parametros)
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
    fecha_desde, fecha_hasta, error = _validar_fechas(parametros)
    if error:
        return error,400

    ocupacion = obtener_ocupacion_consultorios(fecha_desde, fecha_hasta)
    return {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'consultorios': ocupacion,
    }, 200