from flask import Blueprint, render_template, request

from src.api import ErrorAPI, api
from src.permisos import requiere_rol

from ._comun import (
    filtros_fechas,
    formatear_fecha,
    formatear_hora,
    iniciales,
    nombre_completo,
)

turnos_especialidad_admin_routes = Blueprint(
    'rutas_admin_turnos_especialidad',
    __name__
)


def _normalizar_turno(turno):
    medico = turno.get('medico') or {}
    paciente = turno.get('paciente') or {}
    consultorio = turno.get('consultorio') or {}
    estado = turno.get('estado') or {}

    return {
        'id_turno': turno.get('id_turno'),
        'iniciales': iniciales(
            medico.get('nombre'),
            medico.get('apellido'),
        ),
        'nombre': nombre_completo(
            medico.get('nombre'),
            medico.get('apellido'),
        ),
        'paciente': nombre_completo(
            paciente.get('nombre'),
            paciente.get('apellido'),
        ),
        'hora': formatear_hora(turno.get('fecha_horario_inicial')),
        'fecha': formatear_fecha(turno.get('fecha_horario_inicial')),
        'consultorio': consultorio.get('numero'),
        'estado': estado.get('nombre') or '',
    }


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
        especialidad['turnos'].append(_normalizar_turno(turno))

    return list(especialidades.values())


@turnos_especialidad_admin_routes.route("/admin/turnos-especialidad")
@requiere_rol("admin")
def turnos_especialidad():

    parametros = filtros_fechas(request.args)

    error = None
    especialidades = []
    total_turnos = 0

    try:
        datos = api(
            "GET",
            "/turnos",
            params=parametros,
        )

        especialidades = _agrupar_turnos(datos.get('turnos', []))
        total_turnos = sum(
            especialidad['total_turnos']
            for especialidad in especialidades
        )

    except ErrorAPI as e:
        error = e.mensaje

    return render_template(
        "admin/dashboards/turnos_especialidad.html",
        especialidades=especialidades,
        total_turnos=total_turnos,
        fecha_desde=parametros.get('fecha_desde', ''),
        fecha_hasta=parametros.get('fecha_hasta', ''),
        error=error,
    )
