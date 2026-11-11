from src.errores import error_respuesta
from src.validators.common import (
    texto_obligatorio,
    validar_correo_electronico,
    validar_id_positivo,
)


CAMPOS_MEDICO = {
    'nombre',
    'apellido',
    'dni',
    'correo_electronico',
    'password',
    'id_especialidad',
    'matricula',
}


def validar_datos_medico(datos):
    if not isinstance(datos, dict) or set(datos) != CAMPOS_MEDICO:
        return None, error_respuesta(
            'El cuerpo debe incluir nombre, apellido, dni, correo_electronico, password, id_especialidad y matricula',
            'CUERPO_INVALIDO',
        )

    campos_texto = ('nombre', 'apellido', 'dni', 'password', 'matricula')
    if any(not texto_obligatorio(datos[campo]) for campo in campos_texto):
        return None, error_respuesta(
            'Todos los campos de texto son obligatorios',
            'DATOS_INVALIDOS',
        )

    limites = {
        'nombre': 100,
        'apellido': 100,
        'dni': 20,
        'password': 256,
        'matricula': 50,
    }
    if any(len(datos[campo].strip()) > limite for campo, limite in limites.items()):
        return None, error_respuesta(
            'Uno o más campos exceden la longitud permitida',
            'DATOS_INVALIDOS',
        )

    correo, error = validar_correo_electronico(datos['correo_electronico'])
    if error:
        return None, error

    id_especialidad = datos['id_especialidad']
    if (
        isinstance(id_especialidad, bool)
        or not isinstance(id_especialidad, int)
        or id_especialidad <= 0
    ):
        return None, error_respuesta(
            'id_especialidad debe ser un entero positivo',
            'ESPECIALIDAD_INVALIDA',
        )

    return {
        'nombre': datos['nombre'].strip(),
        'apellido': datos['apellido'].strip(),
        'dni': datos['dni'].strip(),
        'correo_electronico': correo,
        'password': datos['password'],
        'id_especialidad': id_especialidad,
        'matricula': datos['matricula'].strip(),
    }, None


def validar_filtros_medicos(parametros):
    filtros = {}
    for nombre in ('id_especialidad', 'id_cobertura'):
        valor, error = validar_id_positivo(parametros.get(nombre), nombre)
        if error:
            return None, error
        filtros[nombre] = valor

    nombre = parametros.get('nombre', '')
    if not isinstance(nombre, str):
        return None, error_respuesta('nombre debe ser texto', 'FILTRO_INVALIDO')
    nombre = nombre.strip()
    if len(nombre) > 100:
        return None, error_respuesta('nombre no puede superar 100 caracteres', 'FILTRO_INVALIDO')
    filtros['nombre'] = nombre or None
    return filtros, None


def validar_datos_cobertura_medico(datos):
    if not isinstance(datos, dict) or set(datos) != {'id_cobertura'}:
        return None, error_respuesta(
            'El cuerpo debe incluir únicamente id_cobertura',
            'CUERPO_INVALIDO',
        )

    id_cobertura = datos['id_cobertura']
    if (
        isinstance(id_cobertura, bool)
        or not isinstance(id_cobertura, int)
        or id_cobertura <= 0
    ):
        return None, error_respuesta(
            'id_cobertura debe ser un entero positivo',
            'COBERTURA_INVALIDA',
        )

    return id_cobertura, None