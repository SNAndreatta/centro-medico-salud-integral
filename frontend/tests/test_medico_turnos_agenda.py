"""Turnos y agenda del médico conectados al backend."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Permite importar los paquetes `src` y `routes` del frontend.
FRONTEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRONTEND))

import routes.medico as medico_module  # noqa: E402
from src.api import ErrorAPI  # noqa: E402
from app import app  # noqa: E402

TURNO = {
    "id_turno": 7,
    "id_agenda": 101,
    "fecha_horario_inicial": "2026-11-16 09:30:00",
    "fecha_horario_llegada": None,
    "duracion_turno": 30,
    "paciente": {
        "id_paciente": 2,
        "nombre": "Ana",
        "apellido": "Rossi",
        "dni": "40000001",
    },
    "medico": {
        "id_medico": 101,
        "id_especialidad": 1,
        "especialidad": "Clinica medica",
        "nombre": "Medico",
        "apellido": "Demo",
    },
    "consultorio": {
        "id_consultorio": 1,
        "numero": 101,
        "piso": 1,
    },
    "estado": {
        "id_estado": 3,
        "nombre": "confirmado",
    },
    "cobertura": {
        "id_cobertura": 1,
        "nombre": "OSDE",
    },
}

AGENDA = {
    "id_agenda": 101,
    "id_medico": 101,
    "medico": {
        "id_usuario": 104,
        "nombre": "Medico",
        "apellido": "Demo",
    },
    "id_consultorio": 1,
    "consultorio": {
        "numero": 101,
        "piso": 1,
    },
    "duracion_turno": 30,
    "fecha_inicio": "2026-11-01",
    "fecha_hasta": "2026-12-31",
    "dias": [
        {
            "id_agenda_dias": 101,
            "dia_semana": 1,
            "horario_inicio_jornada": "09:00:00",
            "horario_final_jornada": "10:00:00",
        },
    ],
}


@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    app.secret_key = "test"
    return app.test_client()


def _iniciar_sesion(cliente, rol="medico"):
    with cliente.session_transaction() as sesion:
        sesion["access_token"] = "token"
        sesion["rol"] = rol
        sesion["nombre"] = "Medico"
        sesion["apellido"] = "Demo"
        sesion["id_usuario"] = 104


def test_mis_turnos_muestran_los_datos_del_backend(cliente):
    _iniciar_sesion(cliente)

    with patch.object(
        medico_module,
        "api",
        return_value={"turnos": [TURNO]},
    ):
        respuesta = cliente.get("/turnos")

    assert respuesta.status_code == 200

    cuerpo = respuesta.data.decode()
    assert "Ana Rossi" in cuerpo
    assert "OSDE" in cuerpo
    assert "09:30" in cuerpo
    assert "101" in cuerpo


def test_mi_agenda_muestra_los_horarios_de_la_agenda(cliente):
    _iniciar_sesion(cliente)

    def fake_api(metodo, ruta, **kwargs):
        if ruta == "/agendas":
            return {"agendas": [AGENDA]}

        if ruta == "/turnos":
            return {"turnos": [TURNO]}

        return {}

    with patch.object(medico_module, "api", side_effect=fake_api):
        respuesta = cliente.get("/agenda?anio=2026&mes=11")

    assert respuesta.status_code == 200

    cuerpo = respuesta.data.decode()
    assert "AGENDA DE Medico Demo" in cuerpo

    # El lunes 02/11/2026 tiene la jornada de 09:00 a 10:00.
    assert '"fecha": "2026-11-02"' in cuerpo
    assert '"hora": "09:00"' in cuerpo
    assert '"hora": "09:30"' in cuerpo


def test_mi_agenda_muestra_los_turnos_ocupados(cliente):
    _iniciar_sesion(cliente)

    turno_ocupado = dict(TURNO)
    turno_ocupado["fecha_horario_inicial"] = "2026-11-02 09:00:00"

    def fake_api(metodo, ruta, **kwargs):
        if ruta == "/agendas":
            return {"agendas": [AGENDA]}

        if ruta == "/turnos":
            return {"turnos": [turno_ocupado]}

        return {}

    with patch.object(medico_module, "api", side_effect=fake_api):
        respuesta = cliente.get("/agenda?anio=2026&mes=11")

    assert respuesta.status_code == 200

    cuerpo = respuesta.data.decode()
    assert "Ana Rossi" in cuerpo


def test_marcar_turno_como_atendido_usa_el_backend(cliente):
    _iniciar_sesion(cliente)

    with patch.object(medico_module, "api") as llamada:
        respuesta = cliente.post("/turno/7/atendido")

    assert respuesta.status_code == 302

    llamada.assert_called_once_with(
        "PUT",
        "/turnos/7/estado",
        json={"estado": "atendido"},
    )


def test_marcar_turno_informa_el_error_del_backend(cliente):
    _iniciar_sesion(cliente)

    with patch.object(
        medico_module,
        "api",
        side_effect=ErrorAPI("El turno no pertenece al médico autenticado", 403),
    ):
        respuesta = cliente.post("/turno/7/atendido")

    assert respuesta.status_code == 302
    assert "Location" in respuesta.headers


def test_los_turnos_requieren_sesion_de_medico(cliente):
    respuesta = cliente.get("/turnos")

    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]
