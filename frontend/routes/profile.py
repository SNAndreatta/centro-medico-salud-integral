from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from src.api import ErrorAPI
from src.api_paciente import (
    perfil_paciente, proximos_turnos_paciente, actualizar_email, cambiar_password,
)

profile_routes = Blueprint('rutas_profile', __name__)

USUARIOS_DE_PRUEBA = {
    "medico": {
        "iniciales": "MG", "nombre": "María", "apellido": "González",
        "fecha_registro": "15/03/2025", "email": "maria.gonzalez@example.com",
        "documento": "30123456", "fecha_nacimiento": "12/05/1985",
        "matricula": "123456",
    },
    "recepcion": {
        "iniciales": "LC", "nombre": "Lucía", "apellido": "Castro",
        "fecha_registro": "20/04/2025", "email": "lucia.castro@example.com",
        "documento": "32456789", "fecha_nacimiento": "08/09/1990",
    },
    "admin": {
        "iniciales": "AR", "nombre": "Ana", "apellido": "Rodríguez",
        "fecha_registro": "01/02/2025", "email": "ana.rodriguez@example.com",
        "documento": "28901234", "fecha_nacimiento": "17/07/1980",
    },
}

ALIAS_ROL = {"administrador": "admin", "recepcionista": "recepcion"}


def _sesion_vencida():
    session.clear()
    flash("Tu sesión expiró. Iniciá sesión de nuevo.", "error")
    return redirect(url_for("rutas_auth.login"))


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
            nombre = session.get("nombre", "")
            apellido = session.get("apellido", "")
            usuario = {
                "nombre": nombre, "apellido": apellido,
                "iniciales": ((nombre[:1] + apellido[:1]).upper() or "NC"),
                "email": "", "documento": "", "fecha_nacimiento": "-",
                "fecha_registro": "-", "numero_afiliado": "-", "cobertura": "-",
            }
            proximos = []

        return render_template("profile.html", rol=rol, usuario=usuario,
                               proximos_turnos=proximos)

    clave = ALIAS_ROL.get(rol, rol)
    if clave not in USUARIOS_DE_PRUEBA:
        clave = "recepcion"
    usuario = dict(USUARIOS_DE_PRUEBA[clave])
    usuario["nombre"] = session.get("nombre") or usuario["nombre"]
    usuario["apellido"] = session.get("apellido") or usuario["apellido"]
    return render_template("profile.html", rol=rol, usuario=usuario)


@profile_routes.route("/profile/actualizar", methods=["POST"])
def actualizar_perfil():
    if "access_token" not in session or session.get("rol") != "paciente":
        return redirect(url_for("rutas_auth.login"))

    email = request.form.get("email", "").strip().lower()
    if not email:
        flash("Ingresá un correo electrónico.", "error")
    else:
        try:
            actualizar_email(email)
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