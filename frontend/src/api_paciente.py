from datetime import datetime
from email.utils import parsedate_to_datetime

from flask import session

from src.api import api, ErrorAPI

DIAS = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
         "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]


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

    estado = _g(t, "estado", "estado_turno", default="")
    if isinstance(estado, dict):
        estado = estado.get("nombre", "")

    return {
        "id": _g(t, "id_turno", "id"),
        "id_medico": id_medico,
        "medico": nombre_medico or "Sin asignar",
        "iniciales": _iniciales(nombre_medico),
        "especialidad": especialidad,
        "consultorio": consultorio,
        "estado": str(estado).lower(),
        "fecha_iso": dt.strftime("%Y-%m-%d"),
        "hora": dt.strftime("%H:%M"),
        "fecha": f"{dt.day} de {MESES[dt.month - 1].capitalize()} de {dt.year}",
        "dia_semana": DIAS[dt.weekday()],
        "dia": dt.day,
        "mes": MESES[dt.month - 1],
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


def turnos_disponibles(**filtros):
    params = {k: v for k, v in filtros.items() if v not in (None, "")}
    datos = como_lista(api("GET", "/turnos/disponibles", params=params), "turnos")
    return [normalizar_turno(t) for t in datos]


def medicos_por_especialidad(id_especialidad):
    vistos = {}
    for t in turnos_disponibles(id_especialidad=id_especialidad):
        if t["id_medico"] and t["id_medico"] not in vistos:
            vistos[t["id_medico"]] = {
                "id": t["id_medico"],
                "nombre": t["medico"],
                "iniciales": t["iniciales"],
            }
    return list(vistos.values())


# ---------- turnos del paciente ----------

def mis_turnos_paciente():
    # GET /turnos ya limita el resultado al paciente autenticado (JWT).
    datos = como_lista(api("GET", "/turnos"), "turnos")
    return [normalizar_turno(t) for t in datos]


def proximos_turnos_paciente(limite=3):
    activos = [t for t in mis_turnos_paciente()
               if t["estado"] in ("reservado", "confirmado")]
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

    return {
        "nombre": nombre,
        "apellido": apellido,
        "iniciales": _iniciales(f"{nombre} {apellido}"),
        "email": _buscar(p, "correo_electronico", "email", default=""),
        "documento": _buscar(p, "dni", "documento", default=""),
        "fecha_nacimiento": _fecha(fecha_nac).strftime("%d/%m/%Y") if fecha_nac else "No informada",
        "fecha_registro": _fecha(fecha_reg).strftime("%d/%m/%Y") if fecha_reg else "-",
        "numero_afiliado": _buscar(p, "nro_afiliado", "numero_afiliado", default="-") or "-",
        "cobertura": cobertura,
    }


def actualizar_email(nuevo_email):
    # PUT /pacientes/{id}: acepta correo_electronico, id_cobertura, nro_afiliado
    api("PUT", f"/pacientes/{id_paciente_actual()}",
        json={"correo_electronico": nuevo_email})


def cambiar_password(nueva_password):
    # PUT /usuarios/{id}/password: solo recibe nueva_password (no valida la anterior)
    id_usuario = session.get("id_usuario")
    api("PUT", f"/usuarios/{id_usuario}/password",
        json={"nueva_password": nueva_password})