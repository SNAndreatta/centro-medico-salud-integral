import re
from datetime import date

from src.errores import error_respuesta


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