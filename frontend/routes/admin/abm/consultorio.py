
from flask import Blueprint, render_template, request, redirect, url_for


consultorio_routes = Blueprint(
    'rutas_admin_consultorio',
    __name__
)


# =========================================
# DATOS DE CONSULTORIOS
# =========================================

consultorios = [

    # PISO 1
    {"id": "987654321", "piso": 1, "numero": 111},
    {"id": "987654322", "piso": 1, "numero": 112},
    {"id": "987654323", "piso": 1, "numero": 113},
    {"id": "987654324", "piso": 1, "numero": 114},

    # PISO 2
    {"id": "987654325", "piso": 2, "numero": 201},
    {"id": "987654326", "piso": 2, "numero": 202},
    {"id": "987654327", "piso": 2, "numero": 203},
    {"id": "987654328", "piso": 2, "numero": 204},

    # PISO 3
    {"id": "987654329", "piso": 3, "numero": 301},
    {"id": "987654330", "piso": 3, "numero": 302},
    {"id": "987654331", "piso": 3, "numero": 303},
    {"id": "987654332", "piso": 3, "numero": 304},

]


pisos_disponibles = [1, 2, 3]


# =========================================
# FUNCIONES AUXILIARES
# =========================================

def buscar_consultorio(consultorio_id):

    return next(
        (
            consultorio
            for consultorio in consultorios
            if consultorio["id"] == str(consultorio_id)
        ),
        None
    )


def existe_consultorio(piso, numero, excluir_id=None):

    return any(
        consultorio["piso"] == piso
        and consultorio["numero"] == numero
        and consultorio["id"] != str(excluir_id)
        for consultorio in consultorios
    )


def generar_nuevo_id():

    if not consultorios:
        return "1"

    return str(
        max(int(c["id"]) for c in consultorios) + 1
    )


# =========================================
# LISTADO DE CONSULTORIOS
# =========================================

@consultorio_routes.route("/consultorios")
def obtener_consultorios():

    return render_template(
        "admin/abm/consultorios/index.html",
        consultorios=consultorios,
        pisos=pisos_disponibles
    )


# =========================================
# CREAR CONSULTORIO
# =========================================

@consultorio_routes.route("/consultorios/crear", methods=["POST"])
def crear_consultorio():

    piso = request.form.get("piso", type=int)

    numero = request.form.get("numero", type=int)

    # Validaciones.
    if (
        piso not in pisos_disponibles
        or numero is None
        or numero < 1
    ):
        return redirect(
            url_for("rutas_admin_consultorio.obtener_consultorios")
        )

    # Evitar consultorios duplicados en el mismo piso.
    if existe_consultorio(piso, numero):

        return redirect(
            url_for("rutas_admin_consultorio.obtener_consultorios")
        )

    # Crear consultorio.
    nuevo_consultorio = {
        "id": generar_nuevo_id(),
        "piso": piso,
        "numero": numero
    }

    consultorios.append(nuevo_consultorio)

    return redirect(
        url_for("rutas_admin_consultorio.obtener_consultorios")
    )


# =========================================
# EDITAR CONSULTORIO
# =========================================

@consultorio_routes.route(
    "/consultorios/<consultorio_id>/editar",
    methods=["POST"]
)
def editar_consultorio(consultorio_id):

    consultorio = buscar_consultorio(consultorio_id)

    if consultorio is None:
        return redirect(
            url_for("rutas_admin_consultorio.obtener_consultorios")
        )

    piso = request.form.get("piso", type=int)

    numero = request.form.get("numero", type=int)

    # Validar datos.
    if (
        piso not in pisos_disponibles
        or numero is None
        or numero < 1
    ):
        return redirect(
            url_for("rutas_admin_consultorio.obtener_consultorios")
        )

    # Evitar duplicados, excepto el propio consultorio.
    if existe_consultorio(
        piso,
        numero,
        excluir_id=consultorio_id
    ):

        return redirect(
            url_for("rutas_admin_consultorio.obtener_consultorios")
        )

    # Actualizar datos.
    consultorio["piso"] = piso

    consultorio["numero"] = numero

    return redirect(
        url_for("rutas_admin_consultorio.obtener_consultorios")
    )


# =========================================
# ELIMINAR CONSULTORIO
# =========================================

@consultorio_routes.route(
    "/consultorios/<consultorio_id>/eliminar",
    methods=["POST"]
)
def eliminar_consultorio(consultorio_id):

    consultorio = buscar_consultorio(consultorio_id)

    if consultorio is not None:

        consultorios.remove(consultorio)

    return redirect(
        url_for("rutas_admin_consultorio.obtener_consultorios")
    )
