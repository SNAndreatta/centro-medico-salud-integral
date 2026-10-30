from src.repositories.especialidades_repositories import (
    obtener_especialidades
)
from src.errores import error_respuesta
from src.utils.roles import ADMINISTRADOR, RECEPCIONISTA

def listar_especialidades():
        especialidades = obtener_especialidades()
        return {'especialidades': especialidades}, 200
