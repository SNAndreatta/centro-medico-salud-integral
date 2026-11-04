from src.services import smtp_service


def test_generar_token_cancelacion_turno_roundtrip(monkeypatch):
    monkeypatch.setattr(smtp_service.Config, 'SECRET_KEY', 'secret-key-para-turnos-1234567890')
    monkeypatch.setattr(smtp_service.Config, 'CANCELACION_TTL_MINUTES', 60)

    token = smtp_service.generar_token_cancelacion_turno(14, 9)
    payload = smtp_service.validar_token_cancelacion_turno(token)

    assert payload['id_turno'] == 14
    assert payload['id_paciente'] == 9
    assert payload['tipo'] == 'cancelacion_turno'


def test_enviar_comprobante_turno_usa_smtp(monkeypatch):
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
    monkeypatch.setattr(smtp_service.Config, 'SMTP_ENABLED', True)
    monkeypatch.setattr(smtp_service.Config, 'SMTP_SERVER', 'smtp.example.com')
    monkeypatch.setattr(smtp_service.Config, 'SMTP_PORT', 587)
    monkeypatch.setattr(smtp_service.Config, 'SMTP_USE_TLS', True)
    monkeypatch.setattr(smtp_service.Config, 'SMTP_USE_SSL', False)
    monkeypatch.setattr(smtp_service.Config, 'SMTP_USERNAME', 'user@example.com')
    monkeypatch.setattr(smtp_service.Config, 'SMTP_PASSWORD', 'secret')
    monkeypatch.setattr(smtp_service.Config, 'SMTP_DEFAULT_SENDER', 'no-reply@saludintegral.test')
    monkeypatch.setattr(smtp_service.Config, 'PUBLIC_BASE_URL', 'http://localhost:5000')
    monkeypatch.setattr(smtp_service, '_crear_servidor_smtp', lambda: dummy)

    turno = {
        'id_turno': 14,
        'fecha_horario_inicial': '2026-11-08 09:30:00',
        'medico': {'nombre': 'Ana', 'apellido': 'Lopez', 'especialidad': 'Cardiología'},
        'consultorio': {'numero': 3, 'piso': 2},
    }
    paciente = {'id_paciente': 9, 'nombre': 'Juan', 'apellido': 'Pérez', 'correo_electronico': 'juan@test.com'}

    result = smtp_service.enviar_comprobante_turno(turno, paciente, b'fake-png-bytes', 'image/png')

    assert result['enviado'] is True
    assert len(dummy.sent) == 1

    html_part = None
    for part in dummy.sent[0].walk():
        if part.get_content_type() == 'text/html':
            html_part = part.get_payload(decode=True).decode('utf-8')
            break

    assert html_part is not None
    assert 'Comprobante de turno' in html_part
    assert 'Cancelar reserva' in html_part
    assert 'juan@test.com' in dummy.sent[0]['To']
