from datetime import date

from src.normalizar import color_avatar, iniciales, nombre_completo
from src.tiempo import a_datetime as _a_datetime, hoy_local


# La paleta y los formateadores viven en src.normalizar; se reexportan
# porque los dashboards y otras vistas los importan de aquí.


def formatear_hora(valor):
    """Convierte 'YYYY-MM-DD HH:MM:SS' en 'HH:MM'."""
    momento = _a_datetime(valor)

    if momento is None:
        return '—'

    return momento.strftime('%H:%M')


def formatear_fecha(valor):
    """Convierte 'YYYY-MM-DD HH:MM:SS' en 'DD/MM/YYYY'."""
    momento = _a_datetime(valor)

    if momento is None:
        return '—'

    return momento.strftime('%d/%m/%Y')


def minutos_espera(fecha_inicial, fecha_llegada):
    """
    Calcula los minutos de espera del paciente.

    Es el tiempo transcurrido entre el check-in y el horario del turno:
    si el paciente llegó antes, espera esa cantidad de minutos; si llegó
    después del horario, la espera es cero.
    """
    inicio = _a_datetime(fecha_inicial)
    llegada = _a_datetime(fecha_llegada)

    if inicio is None or llegada is None:
        return None

    diferencia = (inicio - llegada).total_seconds() / 60

    if diferencia <= 0:
        return 0

    return int(round(diferencia))


def porcentaje_texto(valor):
    """Formatea un porcentaje sin decimales sobrantes ('50', '33,3')."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return '0'

    if numero == int(numero):
        return str(int(numero))

    return f"{numero:.1f}".replace('.', ',')


def fecha_iso(valor):
    """Valida una fecha ISO y, si no es válida, devuelve la fecha de hoy."""
    if valor:
        try:
            return date.fromisoformat(str(valor).strip()).isoformat()
        except ValueError:
            pass

    return hoy_local().isoformat()


def filtros_fechas(args):
    """Arma los parámetros de fecha para los endpoints de la API."""
    parametros = {}

    fecha_desde = fecha_iso(args.get('fecha_desde')) if args.get('fecha_desde') else None
    fecha_hasta = fecha_iso(args.get('fecha_hasta')) if args.get('fecha_hasta') else None

    if fecha_desde:
        parametros['fecha_desde'] = fecha_desde

    if fecha_hasta:
        parametros['fecha_hasta'] = fecha_hasta

    return parametros
