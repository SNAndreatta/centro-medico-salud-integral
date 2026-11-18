import base64
import json
import uuid
from io import BytesIO

import qrcode
import qrcode.image.svg


def construir_payload_turno(turno, *, estado='reservado'):
    fecha_horario = (
        turno.get('fecha_horario_inicial')
        or turno.get('fecha_horario')
        or turno.get('fecha_horario_llegada')
    )
    payload = {
        'id_turno': int(turno['id_turno']),
        'id_agenda': int(turno['id_agenda']),
        'id_paciente': turno.get('id_paciente'),
        'estado': estado,
        'fecha_horario_inicial': fecha_horario,
        'token': uuid.uuid4().hex,
    }
    if payload['id_paciente'] is not None:
        payload['id_paciente'] = int(payload['id_paciente'])
    return payload


def serializar_payload_qr(payload):
    return base64.urlsafe_b64encode(
        json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
    ).decode('ascii')


def decodificar_payload_qr(token):
    if not token or not isinstance(token, str):
        raise ValueError('El token QR es obligatorio')
    try:
        datos = base64.urlsafe_b64decode(token.encode('ascii')).decode('utf-8')
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError('El token QR es inválido') from exc
    try:
        payload = json.loads(datos)
    except json.JSONDecodeError as exc:
        raise ValueError('El token QR no contiene un payload JSON válido') from exc
    return payload


def generar_qr_imagen(codigo_qr, formato='png'):
    if formato not in {'png', 'svg'}:
        raise ValueError('El formato del QR debe ser png o svg')

    if formato == 'svg':
        imagen = qrcode.make(codigo_qr, image_factory=qrcode.image.svg.SvgPathImage)
        buffer = BytesIO()
        imagen.save(buffer)
        svg_bytes = buffer.getvalue()
        return svg_bytes, 'image/svg+xml'

    imagen = qrcode.make(codigo_qr)
    buffer = BytesIO()
    imagen.save(buffer, format='PNG')
    return buffer.getvalue(), 'image/png'


def generar_qr_para_turno(turno, *, estado='reservado', formato='png'):
    payload = construir_payload_turno(turno, estado=estado)
    codigo_qr = serializar_payload_qr(payload)
    imagen_bytes, mime_type = generar_qr_imagen(codigo_qr, formato=formato)
    return {
        'codigo_qr': codigo_qr,
        'payload': payload,
        'mime_type': mime_type,
        'imagen_bytes': imagen_bytes,
    }
