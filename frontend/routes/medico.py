"""Turnos y agenda del médico autenticado.

Los datos salen del backend a través de `src.api_turnos`:

* `GET /turnos` devuelve los turnos del médico (el backend los filtra por
  el usuario del token).
* `GET /agendas` devuelve las agendas del médico con las jornadas de cada
  día de la semana.
* `PUT /turnos/<id>/estado` permite marcar un turno como atendido.
"""

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for,
)

from routes.agenda_mensual import (
    contexto_agenda_mensual,
    mes_seleccionado,
    rango_del_mes,
)
from src.api import ErrorAPI
from src.api_turnos import listar, marcar_atendido, obtener_agendas
from src.errores import atender_error, es_sesion_vencida, sesion_vencida
from src.normalizar import estado_turno, nombre_completo, normalizar_turno
from src.permisos import requiere_rol
from src.tiempo import hoy_local

medico_routes = Blueprint('rutas_medico', __name__)

# Estados que se muestran en la lista de turnos del médico.
# Los horarios 'disponible' no se muestran: no son turnos de pacientes.
ESTADOS_VISIBLES = ('reservado', 'confirmado', 'atendido', 'cancelado', 'ausente')


def _mis_turnos():
    """Turnos del médico autenticado (sin los horarios disponibles)."""
    return [
        turno for turno in listar()
        if estado_turno(turno) in ESTADOS_VISIBLES
    ]


# ==========================================================
# MARCAR TURNO COMO ATENDIDO
# ==========================================================

@medico_routes.route('/turno/<int:id_turno>/atendido', methods=['POST'])
@requiere_rol("medico")
def marcar_turno_atendido(id_turno):
    try:
        marcar_atendido(id_turno)
        flash('El turno se marcó como atendido.', 'success')
    except ErrorAPI as e:
        respuesta = atender_error(
            e,
            redirect_a=url_for('rutas_medico.ver_turnos'),
        )
        if respuesta:
            return respuesta

    return redirect(url_for('rutas_medico.ver_turnos'))


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
            normalizar_turno(turno, indice, vista='medico_tabla')
            for indice, turno in enumerate(_mis_turnos())
        ]
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
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
        agendas = obtener_agendas()

        anio, mes = mes_seleccionado(request.args)
        fecha_desde, fecha_hasta = rango_del_mes(anio, mes)

        turnos = listar({
            'fecha_desde': fecha_desde.isoformat(),
            'fecha_hasta': fecha_hasta.isoformat(),
        })
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        error = e.mensaje

    datos_medico = (agendas[0].get('medico') or {}) if agendas else {}

    medico = {
        'id': agendas[0]['id_medico'] if agendas else None,
        'nombre_completo': nombre_completo(
            datos_medico.get('nombre') or session.get('nombre'),
            datos_medico.get('apellido') or session.get('apellido'),
        ) or 'Mi agenda',
    }

    consultorio = {'numero': '-'}
    if agendas:
        consultorio = agendas[0].get('consultorio') or {'numero': '-'}

    return render_template(
        'agenda/agenda.html',
        es_admin=False,
        medico=medico,
        error=error,
        **contexto_agenda_mensual(
            request.args,
            agendas=agendas,
            turnos=turnos,
            consultorio=consultorio,
        ),
    )
