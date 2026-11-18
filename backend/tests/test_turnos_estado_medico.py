"""Estado de los turnos visto por el médico (ownership, estado por nombre y rango)."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from src.services.turnos_services import actualizar_estado_turno
from src.validators.turnos_validators import validar_estado_turno


def _en(horas):
    """Un horario relativo a la hora local de ahora."""
    return (
        datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
        .replace(tzinfo=None, second=0, microsecond=0)
        + timedelta(hours=horas)
    )


TURNO = {
    'id_estado': 3,
    'id_paciente': 1,
    'fecha_horario_inicial': _en(-1),
    'fecha_horario_llegada': None,
    'estado_actual': 'confirmado',
    'estado_destino': 'atendido',
    'id_usuario_medico': 104,
}


class TestEstadoTurnoMedico(unittest.TestCase):

    def test_medico_puede_marcar_su_propio_turno_como_atendido(self):
        with patch('src.services.turnos_services.buscar_turno_y_estado_destino') as buscar, \
                patch('src.services.turnos_services.guardar_estado_turno') as guardar:
            buscar.return_value = dict(TURNO)
            guardar.return_value = True

            respuesta, status = actualizar_estado_turno(
                10,
                4,
                {'id_usuario': 104, 'id_rol': 4},
            )

        self.assertEqual(status, 200)
        self.assertEqual(respuesta['estado'], 'atendido')
        guardar.assert_called_once()

    def test_medico_no_puede_modificar_el_turno_de_otro_medico(self):
        with patch('src.services.turnos_services.buscar_turno_y_estado_destino') as buscar, \
                patch('src.services.turnos_services.guardar_estado_turno') as guardar:
            buscar.return_value = dict(TURNO)

            respuesta, status = actualizar_estado_turno(
                10,
                4,
                {'id_usuario': 105, 'id_rol': 4},
            )

        self.assertEqual(status, 403)
        self.assertEqual(respuesta['errors'][0]['code'], 'TURNO_NO_AUTORIZADO')
        guardar.assert_not_called()

    def test_admin_puede_modificar_el_turno_de_cualquier_medico(self):
        with patch('src.services.turnos_services.buscar_turno_y_estado_destino') as buscar, \
                patch('src.services.turnos_services.guardar_estado_turno') as guardar:
            buscar.return_value = dict(TURNO)
            guardar.return_value = True

            respuesta, status = actualizar_estado_turno(
                10,
                4,
                {'id_usuario': 101, 'id_rol': 1},
            )

        self.assertEqual(status, 200)
        guardar.assert_called_once()

    def test_el_estado_se_puede_enviar_por_nombre(self):
        id_estado, nombre_estado, error = validar_estado_turno({'estado': 'Atendido'})

        self.assertIsNone(error)
        self.assertIsNone(id_estado)
        self.assertEqual(nombre_estado, 'atendido')

    def test_el_estado_tambien_se_puede_enviar_por_id(self):
        id_estado, nombre_estado, error = validar_estado_turno({'id_estado': 4})

        self.assertIsNone(error)
        self.assertEqual(id_estado, 4)
        self.assertIsNone(nombre_estado)

    def test_un_estado_invalido_es_rechazado(self):
        id_estado, nombre_estado, error = validar_estado_turno({'id_estado': 'atendido'})

        self.assertIsNone(id_estado)
        self.assertIsNone(nombre_estado)
        self.assertEqual(error[1], 400)

    def test_no_se_puede_marcar_como_atendido_un_turno_fuera_de_la_jornada(self):
        turno = dict(TURNO)
        turno['fecha_horario_inicial'] = _en(48)

        with patch('src.services.turnos_services.buscar_turno_y_estado_destino') as buscar, \
                patch('src.services.turnos_services.guardar_estado_turno') as guardar:
            buscar.return_value = turno

            respuesta, status = actualizar_estado_turno(
                10,
                4,
                {'id_usuario': 104, 'id_rol': 4},
            )

        self.assertEqual(status, 409)
        self.assertEqual(respuesta['errors'][0]['code'], 'TURNO_FUERA_DE_RANGO')
        guardar.assert_not_called()

    def test_no_se_puede_marcar_como_atendido_un_turno_que_todavia_no_ocurrio(self):
        turno = dict(TURNO)
        turno['fecha_horario_inicial'] = _en(5)

        with patch('src.services.turnos_services.buscar_turno_y_estado_destino') as buscar, \
                patch('src.services.turnos_services.guardar_estado_turno') as guardar:
            buscar.return_value = turno

            respuesta, status = actualizar_estado_turno(
                10,
                4,
                {'id_usuario': 104, 'id_rol': 4},
            )

        self.assertEqual(status, 409)
        guardar.assert_not_called()

