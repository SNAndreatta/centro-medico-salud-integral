from src.errores import error_respuesta
from src.repositories.agendas_repositories import buscar_agendas
from src.utils.roles import MEDICO

def _id_positivo(valor, nombre):
    if valor is None:
        return None, None
    try:
        id_numerico = int(valor)
    except(TypeError, ValueError):
        return None, error_respuesta(f'{nombre} debe ser un entero positivo', 'FILTRO_INVALIDO')
    if id_numerico <= 0 or str(id_numerico) != str(valor).strip():
        return None, error_respuesta(f'{nombre} debe ser un entero positivo', 'FILTRO_INVALIDO')
    return id_numerico, None

def _booleano_opcional(valor, nombre):
    if valor is None:
        return None, None
    normalizado = str(valor).strip().lower()
    if normalizado == 'true':
        return True, None
    if normalizado == 'false':
        return False, None
    return None, error_respuesta(f'{nombre} debe ser true o false', 'FILTRO_INVALIDO')
    
def filtrar_agendas(parametros, usuario_actual):
    id_medico, error = _id_positivo(parametros.get('id_medico'), 'id_medico')
    if error:
        return error, 400

    id_consultorio, error = _id_positivo(parametros.get('id_consultorio'), 'id_consultorio')
    if error:
        return error, 400

    vigente, error = _booleano_opcional(parametros.get('vigente'), 'vigente')
    if error:
        return error, 400

    id_usuario_medico = (
        usuario_actual['id_usuario']
        if usuario_actual['id_rol'] == MEDICO
        else None
    )

    agendas = buscar_agendas(
        id_medico=id_medico,
        id_consultorio=id_consultorio,
        vigente=vigente,
        id_usuario_medico=id_usuario_medico,
    )
    return {'agendas': agendas}, 200