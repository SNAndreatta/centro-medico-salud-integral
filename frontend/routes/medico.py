"""Turnos y agenda del médico autenticado.

Los datos salen del backend:

* `GET /turnos` devuelve los turnos del médico (el backend los filtra por
  el usuario del token).
* `GET /agendas` devuelve las agendas del médico con las jornadas de cada
  día de la semana.
* `PUT /turnos/<id>/estado` permite marcar un turno como atendido.
"""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from routes.agenda_mensual import (
    contexto_agenda_mensual,
    mes_seleccionado,
    rango_del_mes,
)
from routes.admin.dashboards._comun import color_avatar
from src.api import ErrorAPI, api
from src.permisos import requiere_rol

medico_routes = Blueprint('rutas_medico', __name__)

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def _a_datetime(valor):
    if not valor:
        return None

    try:
        return datetime.fromisoformat(str(valor))
    except ValueError:
        return None


def _nombre_completo(nombre, apellido=''):
    return f"{nombre or ''} {apellido or ''}".strip()


def _iniciales(nombre, apellido=''):
    letras = [
        parte[0]
        for parte in (nombre or '', apellido or '')
        if parte
    ]

    return ''.join(letras).upper() or 'NC'


def _mis_turnos():
    """Turnos del médico autenticado."""
    return api('GET', '/turnos').get('turnos', [])


def _mis_agendas():
    """Agendas del médico autenticado."""
    return api('GET', '/agendas').get('agendas', [])


def _normalizar_turno(turno, indice):
    """Adapta un turno de la API al formato de las tarjetas de la vista."""
    paciente = turno.get('paciente') or {}
    medico = turno.get('medico') or {}
    consultorio = turno.get('consultorio') or {}
    cobertura = turno.get('cobertura') or {}
    estado = (turno.get('estado') or {}).get('nombre') or ''

    momento = _a_datetime(turno.get('fecha_horario_inicial'))
    fecha = momento.date() if momento else None

    nombre = _nombre_completo(
        paciente.get('nombre'),
        paciente.get('apellido'),
    ) or 'Sin paciente'

    especialidad = medico.get('especialidad') or ''
    nombre_cobertura = cobertura.get('nombre') or 'Particular'

    return {
        'id': turno.get('id_turno'),
        'iniciales': _iniciales(
            paciente.get('nombre'),
            paciente.get('apellido'),
        ),
        'nombre_paciente': nombre,
        'nombre_completo': nombre,
        'cobertura': nombre_cobertura,
        'especialidad': especialidad,
        'hora': momento.strftime('%H:%M') if momento else '',
        'fecha': fecha.strftime('%d - %m - %Y') if fecha else '',
        'fecha_filtro': fecha.isoformat() if fecha else '',
        'cobertura_filtro': nombre_cobertura,
        'especialidad_filtro': especialidad,
        'consultorio': consultorio.get('numero', '-'),
        'estado': estado.capitalize() if estado else '',
        'atendido': estado.lower() == 'atendido',
        'color': color_avatar(indice),
    }


# ==========================================================
# MARCAR TURNO COMO ATENDIDO
# ==========================================================

@medico_routes.route('/turno/<int:id_turno>/atendido', methods=['POST'])
@requiere_rol("medico")
def marcar_turno_atendido(id_turno):

    try:
        api('PUT', f'/turnos/{id_turno}/estado', json={'estado': 'atendido'})
        flash('El turno se marcó como atendido.', 'success')

    except ErrorAPI as e:
        flash(e.mensaje, 'error')

    return redirect(
        request.referrer or url_for('rutas_medico.ver_turnos')
    )


# ==========================================================
# VER TURNOS
# ==========================================================

@medico_routes.route('/turnos', methods=['GET'])
@requiere_rol("medico")
def ver_turnos():

    turnos = []
    error = None

    try:
        turnos = [
            _normalizar_turno(turno, indice)
            for indice, turno in enumerate(_mis_turnos())
        ]
    except ErrorAPI as e:
        error = e.mensaje

    # Especialidades disponibles para el filtro
    especialidades = sorted({
        turno['especialidad_filtro']
        for turno in turnos
        if turno['especialidad_filtro']
    })

    # Coberturas disponibles para el filtro
    coberturas = sorted({
        turno['cobertura_filtro']
        for turno in turnos
        if turno['cobertura_filtro']
    })

    return render_template(
        'medico/mis_turnos.html',
        turnos=turnos,
        especialidades=especialidades,
        coberturas=coberturas,
        error=error
    )


# ==========================================================
# AGENDA
# ==========================================================

@medico_routes.route('/agenda', methods=['GET'])
@requiere_rol("medico")
def agenda():

    agendas = []
    turnos = []
    error = None

    try:
        agendas = _mis_agendas()

        anio, mes = mes_seleccionado(request.args)
        fecha_desde, fecha_hasta = rango_del_mes(anio, mes)

        turnos = api(
            'GET',
            '/turnos',
            params={
                'fecha_desde': fecha_desde.isoformat(),
                'fecha_hasta': fecha_hasta.isoformat(),
            },
        ).get('turnos', [])

    except ErrorAPI as e:
        error = e.mensaje

    datos_medico = (agendas[0].get('medico') or {}) if agendas else {}

    medico = {
        'id': agendas[0]['id_medico'] if agendas else None,
        'nombre_completo': _nombre_completo(
            datos_medico.get('nombre') or session.get('nombre'),
            datos_medico.get('apellido') or session.get('apellido'),
        ) or 'Mi agenda',
    }

    consultorio = {'numero': '-'}
    if agendas:
        consultorio = agendas[0].get('consultorio') or {'numero': '-'}

    return render_template(
        'medico/agenda.html',
        medico=medico,
        error=error,
        **contexto_agenda_mensual(
            request.args,
            agendas=agendas,
            turnos=turnos,
            consultorio=consultorio,
        ),
    )
