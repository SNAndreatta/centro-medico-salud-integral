from flask import Blueprint
from flask import render_template, request

consultorio_routes = Blueprint('rutas_admin_consultorio', __name__)

# Datos simulados
consultorios = [
    {"id": "987654321", "piso": 1, "numero": 111},
    {"id": "987654322", "piso": 2, "numero": 222},
    {"id": "987654323", "piso": 3, "numero": 333},
    {"id": "987654324", "piso": 4, "numero": 444},
    {"id": "987654325", "piso": 5, "numero": 555},
]

pisos_disponibles = [1, 2, 3, 4, 5]


@consultorio_routes.route("/consultorios")
def consultorios_view():
    return render_template(
        "/admin/abm/consultorios/index.html",
        consultorios=consultorios,
        pisos=pisos_disponibles
    )


@consultorio_routes.route("/consultorios/crear", methods=["POST"])
def crear_consultorio():
    piso = request.form.get("piso", type=int)
    numero = request.form.get("numero", type=int)

    if piso not in pisos_disponibles or numero is None or numero < 1:
        return render_template(
        '/admin/abm/consultorios/index.html'
        )

    # Evitar repetir un consultorio con el mismo piso y número
    existe = any(
        consultorio["piso"] == piso
        and consultorio["numero"] == numero
        for consultorio in consultorios
    )

    if not existe:
        nuevo_id = str(
            max(int(c["id"]) for c in consultorios) + 1
        ) if consultorios else "1"

        consultorios.append({
            "id": nuevo_id,
            "piso": piso,
            "numero": numero
        })

    return render_template(
        '/admin/abm/consultorios/index.html'
        )