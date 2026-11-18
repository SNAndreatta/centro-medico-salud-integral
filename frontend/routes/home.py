from flask import (
    Blueprint, render_template, session, redirect, url_for, flash
)

from src.api import ErrorAPI, api
from src.api_paciente import perfil_paciente, proximos_turnos_paciente
from src.api_usuario import (
    perfil_usuario, coberturas_medico, turnos_del_dia_medico,
)
from src.permisos import ROLES, requiere_rol, rol_actual
from src.tiempo import hoy_local

home_routes = Blueprint('rutas_home', __name__)

DIA_GENERACION_TURNOS = 15


def _puede_generar_turnos():
    """La apertura de turnos se habilita sólo el día 15 de cada mes."""
    return hoy_local().day == DIA_GENERACION_TURNOS


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
        puede_generar_turnos=_puede_generar_turnos(),
    )


@home_routes.route("/home/generar-turnos", methods=["POST"])
@requiere_rol("admin")
def generar_turnos():
    if not _puede_generar_turnos():
        flash(
            "La generación de turnos sólo está disponible el día 15 de cada mes.",
            "error",
        )
        return redirect(url_for("rutas_home.home"))

    try:
        resultado = api("POST", "/turnos/generar")
    except ErrorAPI as e:
        if e.status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión de nuevo.", "error")
            return redirect(url_for("rutas_auth.login"))
        flash(e.mensaje, "error")
        return redirect(url_for("rutas_home.home"))

    if not isinstance(resultado, dict):
        resultado = {}

    cantidad = resultado.get("turnos_generados", 0)
    periodo = resultado.get("periodo", {})
    mensaje = f"Se generaron {cantidad} turnos correctamente."
    if (
        isinstance(periodo, dict)
        and periodo.get("fecha_desde")
        and periodo.get("fecha_hasta")
    ):
        mensaje += f" Período: {periodo['fecha_desde']} al {periodo['fecha_hasta']}."
    flash(mensaje, "success")

    return redirect(url_for("rutas_home.home"))
