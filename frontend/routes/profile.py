from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from src.api import ErrorAPI
from src.api_paciente import (
    perfil_paciente, proximos_turnos_paciente, actualizar_email, cambiar_password,
    obtener_coberturas,
)
from src.api_usuario import perfil_usuario

profile_routes = Blueprint('rutas_profile', __name__)


def _sesion_vencida():
    session.clear()
    flash("Tu sesión expiró. Iniciá sesión de nuevo.", "error")
    return redirect(url_for("rutas_auth.login"))


def _usuario_fallback():
    nombre = session.get("nombre", "")
    apellido = session.get("apellido", "")
    return {
        "nombre": nombre, "apellido": apellido,
        "iniciales": ((nombre[:1] + apellido[:1]).upper() or "NC"),
        "email": "", "documento": "", "fecha_nacimiento": "-",
        "fecha_registro": "-", "matricula": "-",
    }


@profile_routes.route("/profile")
def profile():
    if "access_token" not in session:
        return redirect(url_for("rutas_auth.login"))

    rol = session.get("rol", "paciente")

    if rol == "paciente":
        try:
            usuario = perfil_paciente()
            proximos = proximos_turnos_paciente()
        except ErrorAPI as e:
            print("ERROR PERFIL:", e.status, e.mensaje, flush=True)
            if e.status == 401:
                return _sesion_vencida()
            flash(e.mensaje, "error")
            usuario = _usuario_fallback()
            usuario.update({"numero_afiliado": "-", "cobertura": "-",
                            "id_cobertura": None})
            proximos = []

        # Catálogo de coberturas para el selector del modal de configuración.
        try:
            coberturas = obtener_coberturas()
        except ErrorAPI as e:
            print("ERROR COBERTURAS:", e.status, e.mensaje, flush=True)
            if e.status == 401:
                return _sesion_vencida()
            coberturas = []

        return render_template("profile.html", rol=rol, usuario=usuario,
                               proximos_turnos=proximos, coberturas=coberturas)

    try:
        usuario = perfil_usuario()
    except ErrorAPI as e:
        print("ERROR PERFIL:", e.status, e.mensaje, flush=True)
        if e.status == 401:
            return _sesion_vencida()
        flash(e.mensaje, "error")
        usuario = _usuario_fallback()

    return render_template("profile.html", rol=rol, usuario=usuario)


@profile_routes.route("/profile/actualizar", methods=["POST"])
def actualizar_perfil():
    if "access_token" not in session or session.get("rol") != "paciente":
        return redirect(url_for("rutas_auth.login"))

    email = request.form.get("email", "").strip().lower()
    cobertura_raw = request.form.get("id_cobertura", "").strip()
    nro_afiliado = request.form.get("nro_afiliado", "").strip()

    if not email:
        flash("Ingresá un correo electrónico.", "error")
        return redirect(url_for("rutas_profile.profile"))

    # id_cobertura y nro_afiliado van juntos: ambos nulos = paciente particular.
    if cobertura_raw:
        try:
            id_cobertura = int(cobertura_raw)
        except ValueError:
            flash("La cobertura seleccionada no es válida.", "error")
            return redirect(url_for("rutas_profile.profile"))

        if not nro_afiliado:
            flash("Ingresá el número de afiliado o elegí la opción Particular.", "error")
            return redirect(url_for("rutas_profile.profile"))
    else:
        id_cobertura = None
        nro_afiliado = None

    try:
        actualizar_email(email, id_cobertura, nro_afiliado)
        flash("Datos actualizados.", "success")
    except ErrorAPI as e:
        if e.status == 401:
            return _sesion_vencida()
        flash(e.mensaje, "error")

    return redirect(url_for("rutas_profile.profile"))


@profile_routes.route("/profile/password", methods=["POST"])
def actualizar_password():
    if "access_token" not in session:
        return redirect(url_for("rutas_auth.login"))

    nueva = request.form.get("nueva_password", "")
    repetir = request.form.get("confirmar_password", "")

    if not nueva or not repetir:
        flash("Completá todos los campos.", "error")
    elif nueva != repetir:
        flash("Las contraseñas nuevas no coinciden.", "error")
    else:
        try:
            cambiar_password(nueva)
            flash("Contraseña actualizada.", "success")
        except ErrorAPI as e:
            if e.status == 401:
                return _sesion_vencida()
            flash(e.mensaje, "error")

    return redirect(url_for("rutas_profile.profile"))