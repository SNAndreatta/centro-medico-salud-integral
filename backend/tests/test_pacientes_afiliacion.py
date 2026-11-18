import unittest

from src.repositories.pacientes_repositories import generar_nro_afiliado
from src.validators.pacientes_validators import (
    validar_datos_actualizacion_paciente,
    validar_datos_registro_paciente,
)


DATOS_REGISTRO = {
    'nombre': 'Juan',
    'apellido': 'Perez',
    'dni': '12345678',
    'correo_electronico': 'juan@example.com',
    'fecha_nacimiento': '1990-05-15',
    'password': 'claveSegura123',
}


class TestNroAfiliadoAutomatico(unittest.TestCase):
    """El nro. de afiliado se genera solo: el cliente nunca lo manda."""

    def test_generar_nro_afiliado_es_estable_y_unico_por_paciente(self):
        self.assertEqual(generar_nro_afiliado(12), 'AFI-000012')
        self.assertEqual(generar_nro_afiliado(1), 'AFI-000001')
        self.assertNotEqual(generar_nro_afiliado(1), generar_nro_afiliado(2))

    def test_registro_acepta_cobertura_sin_nro_afiliado(self):
        datos = dict(DATOS_REGISTRO, id_cobertura=3)

        paciente, error, status = validar_datos_registro_paciente(datos)

        self.assertIsNone(error)
        self.assertEqual(status, None)
        self.assertEqual(paciente['id_cobertura'], 3)
        self.assertNotIn('nro_afiliado', paciente)

    def test_registro_rechaza_nro_afiliado_manual(self):
        datos = dict(DATOS_REGISTRO, id_cobertura=3, nro_afiliado='123456')

        paciente, error, status = validar_datos_registro_paciente(datos)

        self.assertIsNone(paciente)
        self.assertIsNotNone(error)
        self.assertEqual(status, 400)

    def test_actualizacion_acepta_solo_cobertura(self):
        actualizados, error = validar_datos_actualizacion_paciente({'id_cobertura': 5})

        self.assertIsNone(error)
        self.assertEqual(actualizados, {'id_cobertura': 5})
        self.assertNotIn('nro_afiliado', actualizados)

    def test_actualizacion_acepta_particular_sin_cobertura(self):
        actualizados, error = validar_datos_actualizacion_paciente({'id_cobertura': None})

        self.assertIsNone(error)
        self.assertEqual(actualizados, {'id_cobertura': None})

    def test_actualizacion_rechaza_nro_afiliado_manual(self):
        actualizados, error = validar_datos_actualizacion_paciente({'nro_afiliado': '123456'})

        self.assertIsNone(actualizados)
        self.assertIsNotNone(error)
        self.assertEqual(error['errors'][0]['code'], 'CUERPO_INVALIDO')

    def test_actualizacion_rechaza_cobertura_invalida(self):
        actualizados, error = validar_datos_actualizacion_paciente({'id_cobertura': -1})

        self.assertIsNone(actualizados)
        self.assertIsNotNone(error)
        self.assertEqual(error['errors'][0]['code'], 'COBERTURA_INVALIDA')


if __name__ == '__main__':
    unittest.main()
