from datetime import date

from src.errores import error_respuesta
from src.repositories.turnos_repositories import buscar_turnos
from src.utils.roles import PACIENTE, MEDICO

def _id_positivo(valor, nombre):
    if valor is None:
        return None, None
    try:
        id_numerico = int(valor)
    except (TypeError, ValueError):
        return None, error_respuesta(f'{nombre} debe ser un entero positivo', 'FILTRO_INVALIDO')
    if id_numerico <= 0 or str(id_numero) != str(valor).strip():
        return None, error_respuesta(f'{nombre} debe ser un entero positivo', 'FILTRO_INVALIDO')
    return id_numerico, None

def _fecha_opcional(valor, nombre):
    if valor is None or not str(valor).strip():
        return None, None
    try:
        fecha = date.fromisoformat(str(valor).strip())
    except ValueError:
        return None, error_respuesta(f'{nombre} debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA')
    if fecha.isoformat() != str(valor).strip():
        return None, error_respuesta(f'{nombre} debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA')
    return fecha.isoformat(), None

def filtrar_turnos(parametros, usuario_actual):
    fecha_desde, error = _fecha_opcional(parametros.get('fecha_desde'), 'fecha_desde')
    if error:
        return error, 400

    fecha_hasta, error = _fecha_opcional(parametros.get('fecha_hasta'), 'fecha_hasta')
    if error:
        return error, 400

    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        return error_respuesta(
            'fecha_desde no puede ser posterior a fecha_hasta',
            'RANGO_FECHAS_INVALIDO',
        ), 400

    id_medico, error = _id_positivo(parametros.get('id_medico'), 'id_medico')
    if error:
        return error, 400

    id_estado, error = _id_positivo(parametros.get('id_estado'), 'id_estado')
    if error:
        return error, 400

    id_usuario_paciente = None
    id_usuario_medico = None
    if usuario_actual['id_rol'] == PACIENTE:
        id_usuario_paciente = usuario_actual['id_usuario']
    elif usuario_actual['id_rol'] == MEDICO:
        id_usuario_medico = usuario_actual['id_usuario']

    turnos = buscar_turnos(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        id_medico=id_medico,
        id_estado=id_estado,
        id_usuario_paciente=id_usuario_paciente,
        id_usuario_medico=id_usuario_medico,
    )
    return {'turnos': turnos}, 200