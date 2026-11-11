
from flask import Blueprint, render_template, session, redirect, url_for


home_routes = Blueprint('rutas_home', __name__)


ROLES = {
    1: 'administrador',
    2: 'recepcionista',
    3: 'paciente',
    4: 'medico',
}


@home_routes.route("/home")
def home():

    # Si no hay una sesión iniciada, vuelve al login.
    usuario_sesion = session.get('usuario')

    if not usuario_sesion:
        return redirect(url_for('rutas_auth.login'))

    # Recupera el rol del usuario autenticado.
    id_rol = session.get('id_rol')

    if id_rol is None:
        id_rol = usuario_sesion.get('id_rol')

    try:
        id_rol = int(id_rol)
    except (TypeError, ValueError):
        session.clear()
        return redirect(url_for('rutas_auth.login'))

    rol = ROLES.get(id_rol)

    if rol is None:
        session.clear()
        return redirect(url_for('rutas_auth.login'))

    session['rol'] = rol

    reserva_exitosa = session.pop('turno_reservado', False)

    nombre = usuario_sesion.get('nombre', '')
    apellido = usuario_sesion.get('apellido', '')

    usuario = {
        'nombre': nombre,
        'apellido': apellido,
        'nombre_completo': f'{nombre} {apellido}'.strip()
    }

    datos = {}

    if rol == 'medico':
        datos = {
            "consultorio": "123",
            "fecha": "25/10",
            "turnos_del_dia": [
                {
                    "id": 1,
                    "nombre_paciente": "Camila Núñez",
                    "iniciales": "CN",
                    "cobertura": "Galeno",
                    "hora": "15:00 pm.",
                    "fecha": "25 - 10 - 2026",
                    "consultorio": "123",
                    "color_fondo": "bg-pink-500/30 text-pink-500"
                },
                {
                    "id": 2,
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

    elif rol == 'recepcionista':
        datos = {}

    elif rol == 'paciente':
        datos = {}

    elif rol == 'administrador':
        datos = {}

    return render_template(
        "home.html",
        rol=rol,
        usuario=usuario,
        datos=datos,
        reserva_exitosa=reserva_exitosa
    )
