from flask import Blueprint, render_template, request

from src import api_estadisticas
from src.api import ErrorAPI
from src.api_turnos import listar as listar_turnos
from src.permisos import requiere_rol

from ._comun import (
    color_avatar,
    filtros_fechas,
    iniciales,
    nombre_completo,
    porcentaje_texto,
)

ausentismo_admin_routes = Blueprint(
    'rutas_admin_ausentismo',
    __name__
)

# Estados que se consideran para el cálculo del ausentismo.
ESTADOS_CONSIDERADOS = ('atendido', 'ausente')


def _calcular_ausentismo(turnos):
    """Calcula los porcentajes de ausentismo por médico y especialidad."""
    medicos = {}
    especialidades = {}

    for turno in turnos:
        estado = ((turno.get('estado') or {}).get('nombre') or '').lower()

        if estado not in ESTADOS_CONSIDERADOS:
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
                'ausentes': 0,
                'considerados': 0,
            }

        medicos[id_medico]['considerados'] += 1

        if estado == 'ausente':
            medicos[id_medico]['ausentes'] += 1

        if nombre_especialidad not in especialidades:
            especialidades[nombre_especialidad] = {
                'nombre': nombre_especialidad,
                'ausentes': 0,
                'considerados': 0,
            }

        especialidades[nombre_especialidad]['considerados'] += 1

        if estado == 'ausente':
            especialidades[nombre_especialidad]['ausentes'] += 1

    lista_medicos = []
    lista_especialidades = []

    for indice, medico in enumerate(medicos.values()):
        considerados = medico['considerados']

        if not considerados:
            continue

        porcentaje = round(medico['ausentes'] * 100 / considerados, 1)

        lista_medicos.append({
            'id': medico['id'],
            'nombre': medico['nombre'],
            'iniciales': medico['iniciales'],
            'ausentes': medico['ausentes'],
            'considerados': considerados,
            'porcentaje': porcentaje,
            'porcentaje_texto': porcentaje_texto(porcentaje),
            'color': color_avatar(indice),
        })

    lista_medicos.sort(key=lambda medico: (-medico['porcentaje'], medico['nombre']))

    for especialidad in especialidades.values():
        considerados = especialidad['considerados']

        if not considerados:
            continue

        porcentaje = round(especialidad['ausentes'] * 100 / considerados, 1)

        lista_especialidades.append({
            'nombre': especialidad['nombre'],
            'ausentes': especialidad['ausentes'],
            'considerados': considerados,
            'porcentaje': porcentaje,
            'porcentaje_texto': porcentaje_texto(porcentaje),
        })

    lista_especialidades.sort(
        key=lambda especialidad: (-especialidad['porcentaje'], especialidad['nombre'])
    )

    return lista_medicos, lista_especialidades


def _resumen(turnos):
    """Resumen de los turnos del período."""
    resumen = {
        'total': len(turnos),
        'atendidos': 0,
        'ausentes': 0,
        'cancelados': 0,
    }

    for turno in turnos:
        estado = ((turno.get('estado') or {}).get('nombre') or '').lower()

        if estado == 'atendido':
            resumen['atendidos'] += 1
        elif estado == 'ausente':
            resumen['ausentes'] += 1
        elif estado == 'cancelado':
            resumen['cancelados'] += 1

    return resumen


def _medico_desde_api(medico, indice):
    porcentaje = float(medico.get('porcentaje') or 0)

    return {
        'id': medico.get('id_medico'),
        'nombre': nombre_completo(medico.get('nombre'), medico.get('apellido')),
        'iniciales': iniciales(medico.get('nombre'), medico.get('apellido')),
        'ausentes': int(medico.get('ausentes') or 0),
        'considerados': int(medico.get('considerados') or 0),
        'porcentaje': porcentaje,
        'porcentaje_texto': porcentaje_texto(porcentaje),
        'color': color_avatar(indice),
    }


def _especialidad_desde_api(especialidad):
    porcentaje = float(especialidad.get('porcentaje') or 0)

    return {
        'nombre': especialidad.get('nombre') or 'Sin especialidad',
        'ausentes': int(especialidad.get('ausentes') or 0),
        'considerados': int(especialidad.get('considerados') or 0),
        'porcentaje': porcentaje,
        'porcentaje_texto': porcentaje_texto(porcentaje),
    }


@ausentismo_admin_routes.route("/admin/ausentismo")
@requiere_rol("admin")
def ausentismo():

    parametros = filtros_fechas(request.args)

    error = None
    medicos = []
    especialidades = []
    resumen = {'total': 0, 'atendidos': 0, 'ausentes': 0, 'cancelados': 0}

    try:
        datos = api_estadisticas.ausentismo(parametros)
        resumen_api = datos.get('resumen') or {}

        resumen = {
            'total': int(resumen_api.get('total') or 0),
            'atendidos': int(resumen_api.get('atendidos') or 0),
            'ausentes': int(resumen_api.get('ausentes') or 0),
            'cancelados': int(resumen_api.get('cancelados') or 0),
        }
        medicos = [
            _medico_desde_api(medico, indice)
            for indice, medico in enumerate(datos.get('medicos', []))
        ]
        especialidades = [
            _especialidad_desde_api(especialidad)
            for especialidad in datos.get('especialidades', [])
        ]

    except ErrorAPI as e:
        error = e.mensaje

        try:
            turnos = listar_turnos(parametros)
            medicos, especialidades = _calcular_ausentismo(turnos)
            resumen = _resumen(turnos)
        except ErrorAPI:
            pass

    return render_template(
        "admin/dashboards/ausentismo.html",
        medicos=medicos,
        especialidades=especialidades,
        resumen=resumen,
        fecha_desde=parametros.get('fecha_desde', ''),
        fecha_hasta=parametros.get('fecha_hasta', ''),
        error=error,
    )
