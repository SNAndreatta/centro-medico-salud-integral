from src.repositories.coberturas_repositories import (
    actualizar_cobertura,
    borrar_cobertura,
    guardar_cobertura,
    obtener_coberturas,
)
from src.errores import error_respuesta
from src.validators.coberturas_validators import validar_datos_cobertura

def listar_coberturas():
    especialidades = obtener_coberturas()
    return {'coberturas': especialidades}, 200


def crear_cobertura(datos):
    nombre, error = validar_datos_cobertura(datos)
    if error:
        return error, 400

    cobertura, error = guardar_cobertura(nombre)
    if error == 'COBERTURA_DUPLICADA':
        return error_respuesta(
            'Ya existe una cobertura con ese nombre',
            'COBERTURA_DUPLICADA',
        ), 400
    
    return {'cobertura': cobertura}, 201


def modificar_cobertura(id_cobertura, datos):
    nombre, error = validar_datos_cobertura(datos)
    if error:
        return error, 400

    resultado, error = actualizar_cobertura(id_cobertura, nombre)
    if error == 'NO_EXISTE':
        return error_respuesta(
        'La cobertura indicada no existe',
        'COBERTURA_INEXISTENTE',
        ), 404
    if error == 'COBERTURA_DUPLICADA':
        return error_respuesta(
            'Ya existe una cobertura con ese nombre',
            'COBERTURA_DUPLICADA',
        ), 400
    
    return {'cobertura': resultado}, 200


def eliminar_cobertura(id_cobertura):
    _, error = borrar_cobertura(id_cobertura)
    if error == 'NO_EXISTE':
        return error_respuesta(
        'La cobertura indicada no existe',
        'COBERTURA_INEXISTENTE',
        ), 404
    if error == 'EN_USO':
        return error_respuesta(
            'No se puede eliminar: hay pacientes o médicos que atienden por esta cobertura',
            'COBERTURA_EN_USO',
        ), 409
    return {'mensaje': 'Cobertura eliminada'}, 200