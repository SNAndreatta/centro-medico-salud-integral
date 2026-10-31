from src.repositories.especialidades_repositories import (
    obtener_especialidades,
    guardar_especialidad
)
from src.errores import error_respuesta
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA

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
 
    especialidad = guardar_especialidad(nombre)
    if especialidad is None:
        return error_respuesta(
            'Ya existe una especialidad con ese nombre',
            'ESPECIALIDAD_DUPLICADA',
        ), 400
 
    return {'especialidad': especialidad}, 201
