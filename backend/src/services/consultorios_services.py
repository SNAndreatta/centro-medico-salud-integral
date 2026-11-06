from src.repositories.consultorios_repositories import (
    obtener_consultorios,
    guardar_consultorio,
    actualizar_consultorio,
    borrar_consultorio,
)
from src.errores import error_respuesta
from src.validators.consultorios_validators import validar_datos_consultorio

def listar_consultorios():
    consultorios = obtener_consultorios()
    return {'consultorios': consultorios}, 200

def crear_consultorio(datos):
    datos_validados, error = validar_datos_consultorio(datos)

    if error:
        return error, 400

    consultorio, error_codigo = guardar_consultorio(
        datos_validados['numero'],
        datos_validados['piso'],
    )

    if error_codigo == 'CONSULTORIO_DUPLICADO':
        return error_respuesta(
            'Ya existe un consultorio con el mismo numero y piso.', 
            'CONSULTORIO_DUPLICADO'
        ), 409
    
    if error_codigo:
        return error_respuesta(
            'Ocurrio un error al guardar el consultorio.', 
            'ERROR_INTERNO'
        ), 500

    return {'consultorio': consultorio}, 201

def modificar_consultorio(id_consultorio, datos):
    datos_validados, error = validar_datos_consultorio(datos)

    if error:
        return error, 400

    resultado, error_codigo = actualizar_consultorio(
        id_consultorio,
        datos_validados['numero'],
        datos_validados['piso'],
    )

    if error_codigo == 'NO_EXISTE':
        return error_respuesta(
            'El consultorio indicado no existe.', 
            'CONSULTORIO_INEXISTENTE'
        ), 404

    if error_codigo == 'YA_EXISTE':
        return error_respuesta(
            'Ya existe otro consultorio con ese numero y piso.', 
            'CONSULTORIO_DUPLICADO'
        ), 409

    if error_codigo:
        return error_respuesta(
            'Ocurrio un error al actualizar el consultorio.', 
            'ERROR_INTERNO'
        ), 500

    return {'consultorio': resultado}, 200

def eliminar_consultorio(id_consultorio):
    _, error_codigo = borrar_consultorio(id_consultorio)

    if error_codigo == 'NO_EXISTE':
        return error_respuesta(
            'El consultorio inidicado no existe', 
            'CONSULTORIO_INEXISTENTE'
        ), 404

    if error_codigo == 'EN_USO':
        return error_respuesta(
            'No se puede eliminar: el consultorio tiene agendas asociadas.', 
            'CONSULTORIO_EN_USO'
        ), 409

    if error_codigo:
            return error_respuesta(
                'Ocurrio un error al eliminar el consultorio.', 
                'ERROR_INTERNO'
            ), 500

    return {'mensaje': 'Consultorio eliminado exitosamente.'}, 200