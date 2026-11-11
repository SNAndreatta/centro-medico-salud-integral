from src.validators.common import validar_fecha_iso_opcional, validar_rango_fechas


def validar_fechas_estadisticas(parametros):
    fecha_desde, error = validar_fecha_iso_opcional(parametros.get('fecha_desde'), 'fecha_desde')
    if error:
        return None, None, error

    fecha_hasta, error = validar_fecha_iso_opcional(parametros.get('fecha_hasta'), 'fecha_hasta')
    if error:
        return None, None, error

    error = validar_rango_fechas(fecha_desde, fecha_hasta)
    if error:
        return None, None, error
    return fecha_desde, fecha_hasta, None