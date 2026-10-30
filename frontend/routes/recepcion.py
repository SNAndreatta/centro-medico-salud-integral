from flask import Blueprint
from flask import render_template

recepcion_routes = Blueprint('rutas_recepcion_prefijo_api', __name__)

@recepcion_routes.route('/r')
def home():
    return render_template('/recepcion/home.html')

@recepcion_routes.route('/recepcion/sala-espera')
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
        'recepcion/sala_espera.html',
        pacientes_en_espera=pacientes_en_espera
    )

@recepcion_routes.route("/recepcion/usuarios")
def ver_usuarios():

    usuarios = [
        {
            "id": 1,
            "nombre": "Camila",
            "apellido": "Núñez",
            "cobertura": "OSDE",
            "plan": "210",
            "iniciales": "CN",
            "color_fondo": "bg-pink-500/30 text-pink-500"
        },
        {
            "id": 2,
            "nombre": "Martín",
            "apellido": "Pérez",
            "cobertura": "Swiss Medical",
            "plan": "SMG20",
            "iniciales": "MP",
            "color_fondo": "bg-purple-500/30 text-purple-500"
        },
        {
            "id": 3,
            "nombre": "Lucía",
            "apellido": "Fernández",
            "cobertura": "Galeno",
            "plan": "Oro",
            "iniciales": "LF",
            "color_fondo": "bg-green-500/30 text-green-500"
        },
        {
            "id": 4,
            "nombre": "Tomás",
            "apellido": "Gómez",
            "cobertura": "Medifé",
            "plan": "Plata",
            "iniciales": "TG",
            "color_fondo": "bg-red-500/30 text-red-500"
        }
    ]

    return render_template(
        "recepcion/ver_usuarios.html",
        usuarios=usuarios
    )

@recepcion_routes.route("/recepcion/profile")
def perfil():

    usuario = {
        "nombre": "Camila",
        "apellido": "Núñez",
        "iniciales": "CN",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA",
        "fecha_registro": "DD/MM/AAAA"
    }

    return render_template(
        "/recepcion/profile.html",
        usuario=usuario
    )