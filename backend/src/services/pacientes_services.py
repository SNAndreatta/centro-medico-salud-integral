from src.repositories.pacientes_repositories import (
    buscar_pacientes,
    obtener_paciente_por_usuario,
    obtener_usuario_por_paciente,
    obtener_paciente_por_id,
    actualizar_datos_paciente,
    obtener_turnos_de_paciente
)
from src.errores import error_respuesta
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA
from src.validators.pacientes_validators import (
    validar_filtros_pacientes,
    validar_datos_actualizacion_paciente
)

from datetime import date

def obtener_id_paciente_por_usuario(id_usuario):
    return obtener_paciente_por_usuario(id_usuario)

def obtener_id_usuario_por_paciente(id_paciente):
    return obtener_usuario_por_paciente(id_paciente)

def obtener_paciente(id_paciente):
    paciente = obtener_paciente_por_id(id_paciente)

    if paciente is None:
        return error_respuesta(
            'El paciente indicado no existe.',
            'PACIENTE_INEXISTENTE',
        ), 404

    return {'paciente': paciente}, 200

def modificar_paciente(id_paciente, datos, usuario_actual):
    if usuario_actual['id_rol'] not in (ADMINISTRADOR, RECEPCIONISTA):
        id_propio = obtener_id_paciente_por_usuario(usuario_actual['id_usuario'])
        if id_propio is None or int(id_propio) != id_paciente:
            return error_respuesta(
                'No tenés permiso para modificar este paciente',
                'PERMISOS_INSUFICIENTES',
            ), 403

    datos_validados, error = validar_datos_actualizacion_paciente(datos)
    if error:
        return error, 400

    error = actualizar_datos_paciente(id_paciente, datos_validados)
    if error == 'PACIENTE_NO_EXISTE':
        return error_respuesta(
            'El paciente indicado no existe.',
            'PACIENTE_INEXISTENTE',
        ), 404
    if error == 'EMAIL_DUPLICADO':
        return error_respuesta(
            'Ese correo ya se encuentra en uso.',
            'EMAIL_DUPLICADO',
        ), 400
    if error == 'COBERTURA_INEXISTENTE':
        return error_respuesta(
            'La cobertura indicada no existe.',
            'COBERTURA_INEXISTENTE',
        ), 400

    return {'paciente': obtener_paciente_por_id(id_paciente)}, 200

def listar_turnos_paciente(id_paciente):
    turnos, error = obtener_turnos_de_paciente(id_paciente)
    if error == 'PACIENTE_NO_EXISTE':
        return error_respuesta(
            'El paciente indicado no existe',
            'PACIENTE_INEXISTENTE',
        ), 404

    proximos = []
    historial = []

    for turno in turnos:
        if isinstance(turno.get('fecha'), date):
            turno['fecha'] = turno['fecha'].isoformat()
        if turno.get('hora') is not None:
            turno['hora'] = (turno['hora'])

        estado = (turno.get('estado') or '').lower()
        if estado == 'reservado':
            proximos.append(turno)
        else:
            historial.append(turno)

    proximos.reverse()

    return {
        'turnos': turnos,
        'proximos': proximos,
        'historial': historial,
    }, 200

def filtrar_pacientes(parametros):
    filtros, error = validar_filtros_pacientes(parametros)
    if error:
        return error, 400

    return {'pacientes': buscar_pacientes(**filtros)}, 200