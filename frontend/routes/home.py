from flask import (
    Blueprint, render_template, session, redirect, url_for, flash, request
)

from src.api import ErrorAPI
from src.api_catalogos import coberturas_medico
from src.api_paciente import perfil_paciente
from src.api_turnos import (
    generar_turnos as api_generar_turnos,
    proximos_turnos_paciente,
    turnos_del_dia_medico,
)
from src.api_usuario import perfil_usuario
from src.errores import atender_error
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
        respuesta = atender_error(e)
        if respuesta:
            return respuesta

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
        resultado = api_generar_turnos()
    except ErrorAPI as e:
        return atender_error(e, redirect_a=url_for("rutas_home.home"))

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


@home_routes.route("/cancelar-turno")
def cancelar_turno_desde_correo():
    """Página pública para mostrar el resultado de cancelar un turno desde el correo.

    El backend redirige acá pasando el resultado por query string.
    No requiere iniciar sesión.
    """
    estado = request.args.get("estado", "exito")
    status_code = 200 if estado == "exito" else 400
    return (
        render_template(
            "components/cancelar_turno.html",
            titulo=request.args.get("titulo", "Turno cancelado"),
            mensaje=request.args.get("mensaje", ""),
            icono=request.args.get("icono", "✅"),
            color=request.args.get("color", "#10b981"),
            boton_texto=request.args.get("boton_texto", "Volver al inicio"),
            boton_url=request.args.get("boton_url", "/"),
        ),
        status_code,
    )
