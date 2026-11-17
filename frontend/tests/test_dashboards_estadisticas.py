import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

FRONTEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRONTEND))

from app import app  # noqa: E402
from src.api import ErrorAPI  # noqa: E402
from routes.admin.dashboards import ausentismo as ausentismo_module  # noqa: E402
from routes.admin.dashboards import tiempo_espera as tiempo_module  # noqa: E402
from routes.admin.dashboards import turnos_especialidad as especialidad_module  # noqa: E402


AUSENTISMO = {
    'resumen': {'total': 11, 'atendidos': 8, 'ausentes': 2, 'cancelados': 1},
    'medicos': [{
        'id_medico': 2, 'nombre': 'Luis', 'apellido': 'Pérez',
        'ausentes': 2, 'considerados': 4, 'porcentaje': 50,
    }],
    'especialidades': [{
        'id_especialidad': 1, 'nombre': 'Cardiología',
        'ausentes': 1, 'considerados': 10, 'porcentaje': 10,
    }],
}

TIEMPO_ESPERA = {
    'turnos_considerados': 3,
    'medicos': [{
        'id_medico': 2, 'nombre': 'Luis', 'apellido': 'Pérez',
        'espera': 13, 'turnos': 3,
    }],
    'especialidades': [{
        'id_especialidad': 1, 'nombre': 'Cardiología', 'espera': 13, 'turnos': 3,
    }],
}

TURNO = {
    'id_turno': 7,
    'fecha_horario_inicial': '2026-11-20 09:30:00',
    'medico': {
        'id_medico': 2, 'nombre': 'Luis', 'apellido': 'Pérez',
        'especialidad': 'Cardiología',
    },
    'paciente': {'nombre': 'Ana', 'apellido': 'Sosa'},
    'consultorio': {'numero': 3},
    'estado': {'nombre': 'reservado'},
}

TURNOS_ESPECIALIDAD = {
    'total_turnos': 1,
    'especialidades': [{
        'id_especialidad': 1, 'nombre': 'Cardiología',
        'total_turnos': 1, 'turnos': [TURNO],
    }],
}


@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    app.secret_key = 'test'
    return app.test_client()


def _iniciar_sesion(cliente):
    with cliente.session_transaction() as sesion:
        sesion['access_token'] = 'token'
        sesion['rol'] = 'administrador'
        sesion['nombre'] = 'Admin'
        sesion['apellido'] = 'Root'


def test_ausentismo_usa_el_endpoint_agregado(cliente):
    _iniciar_sesion(cliente)

    with patch.object(ausentismo_module.api_estadisticas, 'ausentismo', return_value=AUSENTISMO) as getter:
        respuesta = cliente.get('/admin/ausentismo?fecha_desde=2026-11-01&fecha_hasta=2026-11-30')

    assert respuesta.status_code == 200
    cuerpo = respuesta.data.decode()
    assert 'Luis Pérez' in cuerpo
    assert '2 de 4 turnos' in cuerpo
    assert '50%' in cuerpo
    getter.assert_called_once_with({
        'fecha_desde': '2026-11-01', 'fecha_hasta': '2026-11-30',
    })


def test_ausentismo_hace_fallback_si_falla_el_endpoint(cliente):
    _iniciar_sesion(cliente)
    turnos = [{
        'estado': {'nombre': 'ausente'},
        'medico': {'id_medico': 1, 'nombre': 'Ana', 'apellido': 'Martínez',
                   'especialidad': 'Clínica'},
    }]

    with patch.object(ausentismo_module.api_estadisticas, 'ausentismo',
                      side_effect=ErrorAPI('sin servicio', 503)), \
         patch.object(ausentismo_module, 'api', return_value={'turnos': turnos}) as api_mock:
        respuesta = cliente.get('/admin/ausentismo')

    cuerpo = respuesta.data.decode()
    assert 'sin servicio' in cuerpo
    assert 'Ana Martínez' in cuerpo
    assert api_mock.call_args.args[:2] == ('GET', '/turnos')


def test_tiempo_espera_usa_el_endpoint_agregado(cliente):
    _iniciar_sesion(cliente)

    with patch.object(tiempo_module.api_estadisticas, 'tiempo_espera', return_value=TIEMPO_ESPERA) as getter:
        respuesta = cliente.get('/admin/tiempo-espera')

    assert respuesta.status_code == 200
    cuerpo = respuesta.data.decode()
    assert 'Luis Pérez' in cuerpo
    assert '13 min' in cuerpo
    assert '3 turnos con registro de llegada' in re.sub(r'\s+', ' ', cuerpo)
    getter.assert_called_once_with({})


def test_turnos_por_especialidad_usa_el_endpoint_agregado(cliente):
    _iniciar_sesion(cliente)

    with patch.object(especialidad_module.api_estadisticas, 'turnos_por_especialidad',
                      return_value=TURNOS_ESPECIALIDAD) as getter:
        respuesta = cliente.get('/admin/turnos-especialidad')

    assert respuesta.status_code == 200
    cuerpo = respuesta.data.decode()
    assert 'Cardiología' in cuerpo
    assert 'Luis Pérez' in cuerpo
    assert '09:30' in cuerpo
    getter.assert_called_once_with({})


def test_turnos_por_especialidad_hace_fallback(cliente):
    _iniciar_sesion(cliente)

    with patch.object(especialidad_module.api_estadisticas, 'turnos_por_especialidad',
                      side_effect=ErrorAPI('sin servicio', 503)), \
         patch.object(especialidad_module, 'api', return_value={'turnos': [TURNO]}) as api_mock:
        respuesta = cliente.get('/admin/turnos-especialidad')

    cuerpo = respuesta.data.decode()
    assert 'sin servicio' in cuerpo
    assert 'Luis Pérez' in cuerpo
    assert api_mock.call_args.args[:2] == ('GET', '/turnos')
