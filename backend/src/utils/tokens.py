from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from src.config import Config


def _serializer():
    return URLSafeTimedSerializer(Config.SECRET_KEY)


def generar_token_cancelacion_turno(id_turno, id_paciente):
    return _serializer().dumps({
        'id_turno': int(id_turno),
        'id_paciente': int(id_paciente),
        'tipo': 'cancelacion_turno',
    })


def validar_token_cancelacion_turno(token):
    if not token or not token.strip():
        raise ValueError('Se requiere un token de cancelación válido')

    try:
        payload = _serializer().loads(
            token,
            max_age=Config.CANCELACION_TTL_MINUTES * 60,
        )
    except (BadSignature, SignatureExpired) as exc:
        raise ValueError('El enlace de cancelación es inválido o expiró') from exc

    if payload.get('tipo') != 'cancelacion_turno':
        raise ValueError('El token no corresponde a una cancelación de turno')

    if int(payload.get('id_turno', -1)) <= 0 or int(payload.get('id_paciente', -1)) <= 0:
        raise ValueError('El token de cancelación es inválido')

    return payload


def generar_url_cancelacion_turno(id_turno, id_paciente):
    token = generar_token_cancelacion_turno(id_turno, id_paciente)
    base_url = Config.PUBLIC_BASE_URL.rstrip('/')
    return f'{base_url}/cancelar-turno/{id_turno}?token={token}'
