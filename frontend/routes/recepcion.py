from flask import Blueprint, jsonify, render_template, request

from src.api import ErrorAPI, api
from src.permisos import requiere_rol
from routes.admin.dashboards._comun import (
    color_avatar,
    formatear_hora,
    iniciales,
    nombre_completo,
)

recepcion_routes = Blueprint('rutas_recepcion', __name__)


def _listar_especialidades():
    """Devuelve las especialidades de la API para el filtro."""
    try:
        datos = api('GET', '/especialidades')
    except ErrorAPI:
        return []

    return [
        {
            'id': especialidad.get('id_especialidad'),
            'nombre': especialidad.get('nombre_especialidad'),
        }
        for especialidad in datos.get('especialidades', [])
    ]


def _normalizar_turno(turno, indice):
    """Adapta un turno de la API al formato de la tarjeta de la sala."""
    paciente = turno.get('paciente') or {}
    medico = turno.get('medico') or {}

    especialidad = medico.get('especialidad') or ''

    return {
        'id_turno': turno.get('id_turno'),
        'iniciales': iniciales(
            paciente.get('nombre'),
            paciente.get('apellido'),
        ),
        'nombre_completo': nombre_completo(
            paciente.get('nombre'),
            paciente.get('apellido'),
        ),
        'dni': paciente.get('dni') or '',
        'hora_turno': formatear_hora(turno.get('fecha_horario_inicial')),
        'hora_llegada': formatear_hora(turno.get('fecha_horario_llegada')),
        'modalidad': especialidad[:3].upper(),
        'especialidad': especialidad,
        'medico': nombre_completo(
            medico.get('nombre'),
            medico.get('apellido'),
        ),
        'consultorio': turno.get('numero_consultorio'),
        'color_avatar': color_avatar(indice),
    }


# ==========================================
# SALA DE ESPERA
# ==========================================

@recepcion_routes.route('/recepcion/sala-espera')
@requiere_rol("recepcion")
def sala_espera():

    pacientes_en_espera = []
    error = None

    try:
        datos = api('GET', '/estadisticas/sala_espera')

        pacientes_en_espera = [
            _normalizar_turno(turno, indice)
            for indice, turno in enumerate(datos.get('sala_espera', []))
        ]

    except ErrorAPI as e:
        error = e.mensaje

    especialidades = _listar_especialidades()

    if not especialidades:
        especialidades = [
            {'id': None, 'nombre': especialidad}
            for especialidad in sorted({
                paciente['especialidad']
                for paciente in pacientes_en_espera
                if paciente['especialidad']
            })
        ]

    return render_template(
        'recepcion/sala_espera.html',
        pacientes_en_espera=pacientes_en_espera,
        especialidades=especialidades,
        error=error
    )


# ==========================================
# INGRESO DE PACIENTE (CHECK-IN POR QR)
# ==========================================

@recepcion_routes.route('/recepcion/checkin', methods=['POST'])
@requiere_rol("recepcion")
def registrar_ingreso():
    """Registra el ingreso del paciente a partir del QR de su turno."""

    datos = request.get_json(silent=True) or {}
    token = str(datos.get('token') or '').strip()

    if not token:
        return jsonify({
            'ok': False,
            'mensaje': 'El código QR está vacío.',
        })

    try:
        api('POST', '/turnos/checkin', json={'token': token})

    except ErrorAPI as e:
        return jsonify({
            'ok': False,
            'mensaje': e.mensaje or 'No se pudo registrar el ingreso.',
        })

    return jsonify({
        'ok': True,
        'mensaje': 'Ingreso registrado correctamente.',
    })


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