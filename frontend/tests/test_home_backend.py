"""Tests de la conexión del home del frontend con el backend."""

import re
import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

# Permite importar los paquetes `src` y `routes` del frontend.
FRONTEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRONTEND))

import routes.home as home_module  # noqa: E402
from app import app  # noqa: E402

PERFIL_ADMIN = {
    "id_usuario": 1,
    "id_rol": 1,
    "nombre": "Admin",
    "apellido": "Root",
}

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


def _boton_crear_turnos(cuerpo):
    bloque = re.search(
        r'<div[^>]*class="[^"]*mt-8[^"]*"[^>]*>[\s\S]*?'
        r'action="/home/generar-turnos"[\s\S]*?</form>[\s\S]*?</div>',
        cuerpo,
    )
    assert bloque, "No se encontró el botón de 'Crear turnos'"
    return bloque.group(0)


def test_home_admin_habilita_crear_turnos_el_dia_15(cliente):
    _iniciar_sesion(cliente, "admin")

    with patch.object(home_module, "perfil_usuario", return_value=PERFIL_ADMIN), \
         patch.object(home_module, "hoy_local", return_value=date(2026, 11, 15)):
        respuesta = cliente.get("/home")

    assert respuesta.status_code == 200
    cuerpo = respuesta.data.decode()
    boton = _boton_crear_turnos(cuerpo)
    assert "Crear turnos" in boton
    assert "disabled" not in boton
    assert "bg-acento" in boton
    assert "fixed" not in boton
    assert "bottom-6" not in boton
    assert "mt-8 flex justify-end" in boton


def test_home_admin_deshabilita_crear_turnos_fuera_del_dia_15(cliente):
    _iniciar_sesion(cliente, "admin")

    with patch.object(home_module, "perfil_usuario", return_value=PERFIL_ADMIN), \
         patch.object(home_module, "hoy_local", return_value=date(2026, 11, 16)):
        respuesta = cliente.get("/home")

    assert respuesta.status_code == 200
    boton = _boton_crear_turnos(respuesta.data.decode())
    assert "disabled" in boton
    assert "bg-acento/50" in boton


def test_generar_turnos_llama_al_endpoint_y_informa_el_resultado(cliente):
    _iniciar_sesion(cliente, "admin")

    with patch.object(home_module, "hoy_local", return_value=date(2026, 11, 15)), \
         patch.object(home_module, "api", return_value={
             "mensaje": "Disponibilidad generada correctamente",
             "turnos_generados": 42,
             "periodo": {"fecha_desde": "2026-12-01", "fecha_hasta": "2026-12-31"},
         }) as api_mock, \
         patch.object(home_module, "perfil_usuario", return_value=PERFIL_ADMIN):
        respuesta = cliente.post("/home/generar-turnos", follow_redirects=True)

    api_mock.assert_called_once_with("POST", "/turnos/generar")
    assert respuesta.status_code == 200
    assert "Se generaron 42 turnos correctamente." in respuesta.data.decode()


def test_generar_turnos_informa_el_error_del_endpoint(cliente):
    _iniciar_sesion(cliente, "admin")

    with patch.object(home_module, "hoy_local", return_value=date(2026, 11, 15)), \
         patch.object(home_module, "api", side_effect=home_module.ErrorAPI(
             "No se pudo generar la disponibilidad.", 500
         )) as api_mock, \
         patch.object(home_module, "perfil_usuario", return_value=PERFIL_ADMIN):
        respuesta = cliente.post("/home/generar-turnos", follow_redirects=True)

    api_mock.assert_called_once_with("POST", "/turnos/generar")
    assert "No se pudo generar la disponibilidad." in respuesta.data.decode()


def test_generar_turnos_no_se_ejecuta_fuera_del_dia_15(cliente):
    _iniciar_sesion(cliente, "admin")

    with patch.object(home_module, "hoy_local", return_value=date(2026, 11, 16)), \
         patch.object(home_module, "api") as api_mock, \
         patch.object(home_module, "perfil_usuario", return_value=PERFIL_ADMIN):
        respuesta = cliente.post("/home/generar-turnos", follow_redirects=True)

    api_mock.assert_not_called()
    assert "sólo está disponible el día 15" in respuesta.data.decode()


def test_generar_turnos_rechaza_otros_roles(cliente):
    _iniciar_sesion(cliente, "recepcion")

    with patch.object(home_module, "api") as api_mock:
        respuesta = cliente.post("/home/generar-turnos")

    assert respuesta.status_code == 302
    assert "/home" in respuesta.headers["Location"]
    api_mock.assert_not_called()
