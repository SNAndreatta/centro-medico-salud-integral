"""Protección de rutas del frontend según el rol del usuario.

El rol se guarda en la sesión al iniciar sesión (`session['rol']`) con los
nombres que usa el backend: administrador, recepcionista, medico o paciente.
Acá se normalizan a los nombres que usan las plantillas: admin, recepcion,
medico y paciente.
"""

from functools import wraps

from flask import flash, redirect, session, url_for

# session['rol'] (lo que guarda auth.py) -> nombre que usan las plantillas
ALIAS_ROL = {
    "administrador": "admin",
    "recepcionista": "recepcion",
}

ROLES = ("paciente", "medico", "recepcion", "admin")


def rol_actual():
    """Rol del usuario autenticado, normalizado."""
    rol = session.get("rol", "paciente")
    return ALIAS_ROL.get(rol, rol)


def requiere_rol(*roles):
    """Decorador que sólo deja pasar a los roles indicados.

    Sin sesión iniciada redirige al login. Con una sesión iniciada pero sin
    permiso para la ruta redirige al home y avisa con un mensaje.
    """
    permitidos = set(roles)

    def decorador(funcion):
        @wraps(funcion)
        def envoltorio(*args, **kwargs):
            if "access_token" not in session:
                session.clear()
                flash("Iniciá sesión para continuar.", "error")
                return redirect(url_for("rutas_auth.login"))

            rol = rol_actual()

            if rol not in permitidos:
                flash("No tenés permisos para acceder a esta sección.", "error")
                return redirect(url_for("rutas_home.home"))

            return funcion(*args, **kwargs)

        return envoltorio

    return decorador
