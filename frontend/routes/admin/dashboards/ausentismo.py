from flask import Blueprint, render_template

ausentismo_admin_routes = Blueprint('rutas_ausentismo_admin_prefijo_api', __name__)

@ausentismo_admin_routes.route("/admin/ausentismo")
def ausentismo():

    medicos = [
        {
            "iniciales": "NC",
            "nombre": "Nombre Completo",
            "porcentaje": 17,
            "color": "bg-[#FAD8E0] text-[#E47789]"
        },
        {
            "iniciales": "NC",
            "nombre": "Nombre Completo",
            "porcentaje": 25,
            "color": "bg-[#DDF2F2] text-[#71C9C9]"
        },
        {
            "iniciales": "NC",
            "nombre": "Nombre Completo",
            "porcentaje": 27,
            "color": "bg-[#E6D5E9] text-[#A36BAA]"
        },
        {
            "iniciales": "NC",
            "nombre": "Nombre Completo",
            "porcentaje": 15,
            "color": "bg-[#EFB9B9] text-[#B91C1C]"
        },
        {
            "iniciales": "NC",
            "nombre": "Nombre Completo",
            "porcentaje": 23,
            "color": "bg-[#B6C6D1] text-[#003B5C]"
        },
        {
            "iniciales": "NC",
            "nombre": "Nombre Completo",
            "porcentaje": 12,
            "color": "bg-[#FAD8E0] text-[#E47789]"
        }
    ]

    especialidades = [
        {"nombre": "Cardiología", "porcentaje": 17},
        {"nombre": "Clínica Médica", "porcentaje": 25},
        {"nombre": "Dermatología", "porcentaje": 27},
        {"nombre": "Oftalmología", "porcentaje": 15},
        {"nombre": "Pediatría", "porcentaje": 23},
        {"nombre": "Traumatología", "porcentaje": 12}
    ]

    return render_template(
        "admin/dashboards/ausentismo.html",
        medicos=medicos,
        especialidades=especialidades
    )