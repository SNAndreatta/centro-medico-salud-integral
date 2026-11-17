"""Procesamiento automático de ausentismo (issue #53/#54).

Verifica que `ejecutar_ausentismo_automatico` delega correctamente en el
repositorio y que `marcar_ausentes_automatico` llama a la base de datos
con los parámetros correctos.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.services.turnos_services import ejecutar_ausentismo_automatico


class TestAusentismoAutomatico(unittest.TestCase):

    def test_devuelve_cantidad_de_turnos_marcados(self):
        with patch('src.services.turnos_services.marcar_ausentes_automatico') as mock_marcar:
            mock_marcar.return_value = 3

            resultado = ejecutar_ausentismo_automatico()

        self.assertEqual(resultado, 3)
        mock_marcar.assert_called_once()

    def test_devuelve_cero_cuando_no_hay_turnos_vencidos(self):
        with patch('src.services.turnos_services.marcar_ausentes_automatico') as mock_marcar:
            mock_marcar.return_value = 0

            resultado = ejecutar_ausentismo_automatico()

        self.assertEqual(resultado, 0)

    def test_repositorio_ejecuta_update_con_condiciones_correctas(self):
        conexion_mock = MagicMock()
        cursor_mock = MagicMock()
        cursor_mock.rowcount = 2
        conexion_mock.__enter__ = MagicMock(return_value=conexion_mock)

        with patch('src.repositories.turnos_repositories.obtener_cursor') as mock_cursor:
            mock_cursor.return_value = (conexion_mock, cursor_mock)

            from src.repositories.turnos_repositories import marcar_ausentes_automatico
            resultado = marcar_ausentes_automatico()

        self.assertEqual(resultado, 2)
        cursor_mock.execute.assert_called_once()
        sql = cursor_mock.execute.call_args[0][0]
        self.assertIn('reservado', sql.lower())
        self.assertIn('ausente', sql.lower())
        self.assertIn('fecha_horario_llegada', sql.lower())
        self.assertIn('interval 15 minute', sql.lower())
        conexion_mock.commit.assert_called_once()

    def test_repositorio_hace_rollback_ante_excepcion(self):
        conexion_mock = MagicMock()
        cursor_mock = MagicMock()
        cursor_mock.execute.side_effect = Exception('error de base de datos')

        with patch('src.repositories.turnos_repositories.obtener_cursor') as mock_cursor:
            mock_cursor.return_value = (conexion_mock, cursor_mock)

            from src.repositories.turnos_repositories import marcar_ausentes_automatico
            with self.assertRaises(Exception):
                marcar_ausentes_automatico()

        conexion_mock.rollback.assert_called_once()
        conexion_mock.commit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
