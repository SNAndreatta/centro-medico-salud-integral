import unittest
from unittest.mock import patch

from src.services import smtp_service
from src.utils import tokens


class TestSmtpTurnos(unittest.TestCase):
    def test_generar_token_cancelacion_turno_roundtrip(self):
        with patch.multiple(
            tokens.Config,
            SECRET_KEY='secret-key-para-turnos-1234567890',
            CANCELACION_TTL_MINUTES=60,
        ):
            token = tokens.generar_token_cancelacion_turno(14, 9)
            payload = tokens.validar_token_cancelacion_turno(token)

        self.assertEqual(payload['id_turno'], 14)
        self.assertEqual(payload['id_paciente'], 9)
        self.assertEqual(payload['tipo'], 'cancelacion_turno')

    def test_enviar_comprobante_turno_usa_smtp(self):
        class DummySMTP:
            def __init__(self):
                self.sent = []

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def send_message(self, mensaje):
                self.sent.append(mensaje)

        dummy = DummySMTP()
        with patch.multiple(
            smtp_service.Config,
            SMTP_ENABLED=True,
            SMTP_SERVER='smtp.example.com',
            SMTP_PORT=587,
            SMTP_USE_TLS=True,
            SMTP_USE_SSL=False,
            SMTP_USERNAME='user@example.com',
            SMTP_PASSWORD='secret',
            SMTP_DEFAULT_SENDER='no-reply@saludintegral.test',
            PUBLIC_BASE_URL='http://localhost:5000',
        ), patch.object(smtp_service, '_crear_servidor_smtp', return_value=dummy):
            turno = {
                'id_turno': 14,
                'fecha_horario_inicial': '2026-11-08 09:30:00',
                'medico': {'nombre': 'Ana', 'apellido': 'Lopez', 'especialidad': 'Cardiología'},
                'consultorio': {'numero': 3, 'piso': 2},
            }
            paciente = {
                'id_paciente': 9,
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'correo_electronico': 'juan@test.com',
            }

            result = smtp_service.enviar_comprobante_turno(
                turno,
                paciente,
                b'fake-png-bytes',
                'image/png',
            )

        self.assertTrue(result['enviado'])
        self.assertEqual(len(dummy.sent), 1)

        html_part = next(
            (
                part.get_payload(decode=True).decode('utf-8')
                for part in dummy.sent[0].walk()
                if part.get_content_type() == 'text/html'
            ),
            None,
        )

        self.assertIsNotNone(html_part)
        self.assertIn('Comprobante de turno', html_part)
        self.assertIn('Cancelar reserva', html_part)
        self.assertIn('juan@test.com', dummy.sent[0]['To'])


if __name__ == '__main__':
    unittest.main()
