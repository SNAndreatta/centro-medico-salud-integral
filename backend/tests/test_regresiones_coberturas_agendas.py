"""Regresiones de los issues #65 y #66, sin dependencias nuevas de testing."""

from contextlib import contextmanager
import os
import unittest
from uuid import uuid4

from src.validators.agendas_validators import validar_datos_agenda


def _agenda():
    return {
        'id_medico': 1,
        'id_consultorio': 1,
        'duracion_turno': 30,
        'fecha_inicio': '2037-01-01',
        'fecha_hasta': '2037-01-31',
        'dias': [{'dia_semana': 1, 'hora_inicio': '09:00', 'hora_fin': '12:00'}],
    }


def _codigo_error(respuesta):
    return respuesta['errors'][0]['code']


def test_horarios_locales_validos():
    for inicio, fin in [('09:00', '12:00'), ('09:00:00', '12:00:00')]:
        datos = _agenda()
        datos['dias'][0].update(hora_inicio=inicio, hora_fin=fin)
        agenda, error = validar_datos_agenda(datos)
        assert error is None, error
        assert agenda['dias'][0]['horario_inicio_jornada'] == '09:00:00'
        assert agenda['dias'][0]['horario_final_jornada'] == '12:00:00'


def test_zonas_horarias_rechazadas():
    for campo in ('hora_inicio', 'hora_fin'):
        for zona in ('+03:00', '-03:00', '+00:00', 'Z'):
            datos = _agenda()
            datos['dias'][0][campo] += zona
            agenda, error = validar_datos_agenda(datos)
            assert agenda is None, (campo, zona, agenda)
            assert _codigo_error(error) == 'HORA_INVALIDA', (campo, zona, error)


def test_validaciones_existentes_de_jornada():
    casos = [
        ('hora_inicio', '25:00', 'HORA_INVALIDA'),
        ('hora_inicio', None, 'HORA_INVALIDA'),
        ('hora_fin', '08:00', 'RANGO_HORARIO_INVALIDO'),
        ('hora_fin', '11:45', 'DURACION_JORNADA_INVALIDA'),
    ]
    for campo, valor, codigo in casos:
        datos = _agenda()
        datos['dias'][0][campo] = valor
        agenda, error = validar_datos_agenda(datos)
        assert agenda is None
        assert _codigo_error(error) == codigo, error


@contextmanager
def _entorno_api():
    # Las pruebas de integración nunca se ejecutan contra la base habitual.
    if not os.environ.get('DB_NAME', '').startswith('test_'):
        raise unittest.SkipTest('Configurar una base desechable con DB_NAME=test_...')

    from app import app
    from src.config import Config
    from src.db import obtener_conexion

    if not Config.DB_NAME.startswith('test_'):
        raise RuntimeError('La conexión efectiva no apunta a una base de pruebas')

    conexion = obtener_conexion()
    conexion.autocommit = True  # Cada lectura debe ver lo confirmado por la API.
    try:
        cliente = app.test_client()
        login = cliente.post('/api/auth/login', json={
            'correo_electronico': 'admin@saludintegral.test',
            'password': 'admin123',
        })
        assert login.status_code == 200, 'Cargar init_db.sql y seed.sql de prueba'
        cabeceras = {'Authorization': 'Bearer ' + login.get_json()['access_token']}
        yield cliente, cabeceras, conexion
    finally:
        conexion.close()


def _sql(conexion, consulta, parametros=()):
    cursor = conexion.cursor()
    try:
        cursor.execute(consulta, parametros)
        return cursor.fetchall() if cursor.with_rows else []
    finally:
        cursor.close()


def _crear_cobertura_y_plan(cliente, cabeceras):
    respuesta = cliente.post('/api/coberturas', headers=cabeceras,
                             json={'nombre': 'QA-regresion-' + uuid4().hex})
    assert respuesta.status_code == 201, respuesta.get_json()
    cobertura = respuesta.get_json()['cobertura']['id_cobertura']
    respuesta = cliente.post(f'/api/coberturas/{cobertura}/planes',
                             headers=cabeceras, json={'nombre': 'Plan de prueba'})
    assert respuesta.status_code == 201, respuesta.get_json()
    return cobertura, respuesta.get_json()['plan']['id_plan']


def _limpiar_cobertura(conexion, cobertura):
    _sql(conexion, 'DELETE FROM cobertura_medico WHERE id_cobertura=%s', (cobertura,))
    _sql(conexion, 'DELETE FROM plan WHERE id_cobertura=%s', (cobertura,))
    _sql(conexion, 'DELETE FROM cobertura WHERE id_cobertura=%s', (cobertura,))


def test_api_borrado_persistente_de_cobertura_y_planes():
    with _entorno_api() as (cliente, cabeceras, conexion):
        cobertura, plan = _crear_cobertura_y_plan(cliente, cabeceras)
        try:
            respuesta = cliente.delete(f'/api/coberturas/{cobertura}', headers=cabeceras)
            assert respuesta.status_code == 200, respuesta.get_json()
            assert not _sql(conexion, 'SELECT 1 FROM cobertura WHERE id_cobertura=%s', (cobertura,))
            assert not _sql(conexion, 'SELECT 1 FROM plan WHERE id_plan=%s', (plan,))
            listado = cliente.get('/api/coberturas', headers=cabeceras).get_json()['coberturas']
            assert all(fila['id_cobertura'] != cobertura for fila in listado)
            respuesta = cliente.delete(f'/api/coberturas/{cobertura}', headers=cabeceras)
            assert respuesta.status_code == 404
            assert _codigo_error(respuesta.get_json()) == 'COBERTURA_INEXISTENTE'
        finally:
            _limpiar_cobertura(conexion, cobertura)


def test_api_cobertura_con_pacientes_conserva_dependencias():
    with _entorno_api() as (cliente, cabeceras, conexion):
        filas = _sql(conexion, '''
            SELECT DISTINCT pl.id_cobertura FROM plan pl
            JOIN paciente p ON p.id_plan=pl.id_plan ORDER BY pl.id_cobertura
        ''')
        assert filas, 'El seed debe incluir un paciente con cobertura'
        cobertura = filas[0][0]
        planes = _sql(conexion, 'SELECT id_plan,nombre FROM plan WHERE id_cobertura=%s ORDER BY id_plan', (cobertura,))
        respuesta = cliente.delete(f'/api/coberturas/{cobertura}', headers=cabeceras)
        assert respuesta.status_code == 409
        assert _codigo_error(respuesta.get_json()) == 'COBERTURA_EN_USO'
        assert _sql(conexion, 'SELECT 1 FROM cobertura WHERE id_cobertura=%s', (cobertura,))
        assert _sql(conexion, 'SELECT id_plan,nombre FROM plan WHERE id_cobertura=%s ORDER BY id_plan', (cobertura,)) == planes


def test_api_cobertura_con_medico_conserva_dependencias():
    with _entorno_api() as (cliente, cabeceras, conexion):
        cobertura, plan = _crear_cobertura_y_plan(cliente, cabeceras)
        try:
            medico = _sql(conexion, 'SELECT MIN(id_medico) FROM medico')[0][0]
            assert medico is not None, 'Cargar médicos del seed'
            _sql(conexion, 'INSERT INTO cobertura_medico(id_cobertura,id_medico) VALUES (%s,%s)', (cobertura, medico))
            respuesta = cliente.delete(f'/api/coberturas/{cobertura}', headers=cabeceras)
            assert respuesta.status_code == 409
            assert _codigo_error(respuesta.get_json()) == 'COBERTURA_EN_USO'
            assert _sql(conexion, 'SELECT 1 FROM cobertura WHERE id_cobertura=%s', (cobertura,))
            assert _sql(conexion, 'SELECT 1 FROM plan WHERE id_plan=%s', (plan,))
            assert _sql(conexion, 'SELECT 1 FROM cobertura_medico WHERE id_cobertura=%s AND id_medico=%s', (cobertura, medico))
        finally:
            _limpiar_cobertura(conexion, cobertura)


def _limpiar_agenda(conexion, agenda):
    _sql(conexion, 'DELETE FROM agenda_dias WHERE id_agenda=%s', (agenda,))
    _sql(conexion, 'DELETE FROM agenda WHERE id_agenda=%s', (agenda,))


def test_api_zonas_horarias_no_crean_agendas():
    with _entorno_api() as (cliente, cabeceras, conexion):
        antes = (_sql(conexion, 'SELECT COUNT(*) FROM agenda'),
                 _sql(conexion, 'SELECT COUNT(*) FROM agenda_dias'))
        for campo in ('hora_inicio', 'hora_fin'):
            for zona in ('+03:00', '-03:00', '+00:00', 'Z'):
                datos = _agenda()
                datos['dias'][0][campo] += zona
                respuesta = cliente.post('/api/agendas', headers=cabeceras, json=datos)
                agenda_creada = (respuesta.get_json().get('agenda') or {}).get('id_agenda')
                try:
                    assert respuesta.status_code == 400, (campo, zona, respuesta.get_json())
                    assert _codigo_error(respuesta.get_json()) == 'HORA_INVALIDA'
                    despues = (_sql(conexion, 'SELECT COUNT(*) FROM agenda'),
                               _sql(conexion, 'SELECT COUNT(*) FROM agenda_dias'))
                    assert despues == antes, 'La petición inválida dejó filas guardadas'
                finally:
                    if agenda_creada:
                        _limpiar_agenda(conexion, agenda_creada)


def test_api_horarios_locales_se_guardan_correctamente():
    with _entorno_api() as (cliente, cabeceras, conexion):
        for inicio, fin in [('09:00', '12:00'), ('09:00:00', '12:00:00')]:
            datos = _agenda()
            datos['dias'][0].update(hora_inicio=inicio, hora_fin=fin)
            respuesta = cliente.post('/api/agendas', headers=cabeceras, json=datos)
            assert respuesta.status_code == 201, respuesta.get_json()
            agenda = respuesta.get_json()['agenda']['id_agenda']
            try:
                filas = _sql(conexion, '''
                    SELECT CAST(horario_inicio_jornada AS CHAR),
                           CAST(horario_final_jornada AS CHAR)
                    FROM agenda_dias WHERE id_agenda=%s
                ''', (agenda,))
                assert filas == [('09:00:00', '12:00:00')], filas
                respuesta = cliente.delete(f'/api/agendas/{agenda}', headers=cabeceras)
                assert respuesta.status_code == 200
            finally:
                _limpiar_agenda(conexion, agenda)


def load_tests(loader, tests, pattern):
    # unittest permite registrar funciones, sin clases ni paquetes adicionales.
    return unittest.TestSuite(unittest.FunctionTestCase(prueba) for prueba in (
        test_horarios_locales_validos,
        test_zonas_horarias_rechazadas,
        test_validaciones_existentes_de_jornada,
        test_api_borrado_persistente_de_cobertura_y_planes,
        test_api_cobertura_con_pacientes_conserva_dependencias,
        test_api_cobertura_con_medico_conserva_dependencias,
        test_api_zonas_horarias_no_crean_agendas,
        test_api_horarios_locales_se_guardan_correctamente,
    ))
