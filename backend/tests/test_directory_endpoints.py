import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

os.environ.setdefault('FLASK_DEBUG', 'true')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-jwt-authentication')

import jwt
from werkzeug.security import check_password_hash

from app import app
from src.config import Config


def authorization(role_id):
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            'sub': '10',
            'id_rol': role_id,
            'iat': now,
            'exp': now + timedelta(minutes=5),
        },
        Config.SECRET_KEY,
        algorithm='HS256',
    )
    return {'Authorization': f'Bearer {token}'}


class DirectoryEndpointTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_list_users_is_admin_only_and_accepts_role_filter(self):
        with patch(
            'src.routes.usuarios_routes.listar_usuarios_staff',
            return_value=[{'id_usuario': 1, 'id_rol': 1, 'nombre': 'Admin'}],
        ) as listar:
            response = self.client.get(
                '/api/usuarios?rol=admin',
                headers=authorization(1),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['usuarios']), 1)
        listar.assert_called_once_with('admin')

        forbidden = self.client.get('/api/usuarios', headers=authorization(2))
        self.assertEqual(forbidden.status_code, 403)

    def test_list_users_rejects_unknown_role_filter(self):
        response = self.client.get('/api/usuarios?rol=paciente', headers=authorization(1))
        self.assertEqual(response.status_code, 400)

    def test_create_staff_hashes_password_and_returns_safe_profile(self):
        with patch(
            'src.services.usuarios_services.guardar_usuario_staff',
            return_value={
                'id_usuario': 11,
                'id_rol': 2,
                'nombre': 'Sofia',
                'apellido': 'Recepcion',
                'correo_electronico': 'sofia@example.com',
                'dni': '12345678',
            },
        ) as guardar:
            response = self.client.post(
                '/api/usuarios',
                headers=authorization(1),
                json={
                    'nombre': 'Sofia',
                    'apellido': 'Recepcion',
                    'dni': '12345678',
                    'correo_electronico': 'SOFIA@example.com',
                    'password': 'plain-password',
                    'id_rol': 2,
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn('contrasenia', response.json['usuario'])
        stored_user = guardar.call_args.args[0]
        self.assertTrue(check_password_hash(stored_user['contrasenia'], 'plain-password'))
        self.assertEqual(stored_user['correo_electronico'], 'sofia@example.com')

    def test_create_staff_rejects_patient_role_and_non_admin(self):
        payload = {
            'nombre': 'Patient',
            'apellido': 'Example',
            'dni': '12345678',
            'correo_electronico': 'patient@example.com',
            'password': 'secret',
            'id_rol': 3,
        }
        invalid_role = self.client.post('/api/usuarios', headers=authorization(1), json=payload)
        self.assertEqual(invalid_role.status_code, 400)

        payload['id_rol'] = 2
        forbidden = self.client.post('/api/usuarios', headers=authorization(2), json=payload)
        self.assertEqual(forbidden.status_code, 403)

    def test_create_staff_rejects_fields_longer_than_database_columns(self):
        response = self.client.post(
            '/api/usuarios',
            headers=authorization(1),
            json={
                'nombre': 'N' * 101,
                'apellido': 'Example',
                'dni': '12345678',
                'correo_electronico': 'person@example.com',
                'password': 'secret',
                'id_rol': 2,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_doctor_search_requires_token_and_forwards_filters(self):
        unauthenticated = self.client.get('/api/medicos')
        self.assertEqual(unauthenticated.status_code, 401)

        with patch(
            'src.routes.medicos_routes.filtrar_medicos',
            return_value=({'medicos': []}, 200),
        ) as filtrar:
            response = self.client.get(
                '/api/medicos?id_especialidad=3&id_cobertura=1&nombre=ana',
                headers=authorization(3),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(filtrar.call_args.args[0].get('id_especialidad'), '3')
        self.assertEqual(filtrar.call_args.args[0].get('id_cobertura'), '1')

    def test_patient_search_is_limited_to_staff(self):
        with patch(
            'src.routes.pacientes_routes.filtrar_pacientes',
            return_value=({'pacientes': []}, 200),
        ) as filtrar:
            response = self.client.get(
                '/api/pacientes?dni=40000001&apellido=Rossi',
                headers=authorization(2),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(filtrar.call_args.args[0].get('dni'), '40000001')
        self.assertEqual(filtrar.call_args.args[0].get('apellido'), 'Rossi')

        forbidden = self.client.get('/api/pacientes', headers=authorization(3))
        self.assertEqual(forbidden.status_code, 403)


if __name__ == '__main__':
    unittest.main()
