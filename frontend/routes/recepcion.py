from datetime import date, datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from src.api import ErrorAPI, api
from src.permisos import requiere_rol
from routes.admin.dashboards._comun import (
    color_avatar,
    formatear_hora,
    iniciales,
    nombre_completo,
)

recepcion_routes = Blueprint('rutas_recepcion', __name__)


def _formatear_fecha(valor):
    if not valor:
        return '-'
    texto = str(valor)
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(texto[:19], fmt).strftime('%d/%m/%Y')
        except ValueError:
            continue
    try:
        return date.fromisoformat(texto[:10]).strftime('%d/%m/%Y')
    except ValueError:
        return texto


def _listar_especialidades():
    """Devuelve las especialidades de la API para el filtro."""
    try:
        datos = api('GET', '/especialidades')
    except ErrorAPI:
        return []

    return [
        {
            'id': especialidad.get('id_especialidad'),
            'nombre': especialidad.get('nombre_especialidad'),
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


# ==========================================
# SALA DE ESPERA
# ==========================================

@recepcion_routes.route('/recepcion/sala-espera')
@requiere_rol("recepcion")
def sala_espera():

    pacientes_en_espera = []
    error = None

    try:
        datos = api('GET', '/estadisticas/sala_espera')

        pacientes_en_espera = [
            _normalizar_turno(turno, indice)
            for indice, turno in enumerate(datos.get('sala_espera', []))
        ]

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
        api('POST', '/turnos/checkin', json={'token': token})

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
        datos = api('GET', '/pacientes')
        for indice, paciente in enumerate(datos.get('pacientes', [])):
            pacientes.append({
                'id': paciente.get('id_paciente'),
                'nombre': paciente.get('nombre') or '',
                'apellido': paciente.get('apellido') or '',
                'cobertura': paciente.get('cobertura') or paciente.get('nombre_cobertura') or 'Particular',
                'iniciales': iniciales(paciente.get('nombre'), paciente.get('apellido')),
                'color_fondo': color_avatar(indice),
            })
    except ErrorAPI as e:
        error = e.mensaje

    return render_template(
        "recepcion/ver_pacientes.html",
        pacientes=pacientes,
        error=error,
    )





# ==========================================
# TURNOS
# ==========================================

def _normalizar_turno_grilla(turno, indice):
    paciente = turno.get('paciente') or {}
    medico = turno.get('medico') or {}
    consultorio = turno.get('consultorio') or {}
    estado = turno.get('estado') or {}

    nombre_paciente = nombre_completo(paciente.get('nombre'), paciente.get('apellido'))
    nombre_medico = nombre_completo(medico.get('nombre'), medico.get('apellido'))
    especialidad = medico.get('especialidad') or ''

    fecha_iso = ''
    fecha = '-'
    valor_fecha = turno.get('fecha_horario_inicial')
    if valor_fecha:
        texto = str(valor_fecha)
        fecha_iso = texto[:10]
        try:
            fecha = datetime.strptime(texto[:19], '%Y-%m-%d %H:%M:%S').strftime('%d - %m - %Y')
        except ValueError:
            fecha = _formatear_fecha(texto)

    return {
        'id': turno.get('id_turno'),
        'paciente': nombre_paciente or 'Sin paciente',
        'iniciales': iniciales(paciente.get('nombre'), paciente.get('apellido')) if paciente else 'SP',
        'cobertura': '-',
        'hora': formatear_hora(turno.get('fecha_horario_inicial')),
        'fecha': fecha,
        'fecha_filtro': fecha_iso,
        'consultorio': consultorio.get('numero') or '-',
        'medico': nombre_medico,
        'especialidad': especialidad or nombre_medico or '-',
        'estado': estado.get('nombre') or '',
        'color_fondo': color_avatar(indice),
    }


@recepcion_routes.route("/recepcion/turnos")
@requiere_rol("recepcion")
def ver_turnos():
    turnos = []
    medicos = []
    especialidades = []
    error = None

    try:
        datos = api('GET', '/turnos')
        turnos_crudos = [
            turno for turno in datos.get('turnos', [])
            if (turno.get('estado') or {}).get('nombre', '').lower() != 'disponible'
        ]
        turnos = [
            _normalizar_turno_grilla(turno, indice)
            for indice, turno in enumerate(turnos_crudos)
        ]
        medicos = sorted({t['medico'] for t in turnos if t.get('medico')})
        especialidades = sorted({t['especialidad'] for t in turnos if t.get('especialidad')})
    except ErrorAPI as e:
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
        datos = api('GET', f'/pacientes/{id_usuario}')
    except ErrorAPI as e:
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_recepcion.ver_pacientes'))

    paciente = datos.get('paciente')
    if not paciente:
        flash('Paciente no encontrado.', 'error')
        return redirect(url_for('rutas_recepcion.ver_pacientes'))

    usuario = {
        'id': paciente.get('id_paciente'),
        'nombre': paciente.get('nombre') or '',
        'apellido': paciente.get('apellido') or '',
        'iniciales': iniciales(paciente.get('nombre'), paciente.get('apellido')),
        'email': paciente.get('correo_electronico') or '-',
        'documento': paciente.get('dni') or '-',
        'fecha_nacimiento': _formatear_fecha(paciente.get('fecha_nacimiento')),
        'fecha_registro': _formatear_fecha(paciente.get('fecha_creacion')),
        'cobertura': paciente.get('nombre_cobertura') or paciente.get('cobertura') or 'Particular',
        'nro_afiliado': paciente.get('nro_afiliado') or '-',
        'tipo_perfil': 'paciente',
    }

    return render_template(
        "recepcion/profile_paciente.html",
        usuario=usuario
    )