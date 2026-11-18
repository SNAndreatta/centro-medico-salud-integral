"""Tests del selector de coberturas del formulario de registro."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Permite importar los paquetes `src` y `routes` del frontend.
FRONTEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRONTEND))

import routes.auth as auth_module  # noqa: E402
from app import app  # noqa: E402

COBERTURAS = {
    "coberturas": [
        {"id_cobertura": 1, "nombre": "OSDE", "cantidad_medicos": 3},
        {"id_cobertura": 2, "nombre": "Swiss Medical", "cantidad_medicos": 1},
        {"id_cobertura": 3, "nombre": "Galeno", "cantidad_medicos": 2},
    ]
}


@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    app.secret_key = "test"
    return app.test_client()


def _respuesta_falsa(datos):
    respuesta = MagicMock()
    respuesta.json.return_value = datos
    respuesta.raise_for_status.return_value = None
    return respuesta


def test_register_muestra_todas_las_coberturas_de_la_base(cliente):
    with patch.object(
        auth_module.requests,
        "get",
        return_value=_respuesta_falsa(COBERTURAS),
    ):
        respuesta = cliente.get("/register")

    assert respuesta.status_code == 200

    cuerpo = respuesta.data.decode()
    assert "OSDE" in cuerpo
    assert "Swiss Medical" in cuerpo
    assert "Galeno" in cuerpo
    assert 'value="1"' in cuerpo
    assert 'value="2"' in cuerpo
    assert 'value="3"' in cuerpo


def test_register_sigue_funcionando_si_el_backend_no_responde(cliente):
    with patch.object(
        auth_module.requests,
        "get",
        side_effect=auth_module.requests.RequestException("sin conexión"),
    ):
        respuesta = cliente.get("/register")

    assert respuesta.status_code == 200
    assert "Particular" in respuesta.data.decode()
