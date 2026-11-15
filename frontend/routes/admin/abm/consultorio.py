from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from src.api import ErrorAPI, api

consultorio_routes = Blueprint(
    'rutas_admin_consultorio',
    __name__
)

# Pisos que se ofrecen por defecto en los formularios.
PISOS_BASE = [1, 2, 3]


# =========================================
# NORMALIZACIÓN DE DATOS
# =========================================

def _normalizar_consultorio(consultorio):
    piso = consultorio.get('piso')

    return {
        'id': int(consultorio['id_consultorio']),
        'piso': int(piso) if piso is not None else None,
        'numero': int(consultorio['numero']),
    }


def _listar_consultorios():
    datos = api('GET', '/consultorios')
    return [
        _normalizar_consultorio(consultorio)
        for consultorio in datos.get('consultorios', [])
    ]


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
def obtener_consultorios():
    consultorios = []
    error = None

    try:
        consultorios = _listar_consultorios()
    except ErrorAPI as e:
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
def crear_consultorio():
    piso = request.form.get("piso", type=int)
    numero = request.form.get("numero", type=int)

    try:
        api("POST", "/consultorios", json={"numero": numero, "piso": piso})
        flash("Consultorio creado correctamente.", "success")
    except ErrorAPI as e:
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
def editar_consultorio(consultorio_id):
    piso = request.form.get("piso", type=int)
    numero = request.form.get("numero", type=int)

    try:
        api(
            "PUT",
            f"/consultorios/{consultorio_id}",
            json={"numero": numero, "piso": piso},
        )
        flash("Consultorio actualizado correctamente.", "success")
    except ErrorAPI as e:
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
def eliminar_consultorio(consultorio_id):
    try:
        api("DELETE", f"/consultorios/{consultorio_id}")
        flash("Consultorio eliminado correctamente.", "success")
    except ErrorAPI as e:
        flash(e.mensaje, "error")

    return redirect(
        url_for("rutas_admin_consultorio.obtener_consultorios")
    )
