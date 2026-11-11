import unittest

from src.utils.qr_utils import (
    construir_payload_turno,
    decodificar_payload_qr,
    generar_qr_imagen,
    serializar_payload_qr,
)


class TestQrTurnos(unittest.TestCase):
    def test_payload_qr_incluye_datos_essenciales_del_turno(self):
        turno = {
            'id_turno': 42,
            'id_agenda': 7,
            'id_paciente': 12,
            'fecha_horario_inicial': '2026-11-04T09:30:00',
        }

        payload = construir_payload_turno(turno, estado='reservado')

        self.assertEqual(payload['id_turno'], 42)
        self.assertEqual(payload['id_agenda'], 7)
        self.assertEqual(payload['id_paciente'], 12)
        self.assertEqual(payload['estado'], 'reservado')
        self.assertIn('fecha_horario_inicial', payload)

        token = serializar_payload_qr(payload)
        self.assertEqual(decodificar_payload_qr(token)['id_turno'], 42)

    def test_generar_qr_imagen_png_y_svg(self):
        codigo_qr = serializar_payload_qr({'id_turno': 1, 'id_agenda': 2, 'estado': 'reservado'})

        png_bytes, mime_png = generar_qr_imagen(codigo_qr, formato='png')
        svg_bytes, mime_svg = generar_qr_imagen(codigo_qr, formato='svg')

        self.assertEqual(mime_png, 'image/png')
        self.assertTrue(png_bytes.startswith(b'\x89PNG'))
        self.assertEqual(mime_svg, 'image/svg+xml')
        self.assertTrue(b'<svg' in svg_bytes or svg_bytes.startswith(b'<?xml'))


if __name__ == '__main__':
    unittest.main()
