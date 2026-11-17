"""Procesamiento automático de ausentismo (issue #53/#54)."""

import unittest
from unittest.mock import patch, MagicMock

from src.services.turnos_services import ejecutar_ausentismo_automatico


class TestAusentismoAutomatico(unittest.TestCase):

    def _patch_base(self, ids, id_estado_ausente=5):
        return (
            patch('src.services.turnos_services.buscar_id_estado_turno', return_value=id_estado_ausente),
            patch('src.services.turnos_services.buscar_ids_turnos_ausentes_pendientes', return_value=ids),
            patch('src.services.turnos_services.actualizar_estado_turno'),
        )

    def test_devuelve_cantidad_de_turnos_marcados(self):
        p_estado, p_ids, p_actualizar = self._patch_base([10, 20, 30])
        with p_estado, p_ids, p_actualizar as mock_actualizar:
            mock_actualizar.return_value = ({'mensaje': 'ok'}, 200)

            resultado = ejecutar_ausentismo_automatico()

        self.assertEqual(resultado, 3)
        self.assertEqual(mock_actualizar.call_count, 3)

    def test_devuelve_cero_cuando_no_hay_turnos_vencidos(self):
        p_estado, p_ids, p_actualizar = self._patch_base([])
        with p_estado, p_ids, p_actualizar as mock_actualizar:
            resultado = ejecutar_ausentismo_automatico()

        self.assertEqual(resultado, 0)
        mock_actualizar.assert_not_called()

    def test_llama_a_actualizar_con_el_id_correcto(self):
        p_estado, p_ids, p_actualizar = self._patch_base([42], id_estado_ausente=5)
        with p_estado, p_ids, p_actualizar as mock_actualizar:
            mock_actualizar.return_value = ({'mensaje': 'ok'}, 200)

            ejecutar_ausentismo_automatico()

        mock_actualizar.assert_called_once_with(42, 5)

    def test_no_cuenta_turnos_que_no_se_pudieron_marcar(self):
        p_estado, p_ids, p_actualizar = self._patch_base([10, 20])
        with p_estado, p_ids, p_actualizar as mock_actualizar:
            mock_actualizar.side_effect = [
                ({'mensaje': 'ok'}, 200),
                ({'errors': [{'code': 'TRANSICION_ESTADO_INVALIDA'}]}, 400),
            ]

            resultado = ejecutar_ausentismo_automatico()

        self.assertEqual(resultado, 1)

    def test_repositorio_busca_solo_reservados_sin_llegada_vencidos(self):
        conexion_mock = MagicMock()
        cursor_mock = MagicMock()
        cursor_mock.fetchall.return_value = []

        with patch('src.repositories.turnos_repositories.obtener_cursor') as mock_cursor:
            mock_cursor.return_value = (conexion_mock, cursor_mock)

            from src.repositories.turnos_repositories import buscar_ids_turnos_ausentes_pendientes
            buscar_ids_turnos_ausentes_pendientes()

        sql = cursor_mock.execute.call_args[0][0]
        self.assertIn('reservado', sql.lower())
        self.assertIn('fecha_horario_llegada', sql.lower())
        self.assertIn('interval 15 minute', sql.lower())


if __name__ == '__main__':
    unittest.main()
