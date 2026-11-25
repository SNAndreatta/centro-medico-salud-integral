"""Política única de errores de la API en el frontend."""

from flask import flash, redirect, session, url_for

from src.api import ErrorAPI

MENSAJE_SESION_VENCIDA = "Tu sesión expiró. Iniciá sesión de nuevo."


def es_sesion_vencida(error):
    return error.status == 401


def sesion_vencida():
    session.clear()
    flash(MENSAJE_SESION_VENCIDA, "error")
    return redirect(url_for("rutas_auth.login"))


def atender_error(error, redirect_a=None):
    """401 -> login; el resto -> flash y, si se pide, redirect."""
    if es_sesion_vencida(error):
        return sesion_vencida()

    flash(error.mensaje, "error")
    return redirect(redirect_a) if redirect_a else None


def registrar_manejo_errores(app):
    @app.errorhandler(ErrorAPI)
    def _error_de_api(error):
        return atender_error(
            error,
            redirect_a=url_for("rutas_home.home"),
        )
