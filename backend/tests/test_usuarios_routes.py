import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt

from app import app
from src.config import Config
from src.utils.roles import MEDICO, PACIENTE


def _token(id_usuario, id_rol):
    ahora = datetime.now(timezone.utc)
    return jwt.encode(
        {
            'sub': str(id_usuario),
            'id_rol': id_rol,
            'iat': ahora,
            'exp': ahora + timedelta(minutes=5),
        },
        Config.SECRET_KEY,
        algorithm='HS256',
    )


class TestUsuariosMeRoute(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def _get(self, id_usuario, id_rol):
        return self.client.get(
            '/api/usuarios/me',
            headers={'Authorization': f'Bearer {_token(id_usuario, id_rol)}'},
        )

    @patch('src.routes.usuarios_routes.obtener_perfil_usuario')
    def test_paciente_recibe_datos_de_paciente(self, obtener_perfil):
        obtener_perfil.return_value = {
            'id_usuario': 8,
            'nombre': 'Ana',
            'apellido': 'Díaz',
            'id_rol': PACIENTE,
            'paciente': {'id_paciente': 12, 'nombre_cobertura': 'OSDE'},
        }

        respuesta = self._get(8, PACIENTE)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json()['paciente']['id_paciente'], 12)
        obtener_perfil.assert_called_once_with(8)

    @patch('src.routes.usuarios_routes.obtener_perfil_usuario')
    def test_medico_recibe_datos_de_medico(self, obtener_perfil):
        obtener_perfil.return_value = {
            'id_usuario': 9,
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'id_rol': MEDICO,
            'medico': {'id_medico': 5, 'matricula': 'MP-1234'},
        }

        respuesta = self._get(9, MEDICO)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json()['medico']['matricula'], 'MP-1234')

    @patch('src.routes.usuarios_routes.obtener_perfil_usuario')
    def test_usuario_inexistente_devuelve_401(self, obtener_perfil):
        obtener_perfil.return_value = None

        respuesta = self._get(8, PACIENTE)

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(
            respuesta.get_json()['errors'][0]['code'], 'USUARIO_INEXISTENTE'
        )

    def test_sin_token_devuelve_401(self):
        respuesta = self.client.get('/api/usuarios/me')

        self.assertEqual(respuesta.status_code, 401)


if __name__ == '__main__':
    unittest.main()
