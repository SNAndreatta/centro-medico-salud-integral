"""Normalización compartida de los datos que vienen de la API."""

import ast
from datetime import datetime, timedelta

from src.tiempo import a_date, a_datetime, ahora_local, formatear_fecha, hoy_local

DIAS = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
         "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]

ESTADOS_TURNO = ("reservado", "confirmado", "atendido", "cancelado", "ausente")
LIMITE_CANCELACION_HORAS = 24

VENTANA_ATENDIDO_HORAS_ANTES = 1
VENTANA_ATENDIDO_HORAS_DESPUES = 12

COLORES_AVATAR = (
    'bg-pink-500/30 text-pink-500',
    'bg-purple-500/30 text-purple-500',
    'bg-blue-500/30 text-blue-500',
    'bg-green-500/30 text-green-500',
    'bg-orange-500/30 text-orange-500',
    'bg-indigo-500/30 text-indigo-500',
)

COLORES_ESTADO = {
    'disponible': 'bg-gray-200 text-gray-600',
    'reservado': 'bg-pink-500/30 text-pink-500',
    'confirmado': 'bg-lime-500/30 text-lime-500',
    'atendido': 'bg-purple-500/30 text-purple-500',
    'cancelado': 'bg-emerald-500/30 text-emerald-500',
    'ausente': 'bg-orange-500/30 text-orange-500',
}


def g(d, *claves, default=None):
    for clave in claves:
        if isinstance(d, dict) and d.get(clave) is not None:
            return d[clave]
    return default


def buscar(d, *claves, default=None):
    """Busca en la raíz y dentro de los perfiles anidados."""
    fuentes = [d]
    for sub in ("usuario", "paciente", "medico"):
        if isinstance(d, dict) and isinstance(d.get(sub), dict):
            fuentes.append(d[sub])

    for fuente in fuentes:
        valor = g(fuente, *claves)
        if valor is not None:
            return valor
    return default


def como_lista(datos, *claves):
    if isinstance(datos, list):
        return datos
    if isinstance(datos, dict):
        for clave in claves:
            if isinstance(datos.get(clave), list):
                return datos[clave]
    return []


def fecha(valor):
    """Fecha del backend, en ISO o RFC 822, como datetime naive."""
    momento = a_datetime(valor)

    return momento if momento is not None else datetime.min


def texto(valor, default=""):
    return valor if isinstance(valor, str) else default


def iniciales(nombre, apellido=''):
    if apellido:
        partes = [nombre, apellido]
    else:
        partes = (nombre or "").split()

    letras = [parte[0] for parte in partes if parte]
    return "".join(letras).upper() or "NC"


def nombre_completo(nombre, apellido=''):
    return f"{nombre or ''} {apellido or ''}".strip()


def color_avatar(indice):
    return COLORES_AVATAR[indice % len(COLORES_AVATAR)]


def color_estado(estado):
    return COLORES_ESTADO.get(estado, 'bg-pink-500/30 text-pink-500')


def formatear_hora(valor):
    momento = a_datetime(valor)

    return momento.strftime('%H:%M') if momento else '—'


def nombre_estado(turno):
    estado = g(turno, "estado", "estado_turno", default="")

    if isinstance(estado, str):
        valor = estado.strip()
        if valor.startswith(("{", "[")):
            try:
                estado = ast.literal_eval(valor)
            except (SyntaxError, ValueError):
                estado = valor
        else:
            estado = valor

    if isinstance(estado, dict):
        estado = g(estado, "nombre", "NOMBRE", default="")
    elif isinstance(estado, list) and estado and isinstance(estado[0], dict):
        estado = g(estado[0], "nombre", "NOMBRE", default="")

    return str(estado).strip()


def estado_turno(turno):
    """Nombre del estado del turno, en minúsculas."""
    return nombre_estado(turno).lower()


def puede_cancelar(momento, estado):
    if estado != "reservado" or momento is None:
        return False
    return momento > ahora_local() + timedelta(hours=LIMITE_CANCELACION_HORAS)


def puede_marcar_atendido(momento, estado):
    if momento is None or estado != 'confirmado':
        return False

    ahora = ahora_local()
    inicio = momento - timedelta(hours=VENTANA_ATENDIDO_HORAS_ANTES)
    fin = momento + timedelta(hours=VENTANA_ATENDIDO_HORAS_DESPUES)

    return inicio <= ahora <= fin


def nombre_medico(turno):
    medico = g(turno, "medico")
    if isinstance(medico, dict):
        nombre = nombre_completo(medico.get("nombre"), medico.get("apellido"))
        if nombre:
            return nombre
    elif isinstance(medico, str) and medico.strip():
        return medico.strip()

    nombre = texto(g(turno, "medico_nombre", "nombre_medico_pila", "nombre_medico"))
    apellido = texto(g(turno, "medico_apellido"))
    return f"{nombre} {apellido}".strip()


def normalizar_turno(turno, indice=0, vista="base"):
    """Único punto de adaptación de un turno del backend a las vistas.

    La forma `base` es la que usan el paciente y el home; las demás son
    proyecciones para las tablas y tarjetas que muestran otros campos.
    """
    momento = a_datetime(g(turno, "fecha_horario_inicial", "fecha_hora", "fecha"))
    llegada = a_datetime(g(turno, "fecha_horario_llegada"))

    medico = g(turno, "medico") or {}
    paciente = g(turno, "paciente") or {}
    consultorio = g(turno, "consultorio") or {}
    cobertura = g(turno, "cobertura") or {}

    if not isinstance(medico, dict):
        medico = {}
    if not isinstance(paciente, dict):
        paciente = {}
    if not isinstance(consultorio, dict):
        consultorio = {}
    if not isinstance(cobertura, dict):
        cobertura = {}

    nombre_med = nombre_medico(turno)
    nombre_pac = nombre_completo(paciente.get("nombre"), paciente.get("apellido"))

    id_medico = medico.get("id_medico") if medico else g(turno, "id_medico")

    especialidad = texto(g(turno, "nombre_especialidad"))
    if not especialidad:
        especialidad = texto(medico.get("especialidad"))
    if not especialidad:
        especialidad = texto(g(turno, "especialidad"))

    numero_consultorio = g(turno, "numero_consultorio")
    if numero_consultorio is None:
        numero_consultorio = consultorio.get("numero", '-')

    duracion = g(turno, "duracion_turno", "duracion")

    estado = estado_turno(turno)

    nombre_cobertura = cobertura.get("nombre") or 'Particular'

    datos = {
        "id": g(turno, "id_turno", "id"),
        "id_turno": g(turno, "id_turno", "id"),
        "id_medico": id_medico,
        "medico": nombre_med or "Sin asignar",
        "nombre_medico": nombre_med,
        "iniciales": iniciales(nombre_med),
        "especialidad": especialidad,
        "consultorio": numero_consultorio,
        "duracion": int(duracion) if duracion else None,
        "estado": estado,
        "estado_texto": estado.capitalize() if estado else "",
        "estado_nombre": estado.capitalize() if estado else '',
        "cobertura": nombre_cobertura,
        "cobertura_filtro": nombre_cobertura,
        "nombre_paciente": nombre_pac or "Sin paciente",
        "nombre_completo": nombre_pac or "Sin paciente",
        "paciente": nombre_pac or "Sin paciente",
        "dni": paciente.get("dni") or '',
        "hora": momento.strftime("%H:%M") if momento else '',
        "hora_turno": formatear_hora(g(turno, "fecha_horario_inicial")),
        "hora_llegada": formatear_hora(g(turno, "fecha_horario_llegada")),
        "fecha_iso": momento.strftime("%Y-%m-%d") if momento else '',
        "fecha_filtro": momento.strftime("%Y-%m-%d") if momento else '',
        "fecha": (
            f"{momento.day} de {MESES[momento.month - 1].capitalize()} de {momento.year}"
            if momento else ''
        ),
        "fecha_tabla": momento.strftime('%d - %m - %Y') if momento else '',
        "fecha_corta": momento.strftime('%d/%m/%Y') if momento else '',
        "dia_semana": DIAS[momento.weekday()] if momento else '',
        "dia": momento.day if momento else None,
        "mes": MESES[momento.month - 1] if momento else '',
        "es_futuro": momento >= ahora_local() if momento else False,
        "puede_cancelar": puede_cancelar(momento, estado),
        "puede_marcar": puede_marcar_atendido(momento, estado),
        "atendido": estado == "atendido",
        "modalidad": especialidad[:3].upper(),
        "color": color_avatar(indice),
        "color_avatar": color_avatar(indice),
        "color_fondo": color_avatar(indice),
        "color_texto": color_estado(estado),
    }

    if vista == "medico_home":
        datos["iniciales"] = iniciales(paciente.get("nombre"), paciente.get("apellido"))
        datos["nombre_paciente"] = nombre_pac or "Paciente"

    elif vista == "medico_tabla":
        datos["iniciales"] = iniciales(paciente.get("nombre"), paciente.get("apellido"))
        datos["estado"] = estado.capitalize() if estado else ''
        datos["fecha"] = datos["fecha_tabla"]

    elif vista == "sala":
        datos["iniciales"] = iniciales(paciente.get("nombre"), paciente.get("apellido"))
        datos["medico"] = nombre_completo(medico.get("nombre"), medico.get("apellido"))
        datos["consultorio"] = g(turno, "numero_consultorio")

    elif vista == "grilla":
        datos["iniciales"] = (
            iniciales(paciente.get("nombre"), paciente.get("apellido"))
            if paciente else 'SP'
        )
        datos["medico"] = nombre_completo(medico.get("nombre"), medico.get("apellido"))
        datos["especialidad"] = especialidad or datos["medico"] or '-'
        datos["estado"] = estado
        datos["fecha"] = datos["fecha_tabla"]
        datos["cobertura"] = '-'

    elif vista == "admin_tabla":
        datos["iniciales"] = (
            iniciales(paciente.get("nombre"), paciente.get("apellido"))
            if nombre_pac else 'SP'
        )
        datos["fecha"] = datos["fecha_tabla"]
        datos["color"] = color_estado(estado)
        datos["color_texto"] = color_estado(estado)

    elif vista == "dashboard":
        datos["iniciales"] = iniciales(medico.get("nombre"), medico.get("apellido"))
        datos["nombre"] = nombre_completo(medico.get("nombre"), medico.get("apellido"))
        datos["paciente"] = nombre_pac
        datos["fecha"] = datos["fecha_corta"]
        datos["consultorio"] = consultorio.get("numero")

    elif vista == "sala_espera":
        datos["hora_llegada"] = formatear_hora(llegada)

    return datos


__all__ = [
    "DIAS", "MESES", "ESTADOS_TURNO", "LIMITE_CANCELACION_HORAS",
    "a_date", "a_datetime", "ahora_local", "buscar", "color_avatar",
    "estado_turno",
    "color_estado", "como_lista", "fecha", "formatear_fecha", "formatear_hora",
    "g", "iniciales", "nombre_completo", "nombre_estado", "nombre_medico", "normalizar_turno",
    "puede_cancelar", "puede_marcar_atendido", "texto", "hoy_local",
]
