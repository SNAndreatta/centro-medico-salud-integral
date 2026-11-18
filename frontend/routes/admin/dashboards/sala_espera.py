from flask import Blueprint, render_template

from src.api import ErrorAPI, api
from src.permisos import requiere_rol

from ._comun import (
    color_avatar,
    formatear_hora,
    iniciales,
    nombre_completo,
)

sala_espera_admin_routes = Blueprint(
    'rutas_admin_sala_espera',
    __name__
)


def _listar_especialidades():
    """Devuelve las especialidades de la API para el filtro."""
    try:
        datos = api('GET', '/especialidades')
    except ErrorAPI:
        return []

    return [
        {
            'id': int(especialidad['id_especialidad']),
            'nombre': especialidad['nombre_especialidad'],
        }
        for especialidad in datos.get('especialidades', [])
    ]


def _normalizar_turno(turno, indice):
    """Adapta un turno de la API al formato de la tarjeta de la sala."""
    paciente = turno.get('paciente') or {}
    medico = turno.get('medico') or {}

    especialidad = medico.get('especialidad') or ''

    return {
        'id_turno': turno.get('id_turno'),
        'iniciales': iniciales(
            paciente.get('nombre'),
            paciente.get('apellido'),
        ),
        'nombre_completo': nombre_completo(
            paciente.get('nombre'),
            paciente.get('apellido'),
        ),
        'dni': paciente.get('dni') or '',
        'hora_turno': formatear_hora(turno.get('fecha_horario_inicial')),
        'hora_llegada': formatear_hora(turno.get('fecha_horario_llegada')),
        'modalidad': especialidad[:3].upper(),
        'especialidad': especialidad,
        'medico': nombre_completo(
            medico.get('nombre'),
            medico.get('apellido'),
        ),
        'consultorio': turno.get('numero_consultorio'),
        'color_avatar': color_avatar(indice),
    }


@sala_espera_admin_routes.route('/admin/sala-espera')
@requiere_rol("admin")
def sala_espera():

    pacientes_en_espera = []
    error = None
    total = 0

    try:
        datos = api('GET', '/estadisticas/sala_espera')

        pacientes_en_espera = [
            _normalizar_turno(turno, indice)
            for indice, turno in enumerate(datos.get('sala_espera', []))
        ]

        total = int(datos.get('total') or len(pacientes_en_espera))

    except ErrorAPI as e:
        error = e.mensaje

    especialidades = _listar_especialidades()

    if not especialidades:
        especialidades = [
            {'id': None, 'nombre': especialidad}
            for especialidad in sorted({
                paciente['especialidad']
                for paciente in pacientes_en_espera
                if paciente['especialidad']
            })
        ]

    return render_template(
        'admin/dashboards/sala_espera.html',
        pacientes_en_espera=pacientes_en_espera,
        especialidades=especialidades,
        total=total,
        error=error,
    )
