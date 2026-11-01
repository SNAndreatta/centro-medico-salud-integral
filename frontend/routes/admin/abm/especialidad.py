from flask import Blueprint, render_template, request, redirect, url_for

especialidad_routes = Blueprint('rutas_especialidad_prefijo_api', __name__)

# Médicos simulados
medicos = [
    {"id": "1", "nombre_completo": "Dr. Nombre Completo"},
    {"id": "2", "nombre_completo": "Dra. Nombre Completo"},
    {"id": "3", "nombre_completo": "Dr. Juan Pérez"},
    {"id": "4", "nombre_completo": "Dra. María López"},
]


# Especialidades simuladas
especialidades = [
    {
        "id": "987654321",
        "nombre": "Cardiología",
        "medicos_ids": ["1", "2", "3"],
    },
    {
        "id": "987654322",
        "nombre": "Dermatología",
        "medicos_ids": ["1", "2"],
    },
    {
        "id": "987654323",
        "nombre": "Oftalmología",
        "medicos_ids": ["2", "3"],
    },
    {
        "id": "987654324",
        "nombre": "Clínica médica",
        "medicos_ids": ["1", "2", "3", "4"],
    },
    {
        "id": "987654325",
        "nombre": "Pediatría",
        "medicos_ids": ["1", "4"],
    },
]


# Mostrar especialidades
@especialidad_routes.route("/especialidades/")
def especialidades_index():

    # Calculamos la cantidad de médicos de cada especialidad
    for especialidad in especialidades:
        especialidad["cantidad_medicos"] = len(especialidad["medicos_ids"])

    return render_template(
        "/admin/abm/especialidades/index.html",
        especialidades=especialidades,
        medicos=medicos
    )


# Crear especialidad
@especialidad_routes.route("/especialidades/crear", methods=["POST"])
def crear_especialidad():

    nombre = request.form.get("nombre", "").strip()
    medicos_seleccionados = request.form.getlist("medicos")

    if not nombre:
        return redirect(url_for("especialidades_index"))

    nuevo_id = str(
        max(int(e["id"]) for e in especialidades) + 1
    ) if especialidades else "1"

    especialidades.append({
        "id": nuevo_id,
        "nombre": nombre,
        "medicos_ids": medicos_seleccionados
    })

    return redirect(url_for("especialidades_index"))


# Editar especialidad
@especialidad_routes.route("/especialidades/editar/<id_especialidad>", methods=["POST"])
def editar_especialidad(id_especialidad):

    nombre = request.form.get("nombre", "").strip()
    medicos_seleccionados = request.form.getlist("medicos")

    for especialidad in especialidades:
        if especialidad["id"] == id_especialidad:
            if nombre:
                especialidad["nombre"] = nombre

            especialidad["medicos_ids"] = medicos_seleccionados
            break

    return redirect(url_for("especialidades_index"))


# Eliminar especialidad
@especialidad_routes.route("/especialidades/eliminar/<id_especialidad>", methods=["POST"])
def eliminar_especialidad(id_especialidad):

    for especialidad in especialidades:
        if especialidad["id"] == id_especialidad:
            especialidades.remove(especialidad)
            break

    return redirect(url_for("especialidades_index"))