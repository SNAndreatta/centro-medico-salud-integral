"""ABM de médicos del administrador.

Los datos salen del backend:

* `GET /medicos/<id>`: datos del médico.
* `GET /usuarios`: datos del usuario asociado (fechas, documento, etc.).
* `GET /turnos?id_medico=...`: turnos del médico.
* `GET /agendas?id_medico=...`: agendas del médico.
* `POST /agendas`: creación de una agenda nueva.
* `PUT /medicos/<id>`: edición de especialidad y matrícula.
* `DELETE /medicos/<id>`: baja del médico.
"""

from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from routes.agenda_mensual import (
    contexto_agenda_mensual,
    mes_seleccionado,
    rango_del_mes,
)
from src.api import ErrorAPI, api
from src.permisos import requiere_rol

medico_admin_routes = Blueprint('rutas_admin_medico', __name__)

# Días de la semana en el formato ISO que usa el backend (1 = lunes).
DIAS_SEMANA = [
    'Lunes',
    'Martes',
    'Miércoles',
    'Jueves',
    'Viernes',
    'Sábado',
    'Domingo',
]

# Color del avatar según el estado del turno.
COLORES_ESTADO = {
    'disponible': 'bg-gray-200 text-gray-600',
    'reservado': 'bg-pink-500/30 text-pink-500',
    'confirmado': 'bg-lime-500/30 text-lime-500',
    'atendido': 'bg-purple-500/30 text-purple-500',
    'cancelado': 'bg-emerald-500/30 text-emerald-500',
    'ausente': 'bg-orange-500/30 text-orange-500',
}


def _a_datetime(valor):
    if not valor:
        return None

    try:
        return datetime.fromisoformat(str(valor))
    except ValueError:
        return None


def _a_date(valor):
    if not valor:
        return None

    try:
        return date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


def _fecha(valor):
    """Fecha en formato DD/MM/AAAA."""
    momento = _a_date(valor)

    return momento.strftime('%d/%m/%Y') if momento else '-'


def _fecha_iso(valor):
    """Fecha en formato AAAA-MM-DD para los inputs type="date"."""
    momento = _a_date(valor)

    return momento.isoformat() if momento else ''


def _iniciales(nombre, apellido=''):
    letras = [
        parte[0]
        for parte in (nombre or '', apellido or '')
        if parte
    ]

    return ''.join(letras).upper() or 'NC'


def _nombre_completo(nombre, apellido=''):
    return f"{nombre or ''} {apellido or ''}".strip()


def _obtener_medico(id_medico):
    """Datos del médico (GET /medicos/<id>)."""
    return api('GET', f'/medicos/{id_medico}').get('medico')


def _buscar_usuario(id_medico):
    """Usuario asociado al médico (GET /usuarios)."""
    usuarios = api('GET', '/usuarios').get('usuarios', [])

    return next(
        (
            usuario for usuario in usuarios
            if int(usuario.get('id_medico') or 0) == int(id_medico)
        ),
        None,
    )


def _catalogos():
    """Catálogos de especialidades y coberturas."""
    especialidades = []
    coberturas = []

    try:
        especialidades = [
            {
                'id': e['id_especialidad'],
                'nombre': e['nombre_especialidad'],
            }
            for e in api('GET', '/especialidades').get('especialidades', [])
        ]
    except ErrorAPI:
        pass

    try:
        coberturas = [
            {'id': c['id_cobertura'], 'nombre': c['nombre']}
            for c in api('GET', '/coberturas').get('coberturas', [])
        ]
    except ErrorAPI:
        pass

    return especialidades, coberturas


def _coberturas_medico(id_medico):
    """Coberturas ya asociadas al médico."""
    try:
        datos = api('GET', f'/medicos/{id_medico}/coberturas')
    except ErrorAPI:
        return []

    return [
        {'id': c['id_cobertura'], 'nombre': c['nombre']}
        for c in datos.get('coberturas', [])
    ]


def _consultorios():
    """Consultorios disponibles para las agendas."""
    try:
        datos = api('GET', '/consultorios')
    except ErrorAPI:
        return []

    return [
        {
            'id': c.get('id_consultorio', c.get('id')),
            'numero': c.get('numero', c.get('numero_consultorio')),
        }
        for c in datos.get('consultorios', [])
    ]


def _medico_vista(medico, usuario=None):
    """Datos del médico en el formato que usan las plantillas."""
    usuario = usuario or {}

    nombre = medico.get('nombre') or usuario.get('nombre') or ''
    apellido = medico.get('apellido') or usuario.get('apellido') or ''

    return {
        'id': int(medico['id_medico']),
        'id_medico': int(medico['id_medico']),
        'id_usuario': int(medico.get('id_usuario') or usuario.get('id_usuario') or 0),
        'nombre': nombre,
        'apellido': apellido,
        'nombre_completo': _nombre_completo(nombre, apellido),
        'iniciales': _iniciales(nombre, apellido),
        'especialidad': medico.get('nombre_especialidad') or usuario.get('nombre_especialidad') or '',
        'id_especialidad': medico.get('id_especialidad'),
        'matricula': medico.get('matricula') or usuario.get('matricula') or '',
        'email': medico.get('correo_electronico') or usuario.get('correo_electronico') or '',
        'documento': medico.get('dni') or usuario.get('dni') or '',
        'dni': medico.get('dni') or usuario.get('dni') or '',
        'fecha_nacimiento': _fecha(usuario.get('fecha_nacimiento')),
        'fecha_nacimiento_iso': _fecha_iso(usuario.get('fecha_nacimiento')),
        'fecha_registro': _fecha(usuario.get('fecha_creacion')),
    }


def _usuario_vista(medico, usuario=None):
    """Médico visto como usuario (es la plantilla que se usa para el perfil)."""
    datos = _medico_vista(medico, usuario)

    return {
        **datos,
        'id': datos['id_usuario'],
        'id_rol': 4,
        'mail': datos['email'],
        'rol': 'Médico',
    }


def _normalizar_turno(turno):
    """Adapta un turno de la API al formato de la lista del administrador."""
    paciente = turno.get('paciente') or {}
    consultorio = turno.get('consultorio') or {}
    estado = ((turno.get('estado') or {}).get('nombre') or '').lower()

    momento = _a_datetime(turno.get('fecha_horario_inicial'))
    fecha = momento.date() if momento else None

    nombre = _nombre_completo(
        paciente.get('nombre'),
        paciente.get('apellido'),
    )

    return {
        'id': turno.get('id_turno'),
        'iniciales': _iniciales(
            paciente.get('nombre'),
            paciente.get('apellido'),
        ) if nombre else 'SP',
        'nombre_paciente': nombre or 'Sin paciente',
        'estado': estado,
        'estado_nombre': estado.capitalize() if estado else '',
        'hora': momento.strftime('%H:%M') if momento else '',
        'fecha': fecha.strftime('%d - %m - %Y') if fecha else '',
        'consultorio': consultorio.get('numero', '-'),
        'color': COLORES_ESTADO.get(estado, 'bg-pink-500/30 text-pink-500'),
        'color_texto': COLORES_ESTADO.get(estado, 'bg-pink-500/30 text-pink-500'),
    }


def _agenda_resumen(agenda):
    """Resumen de una agenda para listarla en la pantalla del administrador."""
    consultorio = agenda.get('consultorio') or {}

    dias = ', '.join(
        DIAS_SEMANA[int(dia.get('dia_semana') or 1) - 1]
        for dia in agenda.get('dias') or []
    )

    return {
        'id_agenda': agenda.get('id_agenda'),
        'consultorio': consultorio.get('numero', '-'),
        'duracion_turno': agenda.get('duracion_turno'),
        'fecha_inicio': agenda.get('fecha_inicio'),
        'fecha_hasta': agenda.get('fecha_hasta'),
        'dias': dias,
        'jornadas': agenda.get('dias') or [],
    }


# =================================
# PERFIL DE UN MÉDICO
# =================================

@medico_admin_routes.route("/medicos/<int:id_medico>")
@requiere_rol("admin")
def medico_perfil(id_medico):

    try:
        medico = _obtener_medico(id_medico)
        usuario = _buscar_usuario(id_medico)

    except ErrorAPI as e:
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

    if medico is None:
        return "Médico no encontrado", 404

    especialidades, catalogo_coberturas = _catalogos()
    coberturas_medico = _coberturas_medico(id_medico)

    ids_asociadas = {c['id'] for c in coberturas_medico}
    coberturas_disponibles = [
        c for c in catalogo_coberturas if c['id'] not in ids_asociadas
    ]

    return render_template(
        "admin/abm/usuarios/profile.html",
        usuario=_usuario_vista(medico, usuario),
        especialidades=especialidades,
        coberturas_medico=coberturas_medico,
        coberturas_disponibles=coberturas_disponibles,
        consultorios=_consultorios(),
    )


# =================================
# MOSTRAR TURNOS DE UN MÉDICO
# =================================

@medico_admin_routes.route("/turnos/<int:id_medico>")
@requiere_rol("admin")
def turnos(id_medico):

    try:
        medico = _obtener_medico(id_medico)
    except ErrorAPI as e:
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

    if medico is None:
        return "Médico no encontrado", 404

    try:
        datos = api('GET', '/turnos', params={'id_medico': id_medico})
        lista_turnos = [
            _normalizar_turno(turno)
            for turno in datos.get('turnos', [])
        ]
    except ErrorAPI as e:
        flash(e.mensaje, 'error')
        lista_turnos = []

    return render_template(
        "admin/abm/medicos/turnos.html",
        medico=_medico_vista(medico),
        turnos=lista_turnos
    )


# =================================
# MOSTRAR AGENDA DE UN MÉDICO
# =================================

@medico_admin_routes.route("/agenda/<int:id_medico>")
@requiere_rol("admin")
def agenda(id_medico):

    try:
        medico = _obtener_medico(id_medico)
    except ErrorAPI as e:
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

    if medico is None:
        return "Médico no encontrado", 404

    agendas = []
    turnos_del_mes = []

    try:
        agendas = api(
            'GET',
            '/agendas',
            params={'id_medico': id_medico},
        ).get('agendas', [])

        anio, mes = mes_seleccionado(request.args)
        fecha_desde, fecha_hasta = rango_del_mes(anio, mes)

        turnos_del_mes = api(
            'GET',
            '/turnos',
            params={
                'id_medico': id_medico,
                'fecha_desde': fecha_desde.isoformat(),
                'fecha_hasta': fecha_hasta.isoformat(),
            },
        ).get('turnos', [])

    except ErrorAPI as e:
        flash(e.mensaje, 'error')

    consultorio = agendas[0].get('consultorio') if agendas else None
    consultorio = consultorio or {'numero': '-'}

    return render_template(
        "admin/abm/medicos/agenda.html",
        medico=_medico_vista(medico),
        agendas=[_agenda_resumen(agenda) for agenda in agendas],
        consultorios=_consultorios(),
        dias_formulario=DIAS_SEMANA,
        **contexto_agenda_mensual(
            request.args,
            agendas=agendas,
            turnos=turnos_del_mes,
            consultorio=consultorio,
        ),
    )


# =================================
# EDITAR DATOS DEL MÉDICO
# =================================

@medico_admin_routes.route(
    "/medicos/<int:id_medico>/editar",
    methods=["POST"]
)
@requiere_rol("admin")
def editar_medico(id_medico):

    perfil = redirect(
        url_for("rutas_admin_medico.medico_perfil", id_medico=id_medico)
    )

    try:
        medico = _obtener_medico(id_medico)
    except ErrorAPI as e:
        flash(e.mensaje, 'error')
        return perfil

    if medico is None:
        return "Médico no encontrado", 404

    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    email = request.form.get("email", "").strip().lower()
    documento = request.form.get("documento", "").strip()
    fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()
    id_especialidad = request.form.get("id_especialidad", type=int)
    matricula = request.form.get("matricula", "").strip()

    if not all([nombre, apellido, email, documento, id_especialidad, matricula]):
        flash("Completá todos los campos obligatorios.", "error")
        return perfil

    try:
        datos = {
            'nombre': nombre,
            'apellido': apellido,
            'dni': documento,
            'correo_electronico': email,
        }

        if fecha_nacimiento:
            datos['fecha_nacimiento'] = fecha_nacimiento

        api('PUT', f"/usuarios/{medico['id_usuario']}", json=datos)

        api('PUT', f'/medicos/{id_medico}', json={
            'id_especialidad': id_especialidad,
            'matricula': matricula,
        })

        # Coberturas elegidas en el formulario.
        actuales = {c['id'] for c in _coberturas_medico(id_medico)}
        elegidas = {
            int(id_cobertura)
            for id_cobertura in request.form.getlist('coberturas')
            if id_cobertura.isdigit()
        }

        for id_cobertura in elegidas - actuales:
            api(
                'POST',
                f'/medicos/{id_medico}/coberturas',
                json={'id_cobertura': id_cobertura},
            )

        for id_cobertura in actuales - elegidas:
            api(
                'DELETE',
                f'/medicos/{id_medico}/coberturas/{id_cobertura}',
            )

        flash('Médico actualizado correctamente.', 'success')

    except ErrorAPI as e:
        flash(e.mensaje, 'error')

    return perfil


# =================================
# ELIMINAR MÉDICO
# =================================

@medico_admin_routes.route(
    "/medicos/<int:id_medico>/eliminar",
    methods=["POST"]
)
@requiere_rol("admin")
def eliminar_medico(id_medico):

    try:
        api('DELETE', f'/medicos/{id_medico}')
    except ErrorAPI as e:
        flash(e.mensaje, 'error')
        return redirect(
            url_for("rutas_admin_medico.medico_perfil", id_medico=id_medico)
        )

    flash('Médico eliminado correctamente.', 'success')

    return redirect(
        url_for("rutas_admin_usuario.obtener_usuarios")
    )


# =================================
# CREAR AGENDA DE UN MÉDICO
# =================================

@medico_admin_routes.route(
    "/medicos/<int:id_medico>/agenda/crear",
    methods=["POST"]
)
@requiere_rol("admin")
def crear_agenda(id_medico):

    agenda_destino = url_for("rutas_admin_medico.agenda", id_medico=id_medico)

    try:
        medico = _obtener_medico(id_medico)
    except ErrorAPI as e:
        flash(e.mensaje, 'error')
        return redirect(agenda_destino)

    if medico is None:
        return "Médico no encontrado", 404

    id_consultorio = request.form.get("consultorio", type=int)
    duracion_turno = request.form.get("duracion_turno", type=int)
    fecha_inicio = request.form.get("fecha_inicio", "").strip()
    fecha_hasta = request.form.get("fecha_hasta", "").strip()

    dias_seleccionados = {
        int(dia)
        for dia in request.form.getlist("dias")
        if dia.isdigit()
    }

    jornadas = []

    for dia in sorted(dias_seleccionados):
        hora_inicio = request.form.get(f"hora_inicio_{dia}", "").strip()
        hora_fin = request.form.get(f"hora_fin_{dia}", "").strip()

        if not hora_inicio or not hora_fin:
            flash(
                f"Indicá el horario de atención del {DIAS_SEMANA[dia - 1].lower()}.",
                "error",
            )
            return redirect(agenda_destino)

        jornadas.append({
            'dia_semana': dia,
            'hora_inicio': f"{hora_inicio}:00",
            'hora_fin': f"{hora_fin}:00",
        })

    if not all([id_consultorio, duracion_turno, fecha_inicio, fecha_hasta]):
        flash("Completá todos los campos obligatorios.", "error")
        return redirect(agenda_destino)

    if not jornadas:
        flash("Elegí al menos un día de atención.", "error")
        return redirect(agenda_destino)

    try:
        api('POST', '/agendas', json={
            'id_medico': int(id_medico),
            'id_consultorio': int(id_consultorio),
            'duracion_turno': int(duracion_turno),
            'fecha_inicio': fecha_inicio,
            'fecha_hasta': fecha_hasta,
            'dias': jornadas,
        })

        flash('Agenda creada correctamente.', 'success')

    except ErrorAPI as e:
        flash(e.mensaje, 'error')

    return redirect(agenda_destino)
