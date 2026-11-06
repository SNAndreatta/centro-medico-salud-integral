from werkzeug.security import generate_password_hash

from src.errores import error_respuesta
from src.repositories.medicos_repositories import buscar_medicos, guardar_medico
from src.validators.medicos_validators import (
    validar_datos_medico,
    validar_filtros_medicos,
)


def crear_medico(datos):
    medico, error = validar_datos_medico(datos)
    if error:
        return error, 400

    medico['contrasenia'] = generate_password_hash(medico.pop('password'))
    medico_guardado, error = guardar_medico(medico)
    if error == 'ESPECIALIDAD_INEXISTENTE':
        return error_respuesta(
            'La especialidad indicada no existe',
            'ESPECIALIDAD_INEXISTENTE',
        ), 400
    if error == 'USUARIO_DUPLICADO':
        return error_respuesta(
            'Ya existe un usuario con ese correo electrónico',
            'USUARIO_DUPLICADO',
        ), 400
    if error == 'MATRICULA_DUPLICADA':
        return error_respuesta(
            'Ya existe un médico con esa matrícula',
            'MATRICULA_DUPLICADA',
        ), 400
    if error == 'MEDICO_DUPLICADO':
        return error_respuesta(
            'Ya existe un usuario con ese correo electrónico o un médico con esa matrícula',
            'MEDICO_DUPLICADO',
        ), 400
    if error is not None:
        return error_respuesta(
            'No se pudo crear el médico',
            'ERROR_CREACION_MEDICO',
        ), 500

    return {'medico': medico_guardado}, 201


def filtrar_medicos(parametros):
    filtros, error = validar_filtros_medicos(parametros)
    if error:
        return error, 400

    return {'medicos': buscar_medicos(**filtros)}, 200