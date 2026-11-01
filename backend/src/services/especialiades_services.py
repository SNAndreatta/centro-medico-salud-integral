from src.repositories.especialidades_repositories import (
    obtener_especialidades,
    guardar_especialidad,
    actualizar_especialidad,
    borrar_especialidad,
)
from src.errores import error_respuesta

LONGITUD_MAXIMA_NOMBRE = 100

def _validar_nombre(datos):
    """Devuelve (nombre, None) si es válido o (None, (respuesta, status))."""
    if not isinstance(datos, dict) or set(datos) != {'nombre'}:
        return None, (error_respuesta(
            'El cuerpo debe incluir únicamente el campo nombre',
            'CUERPO_INVALIDO',
        ), 400)
 
    nombre = datos['nombre']
    if not isinstance(nombre, str) or not nombre.strip():
        return None, (error_respuesta(
            'El nombre es obligatorio',
            'DATOS_INVALIDOS',
        ), 400)
 
    nombre = nombre.strip()
    if len(nombre) > LONGITUD_MAXIMA_NOMBRE:
        return None, (error_respuesta(
            f'El nombre no puede superar {LONGITUD_MAXIMA_NOMBRE} caracteres',
            'DATOS_INVALIDOS',
        ), 400)
 
    return nombre, None


def listar_especialidades():
        especialidades = obtener_especialidades()
        return {'especialidades': especialidades}, 200

def crear_especialidad(datos):
    nombre, error = _validar_nombre(datos)
    if error:
        return error
 
    especialidad, error = guardar_especialidad(nombre)
    if error == 'ESPECIALIDAD_DUPLICADA':
        return error_respuesta(
            'Ya existe una especialidad con ese nombre',
            'ESPECIALIDAD_DUPLICADA',
        ), 400
 
    return {'especialidad': especialidad}, 201

def modificar_especialidad(id_especialidad, datos):
    nombre, error = _validar_nombre(datos)
    if error:
        return error
 
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
    resultado, error = borrar_especialidad(id_especialidad)
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
 
