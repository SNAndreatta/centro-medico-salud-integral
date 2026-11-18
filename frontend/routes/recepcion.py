from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from src.api import ErrorAPI
from src.api_catalogos import (
    obtener_especialidades, obtener_paciente, obtener_pacientes,
)
from src.api_estadisticas import sala_espera as sala_espera_api
from src.api_turnos import checkin, listar
from src.errores import es_sesion_vencida, sesion_vencida
from src.normalizar import normalizar_turno
from src.permisos import requiere_rol

recepcion_routes = Blueprint('rutas_recepcion', __name__)


def _listar_especialidades():
    """Devuelve las especialidades de la API para el filtro."""
    try:
        return obtener_especialidades()
    except ErrorAPI:
        return []


# ==========================================
# SALA DE ESPERA
# ==========================================

@recepcion_routes.route('/recepcion/sala-espera')
@requiere_rol("recepcion")
def sala_espera():
    pacientes_en_espera = []
    error = None

    try:
        datos = sala_espera_api()
        pacientes_en_espera = [
            normalizar_turno(turno, indice, vista='sala')
            for indice, turno in enumerate(datos.get('sala_espera', []))
        ]
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
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
        'recepcion/sala_espera.html',
        pacientes_en_espera=pacientes_en_espera,
        especialidades=especialidades,
        error=error
    )


# ==========================================
# INGRESO DE PACIENTE (CHECK-IN POR QR)
# ==========================================

@recepcion_routes.route('/recepcion/checkin', methods=['POST'])
@requiere_rol("recepcion")
def registrar_ingreso():
    """Registra el ingreso del paciente a partir del QR de su turno."""
    datos = request.get_json(silent=True) or {}
    token = str(datos.get('token') or '').strip()

    if not token:
        return jsonify({
            'ok': False,
            'mensaje': 'El código QR está vacío.',
        })

    try:
        checkin(token)
    except ErrorAPI as e:
        return jsonify({
            'ok': False,
            'mensaje': e.mensaje or 'No se pudo registrar el ingreso.',
        })

    return jsonify({
        'ok': True,
        'mensaje': 'Ingreso registrado correctamente.',
    })


# ==========================================
# PACIENTES
# ==========================================

@recepcion_routes.route("/recepcion/pacientes")
@requiere_rol("recepcion")
def ver_pacientes():
    pacientes = []
    error = None

    try:
        pacientes = obtener_pacientes()
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        error = e.mensaje

    return render_template(
        "recepcion/ver_pacientes.html",
        pacientes=pacientes,
        error=error,
    )


# ==========================================
# TURNOS
# ==========================================

@recepcion_routes.route("/recepcion/turnos")
@requiere_rol("recepcion")
def ver_turnos():
    turnos = []
    medicos = []
    especialidades = []
    error = None

    try:
        turnos_crudos = [
            turno for turno in listar()
            if (turno.get('estado') or {}).get('nombre', '').lower() != 'disponible'
        ]
        turnos = [
            normalizar_turno(turno, indice, vista='grilla')
            for indice, turno in enumerate(turnos_crudos)
        ]
        medicos = sorted({t['medico'] for t in turnos if t.get('medico')})
        especialidades = sorted({
            t['especialidad'] for t in turnos if t.get('especialidad')
        })
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        error = e.mensaje

    return render_template(
        "recepcion/ver_turnos.html",
        turnos=turnos,
        medicos=medicos,
        especialidades=especialidades,
        error=error,
    )


# ==========================================
# PERFIL DE PACIENTE
# ==========================================

@recepcion_routes.route("/recepcion/profile/<int:id_usuario>")
@requiere_rol("recepcion")
def perfil_usuario(id_usuario):
    try:
        paciente = obtener_paciente(id_usuario)
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_recepcion.ver_pacientes'))

    if not paciente:
        flash('Paciente no encontrado.', 'error')
        return redirect(url_for('rutas_recepcion.ver_pacientes'))

    usuario = {
        **paciente,
        'tipo_perfil': 'paciente',
    }

    return render_template(
        "recepcion/profile_paciente.html",
        usuario=usuario
    )
