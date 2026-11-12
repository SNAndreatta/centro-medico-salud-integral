from flask import (
    Blueprint, render_template, session, request, redirect, url_for, flash
)

from src.api import ErrorAPI
from src.api_paciente import proximos_turnos_paciente

home_routes = Blueprint('rutas_home', __name__)

# session['rol'] (lo que guarda auth.py) -> nombre que usa home.html
ALIAS_ROL = {"administrador": "admin", "recepcionista": "recepcion"}
ROLES_DEMO = ("medico", "recepcion", "admin", "paciente")

# Datos hardcodeados, solo para los roles todavía no conectados.
DATOS_DEMO = {
    "medico": {
        "consultorio": "123",
        "fecha": "25/10",
        "turnos_del_dia": [
            {
                "id": 1, "nombre_paciente": "Camila Núñez", "iniciales": "CN",
                "cobertura": "Galeno", "hora": "15:00 pm.", "fecha": "25 - 10 - 2026",
                "consultorio": "123", "color_fondo": "bg-pink-500/30 text-pink-500",
            },
            {
                "id": 2, "nombre_paciente": "Martín Pérez", "iniciales": "MP",
                "cobertura": "OSDE", "hora": "15:00 pm.", "fecha": "25 - 10 - 2026",
                "consultorio": "123", "color_fondo": "bg-green-500/30 text-green-500",
            },
        ],
        "coberturas": [
            {"nombre": "Galeno"}, {"nombre": "OSDE"},
            {"nombre": "Swiss Medical"}, {"nombre": "PAMI"},
        ],
    },
    "recepcion": {},
    "admin": {},
    "paciente": {},
}


@home_routes.route("/home")
def home():
    if "access_token" not in session:
        return redirect(url_for("rutas_auth.login"))

    rol_sesion = session.get("rol", "paciente")
    rol_real = ALIAS_ROL.get(rol_sesion, rol_sesion)
    es_demo = rol_real != "paciente"

    datos = {}

    if not es_demo:
        # ---------- PACIENTE REAL: datos del backend ----------
        session.pop("rol_demo", None)   # un paciente nunca puede simular otro rol
        rol = "paciente"
        try:
            datos = {"proximos_turnos": proximos_turnos_paciente()}
        except ErrorAPI as e:
            if e.status == 401:
                session.clear()
                flash("Tu sesión expiró. Iniciá sesión de nuevo.", "error")
                return redirect(url_for("rutas_auth.login"))
            flash(e.mensaje, "error")
            datos = {"proximos_turnos": []}
    else:
        # ---------- NO PACIENTE: rol cambiable con datos de prueba ----------
        pedido = request.args.get("rol_demo")
        if pedido in ROLES_DEMO:
            session["rol_demo"] = pedido

        rol = session.get("rol_demo", rol_real)
        if rol not in ROLES_DEMO:
            rol = "recepcion"
        datos = DATOS_DEMO[rol]

    reserva_exitosa = session.pop("turno_reservado", False)

    usuario = {
        "nombre_completo": f"{session.get('nombre', '')} {session.get('apellido', '')}".strip()
    }

    return render_template(
        "home.html",
        rol=rol,
        usuario=usuario,
        datos=datos,
        reserva_exitosa=reserva_exitosa,
        es_demo=es_demo,
        roles_demo=ROLES_DEMO,
    )