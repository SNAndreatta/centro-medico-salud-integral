"""Tests del ingreso de pacientes por QR en la sala de espera de recepción."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Permite importar los paquetes `src` y `routes` del frontend.
FRONTEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRONTEND))

import routes.recepcion as recepcion_module  # noqa: E402
from src.api import ErrorAPI  # noqa: E402
from app import app  # noqa: E402

TURNO_EN_ESPERA = {
    "id_turno": 7,
    "fecha_horario_inicial": "2026-11-16 09:30:00",
    "fecha_horario_llegada": "2026-11-16 09:20:00",
    "paciente": {
        "id_paciente": 2,
        "nombre": "Ana",
        "apellido": "Rossi",
        "dni": "40000001",
    },
    "medico": {
        "id_medico": 3,
        "id_especialidad": 1,
        "especialidad": "Cardiologia",
        "nombre": "Martin",
        "apellido": "Lopez",
    },
    "numero_consultorio": 101,
}

ESPECIALIDADES = {
    "especialidades": [
        {"id_especialidad": 1, "nombre_especialidad": "Cardiologia"},
    ]
}


@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    app.secret_key = "test"
    return app.test_client()


def _iniciar_sesion(cliente, rol="recepcionista"):
    with cliente.session_transaction() as sesion:
        sesion["access_token"] = "token"
        sesion["rol"] = rol
        sesion["nombre"] = "Sofia"
        sesion["apellido"] = "Recepcion"


def test_checkin_registra_el_ingreso_del_paciente(cliente):
    _iniciar_sesion(cliente)

    with patch.object(recepcion_module, "api") as llamada:
        respuesta = cliente.post(
            "/recepcion/checkin",
            json={"token": "TOKEN-QR"},
        )

    assert respuesta.status_code == 200
    assert respuesta.get_json()["ok"] is True

    llamada.assert_called_once_with(
        "POST",
        "/turnos/checkin",
        json={"token": "TOKEN-QR"},
    )


def test_checkin_informa_el_error_del_backend(cliente):
    _iniciar_sesion(cliente)

    with patch.object(
        recepcion_module,
        "api",
        side_effect=ErrorAPI("El token QR es inválido", 400),
    ):
        respuesta = cliente.post(
            "/recepcion/checkin",
            json={"token": "TOKEN-QR"},
        )

    assert respuesta.status_code == 200
    cuerpo = respuesta.get_json()
    assert cuerpo["ok"] is False
    assert cuerpo["mensaje"] == "El token QR es inválido"


def test_checkin_sin_token_no_llama_al_backend(cliente):
    _iniciar_sesion(cliente)

    with patch.object(recepcion_module, "api") as llamada:
        respuesta = cliente.post("/recepcion/checkin", json={})

    assert respuesta.status_code == 200
    cuerpo = respuesta.get_json()
    assert cuerpo["ok"] is False
    assert "QR" in cuerpo["mensaje"]
    llamada.assert_not_called()


def test_checkin_requiere_sesion_de_recepcion(cliente):
    respuesta = cliente.post("/recepcion/checkin", json={"token": "TOKEN-QR"})

    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_sala_espera_muestra_los_pacientes_del_backend(cliente):
    _iniciar_sesion(cliente)

    def fake_api(metodo, ruta, **kwargs):
        if ruta == "/estadisticas/sala_espera":
            return {"sala_espera": [TURNO_EN_ESPERA], "total": 1}
        if ruta == "/especialidades":
            return ESPECIALIDADES
        return {}

    with patch.object(recepcion_module, "api", side_effect=fake_api):
        respuesta = cliente.get("/recepcion/sala-espera")

    assert respuesta.status_code == 200

    cuerpo = respuesta.data.decode()
    assert "Ana Rossi" in cuerpo
    assert "09:30" in cuerpo
    assert "09:20" in cuerpo
    assert "Cardiologia" in cuerpo
