from flask import Blueprint, render_template, request

from src.api import ErrorAPI, api

from ._comun import fecha_iso, formatear_hora

disponibilidad_consultorios_admin_routes = Blueprint(
    'rutas_admin_disponibilidad_consultorios',
    __name__
)


def _listar_consultorios():
    """Devuelve los consultorios de la API."""
    datos = api('GET', '/consultorios')

    return datos.get('consultorios', [])


def _listar_turnos_del_dia(fecha):
    """Devuelve los turnos programados para la fecha indicada."""
    datos = api(
        'GET',
        '/turnos',
        params={'fecha_desde': fecha, 'fecha_hasta': fecha},
    )

    return datos.get('turnos', [])


def _listar_ocupacion(fecha):
    """Devuelve la ocupación de los consultorios para la fecha indicada."""
    datos = api(
        'GET',
        '/estadisticas/ocupacion_consultorios',
        params={'fecha_desde': fecha, 'fecha_hasta': fecha},
    )

    return {
        consultorio['id_consultorio']: consultorio
        for consultorio in datos.get('consultorios', [])
    }


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
        id_consultorio = int(consultorio['id_consultorio'])
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
def disponibilidad_consultorios():

    fecha = fecha_iso(request.args.get("fecha"))

    error = None
    consultorios = []
    turnos = []
    ocupacion = {}

    try:
        consultorios = _listar_consultorios()
    except ErrorAPI as e:
        error = e.mensaje

    try:
        turnos = _listar_turnos_del_dia(fecha)
    except ErrorAPI as e:
        error = error or e.mensaje

    try:
        ocupacion = _listar_ocupacion(fecha)
    except ErrorAPI as e:
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
