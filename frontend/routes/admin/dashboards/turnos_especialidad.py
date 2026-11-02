from flask import Blueprint, render_template

turnos_especialidad_admin_routes = Blueprint('rutas_admin_turnos_especialidad', __name__)

@turnos_especialidad_admin_routes.route("/admin/turnos-especialidad")
def turnos_especialidad():

    especialidades = [
        {
            "nombre": "Cardiología",
            "total_turnos": 153,
            "turnos": [
                {
                    "iniciales": "NC",
                    "nombre": "Dr. Nombre Completo",
                    "hora": "15:00 pm.",
                    "fecha": "Día - Mes - Año",
                    "consultorio": "123"
                },
                {
                    "iniciales": "NC",
                    "nombre": "Dr. Nombre Completo",
                    "hora": "15:00 pm.",
                    "fecha": "Día - Mes - Año",
                    "consultorio": "123"
                },
                {
                    "iniciales": "NC",
                    "nombre": "Dr. Nombre Completo",
                    "hora": "15:00 pm.",
                    "fecha": "Día - Mes - Año",
                    "consultorio": "123"
                }
            ]
        },
        {
            "nombre": "Clínica médica",
            "total_turnos": 153,
            "turnos": [
                {
                    "iniciales": "NC",
                    "nombre": "Dr. Nombre Completo",
                    "hora": "15:00 pm.",
                    "fecha": "Día - Mes - Año",
                    "consultorio": "123"
                },
                {
                    "iniciales": "NC",
                    "nombre": "Dr. Nombre Completo",
                    "hora": "15:00 pm.",
                    "fecha": "Día - Mes - Año",
                    "consultorio": "123"
                },
                {
                    "iniciales": "NC",
                    "nombre": "Dr. Nombre Completo",
                    "hora": "15:00 pm.",
                    "fecha": "Día - Mes - Año",
                    "consultorio": "123"
                }
            ]
        }
    ]

    return render_template(
        "admin/dashboards/turnos_especialidad.html",
        especialidades=especialidades
    )