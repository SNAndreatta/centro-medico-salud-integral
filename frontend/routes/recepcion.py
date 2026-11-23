from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from src.api import ErrorAPI
from src.api_catalogos import (
    obtener_especialidades, obtener_paciente, obtener_pacientes,
)
from src.api_turnos import checkin, listar
from src.errores import es_sesion_vencida, sesion_vencida
from src.normalizar import estado_turno, normalizar_turno
from src.permisos import requiere_rol

recepcion_routes = Blueprint('rutas_recepcion', __name__)


# ==========================================
# INGRESO DE PACIENTE (CHECK-IN POR QR)
# ==========================================

@recepcion_routes.route('/recepcion/checkin', methods=['POST'])
@requiere_rol("recepcion")
def registrar_ingreso():
    """Registra el ingreso del paciente a partir del formulario de check-in."""
    token = str(request.form.get('token') or '').strip()

    if not token:
        return redirect(url_for(
            'rutas_recepcion.sala_espera',
            resultado='error',
            mensaje='El código QR está vacío.',
        ))

    try:
        checkin(token)
    except ErrorAPI as e:
        return redirect(url_for(
            'rutas_recepcion.sala_espera',
            resultado='error',
            mensaje=e.mensaje or 'No se pudo registrar el ingreso.',
        ))

    return redirect(url_for(
        'rutas_recepcion.sala_espera',
        resultado='ok',
        mensaje='Ingreso registrado correctamente.',
    ))


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
            if estado_turno(turno) != 'disponible'
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
