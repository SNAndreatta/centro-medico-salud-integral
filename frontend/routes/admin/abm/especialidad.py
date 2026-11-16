from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from src.api import ErrorAPI, api
from src.permisos import requiere_rol

especialidad_routes = Blueprint('rutas_admin_especialidad', __name__)


# =================================
# NORMALIZACIÓN DE DATOS
# =================================

def _iniciales(nombre, apellido):
    return f"{(nombre or ' ')[0]}{(apellido or ' ')[0]}".upper().strip() or 'NC'


def _normalizar_medico(medico):
    return {
        'id': int(medico['id_medico']),
        'id_usuario': int(medico['id_usuario']),
        'nombre': f"{medico['nombre']} {medico['apellido']}".strip(),
        'iniciales': _iniciales(medico['nombre'], medico['apellido']),
    }


def _listar_medicos_por_especialidad():
    medicos = {}

    try:
        datos = api('GET', '/medicos')
    except ErrorAPI:
        return medicos

    for medico in datos.get('medicos', []):
        id_especialidad = medico.get('id_especialidad')
        if id_especialidad is None:
            continue

        medicos.setdefault(int(id_especialidad), []).append(
            _normalizar_medico(medico)
        )

    return medicos


def _listar_especialidades():
    datos = api('GET', '/especialidades')
    medicos = _listar_medicos_por_especialidad()

    return [
        {
            'id': int(especialidad['id_especialidad']),
            'nombre': especialidad['nombre_especialidad'],
            'cantidad_medicos': int(
                especialidad.get('cantidad_medicos') or 0
            ),
            'medicos': medicos.get(
                int(especialidad['id_especialidad']),
                [],
            ),
        }
        for especialidad in datos.get('especialidades', [])
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
        api("POST", "/especialidades", json={"nombre": nombre})
        flash("Especialidad creada correctamente.", "success")
    except ErrorAPI as e:
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
        api(
            "PUT",
            f"/especialidades/{especialidad_id}",
            json={"nombre": nombre},
        )
        flash("Especialidad actualizada correctamente.", "success")
    except ErrorAPI as e:
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
        api("DELETE", f"/especialidades/{especialidad_id}")
        flash("Especialidad eliminada correctamente.", "success")
    except ErrorAPI as e:
        flash(e.mensaje, "error")

    return redirect(
        url_for("rutas_admin_especialidad.obtener_especialidades")
    )
