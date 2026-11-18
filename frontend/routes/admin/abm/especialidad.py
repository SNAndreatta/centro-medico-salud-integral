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
    crear_especialidad as api_crear_especialidad,
    editar_especialidad as api_editar_especialidad,
    eliminar_especialidad as api_eliminar_especialidad,
    listar_medicos,
    obtener_especialidades as api_obtener_especialidades,
)
from src.errores import es_sesion_vencida, sesion_vencida
from src.permisos import requiere_rol

especialidad_routes = Blueprint('rutas_admin_especialidad', __name__)


def _listar_especialidades():
    especialidades = api_obtener_especialidades()
    medicos = {}

    for medico in listar_medicos():
        if medico['id_especialidad'] is None:
            continue
        medicos.setdefault(int(medico['id_especialidad']), []).append({
            'id': medico['id'],
            'id_usuario': medico['id_usuario'],
            'nombre': medico['nombre_completo'],
            'iniciales': medico['iniciales'],
        })

    return [
        {
            'id': int(especialidad['id']),
            'nombre': especialidad['nombre'],
            'cantidad_medicos': especialidad['cantidad_medicos'],
            'medicos': medicos.get(int(especialidad['id']), []),
        }
        for especialidad in especialidades
    ]


# MOSTRAR ESPECIALIDADES
@especialidad_routes.route("/especialidades/")
@requiere_rol("admin")
def obtener_especialidades():
    especialidades = []
    error = None

    try:
        especialidades = _listar_especialidades()
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        error = e.mensaje

    return render_template(
        "admin/abm/especialidades/index.html",
        especialidades=especialidades,
        error=error,
    )


# CREAR ESPECIALIDAD
@especialidad_routes.route("/especialidades/crear", methods=["POST"])
@requiere_rol("admin")
def crear_especialidad():
    nombre = request.form.get("nombre", "").strip()

    try:
        api_crear_especialidad(nombre)
        flash("Especialidad creada correctamente.", "success")
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, "error")

    return redirect(
        url_for("rutas_admin_especialidad.obtener_especialidades")
    )


# EDITAR ESPECIALIDAD
@especialidad_routes.route(
    "/especialidades/<int:especialidad_id>/editar",
    methods=["POST"]
)
@requiere_rol("admin")
def editar_especialidad(especialidad_id):
    nombre = request.form.get("nombre", "").strip()

    try:
        api_editar_especialidad(especialidad_id, nombre)
        flash("Especialidad actualizada correctamente.", "success")
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, "error")

    return redirect(
        url_for("rutas_admin_especialidad.obtener_especialidades")
    )


# ELIMINAR ESPECIALIDAD
@especialidad_routes.route(
    "/especialidades/<int:especialidad_id>/eliminar",
    methods=["POST"]
)
@requiere_rol("admin")
def eliminar_especialidad(especialidad_id):
    try:
        api_eliminar_especialidad(especialidad_id)
        flash("Especialidad eliminada correctamente.", "success")
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, "error")

    return redirect(
        url_for("rutas_admin_especialidad.obtener_especialidades")
    )
