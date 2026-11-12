from src.repositories.pacientes_repositories import (
    buscar_pacientes,
    obtener_paciente_por_usuario,
    obtener_usuario_por_paciente,
    obtener_paciente_por_id,
    actualizar_datos_paciente
)
from src.errores import error_respuesta
from src.validators.pacientes_validators import (
    validar_filtros_pacientes,
    validar_datos_actualizacion_paciente
)

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

def modificar_paciente(id_paciente, datos):
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

def filtrar_pacientes(parametros):
    filtros, error = validar_filtros_pacientes(parametros)
    if error:
        return error, 400

    return {'pacientes': buscar_pacientes(**filtros)}, 200