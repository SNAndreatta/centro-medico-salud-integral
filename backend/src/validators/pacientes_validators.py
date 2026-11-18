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
CAMPOS_OPCIONALES = {'id_cobertura'}

CAMPOS_ACTUALIZACION_PACIENTE = {
    'nombre',
    'apellido',
    'dni',
    'correo_electronico',
    'fecha_nacimiento',
    'id_cobertura',
}

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
    if len(password) < 8:
        return None, error_respuesta('La contraseña debe tener al menos 8 caracteres', 'PASSWORD_INVALIDO'), 400
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

    # El nro. de afiliado NO se recibe del cliente: se genera automáticamente.
    return {
        'nombre': nombre,
        'apellido': apellido,
        'dni': dni,
        'correo_electronico': correo,
        'fecha_nacimiento': fecha_nacimiento,
        'password': password,
        'id_cobertura': id_cobertura,
    }, None, None

def validar_datos_actualizacion_paciente(datos):
    if not isinstance(datos, dict) or not datos:
        return None, error_respuesta(
            'Debe enviar al menos un campo para actualizar',
            'CUERPO_INVALIDO',
        )

    if set(datos) - CAMPOS_ACTUALIZACION_PACIENTE:
        return None, error_respuesta(
            'Se recibieron campos desconocidos o no permitidos',
            'CUERPO_INVALIDO',
        )

    actualizados = {}

    for campo in ('nombre', 'apellido'):
        if campo in datos:
            if not texto_obligatorio(datos[campo]):
                return None, error_respuesta(f'{campo} es obligatorio', 'CAMPO_INVALIDO')
            valor = datos[campo].strip()
            if len(valor) > 100:
                return None, error_respuesta(
                    'Nombre y apellido no pueden superar 100 caracteres',
                    'CAMPO_INVALIDO',
                )
            actualizados[campo] = valor

    if 'dni' in datos:
        if not texto_obligatorio(datos['dni']):
            return None, error_respuesta('dni es obligatorio', 'CAMPO_INVALIDO')
        dni = datos['dni'].strip()
        if not re.fullmatch(r'\d{7,8}', dni):
            return None, error_respuesta('El DNI debe contener 7 u 8 dígitos', 'DNI_INVALIDO')
        actualizados['dni'] = dni

    if 'correo_electronico' in datos:
        if not texto_obligatorio(datos['correo_electronico']):
            return None, error_respuesta('correo_electronico es obligatorio', 'CAMPO_INVALIDO')
        correo, error = validar_correo_electronico(datos['correo_electronico'])
        if error:
            return None, error
        actualizados['correo_electronico'] = correo

    if 'fecha_nacimiento' in datos:
        if not texto_obligatorio(datos['fecha_nacimiento']):
            return None, error_respuesta('fecha_nacimiento es obligatorio', 'CAMPO_INVALIDO')
        fecha_iso, error = validar_fecha_iso_opcional(datos['fecha_nacimiento'], 'fecha_nacimiento')
        if error:
            return None, error
        fecha_nacimiento = date.fromisoformat(fecha_iso)
        if fecha_nacimiento > date.today():
            return None, error_respuesta('fecha_nacimiento no puede ser futura', 'FECHA_INVALIDA')
        actualizados['fecha_nacimiento'] = fecha_nacimiento

    if 'id_cobertura' in datos:
        id_cobertura = datos['id_cobertura']
        if id_cobertura is not None and (
            isinstance(id_cobertura, bool) or not isinstance(id_cobertura, int) or id_cobertura <= 0
        ):
            return None, error_respuesta(
                'id_cobertura debe ser un entero positivo o nulo',
                'COBERTURA_INVALIDA',
            )
        actualizados['id_cobertura'] = id_cobertura

    # El nro. de afiliado no se actualiza manualmente:
    # se genera automáticamente en el repositorio cuando cambia la cobertura.

    return actualizados, None

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