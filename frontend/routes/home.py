from flask import Blueprint, render_template, session

home_routes = Blueprint('rutas_home', __name__)

@home_routes.route("/home")
def home():

    # ROL TEMPORAL PARA PROBAR LAS PANTALLAS
    rol = "admin"

    session["rol"] = rol

    usuario = {
        "nombre_completo": "Juan Pérez"
    }

    datos = {}

    if rol == "medico":
        datos = {
            "consultorio": "123",
            "fecha": "25/10",
            "turnos_del_dia": [
                {
                    "nombre_paciente": "Camila Núñez",
                    "iniciales": "CN",
                    "cobertura": "Galeno",
                    "hora": "15:00 pm.",
                    "fecha": "25 - 10 - 2026",
                    "consultorio": "123",
                    "color_fondo": "bg-pink-500/30 text-pink-500"
                },
                {
                    "nombre_paciente": "Martín Pérez",
                    "iniciales": "MP",
                    "cobertura": "OSDE",
                    "hora": "15:00 pm.",
                    "fecha": "25 - 10 - 2026",
                    "consultorio": "123",
                    "color_fondo": "bg-green-500/30 text-green-500"
                }
            ],
            "coberturas": [
                {"nombre": "Galeno"},
                {"nombre": "OSDE"},
                {"nombre": "Swiss Medical"},
                {"nombre": "PAMI"}
            ]
        }

    elif rol == "recepcion":
        datos = {}

    elif rol == "paciente":
        datos = {}

    return render_template(
        "home.html",
        rol=rol,
        usuario=usuario,
        datos=datos
    )
