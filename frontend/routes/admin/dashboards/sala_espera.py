
from flask import Blueprint, render_template


sala_espera_admin_routes = Blueprint('rutas_admin_sala_espera',__name__)


# =========================================
# SALA DE ESPERA
# =========================================

@sala_espera_admin_routes.route('/admin/sala-espera')
def sala_espera():

    # =====================================
    # PACIENTES EN ESPERA
    # =====================================

    pacientes_en_espera = [

        {
            "iniciales": "NC",
            "nombre_completo": "Nombre Completo",
            "hora_turno": "15:45",
            "hora_llegada": "15:40",
            "modalidad": "CAR",
            "especialidad": "Cardiología",
            "color_avatar": "bg-pink-500/30 text-pink-500"
        },

        {
            "iniciales": "NC",
            "nombre_completo": "Nombre Completo",
            "hora_turno": "15:50",
            "hora_llegada": "15:45",
            "modalidad": "PED",
            "especialidad": "Pediatría",
            "color_avatar": "bg-purple-500/30 text-purple-500"
        },

        {
            "iniciales": "JP",
            "nombre_completo": "Juan Pérez",
            "hora_turno": "16:00",
            "hora_llegada": "15:55",
            "modalidad": "CLI",
            "especialidad": "Clínica Médica",
            "color_avatar": "bg-blue-500/30 text-blue-500"
        },

        {
            "iniciales": "MG",
            "nombre_completo": "María González",
            "hora_turno": "16:10",
            "hora_llegada": "16:02",
            "modalidad": "DER",
            "especialidad": "Dermatología",
            "color_avatar": "bg-green-500/30 text-green-500"
        },

        {
            "iniciales": "LR",
            "nombre_completo": "Laura Rodríguez",
            "hora_turno": "16:20",
            "hora_llegada": "16:15",
            "modalidad": "OFT",
            "especialidad": "Oftalmología",
            "color_avatar": "bg-orange-500/30 text-orange-500"
        },

        {
            "iniciales": "CM",
            "nombre_completo": "Carlos Martínez",
            "hora_turno": "16:30",
            "hora_llegada": "16:25",
            "modalidad": "TRA",
            "especialidad": "Traumatología",
            "color_avatar": "bg-indigo-500/30 text-indigo-500"
        }

    ]


    # =====================================
    # ESPECIALIDADES
    # =====================================

    especialidades = [

        {"nombre": "Cardiología"},

        {"nombre": "Clínica Médica"},

        {"nombre": "Dermatología"},

        {"nombre": "Oftalmología"},

        {"nombre": "Pediatría"},

        {"nombre": "Traumatología"}

    ]


    # =====================================
    # RENDERIZAR PLANTILLA
    # =====================================

    return render_template(
        'admin/dashboards/sala_espera.html',
        pacientes_en_espera=pacientes_en_espera,
        especialidades=especialidades
    )
