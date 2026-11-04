from datetime import time

from src.errores import error_respuesta
from src.utils.utils import (
    validar_fecha_iso_opcional,
    validar_id_positivo,
    validar_rango_fechas,
    validar_objeto_json,
)


def validar_hora_opcional(valor, nombre):
    if valor is None or not str(valor).strip():
        return None, None
    try:
        hora = time.fromisoformat(str(valor).strip())
    except ValueError:
        return None, error_respuesta(f'{nombre} debe tener formato HH:MM o HH:MM:SS', 'HORA_INVALIDA')
    if hora.tzinfo is not None:
        return None, error_respuesta(f'{nombre} no debe incluir zona horaria', 'HORA_INVALIDA')
    return hora.strftime('%H:%M:%S'), None


def _validar_fechas_turnos(parametros):
    fechas = {}
    for nombre in ('fecha_desde', 'fecha_hasta'):
        valor, error = validar_fecha_iso_opcional(parametros.get(nombre), nombre)
        if error:
            return None, error
        fechas[nombre] = valor

    error = validar_rango_fechas(fechas['fecha_desde'], fechas['fecha_hasta'])
    if error:
        return None, error
    return fechas, None


def validar_filtros_turnos_disponibles(parametros):
    filtros = {}
    for nombre in ('id_especialidad', 'id_medico', 'id_cobertura'):
        valor, error = validar_id_positivo(parametros.get(nombre), nombre)
        if error:
            return None, error
        filtros[nombre] = valor

    fechas, error = _validar_fechas_turnos(parametros)
    if error:
        return None, error
    filtros.update(fechas)

    for nombre in ('hora_desde', 'hora_hasta'):
        valor, error = validar_hora_opcional(parametros.get(nombre), nombre)
        if error:
            return None, error
        filtros[nombre] = valor

    if (
        filtros['hora_desde']
        and filtros['hora_hasta']
        and filtros['hora_desde'] > filtros['hora_hasta']
    ):
        return None, error_respuesta(
            'hora_desde no puede ser posterior a hora_hasta',
            'RANGO_HORARIO_INVALIDO',
        )
    return filtros, None


def validar_filtros_turnos(parametros):
    fechas, error = _validar_fechas_turnos(parametros)
    if error:
        return None, error

    filtros = dict(fechas)
    for nombre in ('id_medico', 'id_estado'):
        valor, error = validar_id_positivo(parametros.get(nombre), nombre)
        if error:
            return None, error
        filtros[nombre] = valor
    return filtros, None


def validar_cancelacion_turno(datos):
    error_json = validar_objeto_json(datos)
    if error_json:
        return None, error_json

    id_turno, error = validar_id_positivo(datos.get('id_turno'), 'id_turno')
    if error:
        return None, (error, 400)
    if id_turno is None:
        return None, (
            error_respuesta('id_turno es obligatorio', 'ID_TURNO_REQUERIDO'),
            400,
        )
    return id_turno, None