from flask import Blueprint
from flask import render_template, request

profile_routes = Blueprint('rutas_profile_prefijo_api', __name__)

USUARIOS_DE_PRUEBA = {
    "medico": {
        "rol": "medico",
        "iniciales": "MG",
        "nombre": "María",
        "apellido": "González",
        "fecha_registro": "15/03/2025",
        "email": "maria.gonzalez@example.com",
        "documento": "30123456",
        "fecha_nacimiento": "12/05/1985",
        "matricula": "123456"
    },

    "recepcion": {
        "rol": "recepcion",
        "iniciales": "LC",
        "nombre": "Lucía",
        "apellido": "Castro",
        "fecha_registro": "20/04/2025",
        "email": "lucia.castro@example.com",
        "documento": "32456789",
        "fecha_nacimiento": "08/09/1990",
    },

    "paciente": {
        "rol": "paciente",
        "iniciales": "JP",
        "nombre": "Juan",
        "apellido": "Pérez",
        "fecha_registro": "10/06/2025",
        "email": "juan.perez@example.com",
        "documento": "35678901",
        "fecha_nacimiento": "21/11/1995",
        "numero_afiliado": "987654321",
        "cobertura": "Nombre de cobertura",
        "plan": "Nombre de plan",
    },

    "admin": {
        "rol": "admin",
        "iniciales": "AR",
        "nombre": "Ana",
        "apellido": "Rodríguez",
        "fecha_registro": "01/02/2025",
        "email": "ana.rodriguez@example.com",
        "documento": "28901234",
        "fecha_nacimiento": "17/07/1980",
    },
}


@profile_routes.route("/profile", methods=["GET"])
def profile():

    # Selección temporal del usuario para las pruebas.
    rol = request.args.get("rol", "paciente").lower()

    # Si el rol no existe, mostrar el perfil de recepción.
    if rol not in USUARIOS_DE_PRUEBA:
        rol = "recepcion"

    usuario = USUARIOS_DE_PRUEBA[rol]

    return render_template(
        "profile.html",
        rol=rol,
        usuario=usuario
    )