from flask import Blueprint, render_template

from src.permisos import requiere_rol

recepcion_routes = Blueprint('rutas_recepcion', __name__)


# ==========================================
# SALA DE ESPERA
# ==========================================

@recepcion_routes.route('/recepcion/sala-espera')
@requiere_rol("recepcion")
def sala_espera():

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
        }
    ]

    especialidades = [
        {"nombre": "Cardiología"},
        {"nombre": "Clínica Médica"},
        {"nombre": "Dermatología"},
        {"nombre": "Oftalmología"},
        {"nombre": "Pediatría"},
        {"nombre": "Traumatología"}
    ]

    return render_template(
        'recepcion/sala_espera.html',
        pacientes_en_espera=pacientes_en_espera,
        especialidades=especialidades
    )


# ==========================================
# USUARIOS
# ==========================================

@recepcion_routes.route("/recepcion/usuarios")
@requiere_rol("recepcion")
def ver_usuarios():

    usuarios = [
        {
            "id": 1,
            "nombre": "Camila",
            "apellido": "Núñez",
            "cobertura": "OSDE",
            "iniciales": "CN",
            "color_fondo": "bg-pink-500/30 text-pink-500"
        },
        {
            "id": 2,
            "nombre": "Martín",
            "apellido": "Pérez",
            "cobertura": "Swiss Medical",
            "iniciales": "MP",
            "color_fondo": "bg-purple-500/30 text-purple-500"
        },
        {
            "id": 3,
            "nombre": "Lucía",
            "apellido": "Fernández",
            "cobertura": "Galeno",
            "iniciales": "LF",
            "color_fondo": "bg-green-500/30 text-green-500"
        },
        {
            "id": 4,
            "nombre": "Tomás",
            "apellido": "Gómez",
            "cobertura": "Medifé",
            "iniciales": "TG",
            "color_fondo": "bg-red-500/30 text-red-500"
        }
    ]

    return render_template(
        "recepcion/ver_usuarios.html",
        usuarios=usuarios
    )


# ==========================================
# PERFIL
# ==========================================

@recepcion_routes.route("/recepcion/profile")
@requiere_rol("recepcion")
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


# ==========================================
# TURNOS
# ==========================================

@recepcion_routes.route("/recepcion/turnos")
@requiere_rol("recepcion")
def ver_turnos():

    turnos = [
        {
            "id": 1,
            "paciente": "Camila Núñez",
            "iniciales": "CN",
            "cobertura": "OSDE",
            "hora": "10:30 am.",
            "fecha": "11 - 10 - 2026",
            "fecha_filtro": "2026-10-11",
            "consultorio": "123",
            "especialidad": "Dr. Juan Pérez",
            "color_fondo": "bg-pink-500/30 text-pink-500"
        },
        {
            "id": 2,
            "paciente": "Lucía Fernández",
            "iniciales": "LF",
            "cobertura": "Galeno",
            "hora": "10:30 am.",
            "fecha": "11 - 10 - 2026",
            "fecha_filtro": "2026-10-11",
            "consultorio": "123",
            "especialidad": "Dra. Ana Martínez",
            "color_fondo": "bg-purple-500/30 text-purple-500"
        },
        {
            "id": 3,
            "paciente": "Martín Pérez",
            "iniciales": "MP",
            "cobertura": "Swiss Medical",
            "hora": "10:30 am.",
            "fecha": "11 - 10 - 2026",
            "fecha_filtro": "2026-10-11",
            "consultorio": "123",
            "especialidad": "Dr. Carlos Gómez",
            "color_fondo": "bg-green-500/30 text-green-500"
        },
        {
            "id": 4,
            "paciente": "Tomás Gómez",
            "iniciales": "TG",
            "cobertura": "Medifé",
            "hora": "10:30 am.",
            "fecha": "11 - 10 - 2026",
            "fecha_filtro": "2026-10-11",
            "consultorio": "123",
            "especialidad": "Dr. Juan Pérez",
            "color_fondo": "bg-red-500/30 text-red-500"
        },
        {
            "id": 5,
            "paciente": "Nicolás Castro",
            "iniciales": "NC",
            "cobertura": "OSDE",
            "hora": "10:30 am.",
            "fecha": "11 - 10 - 2026",
            "fecha_filtro": "2026-10-11",
            "consultorio": "123",
            "especialidad": "Dra. Ana Martínez",
            "color_fondo": "bg-cyan-500/30 text-cyan-500"
        }
    ]

    return render_template(
        "recepcion/ver_turnos.html",
        turnos=turnos
    )


# ==========================================
# PERFIL DE USUARIO
# ==========================================

@recepcion_routes.route("/recepcion/profile/<int:id_usuario>")
@requiere_rol("recepcion")
def perfil_usuario(id_usuario):

    usuarios = {
        1: {
            "id": 1,
            "nombre": "Camila",
            "apellido": "Núñez",
            "iniciales": "CN",
            "email": "ejemplo.usuario@gmail.com",
            "documento": "44.444.444",
            "fecha_nacimiento": "DD/MM/AAAA",
            "fecha_registro": "DD/MM/AAAA"
        }
    }

    usuario = usuarios.get(id_usuario)

    if not usuario:
        return "Usuario no encontrado", 404

    return render_template(
        "recepcion/profile.html",
        usuario=usuario
    )