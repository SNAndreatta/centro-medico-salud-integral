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
    crear_cobertura as api_crear_cobertura,
    editar_cobertura as api_editar_cobertura,
    eliminar_cobertura as api_eliminar_cobertura,
    listar_medicos,
    obtener_coberturas as api_obtener_coberturas,
)
from src.errores import es_sesion_vencida, sesion_vencida
from src.permisos import requiere_rol

cobertura_routes = Blueprint('rutas_admin_cobertura', __name__)


# LISTADO DE COBERTURAS
@cobertura_routes.route('/coberturas')
@requiere_rol("admin")
def obtener_coberturas():
    coberturas = []
    error = None

    try:
        coberturas = api_obtener_coberturas()
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        error = e.mensaje

    return render_template(
        'admin/abm/coberturas/index.html',
        coberturas=coberturas,
        error=error,
    )


# DETALLE DE UNA COBERTURA
@cobertura_routes.route('/coberturas/<int:cobertura_id>')
@requiere_rol("admin")
def detalle_cobertura(cobertura_id):
    try:
        coberturas = api_obtener_coberturas()
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_admin_cobertura.obtener_coberturas'))

    cobertura = next(
        (c for c in coberturas if c['id'] == cobertura_id),
        None,
    )

    if cobertura is None:
        return 'Cobertura no encontrada', 404

    medicos = []

    try:
        medicos = listar_medicos({'id_cobertura': cobertura_id})
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')

    return render_template(
        'admin/abm/coberturas/detalle.html',
        cobertura=cobertura,
        medicos=medicos,
    )


# CREAR COBERTURA
@cobertura_routes.route('/coberturas/crear', methods=['POST'])
@requiere_rol("admin")
def crear_cobertura():
    nombre = request.form.get('nombre', '').strip()

    try:
        api_crear_cobertura(nombre)
        flash('Cobertura creada correctamente.', 'success')
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')

    return redirect(
        url_for('rutas_admin_cobertura.obtener_coberturas')
    )


# EDITAR COBERTURA
@cobertura_routes.route(
    '/coberturas/<int:cobertura_id>/editar',
    methods=['POST']
)
@requiere_rol("admin")
def editar_cobertura(cobertura_id):
    nombre = request.form.get('nombre', '').strip()

    try:
        api_editar_cobertura(cobertura_id, nombre)
        flash('Cobertura actualizada correctamente.', 'success')
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')

    return redirect(
        url_for(
            'rutas_admin_cobertura.detalle_cobertura',
            cobertura_id=cobertura_id,
        )
    )


# ELIMINAR COBERTURA
@cobertura_routes.route(
    '/coberturas/<int:cobertura_id>/eliminar',
    methods=['POST']
)
@requiere_rol("admin")
def eliminar_cobertura(cobertura_id):
    try:
        api_eliminar_cobertura(cobertura_id)
        flash('Cobertura eliminada correctamente.', 'success')
        return redirect(
            url_for('rutas_admin_cobertura.obtener_coberturas')
        )
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')
        return redirect(
            url_for(
                'rutas_admin_cobertura.detalle_cobertura',
                cobertura_id=cobertura_id,
            )
        )
