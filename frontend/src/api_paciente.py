"""Perfil y datos de la cuenta del paciente autenticado."""

from flask import session

from src.api import ErrorAPI, api
from src.normalizar import buscar, fecha, iniciales

_SIN_ENVIAR = object()


def id_paciente_actual():
    usuario = session.get("usuario") or {}
    id_paciente = usuario.get("id_paciente")
    if id_paciente:
        return id_paciente

    # El login no devuelve id_paciente: lo resolvemos con el perfil del
    # usuario autenticado y lo guardamos en sesión para no repetir la llamada.
    datos = api("GET", "/usuarios/me")
    id_paciente = buscar(datos, "id_paciente")
    if not id_paciente:
        raise ErrorAPI("No se pudo identificar al paciente.", 500)

    usuario["id_paciente"] = id_paciente
    session["usuario"] = usuario
    return id_paciente


def cobertura_paciente():
    """Cobertura del paciente autenticado (id y nombre)."""
    perfil = api("GET", "/usuarios/me")

    nombre = buscar(perfil, "nombre_cobertura", "cobertura")
    if isinstance(nombre, dict):
        nombre = nombre.get("nombre")

    id_cobertura = buscar(perfil, "id_cobertura")

    return {
        "id": int(id_cobertura) if id_cobertura else None,
        "nombre": nombre or "Particular",
    }


def perfil_paciente():
    perfil = api("GET", "/usuarios/me")

    nombre = buscar(perfil, "nombre", default=session.get("nombre", ""))
    apellido = buscar(perfil, "apellido", default=session.get("apellido", ""))
    fecha_nac = buscar(perfil, "fecha_nacimiento")
    fecha_reg = buscar(perfil, "fecha_creacion", "fecha_registro")

    cobertura = buscar(perfil, "nombre_cobertura", "cobertura")
    if isinstance(cobertura, dict):
        cobertura = cobertura.get("nombre")
    cobertura = cobertura or "Particular"

    id_cobertura = buscar(perfil, "id_cobertura")

    return {
        "nombre": nombre,
        "apellido": apellido,
        "iniciales": iniciales(f"{nombre} {apellido}"),
        "email": buscar(perfil, "correo_electronico", "email", default=""),
        "documento": buscar(perfil, "dni", "documento", default=""),
        "dni": buscar(perfil, "dni", "documento", default=""),
        "fecha_nacimiento": fecha(fecha_nac).strftime("%d/%m/%Y") if fecha_nac else "No informada",
        "fecha_nacimiento_iso": fecha(fecha_nac).strftime("%Y-%m-%d") if fecha_nac else "",
        "fecha_registro": fecha(fecha_reg).strftime("%d/%m/%Y") if fecha_reg else "-",
        "numero_afiliado": buscar(perfil, "nro_afiliado", "numero_afiliado", default="-") or "-",
        "id_cobertura": int(id_cobertura) if id_cobertura else None,
        "cobertura": cobertura,
    }


def actualizar_datos_paciente(datos):
    """Actualiza los datos personales y la cobertura del paciente actual."""
    api("PUT", f"/pacientes/{id_paciente_actual()}", json=datos)


def actualizar_email(nuevo_email, id_cobertura=_SIN_ENVIAR):
    datos = {}
    if nuevo_email:
        datos["correo_electronico"] = nuevo_email
    if id_cobertura is not _SIN_ENVIAR:
        datos["id_cobertura"] = id_cobertura

    if not datos:
        raise ErrorAPI("No hay datos para actualizar.", 400)

    actualizar_datos_paciente(datos)
