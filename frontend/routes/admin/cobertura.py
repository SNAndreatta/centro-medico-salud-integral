from flask import Blueprint, render_template, request, redirect, url_for

cobertura_routes = Blueprint('rutas_cobertura_prefijo_api', __name__)


# DATOS DE PRUEBA
def obtener_coberturas():
    return [
        {"id": 1, "nombre": "Galeno", "cantidad_planes": 4},
        {"id": 2, "nombre": "IOMA", "cantidad_planes": 12},
        {"id": 3, "nombre": "OSDE", "cantidad_planes": 14},
        {"id": 4, "nombre": "PAMI", "cantidad_planes": 28},
        {"id": 5, "nombre": "Swiss Medical", "cantidad_planes": 22}
    ]


# LISTADO DE COBERTURAS
@cobertura_routes.route('/admin/coberturas')
def listar_coberturas():

    coberturas = obtener_coberturas()

    return render_template(
        'admin/abm/coberturas/index.html',
        coberturas=coberturas
    )


# DETALLE DE UNA COBERTURA
@cobertura_routes.route('/admin/coberturas/<int:cobertura_id>')
def detalle_cobertura(cobertura_id):

    coberturas = obtener_coberturas()

    cobertura = next(
        (c for c in coberturas if c["id"] == cobertura_id),
        None
    )

    if cobertura is None:
        return "Cobertura no encontrada", 404

    planes = [
        {"id": 1, "nombre": "Plan 220"},
        {"id": 2, "nombre": "Plan 330"},
        {"id": 3, "nombre": "Plan 440"},
        {"id": 4, "nombre": "Plan 550"}
    ]

    medicos = [
        {
            "id": 1,
            "nombre": "Dr. Nombre Completo",
            "iniciales": "NC",
            "planes_asociados": 1
        },
        {
            "id": 2,
            "nombre": "Dr. Nombre Completo",
            "iniciales": "NC",
            "planes_asociados": 2
        },
        {
            "id": 3,
            "nombre": "Dr. Nombre Completo",
            "iniciales": "NC",
            "planes_asociados": 2
        },
        {
            "id": 4,
            "nombre": "Dr. Nombre Completo",
            "iniciales": "NC",
            "planes_asociados": 1
        }
    ]

    return render_template(
        'admin/abm/coberturas/detalle.html',
        cobertura=cobertura,
        planes=planes,
        medicos=medicos
    )


# CREAR COBERTURA
@cobertura_routes.route('/admin/coberturas/crear', methods=['POST'])
def crear_cobertura():

    nombre = request.form.get('nombre', '').strip()
    cantidad_planes = request.form.get('cantidad_planes', '0')

    if not nombre:
        return "El nombre de la cobertura es obligatorio", 400

    # TODO: guardar la cobertura en la base de datos.

    return redirect(url_for('rutas_admin_prefijo_api.listar_coberturas'))


# EDITAR COBERTURA
@cobertura_routes.route(
    '/admin/coberturas/<int:cobertura_id>/editar',
    methods=['POST']
)
def editar_cobertura(cobertura_id):

    nombre = request.form.get('nombre', '').strip()

    if not nombre:
        return "El nombre de la cobertura es obligatorio", 400

    # TODO: actualizar la cobertura en la base de datos.

    return redirect(
        url_for(
            'rutas_admin_prefijo_api.detalle_cobertura',
            cobertura_id=cobertura_id
        )
    )


# ELIMINAR COBERTURA
@cobertura_routes.route(
    '/admin/coberturas/<int:cobertura_id>/eliminar',
    methods=['POST']
)
def eliminar_cobertura(cobertura_id):

    # TODO: eliminar la cobertura de la base de datos.
    # Antes de eliminar, verificar si tiene planes o médicos asociados.

    return redirect(url_for('rutas_admin_prefijo_api.listar_coberturas'))


# CREAR PLAN
@cobertura_routes.route(
    '/admin/coberturas/<int:cobertura_id>/planes/crear',
    methods=['POST']
)
def crear_plan(cobertura_id):

    nombre = request.form.get('nombre', '').strip()

    if not nombre:
        return "El nombre del plan es obligatorio", 400

    # TODO: guardar el plan asociado a la cobertura en la base de datos.

    return redirect(
        url_for(
            'rutas_admin_prefijo_api.detalle_cobertura',
            cobertura_id=cobertura_id
        )
    )


# EDITAR PLAN
@cobertura_routes.route(
    '/admin/coberturas/<int:cobertura_id>/planes/<int:plan_id>/editar',
    methods=['POST']
)
def editar_plan(cobertura_id, plan_id):

    nombre = request.form.get('nombre', '').strip()

    if not nombre:
        return "El nombre del plan es obligatorio", 400

    # TODO: actualizar el plan en la base de datos.

    return redirect(
        url_for(
            'rutas_admin_prefijo_api.detalle_cobertura',
            cobertura_id=cobertura_id
        )
    )


# ELIMINAR PLAN
@cobertura_routes.route(
    '/admin/coberturas/<int:cobertura_id>/planes/<int:plan_id>/eliminar',
    methods=['POST']
)
def eliminar_plan(cobertura_id, plan_id):

    # TODO: eliminar el plan de la base de datos.

    return redirect(
        url_for(
            'rutas_admin_prefijo_api.detalle_cobertura',
            cobertura_id=cobertura_id
        )
    )