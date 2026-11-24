"""ABM de médicos del administrador.

Todas las llamadas a la API pasan por los helpers de ``src``.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from routes.agenda_mensual import (
    contexto_agenda_mensual,
    mes_seleccionado,
    rango_del_mes,
)
from src.api import ErrorAPI
from src.api_catalogos import (
    agregar_coberturas_medico,
    coberturas_medico as coberturas_del_medico,
    obtener_coberturas,
    obtener_consultorios,
    obtener_especialidades,
    obtener_medico,
    quitar_cobertura_medico,
)
from src.api_turnos import crear_agenda as api_crear_agenda, listar as listar_turnos
from src.api_turnos import obtener_agendas
from src.api_usuario import (
    editar_medico as api_editar_medico,
    editar_usuario as api_editar_usuario,
    eliminar_medico as api_eliminar_medico,
    listar_usuarios,
)
from src.errores import es_sesion_vencida, sesion_vencida
from src.normalizar import (
    estado_turno,
    g,
    iniciales,
    nombre_completo,
    normalizar_turno,
)
from src.permisos import requiere_rol
from src.tiempo import a_date, formatear_fecha

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


def _entero(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return valor


def _obtener_medico(id_medico):
    medico = obtener_medico(id_medico)

    return medico


def _buscar_usuario(id_medico):
    """Usuario asociado al médico, buscando en el listado de la API."""
    return next(
        (
            usuario for usuario in listar_usuarios()
            if _entero(usuario.get('id_medico')) == _entero(id_medico)
        ),
        None,
    )


def _catalogos():
    """Catálogos de especialidades y coberturas, con fallbacks explícitos."""
    especialidades = []
    coberturas = []

    try:
        especialidades = obtener_especialidades()
    except ErrorAPI:
        pass

    try:
        coberturas = obtener_coberturas()
    except ErrorAPI:
        pass

    return especialidades, coberturas


def _coberturas_medico(id_medico):
    try:
        return coberturas_del_medico(id_medico)
    except ErrorAPI:
        return []


def _consultorios():
    try:
        return obtener_consultorios()
    except ErrorAPI:
        return []


def _medico_vista(medico, usuario=None):
    """Datos del médico en el formato que usan las plantillas."""
    usuario = usuario or {}

    id_medico = _entero(g(medico, 'id_medico', 'id'))
    id_usuario = _entero(g(medico, 'id_usuario', default=g(usuario, 'id_usuario')))
    nombre = g(medico, 'nombre', default=g(usuario, 'nombre', default='')) or ''
    apellido = g(medico, 'apellido', default=g(usuario, 'apellido', default='')) or ''
    mail = (
        g(medico, 'correo_electronico')
        or g(medico, 'email')
        or g(usuario, 'mail')
        or ''
    )
    documento = g(medico, 'dni') or g(usuario, 'dni') or ''
    fecha_nac = g(medico, 'fecha_nacimiento') or g(usuario, 'fecha_nacimiento_iso')
    fecha_reg = g(medico, 'fecha_creacion') or g(usuario, 'fecha_registro')
    nacimiento = a_date(fecha_nac)

    return {
        'id': id_usuario,
        'id_usuario': id_usuario,
        'id_medico': id_medico,
        'id_rol': 4,
        'nombre': nombre,
        'apellido': apellido,
        'nombre_completo': nombre_completo(nombre, apellido),
        'iniciales': iniciales(nombre, apellido),
        'especialidad': (
            g(medico, 'nombre_especialidad')
            or g(usuario, 'especialidad')
            or ''
        ),
        'id_especialidad': (
            g(medico, 'id_especialidad')
            or g(usuario, 'id_especialidad')
        ),
        'matricula': g(medico, 'matricula') or g(usuario, 'matricula') or '',
        'email': mail,
        'mail': mail,
        'documento': documento,
        'dni': documento,
        'fecha_nacimiento': (
            g(usuario, 'fecha_nacimiento')
            if g(usuario, 'fecha_nacimiento')
            else (formatear_fecha(fecha_nac) if fecha_nac else '-')
        ),
        'fecha_nacimiento_iso': (
            nacimiento.isoformat() if nacimiento else ''
        ),
        'fecha_registro': (
            g(usuario, 'fecha_registro')
            if g(usuario, 'fecha_registro')
            else (formatear_fecha(fecha_reg) if fecha_reg else '-')
        ),
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
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

    if medico is None:
        return "Médico no encontrado", 404

    especialidades, catalogo_coberturas = _catalogos()
    actuales = _coberturas_medico(id_medico)

    ids_asociadas = {c['id'] for c in actuales}
    coberturas_disponibles = [
        c for c in catalogo_coberturas if c['id'] not in ids_asociadas
    ]

    return render_template(
        "admin/abm/usuarios/profile.html",
        usuario=_medico_vista(medico, usuario),
        especialidades=especialidades,
        coberturas_medico=actuales,
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
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

    if medico is None:
        return "Médico no encontrado", 404

    lista_turnos = []

    try:
        turnos_api = [
            turno for turno in listar_turnos({'id_medico': id_medico})
            if estado_turno(turno) != 'disponible'
        ]
        lista_turnos = [
            normalizar_turno(turno, indice, vista='admin_tabla')
            for indice, turno in enumerate(turnos_api)
        ]
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')

    return render_template(
        "admin/abm/medicos/turnos.html",
        medico=_medico_vista(medico),
        turnos=lista_turnos,
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
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

    if medico is None:
        return "Médico no encontrado", 404

    agendas = []
    turnos_del_mes = []

    try:
        agendas = obtener_agendas(id_medico=id_medico)

        anio, mes = mes_seleccionado(request.args)
        fecha_desde, fecha_hasta = rango_del_mes(anio, mes)

        turnos_del_mes = listar_turnos({
            'id_medico': id_medico,
            'fecha_desde': fecha_desde.isoformat(),
            'fecha_hasta': fecha_hasta.isoformat(),
        })
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')

    consultorio = agendas[0].get('consultorio') if agendas else None
    consultorio = consultorio or {'numero': '-'}

    return render_template(
        "agenda/agenda.html",
        es_admin=True,
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
        if es_sesion_vencida(e):
            return sesion_vencida()
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

    datos = {
        'nombre': nombre,
        'apellido': apellido,
        'dni': documento,
        'correo_electronico': email,
    }
    if fecha_nacimiento:
        datos['fecha_nacimiento'] = fecha_nacimiento

    try:
        api_editar_usuario(medico['id_usuario'], datos)
        api_editar_medico(id_medico, {
            'id_especialidad': id_especialidad,
            'matricula': matricula,
        })

        actuales = {c['id'] for c in _coberturas_medico(id_medico)}
        elegidas = {
            int(id_cobertura)
            for id_cobertura in request.form.getlist('coberturas')
            if id_cobertura.isdigit()
        }

        agregar_coberturas_medico(id_medico, elegidas - actuales)

        for id_cobertura in actuales - elegidas:
            quitar_cobertura_medico(id_medico, id_cobertura)

        flash('Médico actualizado correctamente.', 'success')

    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
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
        api_eliminar_medico(id_medico)
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
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
        if es_sesion_vencida(e):
            return sesion_vencida()
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
        api_crear_agenda({
            'id_medico': int(id_medico),
            'id_consultorio': int(id_consultorio),
            'duracion_turno': int(duracion_turno),
            'fecha_inicio': fecha_inicio,
            'fecha_hasta': fecha_hasta,
            'dias': jornadas,
        })

        flash('Agenda creada correctamente.', 'success')

    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')

    return redirect(agenda_destino)
