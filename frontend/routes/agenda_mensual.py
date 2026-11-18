"""Calendario mensual de la agenda de un médico.

La grilla se arma con los datos reales del backend:

* `GET /agendas` devuelve las agendas del médico con los días de la semana
  en los que atiende y el horario de cada jornada.
* `GET /turnos` devuelve los turnos reales (reservados, confirmados, etc.)
  de esas agendas.

Cada día del mes muestra los turnos que genera la agenda y marca como
ocupados los que tienen un turno asignado.
"""

import calendar
from datetime import date, datetime, time, timedelta

from routes.admin.dashboards._comun import color_avatar
from src.tiempo import hoy_local

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def _a_time(valor):
    """Convierte 'HH:MM:SS' en un objeto time."""
    if not valor:
        return None

    try:
        return time.fromisoformat(str(valor))
    except ValueError:
        return None


def _a_datetime(valor):
    """Convierte la fecha/hora de un turno en un datetime."""
    if not valor:
        return None

    try:
        return datetime.fromisoformat(str(valor))
    except ValueError:
        return None


def _a_date(valor):
    """Convierte 'YYYY-MM-DD' en un objeto date."""
    if not valor:
        return None

    try:
        return date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


def _nombre_completo(nombre, apellido=''):
    return f"{nombre or ''} {apellido or ''}".strip()


def _iniciales(nombre, apellido=''):
    letras = [
        parte[0]
        for parte in (nombre or '', apellido or '')
        if parte
    ]

    return ''.join(letras).upper() or 'NC'


def _jornadas_del_dia(agendas, fecha):
    """Agendas que cubren la fecha y las jornadas de ese día de la semana.

    El backend usa el formato ISO para `dia_semana` (1 = lunes, 7 = domingo).
    """
    dia_semana = fecha.isoweekday()
    jornadas = []

    for agenda in agendas or []:
        fecha_inicio = _a_date(agenda.get('fecha_inicio'))
        fecha_hasta = _a_date(agenda.get('fecha_hasta'))

        if fecha_inicio is None or fecha_hasta is None:
            continue

        if not fecha_inicio <= fecha <= fecha_hasta:
            continue

        for dia in agenda.get('dias') or []:
            if int(dia.get('dia_semana') or 0) != dia_semana:
                continue

            jornadas.append((agenda, dia))

    return jornadas


def _turnos_por_momento(turnos):
    """Indexa los turnos por su fecha y hora exactas."""
    indice = {}

    for turno in turnos or []:
        momento = _a_datetime(turno.get('fecha_horario_inicial'))

        if momento is not None:
            indice[momento] = turno

    return indice


def _numero_consultorio(agenda):
    consultorio = (agenda or {}).get('consultorio') or {}

    numero = consultorio.get('numero')

    return numero if numero is not None else '-'


def _slot(agenda, momento, turno, indice_color):
    """Arma un horario del día con su turno (si lo tiene)."""
    estado = ''
    paciente = None

    if turno is not None:
        datos_paciente = turno.get('paciente') or {}
        estado = ((turno.get('estado') or {}).get('nombre') or '').lower()

        cobertura = turno.get('cobertura') or {}
        nombre_cobertura = cobertura.get('nombre') or 'Particular'

        paciente = {
            'nombre': _nombre_completo(
                datos_paciente.get('nombre'),
                datos_paciente.get('apellido'),
            ) or 'Sin paciente',
            'cobertura': nombre_cobertura,
            'iniciales': _iniciales(
                datos_paciente.get('nombre'),
                datos_paciente.get('apellido'),
            ),
            'color': color_avatar(indice_color),
        }

    return {
        'hora': momento.strftime('%H:%M'),
        'disponible': turno is None,
        'estado': estado,
        'consultorio': _numero_consultorio(agenda),
        'paciente': paciente,
    }


def mes_seleccionado(args):
    """Año y mes pedidos en los query args (por defecto, el mes actual)."""
    hoy = hoy_local()

    try:
        anio = int(args.get("anio", hoy.year))
        mes = int(args.get("mes", hoy.month))
    except (TypeError, ValueError):
        anio, mes = hoy.year, hoy.month

    if not 1 <= mes <= 12:
        mes = hoy.month

    return anio, mes


def rango_del_mes(anio, mes):
    """Primer y último día del mes, para consultar los turnos del período."""
    primero = date(anio, mes, 1)
    ultimo = calendar.monthrange(anio, mes)[1]

    return primero, primero.replace(day=ultimo)


def generar_agenda_mensual(anio, mes, agendas=None, turnos=None):
    """Días del mes con los horarios de la agenda y los turnos reales."""
    turnos_por_momento = _turnos_por_momento(turnos)
    color = 0

    dias = []

    for numero in range(1, calendar.monthrange(anio, mes)[1] + 1):
        fecha = date(anio, mes, numero)

        horarios = {}

        # Horarios que define la agenda para ese día de la semana.
        for agenda, jornada in _jornadas_del_dia(agendas, fecha):
            duracion = int(agenda.get('duracion_turno') or 0)
            hora_inicio = _a_time(jornada.get('horario_inicio_jornada'))
            hora_fin = _a_time(jornada.get('horario_final_jornada'))

            if duracion <= 0 or hora_inicio is None or hora_fin is None:
                continue

            momento = datetime.combine(fecha, hora_inicio)
            fin_jornada = datetime.combine(fecha, hora_fin)

            while momento + timedelta(minutes=duracion) <= fin_jornada:
                horarios[momento] = (agenda, turnos_por_momento.get(momento))
                momento += timedelta(minutes=duracion)

        # Turnos reales que ya no coinciden con un horario de la agenda
        # (por ejemplo, porque se modificó la jornada después de reservar).
        for momento, turno in turnos_por_momento.items():
            if momento.date() == fecha and momento not in horarios:
                horarios[momento] = (None, turno)

        lista_horarios = []

        for momento in sorted(horarios):
            agenda, turno = horarios[momento]
            lista_horarios.append(_slot(agenda, momento, turno, color))
            color += 1

        dias.append({
            "fecha": fecha.isoformat(),
            "numero": numero,
            "dia_semana": fecha.weekday(),
            "turnos": lista_horarios,
            "libres": sum(1 for t in lista_horarios if t["disponible"]),
        })

    return dias


def contexto_agenda_mensual(args, agendas=None, turnos=None, consultorio=None):
    """Usar con request.args. Devuelve todo lo que necesita components/agenda_mensual.html."""
    hoy = hoy_local()
    anio, mes = mes_seleccionado(args)

    anios = list(range(hoy.year - 2, hoy.year + 5))
    if anio not in anios:
        anios.append(anio)
        anios.sort()

    dias = generar_agenda_mensual(anio, mes, agendas, turnos)

    # Día por defecto: hoy si está en el mes, si no el primero del mes
    fecha_inicial = hoy.isoformat() if (hoy.year, hoy.month) == (anio, mes) else dias[0]["fecha"]

    if consultorio is None:
        consultorio = {"numero": '-'}
    elif "numero" not in consultorio:
        consultorio = {**consultorio, "numero": '-'} if isinstance(consultorio, dict) else {"numero": '-'}

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
        "consultorio": consultorio,
    }
