
from flask import Blueprint, render_template, request, redirect, url_for
from datetime import date


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
# HORARIOS SIMULADOS
# =========================================

def obtener_horarios_consultorio(consultorio_id):

    """
    Devuelve los horarios de un consultorio.

    disponible = True  -> Horario disponible.
    disponible = False -> Horario no disponible.
    """

    horarios = [
        "08:00",
        "08:30",
        "09:00",
        "09:30",
        "10:00",
        "10:30",
        "11:00",
        "11:30",
        "12:00",
        "12:30",
        "13:00",
        "13:30",
        "14:00",
        "14:30",
        "15:00",
        "15:30",
    ]

    # Patrones de disponibilidad de cada consultorio.
    # True = Disponible.
    # False = No disponible.

    disponibilidad = {

        111: [True, True, False, True, False, True, True, False,
              True, True, False, True, True, False, True, True],

        112: [False, True, True, False, True, True, False, True,
              True, False, True, True, False, True, True, False],

        113: [True, False, True, True, True, False, True, False,
              True, True, True, False, True, False, True, True],

        114: [True, True, True, False, False, True, True, True,
              False, True, False, True, True, True, False, True],

        201: [False, True, True, False, True, True, True, False,
              True, False, True, True, False, True, True, True],

        202: [True, False, True, True, False, True, False, True,
              True, True, False, True, True, False, True, False],

        203: [True, True, False, True, True, False, True, True,
              False, True, True, False, True, True, False, True],

        204: [False, True, False, True, True, True, False, True,
              True, False, True, False, True, True, True, False],

        301: [True, False, True, True, False, True, True, False,
              True, True, False, True, False, True, True, True],

        302: [True, True, False, True, True, False, True, True,
              False, True, False, True, True, False, True, True],

        303: [False, True, True, True, False, True, False, True,
              True, True, False, True, True, False, True, False],

        304: [True, False, True, False, True, True, True, False,
              True, False, True, True, False, True, True, True],

    }

    # Buscamos el consultorio por su identificador.
    consultorio = next(
        (
            c for c in consultorios
            if c["id"] == str(consultorio_id)
        ),
        None
    )

    if consultorio is None:
        return []

    numero = consultorio["numero"]

    # Obtenemos el patrón correspondiente.
    patron = disponibilidad.get(numero)

    if patron is None:
        patron = [True] * len(horarios)

    # Construimos la lista de horarios.
    resultado = []

    for hora, disponible in zip(horarios, patron):

        resultado.append({
            "hora": hora,
            "disponible": disponible
        })

    return resultado


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

    if piso not in pisos_disponibles or numero is None or numero < 1:

        return redirect(
            url_for("rutas_admin_consultorio.obtener_consultorios")
        )

    existe = any(
        c["piso"] == piso and c["numero"] == numero
        for c in consultorios
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

    return redirect(
        url_for("rutas_admin_consultorio.obtener_consultorios")
    )


# =========================================
# DISPONIBILIDAD DE CONSULTORIOS
# =========================================

@consultorio_routes.route("/disponibilidad-consultorios")
def disponibilidad_consultorios():

    # -------------------------------------
    # FECHA SELECCIONADA
    # -------------------------------------

    fecha = request.args.get("fecha")

    if fecha:

        try:
            date.fromisoformat(fecha)

        except ValueError:
            fecha = date.today().isoformat()

    else:
        fecha = date.today().isoformat()


    # -------------------------------------
    # AGRUPAR CONSULTORIOS POR PISO
    # -------------------------------------

    pisos = []

    for numero_piso in pisos_disponibles:

        consultorios_del_piso = []

        for consultorio in consultorios:

            if consultorio["piso"] == numero_piso:

                consultorio_con_horarios = {
                    **consultorio,

                    "horarios": obtener_horarios_consultorio(
                        consultorio["id"]
                    )
                }

                consultorios_del_piso.append(
                    consultorio_con_horarios
                )

        # Agregamos únicamente los pisos que tienen consultorios.
        if consultorios_del_piso:

            pisos.append({
                "numero": numero_piso,
                "consultorios": consultorios_del_piso
            })


    # -------------------------------------
    # ENVIAR INFORMACIÓN A LA PLANTILLA
    # -------------------------------------

    return render_template(
        "admin/dashboards/disponibilidad_consultorio.html",
        pisos=pisos,
        fecha=fecha
    )
