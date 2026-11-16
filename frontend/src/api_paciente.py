from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from flask import session

from src.api import api, ErrorAPI

DIAS = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
         "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]

# Estados reales de un turno (tabla estado_turno del backend).
ESTADOS_TURNO = ("reservado", "confirmado", "atendido", "cancelado", "ausente")

# La cancelación del turno por parte del paciente sólo se permite
# hasta 24 horas antes del horario del turno.
LIMITE_CANCELACION_HORAS = 24

# Marca para no enviar un campo opcional al backend.
_SIN_ENVIAR = object()


# ---------- helpers ----------

def _g(d, *claves, default=None):
    for c in claves:
        if isinstance(d, dict) and d.get(c) is not None:
            return d[c]
    return default


def _buscar(p, *claves, default=None):
    """Busca en la raíz y dentro de los perfiles anidados."""
    fuentes = [p]
    for sub in ("usuario", "paciente", "medico"):
        if isinstance(p.get(sub), dict):
            fuentes.append(p[sub])
    for f in fuentes:
        v = _g(f, *claves)
        if v is not None:
            return v
    return default


def como_lista(datos, *claves):
    if isinstance(datos, list):
        return datos
    if isinstance(datos, dict):
        for c in claves:
            if isinstance(datos.get(c), list):
                return datos[c]
    return []


def _fecha(valor):
    """Soporta ISO ('2026-11-02 09:00:00') y RFC 822 ('Mon, 02 Nov 2026 ...')."""
    if isinstance(valor, datetime):
        return valor
    try:
        return datetime.fromisoformat(str(valor))
    except ValueError:
        return parsedate_to_datetime(str(valor)).replace(tzinfo=None)


def _iniciales(nombre):
    partes = [p for p in (nombre or "").split() if p]
    return "".join(p[0] for p in partes[:2]).upper() or "NC"


def _texto(valor, default=""):
    return valor if isinstance(valor, str) else default


def _puede_cancelar(momento, estado):
    """Indica si el paciente todavía puede cancelar ese turno."""
    if estado != "reservado" or momento is None:
        return False

    return momento > datetime.now() + timedelta(hours=LIMITE_CANCELACION_HORAS)


def _nombre_medico(t):
    medico = _g(t, "medico")
    if isinstance(medico, dict):
        nombre = " ".join(
            p for p in (medico.get("nombre"), medico.get("apellido")) if p
        )
        if nombre:
            return nombre
    elif isinstance(medico, str) and medico.strip():
        return medico.strip()

    nombre = _texto(_g(t, "medico_nombre", "nombre_medico_pila", "nombre_medico"))
    apellido = _texto(_g(t, "medico_apellido"))
    return f"{nombre} {apellido}".strip()


def normalizar_turno(t):
    dt = _fecha(_g(t, "fecha_horario_inicial", "fecha_hora", "fecha"))

    medico = _g(t, "medico")
    nombre_medico = _nombre_medico(t)
    id_medico = (
        medico.get("id_medico") if isinstance(medico, dict)
        else _g(t, "id_medico")
    )

    especialidad = _texto(_g(t, "nombre_especialidad"))
    if not especialidad and isinstance(medico, dict):
        especialidad = _texto(medico.get("especialidad"))
    if not especialidad:
        especialidad = _texto(_g(t, "especialidad"))

    consultorio = _g(t, "numero_consultorio", "consultorio", default="-")
    if isinstance(consultorio, dict):
        consultorio = consultorio.get("numero", "-")

    duracion = _g(t, "duracion_turno", "duracion")

    estado = _g(t, "estado", "estado_turno", default="")
    if isinstance(estado, dict):
        estado = estado.get("nombre", "")

    estado = str(estado).lower()

    return {
        "id": _g(t, "id_turno", "id"),
        "id_medico": id_medico,
        "medico": nombre_medico or "Sin asignar",
        "iniciales": _iniciales(nombre_medico),
        "especialidad": especialidad,
        "consultorio": consultorio,
        "duracion": int(duracion) if duracion else None,
        "estado": estado,
        "estado_texto": estado.capitalize() if estado else "",
        "fecha_iso": dt.strftime("%Y-%m-%d"),
        "hora": dt.strftime("%H:%M"),
        "fecha": f"{dt.day} de {MESES[dt.month - 1].capitalize()} de {dt.year}",
        "dia_semana": DIAS[dt.weekday()],
        "dia": dt.day,
        "mes": MESES[dt.month - 1],
        "es_futuro": dt >= datetime.now(),
        "puede_cancelar": _puede_cancelar(dt, estado),
    }


# ---------- paciente actual ----------

def id_paciente_actual():
    usuario = session.get("usuario") or {}
    id_p = usuario.get("id_paciente")
    if id_p:
        return id_p

    # El login no devuelve id_paciente: lo resolvemos con el perfil del usuario
    # autenticado y lo guardamos en sesión para no repetir la llamada.
    datos = api("GET", "/usuarios/me")
    id_p = _buscar(datos, "id_paciente")
    if not id_p:
        raise ErrorAPI("No se pudo identificar al paciente.", 500)

    usuario["id_paciente"] = id_p
    session["usuario"] = usuario
    return id_p


# ---------- catálogos ----------

def obtener_especialidades():
    datos = como_lista(api("GET", "/especialidades"), "especialidades")
    return [
        {"id": _g(e, "id_especialidad", "id"),
         "nombre": _g(e, "nombre_especialidad", "nombre")}
        for e in datos
    ]


def obtener_coberturas():
    """Catálogo de coberturas para el perfil del paciente."""
    datos = como_lista(api("GET", "/coberturas"), "coberturas")
    return [
        {"id": _g(c, "id_cobertura", "id"),
         "nombre": _g(c, "nombre")}
        for c in datos
    ]


def turnos_disponibles(**filtros):
    params = {k: v for k, v in filtros.items() if v not in (None, "")}
    datos = como_lista(api("GET", "/turnos/disponibles", params=params), "turnos")
    return [normalizar_turno(t) for t in datos]


def cobertura_paciente():
    """Cobertura del paciente autenticado (id y nombre)."""
    p = api("GET", "/usuarios/me")

    nombre = _buscar(p, "nombre_cobertura", "cobertura")
    if isinstance(nombre, dict):
        nombre = nombre.get("nombre")

    id_cobertura = _buscar(p, "id_cobertura")

    return {
        "id": int(id_cobertura) if id_cobertura else None,
        "nombre": nombre or "Particular",
    }


def medicos_por_especialidad(id_especialidad, id_cobertura=_SIN_ENVIAR):
    """
    Médicos reales de una especialidad (GET /medicos).

    Si se recibe id_cobertura se marca cuáles atienden esa cobertura.
    id_cobertura None (o vacío) representa a un paciente particular.
    """
    datos = como_lista(
        api("GET", "/medicos", params={"id_especialidad": id_especialidad}),
        "medicos",
    )

    aceptan = None
    if id_cobertura is not _SIN_ENVIAR and id_cobertura:
        aceptan = {
            _g(m, "id_medico", "id")
            for m in como_lista(
                api("GET", "/medicos", params={
                    "id_especialidad": id_especialidad,
                    "id_cobertura": id_cobertura,
                }),
                "medicos",
            )
        }

    es_particular = id_cobertura is not _SIN_ENVIAR and not id_cobertura

    medicos = []
    for m in datos:
        id_medico = _g(m, "id_medico", "id")
        nombre = " ".join(
            p for p in (_g(m, "nombre"), _g(m, "apellido")) if p
        )

        if es_particular or aceptan is None:
            acepta_cobertura = None
        else:
            acepta_cobertura = id_medico in aceptan

        medicos.append({
            "id": id_medico,
            "nombre": nombre,
            "iniciales": _iniciales(nombre),
            "matricula": _g(m, "matricula"),
            "especialidad": _g(m, "nombre_especialidad", "especialidad"),
            "acepta_cobertura": acepta_cobertura,
            "es_particular": es_particular,
        })

    return medicos


# ---------- turnos del paciente ----------

def mis_turnos_paciente():
    # GET /turnos ya limita el resultado al paciente autenticado (JWT).
    datos = como_lista(api("GET", "/turnos"), "turnos")
    return [normalizar_turno(t) for t in datos]


def proximos_turnos_paciente(limite=3):
    """Turnos futuros (reservados o confirmados) del paciente."""
    activos = [
        t for t in mis_turnos_paciente()
        if t["estado"] in ("reservado", "confirmado") and t["es_futuro"]
    ]
    activos.sort(key=lambda t: (t["fecha_iso"], t["hora"]))
    return activos[:limite]


# ---------- perfil ----------

def perfil_paciente():
    p = api("GET", "/usuarios/me")

    nombre = _buscar(p, "nombre", default=session.get("nombre", ""))
    apellido = _buscar(p, "apellido", default=session.get("apellido", ""))
    fecha_nac = _buscar(p, "fecha_nacimiento")
    fecha_reg = _buscar(p, "fecha_creacion", "fecha_registro")

    cobertura = _buscar(p, "nombre_cobertura", "cobertura")
    if isinstance(cobertura, dict):
        cobertura = cobertura.get("nombre")
    cobertura = cobertura or "Particular"

    id_cobertura = _buscar(p, "id_cobertura")

    return {
        "nombre": nombre,
        "apellido": apellido,
        "iniciales": _iniciales(f"{nombre} {apellido}"),
        "email": _buscar(p, "correo_electronico", "email", default=""),
        "documento": _buscar(p, "dni", "documento", default=""),
        "dni": _buscar(p, "dni", "documento", default=""),
        "fecha_nacimiento": _fecha(fecha_nac).strftime("%d/%m/%Y") if fecha_nac else "No informada",
        "fecha_nacimiento_iso": _fecha(fecha_nac).strftime("%Y-%m-%d") if fecha_nac else "",
        "fecha_registro": _fecha(fecha_reg).strftime("%d/%m/%Y") if fecha_reg else "-",
        "numero_afiliado": _buscar(p, "nro_afiliado", "numero_afiliado", default="-") or "-",
        "id_cobertura": int(id_cobertura) if id_cobertura else None,
        "cobertura": cobertura,
    }


def actualizar_email(nuevo_email, id_cobertura=_SIN_ENVIAR, nro_afiliado=_SIN_ENVIAR):
    """
    Actualiza los datos del paciente.

    PUT /pacientes/{id}: acepta correo_electronico y, opcionalmente,
    id_cobertura y nro_afiliado (ambos juntos; ambos nulos para particulares).
    """
    datos = {}

    if nuevo_email:
        datos["correo_electronico"] = nuevo_email

    if id_cobertura is not _SIN_ENVIAR:
        datos["id_cobertura"] = id_cobertura
        datos["nro_afiliado"] = nro_afiliado

    if not datos:
        raise ErrorAPI("No hay datos para actualizar.", 400)

    api("PUT", f"/pacientes/{id_paciente_actual()}", json=datos)


def actualizar_datos_paciente(datos):
    """Actualiza los datos personales y la cobertura del paciente actual."""
    api("PUT", f"/pacientes/{id_paciente_actual()}", json=datos)


def cambiar_password(nueva_password, password_actual):
    # PUT /usuarios/{id}/password: valida la contraseña actual del usuario.
    id_usuario = session.get("id_usuario")
    api("PUT", f"/usuarios/{id_usuario}/password",
        json={
            "nueva_password": nueva_password,
            "password_actual": password_actual,
        })