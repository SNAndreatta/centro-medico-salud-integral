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

    consultorio, _ = guardar_consultorio(
        datos_validados['numero'],
        datos_validados['piso'],
    )
    return {'consultorio': consultorio}, 201

def modificar_consultorio(id_consultorio, datos):
    datos_validados, error = validar_datos_consultorio(datos)
    if error:
        return error, 400

    resultado, error = actualizar_consultorio(
        id_consultorio,
        datos_validados['numero'],
        datos_validados['piso'],
    )
    if error == 'NO_EXISTE':
        return error_respuesta('El consultorio indicado no esxiste', 'CONSULTORIO_INEXISTENTE'), 404

    return {'consultorio': resultado}, 200

def eliminar_consultorio(id_consultorio):
    _, error = borrar_consultorio(id_consultorio)
    if error == 'NO_EXISTE':
        return error_respuesta('El consultorio inidicado no existe', 'CONSULTORIO_INEXISTENTE'), 404

    if error == 'EN_USO':
        return error_respuesta('No se puede eliminar: el consultorio tiene agendas asociadas', 'CONSULTORIO_EN_USO'), 409

    return {'mensaje': 'Consultorio eliminado'}, 200
