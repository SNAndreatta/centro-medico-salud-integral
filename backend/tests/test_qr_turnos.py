from src.utils.qr_utils import (
    construir_payload_turno,
    decodificar_payload_qr,
    generar_qr_imagen,
    serializar_payload_qr,
)


def test_payload_qr_incluye_datos_essenciales_del_turno():
    turno = {
        'id_turno': 42,
        'id_agenda': 7,
        'id_paciente': 12,
        'fecha_horario_inicial': '2026-11-04T09:30:00',
    }

    payload = construir_payload_turno(turno, estado='reservado')

    assert payload['id_turno'] == 42
    assert payload['id_agenda'] == 7
    assert payload['id_paciente'] == 12
    assert payload['estado'] == 'reservado'
    assert 'fecha_horario_inicial' in payload

    token = serializar_payload_qr(payload)
    assert decodificar_payload_qr(token)['id_turno'] == 42


def test_generar_qr_imagen_png_y_svg():
    codigo_qr = serializar_payload_qr({'id_turno': 1, 'id_agenda': 2, 'estado': 'reservado'})

    png_bytes, mime_png = generar_qr_imagen(codigo_qr, formato='png')
    svg_bytes, mime_svg = generar_qr_imagen(codigo_qr, formato='svg')

    assert mime_png == 'image/png'
    assert png_bytes.startswith(b'\x89PNG')
    assert mime_svg == 'image/svg+xml'
    assert b'<svg' in svg_bytes or svg_bytes.startswith(b'<?xml')
