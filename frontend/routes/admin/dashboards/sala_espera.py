from flask import Blueprint, render_template

sala_espera_admin_routes = Blueprint('rutas_admin_sala_espera', __name__)

@sala_espera_admin_routes.route('/admin/sala-espera')
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
            "color_avatar": "bg-purple-500/30 text-purple-500"
        }
    ]

    return render_template(
        'admin/dashboards/sala_espera.html',
        pacientes_en_espera=pacientes_en_espera
    )