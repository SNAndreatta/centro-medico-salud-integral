from flask import (
    Blueprint, render_template, session, redirect, url_for, flash
)

from src.api import ErrorAPI
from src.api_paciente import perfil_paciente, proximos_turnos_paciente
from src.api_usuario import (
    perfil_usuario, coberturas_medico, turnos_del_dia_medico,
)
from src.permisos import ROLES, requiere_rol, rol_actual

home_routes = Blueprint('rutas_home', __name__)


@home_routes.route("/")
def root():
    return redirect(url_for("rutas_home.home"))


@home_routes.route("/home")
@requiere_rol(*ROLES)
def home():
    rol = rol_actual()

    usuario = {
        "nombre_completo": f"{session.get('nombre', '')} {session.get('apellido', '')}".strip()
    }
    datos = {}

    try:
        if rol == "paciente":
            # ---------- PACIENTE ----------
            perfil = perfil_paciente()
            usuario.update({
                "nombre_completo": f"{perfil['nombre']} {perfil['apellido']}".strip(),
                "cobertura": perfil["cobertura"],
                "numero_afiliado": perfil["numero_afiliado"],
            })
            datos = {"proximos_turnos": proximos_turnos_paciente()}

        else:
            # ---------- ADMIN, RECEPCIÓN Y MÉDICO ----------
            perfil = perfil_usuario()
            usuario["nombre_completo"] = f"{perfil['nombre']} {perfil['apellido']}".strip()

            if rol == "medico":
                datos = {
                    "turnos_del_dia": turnos_del_dia_medico(),
                    "coberturas": coberturas_medico(perfil.get("id_medico")),
                }

    except ErrorAPI as e:
        if e.status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión de nuevo.", "error")
            return redirect(url_for("rutas_auth.login"))
        flash(e.mensaje, "error")

    if rol == "medico":
        datos.setdefault("turnos_del_dia", [])
        datos.setdefault("coberturas", [])
    elif rol == "paciente":
        datos.setdefault("proximos_turnos", [])

    reserva_exitosa = session.pop("turno_reservado", False)

    return render_template(
        "home.html",
        rol=rol,
        usuario=usuario,
        datos=datos,
        reserva_exitosa=reserva_exitosa,
    )
