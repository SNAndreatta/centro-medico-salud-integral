"""Fecha y hora del centro médico.

El backend guarda y devuelve los horarios de los turnos en hora local
(hoy, America/Argentina/Buenos_Aires). Si el frontend usara la zona
horaria del servidor (por ejemplo UTC en los contenedores), los turnos
del día se mostrarían como pasados o como futuros equivocados.

Por eso todo el "ahora" del frontend se calcula con esta zona horaria.
"""

from datetime import date, datetime
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
