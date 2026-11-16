from flask import Blueprint, render_template, request

from src.api import ErrorAPI, api

from ._comun import (
    color_avatar,
    filtros_fechas,
    iniciales,
    minutos_espera,
    nombre_completo,
)

tiempo_espera_admin_routes = Blueprint(
    'rutas_admin_tiempo_espera',
    __name__
)


def _calcular_tiempos(turnos):
    """Calcula el promedio de espera por médico y por especialidad."""
    medicos = {}
    especialidades = {}

    for turno in turnos:
        minutos = minutos_espera(
            turno.get('fecha_horario_inicial'),
            turno.get('fecha_horario_llegada'),
        )

        if minutos is None:
            continue

        medico = turno.get('medico') or {}
        id_medico = medico.get('id_medico')
        nombre_especialidad = medico.get('especialidad') or 'Sin especialidad'

        if id_medico not in medicos:
            medicos[id_medico] = {
                'id': id_medico,
                'nombre': nombre_completo(
                    medico.get('nombre'),
                    medico.get('apellido'),
                ),
                'iniciales': iniciales(
                    medico.get('nombre'),
                    medico.get('apellido'),
                ),
                'minutos': 0,
                'turnos': 0,
            }

        medicos[id_medico]['minutos'] += minutos
        medicos[id_medico]['turnos'] += 1

        if nombre_especialidad not in especialidades:
            especialidades[nombre_especialidad] = {
                'nombre': nombre_especialidad,
                'minutos': 0,
                'turnos': 0,
            }

        especialidades[nombre_especialidad]['minutos'] += minutos
        especialidades[nombre_especialidad]['turnos'] += 1

    lista_medicos = []
    lista_especialidades = []

    for indice, medico in enumerate(medicos.values()):
        promedio = round(medico['minutos'] / medico['turnos'])

        lista_medicos.append({
            'id': medico['id'],
            'nombre': medico['nombre'],
            'iniciales': medico['iniciales'],
            'espera': promedio,
            'turnos': medico['turnos'],
            'color_fondo': color_avatar(indice).split(' ')[0],
            'color_texto': color_avatar(indice).split(' ')[1],
        })

    lista_medicos.sort(key=lambda medico: (-medico['espera'], medico['nombre']))

    for especialidad in especialidades.values():
        promedio = round(especialidad['minutos'] / especialidad['turnos'])

        lista_especialidades.append({
            'nombre': especialidad['nombre'],
            'espera': promedio,
            'turnos': especialidad['turnos'],
        })

    lista_especialidades.sort(
        key=lambda especialidad: (-especialidad['espera'], especialidad['nombre'])
    )

    return lista_medicos, lista_especialidades


@tiempo_espera_admin_routes.route('/admin/tiempo-espera')
def tiempo_espera():

    parametros = filtros_fechas(request.args)

    error = None
    medicos = []
    especialidades = []
    turnos_considerados = 0

    try:
        datos = api(
            'GET',
            '/turnos',
            params=parametros,
        )

        turnos = datos.get('turnos', [])

        medicos, especialidades = _calcular_tiempos(turnos)
        turnos_considerados = sum(medico['turnos'] for medico in medicos)

    except ErrorAPI as e:
        error = e.mensaje

    return render_template(
        'admin/dashboards/tiempo_espera.html',
        medicos=medicos,
        especialidades=especialidades,
        turnos_considerados=turnos_considerados,
        fecha_desde=parametros.get('fecha_desde', ''),
        fecha_hasta=parametros.get('fecha_hasta', ''),
        error=error,
    )
