from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from src.api import ErrorAPI
from src.api_catalogos import obtener_especialidades
from src.api_estadisticas import sala_espera as sala_espera_api
from src.api_turnos import checkin
from src.errores import es_sesion_vencida, sesion_vencida
from src.normalizar import normalizar_turno
from src.permisos import requiere_rol, rol_actual as _rol_actual

sala_espera_routes = Blueprint('rutas_sala_espera', __name__)


def _listar_especialidades():
    """Devuelve las especialidades de la API para el filtro."""
    try:
        return obtener_especialidades()
    except ErrorAPI:
        return []


@sala_espera_routes.route('/sala-espera')
@requiere_rol("recepcion", "admin")
def sala_espera():
    """Sala de espera unificada para recepción y admin.

    - Recepción: ve el botón "Ingresar paciente" para hacer check-in por QR.
    - Admin: no ve el botón de ingreso, solo observa la sala.
    """
    rol_actual = _rol_actual()

    pacientes_en_espera = []
    error = None
    total = 0

    try:
        datos = sala_espera_api()
        pacientes_en_espera = [
            normalizar_turno(turno, indice, vista='sala')
            for indice, turno in enumerate(datos.get('sala_espera', []))
        ]
        total = int(datos.get('total') or len(pacientes_en_espera))
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
        'sala_espera/sala_espera.html',
        pacientes_en_espera=pacientes_en_espera,
        especialidades=especialidades,
        total=total,
        error=error,
        rol=rol_actual,
        ingreso_resultado=request.args.get('resultado'),
        ingreso_mensaje=request.args.get('mensaje'),
    )


@sala_espera_routes.route('/checkin', methods=['POST'])
@requiere_rol("recepcion")
def registrar_ingreso():
    """Registra el ingreso del paciente a partir del QR de su turno.

    Acepta JSON (fetch) o form data (submit tradicional). Redirige a la
    sala de espera con los parámetros de resultado para mostrar el cartel.
    """
    datos = request.get_json(silent=True) or request.form or {}
    token = str(datos.get('token') or '').strip()

    if not token:
        return redirect(
            url_for('rutas_sala_espera.sala_espera',
                    resultado='error',
                    mensaje='El código QR está vacío.')
        )

    try:
        checkin(token)
    except ErrorAPI as e:
        return redirect(
            url_for('rutas_sala_espera.sala_espera',
                    resultado='error',
                    mensaje=e.mensaje or 'No se pudo registrar el ingreso.')
        )

    return redirect(
        url_for('rutas_sala_espera.sala_espera',
                resultado='ok',
                mensaje='Ingreso registrado correctamente.')
    )
