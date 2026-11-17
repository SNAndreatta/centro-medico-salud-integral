"""ABM de médicos del administrador conectado al backend."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Permite importar los paquetes `src` y `routes` del frontend.
FRONTEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRONTEND))

import routes.admin.abm.medico as medico_admin_module  # noqa: E402
from src.api import ErrorAPI  # noqa: E402
from app import app  # noqa: E402

MEDICO = {
    "id_medico": 1,
    "id_usuario": 6,
    "nombre": "Ana",
    "apellido": "Gutierrez",
    "correo_electronico": "ana.gutierrez@saludintegral.test",
    "dni": "20000001",
    "matricula": "MN-TEST-1001",
    "id_especialidad": 3,
    "nombre_especialidad": "Cardiologia",
}

USUARIO = {
    "id_usuario": 6,
    "id_rol": 4,
    "id_medico": 1,
    "nombre": "Ana",
    "apellido": "Gutierrez",
    "correo_electronico": "ana.gutierrez@saludintegral.test",
    "dni": "20000001",
    "fecha_nacimiento": "1985-04-12",
    "fecha_creacion": "2026-01-10",
    "matricula": "MN-TEST-1001",
    "nombre_especialidad": "Cardiologia",
}

TURNO = {
    "id_turno": 7,
    "id_agenda": 1,
    "fecha_horario_inicial": "2026-11-16 09:30:00",
    "duracion_turno": 30,
    "paciente": {
        "id_paciente": 2,
        "nombre": "Ana",
        "apellido": "Rossi",
    },
    "medico": {
        "id_medico": 1,
        "especialidad": "Cardiologia",
        "nombre": "Ana",
        "apellido": "Gutierrez",
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
    "cobertura": None,
}

AGENDA = {
    "id_agenda": 1,
    "id_medico": 1,
    "medico": {
        "id_usuario": 6,
        "nombre": "Ana",
        "apellido": "Gutierrez",
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
            "id_agenda_dias": 1,
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


def _iniciar_sesion(cliente):
    with cliente.session_transaction() as sesion:
        sesion["access_token"] = "token"
        sesion["rol"] = "administrador"
        sesion["nombre"] = "Admin"
        sesion["apellido"] = "Demo"
        sesion["id_usuario"] = 101


def _api_falsa(metodo, ruta, **kwargs):
    """Responde como el backend para las rutas que usa el ABM de médicos."""
    if ruta == "/medicos/1":
        return {"medico": MEDICO}

    if ruta == "/usuarios":
        return {"usuarios": [USUARIO]}

    if ruta == "/especialidades":
        return {
            "especialidades": [
                {"id_especialidad": 3, "nombre_especialidad": "Cardiologia"},
            ]
        }

    if ruta == "/coberturas":
        return {
            "coberturas": [
                {"id_cobertura": 1, "nombre": "OSDE"},
                {"id_cobertura": 2, "nombre": "Galeno"},
            ]
        }

    if ruta == "/medicos/1/coberturas":
        return {"coberturas": [{"id_cobertura": 1, "nombre": "OSDE"}]}

    if ruta == "/consultorios":
        return {
            "consultorios": [
                {"id_consultorio": 1, "numero": 101},
                {"id_consultorio": 2, "numero": 102},
            ]
        }

    if ruta == "/agendas":
        return {"agendas": [AGENDA]}

    if ruta == "/turnos":
        return {"turnos": [TURNO]}

    return {}


def test_el_perfil_del_medico_muestra_los_datos_del_backend(cliente):
    _iniciar_sesion(cliente)

    with patch.object(
        medico_admin_module,
        "api",
        side_effect=_api_falsa,
    ):
        respuesta = cliente.get("/medicos/1")

    assert respuesta.status_code == 200

    cuerpo = respuesta.data.decode()
    assert "Ana Gutierrez" in cuerpo
    assert "Cardiologia" in cuerpo
    assert "MN-TEST-1001" in cuerpo
    assert "OSDE" in cuerpo


def test_el_perfil_del_medico_no_tiene_el_formulario_de_agenda(cliente):
    _iniciar_sesion(cliente)

    with patch.object(
        medico_admin_module,
        "api",
        side_effect=_api_falsa,
    ):
        respuesta = cliente.get("/medicos/1")

    cuerpo = respuesta.data.decode()
    assert "modalCrearAgenda" not in cuerpo
    assert "Crear agenda" not in cuerpo


def test_los_turnos_del_medico_muestran_los_datos_del_backend(cliente):
    _iniciar_sesion(cliente)

    with patch.object(
        medico_admin_module,
        "api",
        side_effect=_api_falsa,
    ):
        respuesta = cliente.get("/turnos/1")

    assert respuesta.status_code == 200

    cuerpo = respuesta.data.decode()
    assert "Confirmado" in cuerpo
    assert "09:30" in cuerpo
    assert "101" in cuerpo


def test_la_agenda_del_medico_muestra_el_calendario_y_el_boton(cliente):
    _iniciar_sesion(cliente)

    with patch.object(
        medico_admin_module,
        "api",
        side_effect=_api_falsa,
    ):
        respuesta = cliente.get("/agenda/1?anio=2026&mes=11")

    assert respuesta.status_code == 200

    cuerpo = respuesta.data.decode()
    assert "AGENDA DE Ana Gutierrez" in cuerpo
    assert "Crear agenda" in cuerpo
    assert "modalCrearAgenda" in cuerpo
    assert '"hora": "09:00"' in cuerpo


def test_crear_agenda_envia_los_dias_y_horarios_al_backend(cliente):
    _iniciar_sesion(cliente)

    llamadas = []

    def fake_api(metodo, ruta, **kwargs):
        llamadas.append((metodo, ruta, kwargs))
        return _api_falsa(metodo, ruta, **kwargs)

    with patch.object(medico_admin_module, "api", side_effect=fake_api):
        respuesta = cliente.post(
            "/medicos/1/agenda/crear",
            data={
                "consultorio": "2",
                "duracion_turno": "30",
                "fecha_inicio": "2027-01-01",
                "fecha_hasta": "2027-03-31",
                "dias": ["2", "4"],
                "hora_inicio_2": "08:00",
                "hora_fin_2": "10:00",
                "hora_inicio_4": "16:00",
                "hora_fin_4": "17:30",
            },
        )

    assert respuesta.status_code == 302

    agenda = next(
        llamada for llamada in llamadas
        if llamada[0] == "POST" and llamada[1] == "/agendas"
    )

    assert agenda[2] == {
        "json": {
            "id_medico": 1,
            "id_consultorio": 2,
            "duracion_turno": 30,
            "fecha_inicio": "2027-01-01",
            "fecha_hasta": "2027-03-31",
            "dias": [
                {
                    "dia_semana": 2,
                    "hora_inicio": "08:00:00",
                    "hora_fin": "10:00:00",
                },
                {
                    "dia_semana": 4,
                    "hora_inicio": "16:00:00",
                    "hora_fin": "17:30:00",
                },
            ],
        },
    }


def test_crear_agenda_sin_dias_no_llama_al_backend(cliente):
    _iniciar_sesion(cliente)

    llamadas = []

    def fake_api(metodo, ruta, **kwargs):
        llamadas.append((metodo, ruta, kwargs))
        return _api_falsa(metodo, ruta, **kwargs)

    with patch.object(medico_admin_module, "api", side_effect=fake_api):
        respuesta = cliente.post(
            "/medicos/1/agenda/crear",
            data={
                "consultorio": "2",
                "duracion_turno": "30",
                "fecha_inicio": "2027-01-01",
                "fecha_hasta": "2027-03-31",
            },
        )

    assert respuesta.status_code == 302
    assert not any(
        llamada[0] == "POST" and llamada[1] == "/agendas"
        for llamada in llamadas
    )


def test_editar_medico_actualiza_usuario_y_medico(cliente):
    _iniciar_sesion(cliente)

    llamadas = []

    def fake_api(metodo, ruta, **kwargs):
        llamadas.append((metodo, ruta, kwargs))
        return _api_falsa(metodo, ruta, **kwargs)

    with patch.object(medico_admin_module, "api", side_effect=fake_api):
        respuesta = cliente.post(
            "/medicos/1/editar",
            data={
                "nombre": "Ana",
                "apellido": "Gutierrez",
                "email": "ana.gutierrez@saludintegral.test",
                "documento": "20000001",
                "fecha_nacimiento": "1985-04-12",
                "id_especialidad": "3",
                "matricula": "MN-TEST-1001",
                "coberturas": ["2"],
            },
        )

    assert respuesta.status_code == 302

    rutas = [(metodo, ruta) for metodo, ruta, _ in llamadas]
    assert ("PUT", "/usuarios/6") in rutas
    assert ("PUT", "/medicos/1") in rutas
    assert ("POST", "/medicos/1/coberturas") in rutas


def test_eliminar_medico_llama_al_backend(cliente):
    _iniciar_sesion(cliente)

    with patch.object(medico_admin_module, "api") as llamada:
        respuesta = cliente.post("/medicos/1/eliminar")

    assert respuesta.status_code == 302
    llamada.assert_called_once_with("DELETE", "/medicos/1")


def test_el_abm_de_medicos_requiere_sesion_de_admin(cliente):
    respuesta = cliente.get("/agenda/1")

    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]
