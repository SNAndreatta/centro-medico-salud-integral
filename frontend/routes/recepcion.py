from flask import Blueprint
from flask import render_template

recepcion_routes = Blueprint('rutas_recepcion_prefijo_api', __name__)

@recepcion_routes.route('/r')
def home():
    return render_template('/recepcion/home.html')

@recepcion_routes.route('/sala-espera')
def sala_espera():

    pacientes_en_espera = [
        {
            "iniciales": "NC",
            "nombre_completo": "Nombre Completo",
            "hora_turno": "15:45",
            "hora_llegada": "15:40",
            "modalidad": "CAR",
            "color_avatar": "bg-pink-500/30 text-pink-500"
        },
        {
            "iniciales": "NC",
            "nombre_completo": "Nombre Completo",
            "hora_turno": "15:50",
            "hora_llegada": "15:45",
            "modalidad": "PED",
            "color_avatar": "bg-pink-500/30 text-pink-500"
        }
    ]

    return render_template(
        'recepcion/sala_espera.html',
        pacientes_en_espera=pacientes_en_espera
    )