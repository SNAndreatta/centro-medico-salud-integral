from datetime import date, datetime


# Paleta de avatares ya utilizada por los dashboards.
COLORES_AVATAR = (
    'bg-pink-500/30 text-pink-500',
    'bg-purple-500/30 text-purple-500',
    'bg-blue-500/30 text-blue-500',
    'bg-green-500/30 text-green-500',
    'bg-orange-500/30 text-orange-500',
    'bg-indigo-500/30 text-indigo-500',
)


def iniciales(nombre, apellido=''):
    """Devuelve las iniciales de una persona."""
    letras = []

    for parte in (nombre, apellido):
        parte = (parte or '').strip()
        if parte:
            letras.append(parte[0])

    return ''.join(letras).upper() or 'NC'


def nombre_completo(nombre, apellido=''):
    """Devuelve el nombre y apellido unidos."""
    return f"{nombre or ''} {apellido or ''}".strip()


def _a_datetime(valor):
    if not valor:
        return None

    try:
        return datetime.fromisoformat(str(valor))
    except ValueError:
        return None


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


def color_avatar(indice):
    """Devuelve el color del avatar según la posición del elemento."""
    return COLORES_AVATAR[indice % len(COLORES_AVATAR)]


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

    return date.today().isoformat()


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
