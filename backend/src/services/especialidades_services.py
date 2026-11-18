from src.repositories.especialidades_repositories import (
    obtener_especialidades,
    guardar_especialidad,
    actualizar_especialidad,
    borrar_especialidad,
)
from src.errores import error_respuesta
from src.validators.especialidades_validators import validar_datos_especialidad

def listar_especialidades():
        especialidades = obtener_especialidades()
        return {'especialidades': especialidades}, 200

def crear_especialidad(datos):
    nombre, error = validar_datos_especialidad(datos)
    if error:
        return error, 400
 
    especialidad, error = guardar_especialidad(nombre)
    if error == 'ESPECIALIDAD_DUPLICADA':
        return error_respuesta(
            'Ya existe una especialidad con ese nombre',
            'ESPECIALIDAD_DUPLICADA',
        ), 400
 
    return {'especialidad': especialidad}, 201

def modificar_especialidad(id_especialidad, datos):
    nombre, error = validar_datos_especialidad(datos)
    if error:
        return error, 400
 
    resultado, error = actualizar_especialidad(id_especialidad, nombre)
    if error == 'NO_EXISTE':
        return error_respuesta(
            'La especialidad indicada no existe',
            'ESPECIALIDAD_INEXISTENTE',
        ), 404
    if error == 'YA_EXISTE':
        return error_respuesta(
            'Ya existe una especialidad con ese nombre',
            'ESPECIALIDAD_DUPLICADA',
        ), 400
 
    return {'especialidad': resultado}, 200
 
 
def eliminar_especialidad(id_especialidad):
    _, error = borrar_especialidad(id_especialidad)
    if error == 'NO_EXISTE':
        return error_respuesta(
            'La especialidad indicada no existe',
            'ESPECIALIDAD_INEXISTENTE',
        ), 404
    if error == 'EN_USO':
        return error_respuesta(
            'No se puede eliminar: hay médicos asociados a esta especialidad',
            'ESPECIALIDAD_EN_USO',
        ), 409
 
    return {'mensaje': 'Especialidad eliminada'}, 200
 
