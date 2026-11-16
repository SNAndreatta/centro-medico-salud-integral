from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from src.api import ErrorAPI
from src.api_paciente import (
    perfil_paciente, proximos_turnos_paciente, actualizar_datos_paciente,
    cambiar_password, obtener_coberturas, obtener_especialidades,
)
from src.api_usuario import (
    perfil_usuario, actualizar_datos_usuario, actualizar_datos_medico,
    coberturas_medico, agregar_coberturas_medico,
)

profile_routes = Blueprint('rutas_profile', __name__)

ROLES_ADMIN = ("admin", "administrador")
ROLES_RECEPCION = ("recepcion", "recepcionista")


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
        "email": "", "documento": "", "dni": "",
        "fecha_nacimiento": "-", "fecha_nacimiento_iso": "",
        "fecha_registro": "-", "matricula": "-",
    }


def _catalogos_medico(usuario):
    """Especialidades y coberturas que necesita el formulario del médico."""
    especialidades = []
    coberturas_medico_actuales = []
    coberturas_disponibles = []

    try:
        especialidades = obtener_especialidades()
    except ErrorAPI as e:
        print("ERROR ESPECIALIDADES:", e.status, e.mensaje, flush=True)
        if e.status == 401:
            raise

    id_medico = usuario.get("id_medico")
    if not id_medico:
        return especialidades, coberturas_medico_actuales, coberturas_disponibles

    try:
        coberturas_medico_actuales = coberturas_medico(id_medico)
    except ErrorAPI as e:
        print("ERROR COBERTURAS MEDICO:", e.status, e.mensaje, flush=True)
        if e.status == 401:
            raise

    try:
        catalogo = obtener_coberturas()
    except ErrorAPI as e:
        print("ERROR COBERTURAS:", e.status, e.mensaje, flush=True)
        if e.status == 401:
            raise
        catalogo = []

    ids_asociadas = {c["id"] for c in coberturas_medico_actuales}
    coberturas_disponibles = [c for c in catalogo if c["id"] not in ids_asociadas]

    return especialidades, coberturas_medico_actuales, coberturas_disponibles


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

    especialidades = []
    coberturas_medico_actuales = []
    coberturas_disponibles = []

    if rol == "medico":
        try:
            (especialidades,
             coberturas_medico_actuales,
             coberturas_disponibles) = _catalogos_medico(usuario)
        except ErrorAPI as e:
            if e.status == 401:
                return _sesion_vencida()
            flash(e.mensaje, "error")

    return render_template(
        "profile.html",
        rol=rol,
        usuario=usuario,
        especialidades=especialidades,
        coberturas_medico=coberturas_medico_actuales,
        coberturas_disponibles=coberturas_disponibles,
    )


@profile_routes.route("/profile/actualizar", methods=["POST"])
def actualizar_perfil():
    if "access_token" not in session:
        return redirect(url_for("rutas_auth.login"))

    rol = session.get("rol", "paciente")

    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    dni = request.form.get("dni", "").strip()
    mail = request.form.get("mail", "").strip().lower()
    fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()

    if not all([nombre, apellido, dni, mail]):
        flash("Completá nombre, apellido, DNI y mail.", "error")
        return redirect(url_for("rutas_profile.profile"))

    datos_usuario = {
        "nombre": nombre,
        "apellido": apellido,
        "dni": dni,
        "correo_electronico": mail,
    }
    if fecha_nacimiento:
        datos_usuario["fecha_nacimiento"] = fecha_nacimiento

    # Para médicos validamos los campos extra antes de guardar nada.
    id_medico = None
    id_especialidad = None
    matricula = None
    if rol == "medico":
        try:
            perfil = perfil_usuario()
            id_medico = perfil.get("id_medico")
        except ErrorAPI as e:
            if e.status == 401:
                return _sesion_vencida()
            flash(e.mensaje, "error")
            return redirect(url_for("rutas_profile.profile"))

        id_especialidad = request.form.get("id_especialidad", type=int)
        matricula = request.form.get("matricula", "").strip()

        if not id_medico or not id_especialidad or not matricula:
            flash("Para un médico tenés que indicar especialidad y matrícula.", "error")
            return redirect(url_for("rutas_profile.profile"))

    # Paciente: además de los datos personales se guarda la cobertura.
    datos_paciente = dict(datos_usuario)
    if rol == "paciente":
        cobertura_raw = request.form.get("id_cobertura", "").strip()
        nro_afiliado = request.form.get("nro_afiliado", "").strip()

        # id_cobertura y nro_afiliado van juntos: ambos nulos = particular.
        if cobertura_raw:
            try:
                datos_paciente["id_cobertura"] = int(cobertura_raw)
            except ValueError:
                flash("La cobertura seleccionada no es válida.", "error")
                return redirect(url_for("rutas_profile.profile"))

            if not nro_afiliado:
                flash("Ingresá el número de afiliado o elegí la opción Particular.", "error")
                return redirect(url_for("rutas_profile.profile"))
            datos_paciente["nro_afiliado"] = nro_afiliado
        else:
            datos_paciente["id_cobertura"] = None
            datos_paciente["nro_afiliado"] = None

    try:
        if rol == "paciente":
            actualizar_datos_paciente(datos_paciente)
        else:
            actualizar_datos_usuario(datos_usuario)

            if rol == "medico":
                actualizar_datos_medico(id_medico, {
                    "id_especialidad": id_especialidad,
                    "matricula": matricula,
                })
                agregar_coberturas_medico(
                    id_medico,
                    request.form.getlist("coberturas"),
                )

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

    actual = request.form.get("password_actual", "")
    nueva = request.form.get("nueva_password", "")
    repetir = request.form.get("confirmar_password", "")

    if not actual or not nueva or not repetir:
        flash("Completá todos los campos.", "error")
    elif nueva != repetir:
        flash("Las contraseñas nuevas no coinciden.", "error")
    else:
        try:
            cambiar_password(nueva, actual)
            flash("Contraseña actualizada.", "success")
        except ErrorAPI as e:
            if e.status == 401:
                return _sesion_vencida()
            flash(e.mensaje, "error")

    return redirect(url_for("rutas_profile.profile"))
