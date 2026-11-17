"""Turnos y agenda del médico autenticado.

Los datos salen del backend:

* `GET /turnos` devuelve los turnos del médico (el backend los filtra por
  el usuario del token).
* `GET /agendas` devuelve las agendas del médico con las jornadas de cada
  día de la semana.
* `PUT /turnos/<id>/estado` permite marcar un turno como atendido.
"""

from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from routes.agenda_mensual import (
    contexto_agenda_mensual,
    mes_seleccionado,
    rango_del_mes,
)
from routes.admin.dashboards._comun import color_avatar
from src.api import ErrorAPI, api
from src.permisos import requiere_rol
from src.tiempo import ahora_local, hoy_local

medico_routes = Blueprint('rutas_medico', __name__)

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Ventana para marcar un turno como atendido: desde una hora antes del
# horario del turno (el paciente puede llegar temprano) hasta doce horas
# después del turno (para poder cerrar la jornada).
VENTANA_ATENDIDO_HORAS_ANTES = 1
VENTANA_ATENDIDO_HORAS_DESPUES = 12

# Estados que se muestran en la lista de turnos del médico.
# Los horarios 'disponible' no se muestran: no son turnos de pacientes.
ESTADOS_VISIBLES = ('reservado', 'confirmado', 'atendido', 'cancelado', 'ausente')



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


def _estado_turno(turno):
    """Nombre del estado del turno (en minúsculas)."""
    estado = turno.get('estado') or {}
    if isinstance(estado, dict):
        estado = estado.get('nombre') or ''
    return str(estado).strip().lower()


def _mis_turnos():
    """Turnos del médico autenticado (sin los horarios disponibles)."""
    turnos = api('GET', '/turnos').get('turnos', [])

    return [
        turno for turno in turnos
        if _estado_turno(turno) in ESTADOS_VISIBLES
    ]


def _puede_marcar_atendido(momento, estado):
    """Un turno se puede marcar como atendido dentro de la ventana de la jornada.

    Sólo los turnos confirmados (con la llegada registrada por el check-in)
    se pueden marcar como atendidos.
    """
    if momento is None or estado != 'confirmado':
        return False

    ahora = ahora_local()
    inicio = momento - timedelta(hours=VENTANA_ATENDIDO_HORAS_ANTES)
    fin = momento + timedelta(hours=VENTANA_ATENDIDO_HORAS_DESPUES)

    return inicio <= ahora <= fin


def _mis_agendas():
    """Agendas del médico autenticado."""
    return api('GET', '/agendas').get('agendas', [])


def _normalizar_turno(turno, indice):
    """Adapta un turno de la API al formato de las tarjetas de la vista."""
    paciente = turno.get('paciente') or {}
    medico = turno.get('medico') or {}
    consultorio = turno.get('consultorio') or {}
    cobertura = turno.get('cobertura') or {}
    estado = _estado_turno(turno)

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
        'consultorio': consultorio.get('numero', '-'),
        'estado': estado.capitalize() if estado else '',
        'atendido': estado == 'atendido',
        'puede_marcar': _puede_marcar_atendido(momento, estado),
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

    # Coberturas disponibles para el filtro
    coberturas = sorted({
        turno['cobertura_filtro']
        for turno in turnos
        if turno['cobertura_filtro']
    })

    return render_template(
        'medico/mis_turnos.html',
        turnos=turnos,
        coberturas=coberturas,
        hoy=hoy_local().isoformat(),
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
