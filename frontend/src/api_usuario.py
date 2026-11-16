from flask import session

from src.api import api, ErrorAPI
from src.api_paciente import _buscar, _fecha, _iniciales


def perfil_usuario():
    """Perfil de la cuenta autenticada (admin, recepción o médico).

    `GET /usuarios/me` devuelve los datos comunes de `usuario` y, para los
    médicos, su perfil anidado en `medico` (matrícula y especialidad).
    """
    p = api("GET", "/usuarios/me")

    nombre = _buscar(p, "nombre", default=session.get("nombre", ""))
    apellido = _buscar(p, "apellido", default=session.get("apellido", ""))
    fecha_nac = _buscar(p, "fecha_nacimiento")
    fecha_reg = _buscar(p, "fecha_creacion", "fecha_registro")

    return {
        "id_usuario": _buscar(p, "id_usuario", default=session.get("id_usuario")),
        "id_rol": _buscar(p, "id_rol", default=session.get("id_rol")),
        "nombre": nombre,
        "apellido": apellido,
        "iniciales": _iniciales(f"{nombre} {apellido}"),
        "email": _buscar(p, "correo_electronico", "email", default=""),
        "documento": _buscar(p, "dni", "documento", default=""),
        "dni": _buscar(p, "dni", "documento", default=""),
        "fecha_nacimiento": (
            _fecha(fecha_nac).strftime("%d/%m/%Y") if fecha_nac else "No informada"
        ),
        "fecha_nacimiento_iso": _fecha(fecha_nac).strftime("%Y-%m-%d") if fecha_nac else "",
        "fecha_registro": _fecha(fecha_reg).strftime("%d/%m/%Y") if fecha_reg else "-",
        "id_medico": _buscar(p, "id_medico"),
        "id_especialidad": _buscar(p, "id_especialidad"),
        "especialidad": _buscar(p, "nombre_especialidad", "especialidad", default=""),
        "matricula": _buscar(p, "matricula", default="-") or "-",
    }


def actualizar_datos_usuario(datos):
    """Actualiza los datos personales del usuario autenticado."""
    id_usuario = session.get("id_usuario")
    if not id_usuario:
        raise ErrorAPI("No se pudo identificar al usuario.", 401)

    api("PUT", f"/usuarios/{id_usuario}", json=datos)


def actualizar_datos_medico(id_medico, datos):
    """Actualiza la especialidad y matrícula del médico autenticado."""
    api("PUT", f"/medicos/{id_medico}", json=datos)


def coberturas_medico(id_medico):
    """Coberturas ya asociadas a un médico."""
    if not id_medico:
        return []

    datos = api("GET", f"/medicos/{id_medico}/coberturas")
    return [
        {
            "id": c.get("id_cobertura", c.get("id")),
            "nombre": c.get("nombre"),
        }
        for c in datos.get("coberturas", [])
    ]


def agregar_coberturas_medico(id_medico, ids_cobertura):
    """Asocia al médico las coberturas nuevas elegidas en el formulario."""
    for id_cobertura in ids_cobertura:
        api(
            "POST",
            f"/medicos/{id_medico}/coberturas",
            json={"id_cobertura": int(id_cobertura)},
        )
