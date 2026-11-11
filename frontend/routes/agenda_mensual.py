import calendar
from datetime import date

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
HORARIOS = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
            "11:00", "11:30", "12:00", "12:30"]

PACIENTES = [
    {"nombre": "Lucía Fernández", "cobertura": "OSDE 210", "iniciales": "LF", "color": "bg-dominante text-acento"},
    {"nombre": "Martín Gómez", "cobertura": "Swiss Medical", "iniciales": "MG", "color": "bg-acento/20 text-acento"},
    {"nombre": "Sofía Ruiz", "cobertura": "Galeno", "iniciales": "SR", "color": "bg-acento/30 text-acento"},
    {"nombre": "Juan Pérez", "cobertura": "Particular", "iniciales": "JP", "color": "bg-gray-200 text-acento"},
]


def _turnos_del_dia(fecha):
    """Datos hardcodeados: fines de semana cerrados, horarios ocupados por patrón fijo."""
    if fecha.weekday() >= 5:
        return []
    turnos = []
    for i, hora in enumerate(HORARIOS):
        ocupado = (fecha.day + i) % 3 == 0
        turnos.append({
            "hora": hora,
            "disponible": not ocupado,
            "paciente": PACIENTES[(fecha.day + i) % len(PACIENTES)] if ocupado else None,
        })
    return turnos


def generar_agenda_mensual(anio, mes):
    dias = []
    for numero in range(1, calendar.monthrange(anio, mes)[1] + 1):
        fecha = date(anio, mes, numero)
        turnos = _turnos_del_dia(fecha)
        dias.append({
            "fecha": fecha.isoformat(),
            "numero": numero,
            "dia_semana": fecha.weekday(),
            "turnos": turnos,
            "libres": sum(1 for t in turnos if t["disponible"]),
        })
    return dias


def contexto_agenda_mensual(args):
    """Usar con request.args. Devuelve todo lo que necesita components/agenda_mensual.html."""
    hoy = date.today()
    try:
        anio = int(args.get("anio", hoy.year))
        mes = int(args.get("mes", hoy.month))
    except ValueError:
        anio, mes = hoy.year, hoy.month
    if not 1 <= mes <= 12:
        mes = hoy.month

    anios = list(range(hoy.year - 2, hoy.year + 5))
    if anio not in anios:
        anios.append(anio)
        anios.sort()

    dias = generar_agenda_mensual(anio, mes)

    # Día por defecto: hoy si está en el mes, si no el primero del mes
    fecha_inicial = hoy.isoformat() if (hoy.year, hoy.month) == (anio, mes) else dias[0]["fecha"]

    return {
        "anio": anio,
        "mes": mes,
        "nombre_mes": MESES[mes - 1],
        "meses": list(enumerate(MESES, start=1)),
        "anios": anios,
        "dias": dias,
        "offset_inicio": dias[0]["dia_semana"],  # celdas vacías antes del día 1 (lunes = 0)
        "dias_semana": DIAS_SEMANA,
        "fecha_inicial": fecha_inicial,
    }
