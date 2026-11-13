import unittest
from datetime import date, datetime
from unittest.mock import patch

from src.services.usuarios_services import obtener_perfil_usuario
from src.utils.roles import ADMINISTRADOR, MEDICO, PACIENTE, RECEPCIONISTA


def _usuario(id_rol):
    return {
        'id_usuario': 8,
        'id_rol': id_rol,
        'nombre': 'Ana',
        'apellido': 'Díaz',
        'correo_electronico': 'ana@example.com',
        'dni': '30123456',
        'fecha_nacimiento': date(1990, 5, 12),
        'fecha_creacion': datetime(2026, 1, 2, 3, 4, 5),
    }


class TestObtenerPerfilUsuario(unittest.TestCase):
    @patch('src.services.usuarios_services.obtener_medico_por_usuario')
    @patch('src.services.usuarios_services.obtener_paciente_por_usuario')
    @patch('src.services.usuarios_services.obtener_usuario_por_id')
    def test_admin_recibe_solo_datos_de_cuenta(self, por_id, paciente_por_usuario, medico_por_usuario):
        por_id.return_value = _usuario(ADMINISTRADOR)

        perfil = obtener_perfil_usuario(8)

        self.assertEqual(perfil['id_usuario'], 8)
        self.assertEqual(perfil['id_rol'], ADMINISTRADOR)
        self.assertEqual(perfil['correo_electronico'], 'ana@example.com')
        self.assertNotIn('paciente', perfil)
        self.assertNotIn('medico', perfil)
        paciente_por_usuario.assert_not_called()
        medico_por_usuario.assert_not_called()

    @patch('src.services.usuarios_services.obtener_medico_por_usuario')
    @patch('src.services.usuarios_services.obtener_paciente_por_id')
    @patch('src.services.usuarios_services.obtener_paciente_por_usuario')
    @patch('src.services.usuarios_services.obtener_usuario_por_id')
    def test_paciente_incluye_su_perfil(
        self, por_id, paciente_por_usuario, paciente_por_id, medico_por_usuario
    ):
        por_id.return_value = _usuario(PACIENTE)
        paciente_por_usuario.return_value = 12
        paciente_por_id.return_value = {
            'id_paciente': 12,
            'id_cobertura': 3,
            'nombre_cobertura': 'OSDE',
            'nro_afiliado': '123456',
        }

        perfil = obtener_perfil_usuario(8)

        self.assertEqual(perfil['paciente'], {
            'id_paciente': 12,
            'id_cobertura': 3,
            'nombre_cobertura': 'OSDE',
            'nro_afiliado': '123456',
        })
        self.assertNotIn('medico', perfil)
        paciente_por_usuario.assert_called_once_with(8)
        paciente_por_id.assert_called_once_with(12)
        medico_por_usuario.assert_not_called()

    @patch('src.services.usuarios_services.obtener_medico_por_usuario')
    @patch('src.services.usuarios_services.obtener_paciente_por_usuario')
    @patch('src.services.usuarios_services.obtener_usuario_por_id')
    def test_medico_incluye_su_perfil(self, por_id, paciente_por_usuario, medico_por_usuario):
        por_id.return_value = _usuario(MEDICO)
        medico_por_usuario.return_value = {
            'id_medico': 5,
            'id_especialidad': 2,
            'nombre_especialidad': 'Cardiología',
            'matricula': 'MP-1234',
        }

        perfil = obtener_perfil_usuario(8)

        self.assertEqual(perfil['medico'], {
            'id_medico': 5,
            'id_especialidad': 2,
            'nombre_especialidad': 'Cardiología',
            'matricula': 'MP-1234',
        })
        self.assertNotIn('paciente', perfil)
        medico_por_usuario.assert_called_once_with(8)
        paciente_por_usuario.assert_not_called()

    @patch('src.services.usuarios_services.obtener_usuario_por_id')
    def test_usuario_inexistente_devuelve_none(self, por_id):
        por_id.return_value = None

        self.assertIsNone(obtener_perfil_usuario(8))

    @patch('src.services.usuarios_services.obtener_medico_por_usuario')
    @patch('src.services.usuarios_services.obtener_paciente_por_usuario')
    @patch('src.services.usuarios_services.obtener_usuario_por_id')
    def test_recepcion_no_consulta_perfiles_especificos(
        self, por_id, paciente_por_usuario, medico_por_usuario
    ):
        por_id.return_value = _usuario(RECEPCIONISTA)

        perfil = obtener_perfil_usuario(8)

        self.assertNotIn('paciente', perfil)
        self.assertNotIn('medico', perfil)
        paciente_por_usuario.assert_not_called()
        medico_por_usuario.assert_not_called()


if __name__ == '__main__':
    unittest.main()
