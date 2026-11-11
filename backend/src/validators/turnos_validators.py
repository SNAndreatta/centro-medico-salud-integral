from src.errores import error_respuesta
from src.validators.common import (
    validar_fecha_iso_opcional,
    validar_hora_opcional,
    validar_id_positivo,
    validar_objeto_json,
    validar_rango_fechas,
)


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


def validar_checkin_turno(datos):
    error_json = validar_objeto_json(datos)
    if error_json:
        return None, error_json

    token = datos.get('token')
    if not isinstance(token, str) or not token.strip():
        return None, (
            error_respuesta('token es obligatorio', 'TOKEN_REQUERIDO'),
            400,
        )
    return token.strip(), None


def validar_estado_turno(datos):
    error_json = validar_objeto_json(datos)
    if error_json:
        return None, error_json

    id_estado = datos.get('id_estado')
    if type(id_estado) is not int or not 1 <= id_estado <= 2147483647:
        return None, (
            error_respuesta('id_estado debe ser un entero positivo válido', 'ESTADO_TURNO_INVALIDO'),
            400,
        )
    return id_estado, None


def validar_reserva_turno(datos, requiere_id_paciente):
    error_json = validar_objeto_json(datos)
    if error_json:
        return None, error_json

    if not requiere_id_paciente:
        return None, None

    id_paciente = datos.get('id_paciente')
    if id_paciente is None:
        return None, (
            error_respuesta('id_paciente es obligatorio', 'ID_PACIENTE_REQUERIDO'),
            400,
        )

    id_paciente, error = validar_id_positivo(id_paciente, 'id_paciente')
    if error:
        return None, (error, 400)
    return id_paciente, None
