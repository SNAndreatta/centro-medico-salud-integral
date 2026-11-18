"""Fecha y hora del centro médico.

El backend guarda y devuelve los horarios de los turnos en hora local
(hoy, America/Argentina/Buenos_Aires). Si el frontend usara la zona
horaria del servidor (por ejemplo UTC en los contenedores), los turnos
del día se mostrarían como pasados o como futuros equivocados.

Por eso todo el "ahora" del frontend se calcula con esta zona horaria.
"""

from datetime import date, datetime, time
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

from src.config import Config

ZONA = ZoneInfo(Config.TIMEZONE)


def ahora_local():
    """Ahora mismo, como datetime sin zona (naive) en hora local."""
    return datetime.now(ZONA).replace(tzinfo=None)


def hoy_local():
    """La fecha de hoy, en hora local."""
    return ahora_local().date()


def a_hora_local(valor):
    """Convierte un ISO naive (del backend) a datetime naive local."""
    if isinstance(valor, datetime):
        return valor.replace(tzinfo=None)
    if isinstance(valor, date):
        return datetime.combine(valor, datetime.min.time())
    return datetime.fromisoformat(str(valor)).replace(tzinfo=None)


def a_datetime(valor):
    """Parsea la fecha/hora del backend; devuelve None si no es válida."""
    if isinstance(valor, datetime):
        return valor.replace(tzinfo=None)
    if isinstance(valor, date):
        return datetime.combine(valor, datetime.min.time())
    if not valor:
        return None

    texto = str(valor).strip()
    try:
        return datetime.fromisoformat(texto).replace(tzinfo=None)
    except ValueError:
        try:
            return parsedate_to_datetime(texto).replace(tzinfo=None)
        except (TypeError, ValueError):
            return None


def a_date(valor):
    """Parsea 'YYYY-MM-DD' (o un datetime); devuelve None si no es válida."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if not valor:
        return None

    try:
        return date.fromisoformat(str(valor).strip()[:10])
    except ValueError:
        return None


def a_time(valor):
    """Parsea 'HH:MM' o 'HH:MM:SS'; devuelve None si no es válido."""
    if isinstance(valor, time):
        return valor
    if not valor:
        return None

    try:
        return time.fromisoformat(str(valor).strip())
    except ValueError:
        return None


def formatear_fecha(valor, formato='%d/%m/%Y'):
    """Formatea una fecha del backend con el formato pedido."""
    momento = a_datetime(valor) or a_date(valor)

    return momento.strftime(formato) if momento else '-'
