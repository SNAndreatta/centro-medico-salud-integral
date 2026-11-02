from src.repositories.planes_repositories import (
    actualizar_plan,
    borrar_plan,
    guardar_plan,
    obtener_planes_de_cobertura,
)
from src.errores import error_respuesta
from src.validators.planes_validators import validar_datos_plan

def listar_planes_por_cobertura(id_cobertura):
    planes, error = obtener_planes_de_cobertura(id_cobertura)
    if error == 'COBERTURA_NO_EXISTE':
        return error_respuesta(
            'La cobertura indicada no existe', 
            'COBERTURA_NO_EXISTE'
        ), 404
    return {'planes': planes}, 200


def crear_plan(id_cobertura, datos):
    nombre, error = validar_datos_plan(datos)
    if error:
        return error, 400

    plan, error = guardar_plan(id_cobertura, nombre)
    if error == 'COBERTURA_NO_EXISTE':
        return error_respuesta(
            'La cobertura indicada no existe', 
            'COBERTURA_NO_EXISTE'
            ), 404
    if error == 'PLAN_DUPLICADO':
        return error_respuesta(
            'Ya existe un plan con ese nombre en la cobertura',
            'PLAN_DUPLICADO',
        ), 400
    
    return {'plan': plan}, 201


def modificar_plan(id_plan, datos):
    nombre, error = validar_datos_plan(datos)
    if error:
        return error, 400

    plan, error = actualizar_plan(id_plan, nombre)
    if error == 'NO_EXISTE':
        return error_respuesta(
            'El plan indicado no existe', 
            'PLAN_INEXISTENTE'
        ), 404
    if error == 'PLAN_DUPLICADO':
        return error_respuesta(
            'Ya existe un plan con ese nombre en la cobertura',
            'PLAN_DUPLICADO',
        ), 400
    return {'plan': plan}, 200


def eliminar_plan(id_plan):
    _, error = borrar_plan(id_plan)
    if error == 'NO_EXISTE':
        return error_respuesta(
                'El plan indicado no existe', 
                'PLAN_INEXISTENTE'
            ), 404
    if error == 'EN_USO':
        return error_respuesta(
            'No se puede eliminar: hay pacientes que usan este plan',
            'PLAN_EN_USO',
        ), 409
    return {'mensaje': 'Plan eliminado'}, 200