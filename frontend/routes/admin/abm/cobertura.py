from flask import Blueprint, render_template, request, redirect, url_for

cobertura_routes = Blueprint('rutas_admin_cobertura', __name__)


# DATOS DE PRUEBA
def listar_coberturas():
    return [
        {"id": 1, "nombre": "Galeno", "cantidad_medicos": 4},
        {"id": 2, "nombre": "IOMA", "cantidad_medicos": 12},
        {"id": 3, "nombre": "OSDE", "cantidad_medicos": 14},
        {"id": 4, "nombre": "PAMI", "cantidad_medicos": 28},
        {"id": 5, "nombre": "Swiss Medical", "cantidad_medicos": 22}
    ]


# LISTADO DE COBERTURAS
@cobertura_routes.route('/admin/coberturas')
def obtener_coberturas():

    coberturas = listar_coberturas()

    return render_template(
        'admin/abm/coberturas/index.html',
        coberturas=coberturas
    )


# DETALLE DE UNA COBERTURA
@cobertura_routes.route('/admin/coberturas/<int:cobertura_id>')
def detalle_cobertura(cobertura_id):

    coberturas = listar_coberturas()

    cobertura = next(
        (c for c in coberturas if c["id"] == cobertura_id),
        None
    )

    if cobertura is None:
        return "Cobertura no encontrada", 404

    medicos = [
        {
            "id": 1,
            "nombre": "Dr. Nombre Completo",
            "iniciales": "NC"
        },
        {
            "id": 2,
            "nombre": "Dr. Nombre Completo",
            "iniciales": "NC"
        },
        {
            "id": 3,
            "nombre": "Dr. Nombre Completo",
            "iniciales": "NC"
        },
        {
            "id": 4,
            "nombre": "Dr. Nombre Completo",
            "iniciales": "NC"
        }
    ]

    return render_template(
        'admin/abm/coberturas/detalle.html',
        cobertura=cobertura,
        medicos=medicos
    )


# CREAR COBERTURA
@cobertura_routes.route('/admin/coberturas/crear', methods=['POST'])
def crear_cobertura():

    nombre = request.form.get('nombre', '').strip()

    if not nombre:
        return "El nombre de la cobertura es obligatorio", 400

    # TODO: guardar la cobertura en la base de datos.

    return redirect(
        url_for('rutas_admin_cobertura.obtener_coberturas')
    )

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
            'rutas_admin_cobertura.detalle_cobertura',
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

    return redirect(url_for('rutas_admin_cobertura.obtener_coberturas'))
