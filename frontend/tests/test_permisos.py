"""Tests de la protección de rutas del frontend por rol."""

import sys
from pathlib import Path

import pytest
from flask import Blueprint, Flask, session

# Permite importar el paquete `src` del frontend.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.permisos import requiere_rol, rol_actual  # noqa: E402


@pytest.fixture
def cliente():
    app = Flask(__name__)
    app.secret_key = "test"

    # Blueprints con los mismos endpoints que usa el frontend real.
    auth_bp = Blueprint("rutas_auth", __name__)
    home_bp = Blueprint("rutas_home", __name__)

    @auth_bp.route("/login")
    def login():
        return "login"

    @home_bp.route("/home")
    def home():
        return "home"

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)

    @app.route("/admin")
    @requiere_rol("admin")
    def admin():
        return "admin"

    @app.route("/paciente")
    @requiere_rol("paciente")
    def paciente():
        return "paciente"

    @app.route("/todos")
    @requiere_rol("paciente", "medico", "recepcion", "admin")
    def todos():
        return "todos"

    return app.test_client()


def _iniciar_sesion(cliente, rol):
    with cliente.session_transaction() as sesion:
        sesion["access_token"] = "token"
        sesion["rol"] = rol


def test_sin_sesion_redirige_al_login(cliente):
    respuesta = cliente.get("/admin")

    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_admin_puede_entrar_a_ruta_de_admin(cliente):
    _iniciar_sesion(cliente, "administrador")

    respuesta = cliente.get("/admin")

    assert respuesta.status_code == 200
    assert respuesta.data == b"admin"


def test_paciente_no_puede_entrar_a_ruta_de_admin(cliente):
    _iniciar_sesion(cliente, "paciente")

    respuesta = cliente.get("/admin")

    assert respuesta.status_code == 302
    assert "/home" in respuesta.headers["Location"]


def test_medico_no_puede_entrar_a_ruta_de_admin(cliente):
    _iniciar_sesion(cliente, "medico")

    respuesta = cliente.get("/admin")

    assert respuesta.status_code == 302
    assert "/home" in respuesta.headers["Location"]


def test_recepcion_no_puede_entrar_a_ruta_de_paciente(cliente):
    _iniciar_sesion(cliente, "recepcionista")

    respuesta = cliente.get("/paciente")

    assert respuesta.status_code == 302
    assert "/home" in respuesta.headers["Location"]


def test_cualquier_rol_autenticado_entra_a_ruta_comun(cliente):
    for rol in ("paciente", "medico", "recepcionista", "administrador"):
        _iniciar_sesion(cliente, rol)

        respuesta = cliente.get("/todos")

        assert respuesta.status_code == 200


def test_rol_actual_normaliza_los_alias():
    with_flask = Flask(__name__)
    with_flask.secret_key = "test"

    with with_flask.test_request_context("/"):
        session["rol"] = "administrador"
        assert rol_actual() == "admin"

        session["rol"] = "recepcionista"
        assert rol_actual() == "recepcion"

        session["rol"] = "medico"
        assert rol_actual() == "medico"

        session["rol"] = "paciente"
        assert rol_actual() == "paciente"
