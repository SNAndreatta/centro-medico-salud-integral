import re
from datetime import date

from src.errores import error_respuesta
from src.validators.common import (
    texto_obligatorio,
    validar_correo_electronico,
    validar_fecha_iso_opcional,
)


CAMPOS_REQUERIDOS = {
    'nombre',
    'apellido',
    'dni',
    'correo_electronico',
    'fecha_nacimiento',
    'password',
}
CAMPOS_OPCIONALES = {'id_cobertura', 'nro_afiliado'}


def validar_datos_registro_paciente(datos):
    if not CAMPOS_REQUERIDOS.issubset(datos) or set(datos) - CAMPOS_REQUERIDOS - CAMPOS_OPCIONALES:
        return None, error_respuesta(
            'Faltan campos obligatorios o se recibieron campos desconocidos',
            'CUERPO_INVALIDO',
        ), 400

    for campo in ('nombre', 'apellido', 'dni', 'correo_electronico', 'password', 'fecha_nacimiento'):
        if not texto_obligatorio(datos[campo]):
            return None, error_respuesta(f'{campo} es obligatorio', 'CAMPO_INVALIDO'), 400

    nombre = datos['nombre'].strip()
    apellido = datos['apellido'].strip()
    dni = datos['dni'].strip()
    if len(nombre) > 100 or len(apellido) > 100:
        return None, error_respuesta(
            'Nombre y apellido no pueden superar 100 caracteres',
            'CAMPO_INVALIDO',
        ), 400
    if not re.fullmatch(r'\d{7,8}', dni):
        return None, error_respuesta('El DNI debe contener 7 u 8 dígitos', 'DNI_INVALIDO'), 400

    correo, error = validar_correo_electronico(datos['correo_electronico'])
    if error:
        return None, error, 400

    password = datos['password']
    if len(password) > 256:
        return None, error_respuesta('La contraseña excede la longitud permitida', 'PASSWORD_INVALIDO'), 400

    fecha_iso, error = validar_fecha_iso_opcional(datos['fecha_nacimiento'], 'fecha_nacimiento')
    if error:
        return None, error, 400
    fecha_nacimiento = date.fromisoformat(fecha_iso)
    if fecha_nacimiento > date.today():
        return None, error_respuesta('fecha_nacimiento no puede ser futura', 'FECHA_INVALIDA'), 400

    id_cobertura = datos.get('id_cobertura')
    if id_cobertura is not None and (
        isinstance(id_cobertura, bool) or not isinstance(id_cobertura, int) or id_cobertura <= 0
    ):
        return None, error_respuesta('id_cobertura debe ser un entero positivo o nulo', 'COBERTURA_INVALIDA'), 400

    nro_afiliado = datos.get('nro_afiliado')
    if nro_afiliado is not None:
        if (
            not isinstance(nro_afiliado, str)
            or not nro_afiliado.strip()
            or len(nro_afiliado.strip()) > 50
        ):
            return None, error_respuesta(
                'nro_afiliado debe ser texto de hasta 50 caracteres o nulo',
                'AFILIADO_INVALIDO',
            ), 400
        nro_afiliado = nro_afiliado.strip()

    if (id_cobertura is None) != (nro_afiliado is None):
        return None, error_respuesta(
            'id_cobertura y nro_afiliado deben enviarse juntos; ambos pueden ser nulos para particulares',
            'AFILIACION_INCOMPLETA',
        ), 400

    return {
        'nombre': nombre,
        'apellido': apellido,
        'dni': dni,
        'correo_electronico': correo,
        'fecha_nacimiento': fecha_nacimiento,
        'password': password,
        'id_cobertura': id_cobertura,
        'nro_afiliado': nro_afiliado,
    }, None, None


def validar_filtros_pacientes(parametros):
    dni = parametros.get('dni', '')
    apellido = parametros.get('apellido', '')
    if not isinstance(dni, str) or not isinstance(apellido, str):
        return None, error_respuesta('Los filtros deben ser texto', 'FILTRO_INVALIDO')

    dni = dni.strip()
    apellido = apellido.strip()
    if len(dni) > 20 or len(apellido) > 100:
        return None, error_respuesta('Los filtros exceden la longitud permitida', 'FILTRO_INVALIDO')
    return {'dni': dni or None, 'apellido': apellido or None}, None