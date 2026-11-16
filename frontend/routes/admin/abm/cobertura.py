from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from src.api import ErrorAPI, api

cobertura_routes = Blueprint('rutas_admin_cobertura', __name__)


# =================================
# NORMALIZACIÓN DE DATOS
# =================================

def _iniciales(nombre, apellido):
    return f"{(nombre or ' ')[0]}{(apellido or ' ')[0]}".upper().strip() or 'NC'


def _normalizar_cobertura(cobertura):
    return {
        'id': int(cobertura['id_cobertura']),
        'nombre': cobertura['nombre'],
        'cantidad_medicos': int(cobertura.get('cantidad_medicos') or 0),
    }


def _listar_coberturas():
    datos = api('GET', '/coberturas')
    return [
        _normalizar_cobertura(cobertura)
        for cobertura in datos.get('coberturas', [])
    ]


def _normalizar_medico(medico):
    return {
        'id': int(medico['id_medico']),
        'id_usuario': int(medico['id_usuario']),
        'nombre': f"{medico['nombre']} {medico['apellido']}".strip(),
        'iniciales': _iniciales(medico['nombre'], medico['apellido']),
        'especialidad': medico.get('nombre_especialidad'),
        'matricula': medico.get('matricula'),
    }


# LISTADO DE COBERTURAS
@cobertura_routes.route('/coberturas')
def obtener_coberturas():
    coberturas = []
    error = None

    try:
        coberturas = _listar_coberturas()
    except ErrorAPI as e:
        error = e.mensaje

    return render_template(
        'admin/abm/coberturas/index.html',
        coberturas=coberturas,
        error=error,
    )


# DETALLE DE UNA COBERTURA
@cobertura_routes.route('/coberturas/<int:cobertura_id>')
def detalle_cobertura(cobertura_id):
    try:
        coberturas = _listar_coberturas()
    except ErrorAPI as e:
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
        datos = api('GET', '/medicos', params={'id_cobertura': cobertura_id})
        medicos = [
            _normalizar_medico(medico)
            for medico in datos.get('medicos', [])
        ]
    except ErrorAPI as e:
        flash(e.mensaje, 'error')

    return render_template(
        'admin/abm/coberturas/detalle.html',
        cobertura=cobertura,
        medicos=medicos,
    )


# CREAR COBERTURA
@cobertura_routes.route('/coberturas/crear', methods=['POST'])
def crear_cobertura():
    nombre = request.form.get('nombre', '').strip()

    try:
        api('POST', '/coberturas', json={'nombre': nombre})
        flash('Cobertura creada correctamente.', 'success')
    except ErrorAPI as e:
        flash(e.mensaje, 'error')

    return redirect(
        url_for('rutas_admin_cobertura.obtener_coberturas')
    )


# EDITAR COBERTURA
@cobertura_routes.route(
    '/coberturas/<int:cobertura_id>/editar',
    methods=['POST']
)
def editar_cobertura(cobertura_id):
    nombre = request.form.get('nombre', '').strip()

    try:
        api('PUT', f'/coberturas/{cobertura_id}', json={'nombre': nombre})
        flash('Cobertura actualizada correctamente.', 'success')
    except ErrorAPI as e:
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
def eliminar_cobertura(cobertura_id):
    try:
        api('DELETE', f'/coberturas/{cobertura_id}')
        flash('Cobertura eliminada correctamente.', 'success')
        return redirect(
            url_for('rutas_admin_cobertura.obtener_coberturas')
        )
    except ErrorAPI as e:
        flash(e.mensaje, 'error')
        return redirect(
            url_for(
                'rutas_admin_cobertura.detalle_cobertura',
                cobertura_id=cobertura_id,
            )
        )
