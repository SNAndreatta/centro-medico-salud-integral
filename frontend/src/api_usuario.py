"""Acceso a usuarios y médicos (perfil y ABM)."""

from flask import session

from src.api import ErrorAPI, api
from src.normalizar import (
    a_date,
    buscar,
    como_lista,
    formatear_fecha,
    g,
    iniciales,
)


def _entero(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return valor


def perfil_usuario():
    """Perfil de la cuenta autenticada (admin, recepción o médico)."""
    p = api("GET", "/usuarios/me")

    nombre = buscar(p, "nombre", default=session.get("nombre", ""))
    apellido = buscar(p, "apellido", default=session.get("apellido", ""))
    fecha_nac = buscar(p, "fecha_nacimiento")
    fecha_reg = buscar(p, "fecha_creacion", "fecha_registro")

    return {
        "id_usuario": buscar(p, "id_usuario", default=session.get("id_usuario")),
        "id_rol": buscar(p, "id_rol", default=session.get("id_rol")),
        "nombre": nombre,
        "apellido": apellido,
        "iniciales": iniciales(nombre, apellido),
        "email": buscar(p, "correo_electronico", "email", default=""),
        "documento": buscar(p, "dni", "documento", default=""),
        "dni": buscar(p, "dni", "documento", default=""),
        "fecha_nacimiento": (
            formatear_fecha(fecha_nac) if fecha_nac else "No informada"
        ),
        "fecha_nacimiento_iso": (
            a_date(fecha_nac).isoformat() if a_date(fecha_nac) else ""
        ),
        "fecha_registro": formatear_fecha(fecha_reg) if fecha_reg else "-",
        "id_medico": buscar(p, "id_medico"),
        "id_especialidad": buscar(p, "id_especialidad"),
        "especialidad": buscar(p, "nombre_especialidad", "especialidad", default=""),
        "matricula": buscar(p, "matricula", default="-") or "-",
    }


def normalizar_usuario(usuario):
    """Usuario del ABM, con las claves que usan las plantillas."""
    fecha_nac = g(usuario, "fecha_nacimiento")
    nacimiento = a_date(fecha_nac)

    return {
        "id": _entero(g(usuario, "id_usuario")),
        "id_usuario": _entero(g(usuario, "id_usuario")),
        "nombre": g(usuario, "nombre") or '',
        "apellido": g(usuario, "apellido") or '',
        "iniciales": iniciales(g(usuario, "nombre"), g(usuario, "apellido")),
        "id_rol": _entero(g(usuario, "id_rol")),
        "mail": g(usuario, "correo_electronico", "email"),
        "dni": g(usuario, "dni"),
        "fecha_nacimiento": formatear_fecha(fecha_nac) if fecha_nac else '-',
        "fecha_nacimiento_iso": nacimiento.isoformat() if nacimiento else '',
        "fecha_registro": (
            formatear_fecha(g(usuario, "fecha_creacion"))
            if g(usuario, "fecha_creacion") else '-'
        ),
        "id_medico": g(usuario, "id_medico"),
        "matricula": g(usuario, "matricula"),
        "especialidad": g(usuario, "nombre_especialidad"),
        "id_paciente": g(usuario, "id_paciente"),
        "cobertura": g(usuario, "nombre_cobertura"),
    }


def listar_usuarios():
    datos = api("GET", "/usuarios") or {}

    return [normalizar_usuario(usuario)
            for usuario in como_lista(datos, "usuarios")]


def buscar_usuario(id_usuario):
    return next(
        (usuario for usuario in listar_usuarios()
         if usuario["id"] == id_usuario),
        None,
    )


def crear_usuario(datos):
    api("POST", "/usuarios", json=datos)


def crear_medico(datos):
    respuesta = api("POST", "/medicos", json=datos) or {}

    return (respuesta.get("medico") or {}).get("id_medico")


def editar_usuario(id_usuario, datos):
    api("PUT", f"/usuarios/{id_usuario}", json=datos)


def eliminar_usuario(id_usuario):
    api("DELETE", f"/usuarios/{id_usuario}")


def editar_medico(id_medico, datos):
    api("PUT", f"/medicos/{id_medico}", json=datos)


def eliminar_medico(id_medico):
    api("DELETE", f"/medicos/{id_medico}")


def actualizar_datos_usuario(datos):
    """Actualiza los datos personales del usuario autenticado."""
    id_usuario = session.get("id_usuario")
    if not id_usuario:
        raise ErrorAPI("No se pudo identificar al usuario.", 401)

    editar_usuario(id_usuario, datos)


def actualizar_datos_medico(id_medico, datos):
    """Actualiza la especialidad y matrícula del médico autenticado."""
    editar_medico(id_medico, datos)


def cambiar_password(nueva_password, password_actual):
    id_usuario = session.get("id_usuario")
    api(
        "PUT",
        f"/usuarios/{id_usuario}/password",
        json={
            "nueva_password": nueva_password,
            "password_actual": password_actual,
        },
    )
