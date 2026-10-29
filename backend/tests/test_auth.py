import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

os.environ.setdefault('FLASK_DEBUG', 'true')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-jwt-authentication')

import jwt
from flask import jsonify
from werkzeug.security import generate_password_hash

from app import app
from src.config import Config
from src.utils.auth import roles_required, token_required


@app.get('/_test/admin-only')
@token_required
@roles_required(1)
def admin_only_test_route():
    return jsonify({'ok': True})


class AuthTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_login_returns_jwt_and_safe_profile(self):
        user = {
            'id_usuario': 7,
            'id_rol': 3,
            'nombre': 'Ana',
            'apellido': 'Rossi',
            'correo_electronico': 'ana@example.com',
            'contrasenia': generate_password_hash('correct-password'),
        }
        with patch('src.services.auth_service.obtener_usuario_por_email', return_value=user):
            response = self.client.post(
                '/api/auth/login',
                json={
                    'correo_electronico': 'ana@example.com',
                    'password': 'correct-password',
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['usuario']['id_rol'], 3)
        self.assertNotIn('contrasenia', response.json['usuario'])
        claims = jwt.decode(
            response.json['access_token'],
            Config.SECRET_KEY,
            algorithms=['HS256'],
        )
        self.assertEqual(claims['sub'], '7')
        self.assertEqual(claims['id_rol'], 3)
        self.assertGreater(claims['exp'], claims['iat'])

    def test_invalid_credentials_return_401(self):
        user = {
            'id_usuario': 7,
            'id_rol': 3,
            'contrasenia': generate_password_hash('correct-password'),
        }
        with patch('src.services.auth_service.obtener_usuario_por_email', return_value=user):
            response = self.client.post(
                '/api/auth/login',
                json={
                    'correo_electronico': 'ana@example.com',
                    'password': 'wrong-password',
                },
            )

        self.assertEqual(response.status_code, 401)

    def test_missing_login_fields_return_400(self):
        response = self.client.post('/api/auth/login', json={'correo_electronico': 'ana@example.com'})
        self.assertEqual(response.status_code, 400)

    def test_me_requires_token_and_returns_safe_profile(self):
        missing_token_response = self.client.get('/api/usuarios/me')
        self.assertEqual(missing_token_response.status_code, 401)

        token = jwt.encode(
            {
                'sub': '7',
                'id_rol': 3,
                'iat': datetime.now(timezone.utc),
                'exp': datetime.now(timezone.utc) + timedelta(minutes=5),
            },
            Config.SECRET_KEY,
            algorithm='HS256',
        )
        user = {'id_usuario': 7, 'id_rol': 3, 'nombre': 'Ana', 'apellido': 'Rossi'}
        with patch('src.routes.usuarios_routes.obtener_usuario_por_id', return_value=user):
            response = self.client.get(
                '/api/usuarios/me',
                headers={'Authorization': f'Bearer {token}'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id_usuario'], 7)
        self.assertNotIn('contrasenia', response.json)

    def test_expired_token_returns_401(self):
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {'sub': '7', 'id_rol': 3, 'iat': now - timedelta(minutes=2), 'exp': now - timedelta(minutes=1)},
            Config.SECRET_KEY,
            algorithm='HS256',
        )
        response = self.client.get(
            '/api/usuarios/me',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.status_code, 401)

    def test_role_guard_returns_403_for_wrong_role(self):
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {'sub': '7', 'id_rol': 3, 'iat': now, 'exp': now + timedelta(minutes=5)},
            Config.SECRET_KEY,
            algorithm='HS256',
        )
        response = self.client.get(
            '/api/_test/admin-only',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    unittest.main()