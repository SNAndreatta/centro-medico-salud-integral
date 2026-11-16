"""Fecha y hora local del centro médico.

El backend guarda los horarios de los turnos en hora local (por defecto
America/Argentina/Buenos_Aires). Estas funciones permiten consultar
"hoy" sin depender de la zona horaria con la que corre el contenedor
de MySQL (que puede ser UTC).
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


def fecha_local(valor=None):
    """La fecha dada (date o ISO) o, si no viene, la de hoy en hora local."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if valor:
        try:
            return date.fromisoformat(str(valor)[:10])
        except ValueError:
            pass
    return hoy_local()
