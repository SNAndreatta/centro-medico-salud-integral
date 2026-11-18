from flask import Blueprint, render_template, request

from src import api_estadisticas
from src.api import ErrorAPI
from src.api_turnos import listar as listar_turnos
from src.normalizar import normalizar_turno
from src.permisos import requiere_rol

from ._comun import filtros_fechas

turnos_especialidad_admin_routes = Blueprint(
    'rutas_admin_turnos_especialidad',
    __name__
)


def _agrupar_turnos(turnos):
    """Agrupa los turnos de la API por especialidad."""
    especialidades = {}

    for turno in turnos:
        medico = turno.get('medico') or {}
        nombre_especialidad = medico.get('especialidad') or 'Sin especialidad'

        if nombre_especialidad not in especialidades:
            especialidades[nombre_especialidad] = {
                'nombre': nombre_especialidad,
                'total_turnos': 0,
                'turnos': [],
            }

        especialidad = especialidades[nombre_especialidad]
        especialidad['total_turnos'] += 1
        especialidad['turnos'].append(normalizar_turno(turno, vista='dashboard'))

    return list(especialidades.values())


def _especialidad_desde_api(especialidad):
    return {
        'nombre': especialidad.get('nombre') or 'Sin especialidad',
        'total_turnos': int(especialidad.get('total_turnos') or 0),
        'turnos': [
            normalizar_turno(turno, vista='dashboard')
            for turno in especialidad.get('turnos', [])
        ],
    }


@turnos_especialidad_admin_routes.route("/admin/turnos-especialidad")
@requiere_rol("admin")
def turnos_especialidad():

    parametros = filtros_fechas(request.args)

    error = None
    especialidades = []
    total_turnos = 0

    try:
        datos = api_estadisticas.turnos_por_especialidad(parametros)

        especialidades = [
            _especialidad_desde_api(especialidad)
            for especialidad in datos.get('especialidades', [])
        ]
        total_turnos = int(datos.get('total_turnos') or 0)

    except ErrorAPI as e:
        error = e.mensaje

        try:
            turnos = listar_turnos(parametros)
            especialidades = _agrupar_turnos(turnos)
            total_turnos = sum(
                especialidad['total_turnos']
                for especialidad in especialidades
            )
        except ErrorAPI:
            pass

    return render_template(
        "admin/dashboards/turnos_especialidad.html",
        especialidades=especialidades,
        total_turnos=total_turnos,
        fecha_desde=parametros.get('fecha_desde', ''),
        fecha_hasta=parametros.get('fecha_hasta', ''),
        error=error,
    )
