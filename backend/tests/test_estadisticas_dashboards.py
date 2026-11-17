import unittest
from unittest.mock import patch

from src.services import estadisticas_services as servicios


class TestEstadisticasDashboards(unittest.TestCase):

    def test_ausentismo_resumen_porcentajes_y_orden(self):
        estados = [
            {'estado': 'atendido', 'cantidad': 8},
            {'estado': 'ausente', 'cantidad': 2},
            {'estado': 'cancelado', 'cantidad': 1},
        ]
        medicos = [
            {'id_medico': 1, 'nombre': 'Ana', 'apellido': 'Martinez',
             'ausentes': 1, 'considerados': 10},
            {'id_medico': 2, 'nombre': 'Luis', 'apellido': 'Perez',
             'ausentes': 2, 'considerados': 4},
        ]
        especialidades = [
            {'id_especialidad': 1, 'nombre': 'Cardiologia',
             'ausentes': 1, 'considerados': 10},
        ]

        with patch.object(servicios, 'obtener_turnos_por_estado', return_value=estados), \
             patch.object(servicios, 'obtener_ausentismo_medicos', return_value=medicos), \
             patch.object(servicios, 'obtener_ausentismo_especialidades', return_value=especialidades):
            respuesta, estado = servicios.obtener_estadisticas_ausentismo({
                'fecha_desde': '2026-11-01',
                'fecha_hasta': '2026-11-30',
            })

        self.assertEqual(estado, 200)
        self.assertEqual(respuesta['resumen'], {
            'total': 11, 'atendidos': 8, 'ausentes': 2, 'cancelados': 1,
        })
        self.assertEqual([m['id_medico'] for m in respuesta['medicos']], [2, 1])
        self.assertEqual(respuesta['medicos'][0]['porcentaje'], 50.0)
        self.assertEqual(respuesta['especialidades'][0]['porcentaje'], 10.0)
        self.assertEqual(respuesta['fecha_desde'], '2026-11-01')

    def test_tiempo_espera_promedia_y_ordena(self):
        medicos = [
            {'id_medico': 1, 'nombre': 'Ana', 'apellido': 'Martinez',
             'minutos_totales': 25, 'turnos': 2},
            {'id_medico': 2, 'nombre': 'Luis', 'apellido': 'Perez',
             'minutos_totales': 40, 'turnos': 3},
        ]
        especialidades = [
            {'id_especialidad': 1, 'nombre': 'Cardiologia',
             'minutos_totales': 40, 'turnos': 3},
        ]

        with patch.object(servicios, 'obtener_tiempos_espera_medicos', return_value=medicos), \
             patch.object(servicios, 'obtener_tiempos_espera_especialidades', return_value=especialidades):
            respuesta, estado = servicios.obtener_estadisticas_tiempo_espera({})

        self.assertEqual(estado, 200)
        self.assertEqual(respuesta['turnos_considerados'], 5)
        self.assertEqual([m['id_medico'] for m in respuesta['medicos']], [2, 1])
        self.assertEqual(respuesta['medicos'][0]['espera'], 13)
        self.assertEqual(respuesta['medicos'][1]['espera'], 12)
        self.assertEqual(respuesta['especialidades'][0]['espera'], 13)

    def test_turnos_por_especialidad_agrupa(self):
        turnos = [
            {'id_turno': 1, 'medico': {'id_especialidad': 1, 'especialidad': 'Cardiologia'}},
            {'id_turno': 2, 'medico': {'id_especialidad': 2, 'especialidad': 'Pediatria'}},
            {'id_turno': 3, 'medico': {'id_especialidad': 1, 'especialidad': 'Cardiologia'}},
        ]

        with patch.object(servicios, 'buscar_turnos', return_value=turnos) as buscar:
            respuesta, estado = servicios.obtener_estadisticas_turnos_especialidad({
                'fecha_desde': '2026-11-01',
            })

        self.assertEqual(estado, 200)
        self.assertEqual(respuesta['total_turnos'], 3)
        self.assertEqual(
            [(g['nombre'], g['total_turnos']) for g in respuesta['especialidades']],
            [('Cardiologia', 2), ('Pediatria', 1)],
        )
        self.assertEqual(
            [t['id_turno'] for t in respuesta['especialidades'][0]['turnos']],
            [1, 3],
        )
        buscar.assert_called_once_with(fecha_desde='2026-11-01', fecha_hasta=None)

    def test_rango_de_fechas_invalido(self):
        for funcion in (
            servicios.obtener_estadisticas_ausentismo,
            servicios.obtener_estadisticas_tiempo_espera,
            servicios.obtener_estadisticas_turnos_especialidad,
        ):
            respuesta, estado = funcion({
                'fecha_desde': '2026-12-01',
                'fecha_hasta': '2026-11-01',
            })
            self.assertEqual(estado, 400)
            self.assertEqual(respuesta['errors'][0]['code'], 'RANGO_FECHAS_INVALIDO')


if __name__ == '__main__':
    unittest.main()
