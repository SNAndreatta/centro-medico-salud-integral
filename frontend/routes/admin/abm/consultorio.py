from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from src.api import ErrorAPI
from src.api_catalogos import (
    crear_consultorio as api_crear_consultorio,
    editar_consultorio as api_editar_consultorio,
    eliminar_consultorio as api_eliminar_consultorio,
    obtener_consultorios as api_obtener_consultorios,
)
from src.errores import es_sesion_vencida, sesion_vencida
from src.permisos import requiere_rol

consultorio_routes = Blueprint(
    'rutas_admin_consultorio',
    __name__
)

# Pisos que se ofrecen por defecto en los formularios.
PISOS_BASE = [1, 2, 3]


def _pisos_disponibles(consultorios):
    pisos = {piso for piso in PISOS_BASE}
    pisos.update(
        consultorio['piso']
        for consultorio in consultorios
        if consultorio['piso'] is not None
    )
    return sorted(pisos)


# =========================================
# LISTADO DE CONSULTORIOS
# =========================================

@consultorio_routes.route("/consultorios")
@requiere_rol("admin")
def obtener_consultorios():
    consultorios = []
    error = None

    try:
        consultorios = api_obtener_consultorios()
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        error = e.mensaje

    return render_template(
        "admin/abm/consultorios/index.html",
        consultorios=consultorios,
        pisos=_pisos_disponibles(consultorios),
        error=error,
    )


# =========================================
# CREAR CONSULTORIO
# =========================================

@consultorio_routes.route("/consultorios/crear", methods=["POST"])
@requiere_rol("admin")
def crear_consultorio():
    piso = request.form.get("piso", type=int)
    numero = request.form.get("numero", type=int)

    try:
        api_crear_consultorio(numero, piso)
        flash("Consultorio creado correctamente.", "success")
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, "error")

    return redirect(
        url_for("rutas_admin_consultorio.obtener_consultorios")
    )


# =========================================
# EDITAR CONSULTORIO
# =========================================

@consultorio_routes.route(
    "/consultorios/<int:consultorio_id>/editar",
    methods=["POST"]
)
@requiere_rol("admin")
def editar_consultorio(consultorio_id):
    piso = request.form.get("piso", type=int)
    numero = request.form.get("numero", type=int)

    try:
        api_editar_consultorio(consultorio_id, numero, piso)
        flash("Consultorio actualizado correctamente.", "success")
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, "error")

    return redirect(
        url_for("rutas_admin_consultorio.obtener_consultorios")
    )


# =========================================
# ELIMINAR CONSULTORIO
# =========================================

@consultorio_routes.route(
    "/consultorios/<int:consultorio_id>/eliminar",
    methods=["POST"]
)
@requiere_rol("admin")
def eliminar_consultorio(consultorio_id):
    try:
        api_eliminar_consultorio(consultorio_id)
        flash("Consultorio eliminado correctamente.", "success")
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, "error")

    return redirect(
        url_for("rutas_admin_consultorio.obtener_consultorios")
    )
