from werkzeug.security import generate_password_hash

from src.errores import error_respuesta
from src.repositories.medicos_repositories import (
    buscar_medicos,
    desvincular_cobertura_medico,
    guardar_medico,
    obtener_coberturas_de_medico,
    obtener_medico_por_id,
    vincular_cobertura_medico,
)
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


def obtener_medico(id_medico):
    medico = obtener_medico_por_id(id_medico)
    if medico is None:
        return error_respuesta(
            'El médico indicado no existe',
            'MEDICO_INEXISTENTE',
        ), 404

    return {'medico': medico}, 200


def listar_coberturas_medico(id_medico):
    coberturas, error = obtener_coberturas_de_medico(id_medico)
    if error == 'MEDICO_NO_EXISTE':
        return error_respuesta(
            'El médico indicado no existe',
            'MEDICO_INEXISTENTE',
        ), 404

    return {'coberturas': coberturas}, 200


def agregar_cobertura_medico(id_medico, id_cobertura):
    vinculo, error = vincular_cobertura_medico(id_medico, id_cobertura)
    if error == 'MEDICO_NO_EXISTE':
        return error_respuesta(
            'El médico indicado no existe',
            'MEDICO_INEXISTENTE',
        ), 404
    if error == 'COBERTURA_NO_EXISTE':
        return error_respuesta(
            'La cobertura indicada no existe',
            'COBERTURA_INEXISTENTE',
        ), 404
    if error == 'VINCULO_EXISTENTE':
        return error_respuesta(
            'El médico ya está vinculado a esta cobertura',
            'COBERTURA_MEDICO_DUPLICADA',
        ), 409
    if error is not None:
        return error_respuesta(
            'No se pudo vincular la cobertura al médico',
            'ERROR_VINCULACION_COBERTURA',
        ), 500

    return {'vinculo': vinculo}, 201


def quitar_cobertura_medico(id_medico, id_cobertura):
    error = desvincular_cobertura_medico(id_medico, id_cobertura)
    if error == 'MEDICO_NO_EXISTE':
        return error_respuesta(
            'El médico indicado no existe',
            'MEDICO_INEXISTENTE',
        ), 404
    if error == 'COBERTURA_NO_EXISTE':
        return error_respuesta(
            'La cobertura indicada no existe',
            'COBERTURA_INEXISTENTE',
        ), 404
    if error == 'VINCULO_NO_EXISTE':
        return error_respuesta(
            'El médico no está vinculado a esta cobertura',
            'COBERTURA_MEDICO_INEXISTENTE',
        ), 404
    if error is not None:
        return error_respuesta(
            'No se pudo desvincular la cobertura del médico',
            'ERROR_DESVINCULACION_COBERTURA',
        ), 500

    return {'mensaje': 'Cobertura desvinculada del médico'}, 200