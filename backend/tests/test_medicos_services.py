import unittest
from unittest.mock import patch

from src.services.medicos_services import eliminar_medico, modificar_medico


class TestMedicosServices(unittest.TestCase):
    @patch('src.services.medicos_services.obtener_medico_por_id')
    @patch('src.services.medicos_services.actualizar_especialidad_medico')
    def test_modificar_especialidad_medico(self, actualizar, obtener):
        medico_actualizado = {'id_medico': 5, 'id_especialidad': 3}
        obtener.return_value = medico_actualizado

        respuesta, status = modificar_medico(5, {'id_especialidad': 3})

        self.assertEqual(status, 200)
        self.assertEqual(respuesta, {'medico': medico_actualizado})
        actualizar.assert_called_once_with(5, 3)
        obtener.assert_called_once_with(5)

    @patch('src.services.medicos_services.actualizar_especialidad_medico')
    def test_modificar_medico_rechaza_cuerpo_invalido(self, actualizar):
        respuesta, status = modificar_medico(5, {'id_especialidad': True})

        self.assertEqual(status, 400)
        self.assertEqual(respuesta['errors'][0]['code'], 'ESPECIALIDAD_INVALIDA')
        actualizar.assert_not_called()

    @patch('src.services.medicos_services.actualizar_especialidad_medico')
    def test_modificar_medico_inexistente(self, actualizar):
        actualizar.return_value = 'MEDICO_NO_EXISTE'

        respuesta, status = modificar_medico(99, {'id_especialidad': 3})

        self.assertEqual(status, 404)
        self.assertEqual(respuesta['errors'][0]['code'], 'MEDICO_INEXISTENTE')

    @patch('src.services.medicos_services.eliminar_medico_repositorio')
    def test_eliminar_medico_con_turnos_devuelve_conflicto(self, eliminar):
        eliminar.return_value = 'MEDICO_CON_TURNOS'

        respuesta, status = eliminar_medico(5)

        self.assertEqual(status, 409)
        self.assertEqual(respuesta['errors'][0]['code'], 'MEDICO_CON_TURNOS')

    @patch('src.services.medicos_services.eliminar_medico_repositorio')
    def test_eliminar_medico_exitosamente(self, eliminar):
        eliminar.return_value = None

        respuesta, status = eliminar_medico(5)

        self.assertEqual(status, 200)
        self.assertEqual(respuesta['mensaje'], 'Médico eliminado correctamente')