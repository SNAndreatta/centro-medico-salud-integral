from flask import Blueprint, render_template, request

from src.api import ErrorAPI
from src.api_catalogos import obtener_consultorios
from src.api_estadisticas import ocupacion_consultorios
from src.api_turnos import listar as listar_turnos
from src.errores import es_sesion_vencida, sesion_vencida
from src.normalizar import formatear_hora
from src.permisos import requiere_rol

from ._comun import fecha_iso

disponibilidad_consultorios_admin_routes = Blueprint(
    'rutas_admin_disponibilidad_consultorios',
    __name__
)


def _horarios_por_consultorio(turnos):
    """Agrupa los horarios de la fecha por consultorio."""
    horarios = {}

    for turno in turnos:
        consultorio = turno.get('consultorio') or {}
        id_consultorio = consultorio.get('id_consultorio')
        estado = ((turno.get('estado') or {}).get('nombre') or '')

        horarios.setdefault(id_consultorio, []).append({
            'id_turno': turno.get('id_turno'),
            'hora': formatear_hora(turno.get('fecha_horario_inicial')),
            'estado': estado,
            'disponible': estado.lower() == 'disponible',
        })

    for lista in horarios.values():
        lista.sort(key=lambda horario: horario['hora'])

    return horarios


def _armar_pisos(consultorios, horarios, ocupacion):
    """Agrupa los consultorios por piso con su resumen de disponibilidad."""
    pisos = {}

    for consultorio in consultorios:
        id_consultorio = int(consultorio['id'])
        piso = consultorio.get('piso')
        clave = piso if piso is not None else 'sin-piso'

        if clave not in pisos:
            pisos[clave] = {
                'numero': piso if piso is not None else '—',
                'consultorios': [],
            }

        horarios_consultorio = horarios.get(id_consultorio, [])
        datos_ocupacion = ocupacion.get(id_consultorio, {})

        pisos[clave]['consultorios'].append({
            'id': id_consultorio,
            'numero': int(consultorio['numero']),
            'piso': piso,
            'horarios': horarios_consultorio,
            'total_horarios': len(horarios_consultorio),
            'disponibles': sum(
                1 for horario in horarios_consultorio
                if horario['disponible']
            ),
            'ocupados': sum(
                1 for horario in horarios_consultorio
                if not horario['disponible']
            ),
            'porcentaje_ocupacion': datos_ocupacion.get(
                'porcentaje_ocupacion',
                0,
            ),
        })

    return list(pisos.values())


@disponibilidad_consultorios_admin_routes.route("/disponibilidad-consultorios")
@requiere_rol("admin")
def disponibilidad_consultorios():
    fecha = fecha_iso(request.args.get("fecha"))

    error = None
    consultorios = []
    turnos = []
    ocupacion = {}

    try:
        consultorios = obtener_consultorios()
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        error = e.mensaje

    try:
        turnos = listar_turnos({'fecha_desde': fecha, 'fecha_hasta': fecha})
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        error = error or e.mensaje

    try:
        datos = ocupacion_consultorios({
            'fecha_desde': fecha, 'fecha_hasta': fecha,
        })
        ocupacion = {
            consultorio['id_consultorio']: consultorio
            for consultorio in datos.get('consultorios', [])
        }
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        error = error or e.mensaje

    pisos = _armar_pisos(
        consultorios,
        _horarios_por_consultorio(turnos),
        ocupacion,
    )

    return render_template(
        "admin/dashboards/disponibilidad_consultorio.html",
        pisos=pisos,
        fecha=fecha,
        error=error,
    )
