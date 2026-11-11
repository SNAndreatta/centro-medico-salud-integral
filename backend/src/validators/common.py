import re
from datetime import date, time

from src.errores import error_respuesta


LONGITUD_MAXIMA_NOMBRE = 100


def validar_objeto_json(datos):
    if not isinstance(datos, dict):
        return error_respuesta('El cuerpo debe ser un objeto JSON', 'CUERPO_INVALIDO'), 400
    return None


def texto_obligatorio(valor):
    return isinstance(valor, str) and bool(valor.strip())


def validar_id_positivo(valor, nombre):
    if valor is None:
        return None, None
    try:
        id_numerico = int(valor)
    except (TypeError, ValueError):
        return None, error_respuesta(f'{nombre} debe ser un entero positivo', 'FILTRO_INVALIDO')
    if id_numerico <= 0 or str(id_numerico) != str(valor).strip():
        return None, error_respuesta(f'{nombre} debe ser un entero positivo', 'FILTRO_INVALIDO')
    return id_numerico, None


def validar_fecha_iso_opcional(valor, nombre):
    if valor is None or not str(valor).strip():
        return None, None
    try:
        fecha = date.fromisoformat(str(valor).strip())
    except ValueError:
        return None, error_respuesta(f'{nombre} debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA')
    if fecha.isoformat() != str(valor).strip():
        return None, error_respuesta(f'{nombre} debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA')
    return fecha.isoformat(), None


def validar_fecha_obligatoria(valor, nombre):
    fecha_iso, error = validar_fecha_iso_opcional(valor, nombre)
    if error:
        return None, error
    if fecha_iso is None:
        return None, error_respuesta(f'{nombre} debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA')
    return date.fromisoformat(fecha_iso), None


def validar_rango_fechas(fecha_desde, fecha_hasta):
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        return error_respuesta(
            'fecha_desde no puede ser posterior a fecha_hasta',
            'RANGO_FECHAS_INVALIDO',
        )
    return None


def validar_correo_electronico(valor):
    if not isinstance(valor, str):
        return None, error_respuesta('El correo electrónico no es válido', 'EMAIL_INVALIDO')
    correo = valor.strip().lower()
    if len(correo) > 150 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', correo):
        return None, error_respuesta('El correo electrónico no es válido', 'EMAIL_INVALIDO')
    return correo, None


def validar_hora_opcional(valor, nombre):
    if valor is None or not str(valor).strip():
        return None, None

    texto = str(valor).strip()
    if not re.fullmatch(r'\d{2}:\d{2}(:\d{2})?$', texto):
        return None, error_respuesta(f'{nombre} debe tener formato HH:MM o HH:MM:SS', 'HORA_INVALIDA')
    try:
        hora = time.fromisoformat(texto)
    except ValueError:
        return None, error_respuesta(f'{nombre} debe tener formato HH:MM o HH:MM:SS', 'HORA_INVALIDA')
    if hora.tzinfo is not None:
        return None, error_respuesta(f'{nombre} no debe incluir zona horaria', 'HORA_INVALIDA')
    return hora.strftime('%H:%M:%S'), None


def validar_hora_obligatoria(valor, nombre):
    hora, error = validar_hora_opcional(valor, nombre)
    if error:
        return None, error
    if hora is None:
        return None, error_respuesta(f'{nombre} debe tener formato HH:MM o HH:MM:SS', 'HORA_INVALIDA')
    return hora, None


def validar_booleano_opcional(valor, nombre):
    if valor is None:
        return None, None
    normalizado = str(valor).strip().lower()
    if normalizado == 'true':
        return True, None
    if normalizado == 'false':
        return False, None
    return None, error_respuesta(f'{nombre} debe ser true o false', 'FILTRO_INVALIDO')


def validar_cuerpo_con_nombre(datos, mensaje_cuerpo):
    if not isinstance(datos, dict) or set(datos) != {'nombre'}:
        return None, error_respuesta(mensaje_cuerpo, 'CUERPO_INVALIDO')

    if not texto_obligatorio(datos['nombre']):
        return None, error_respuesta('El nombre es obligatorio', 'DATOS_INVALIDOS')

    nombre = datos['nombre'].strip()
    if len(nombre) > LONGITUD_MAXIMA_NOMBRE:
        return None, error_respuesta(
            f'El nombre no puede superar {LONGITUD_MAXIMA_NOMBRE} caracteres',
            'DATOS_INVALIDOS',
        )

    return nombre, None
