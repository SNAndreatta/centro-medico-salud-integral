"""Tests de la conexión del home del frontend con el backend."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Permite importar los paquetes `src` y `routes` del frontend.
FRONTEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRONTEND))

import routes.home as home_module  # noqa: E402
from app import app  # noqa: E402

PERFIL_MEDICO = {
    "id_usuario": 9,
    "id_rol": 4,
    "nombre": "Ana",
    "apellido": "Martínez",
    "id_medico": 3,
    "nombre_especialidad": "Cardiología",
    "matricula": "12345",
}

TURNO = {
    "id": 7,
    "nombre_paciente": "Juan Pérez",
    "iniciales": "JP",
    "hora": "09:30",
    "fecha": "16 de Noviembre de 2026",
    "consultorio": 123,
    "atendido": True,
}


@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    app.secret_key = "test"
    return app.test_client()


def _iniciar_sesion(cliente, rol):
    with cliente.session_transaction() as sesion:
        sesion["access_token"] = "token"
        sesion["rol"] = rol
        sesion["nombre"] = "Nombre"
        sesion["apellido"] = "Apellido"


def test_home_medico_trae_turnos_y_coberturas_del_backend(cliente):
    _iniciar_sesion(cliente, "medico")

    with patch.object(home_module, "perfil_usuario", return_value=PERFIL_MEDICO), \
         patch.object(home_module, "turnos_del_dia_medico", return_value=[TURNO]) as turnos, \
         patch.object(home_module, "coberturas_medico", return_value=[
             {"id": 1, "nombre": "OSDE"},
         ]) as coberturas:

        respuesta = cliente.get("/home")

    assert respuesta.status_code == 200
    cuerpo = respuesta.data.decode()
    assert "Ana Martínez" in cuerpo
    assert "Juan Pérez" in cuerpo
    assert "OSDE" in cuerpo

    turnos.assert_called_once()
    coberturas.assert_called_once_with(3)


def test_home_admin_no_llama_a_datos_de_turnos(cliente):
    _iniciar_sesion(cliente, "administrador")

    with patch.object(home_module, "perfil_usuario", return_value={
                 "id_usuario": 1, "nombre": "Admin", "apellido": "Root",
             }), \
         patch.object(home_module, "turnos_del_dia_medico") as turnos, \
         patch.object(home_module, "coberturas_medico") as coberturas:

        respuesta = cliente.get("/home")

    assert respuesta.status_code == 200
    assert "Admin Root" in respuesta.data.decode()
    turnos.assert_not_called()
    coberturas.assert_not_called()


def test_home_paciente_usa_el_perfil_del_backend(cliente):
    _iniciar_sesion(cliente, "paciente")

    with patch.object(home_module, "perfil_paciente", return_value={
                 "nombre": "Lucia", "apellido": "Sosa",
                 "cobertura": "Galeno", "numero_afiliado": "AFI-000004",
             }), \
         patch.object(home_module, "proximos_turnos_paciente", return_value=[]):

        respuesta = cliente.get("/home")

    assert respuesta.status_code == 200
    cuerpo = respuesta.data.decode()
    assert "Lucia Sosa" in cuerpo
    assert "Galeno" in cuerpo
    assert "AFI-000004" in cuerpo


def test_home_sin_sesion_redirige_al_login(cliente):
    respuesta = cliente.get("/home")

    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_paciente_no_puede_ver_el_home_de_admin(cliente):
    _iniciar_sesion(cliente, "paciente")

    with patch.object(home_module, "perfil_paciente", return_value={
                 "nombre": "Lucia", "apellido": "Sosa",
                 "cobertura": "Galeno", "numero_afiliado": "AFI-000004",
             }), \
         patch.object(home_module, "proximos_turnos_paciente", return_value=[]):

        respuesta = cliente.get("/home?rol_demo=admin")

    # El selector de rol demo ya no existe: siempre se muestra el home del
    # propio rol, sin datos de otro rol.
    assert respuesta.status_code == 200
    assert "Administración" not in respuesta.data.decode()
