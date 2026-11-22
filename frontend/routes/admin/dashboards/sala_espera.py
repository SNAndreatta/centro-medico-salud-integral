from flask import Blueprint, render_template

from src.api import ErrorAPI
from src.api_catalogos import obtener_especialidades
from src.api_estadisticas import sala_espera as sala_espera_api
from src.errores import es_sesion_vencida, sesion_vencida
from src.normalizar import normalizar_turno
from src.permisos import requiere_rol

sala_espera_admin_routes = Blueprint(
    'rutas_admin_sala_espera',
    __name__
)


def _listar_especialidades():
    """Devuelve las especialidades de la API para el filtro."""
    try:
        return obtener_especialidades()
    except ErrorAPI:
        return []


@sala_espera_admin_routes.route('/admin/sala-espera')
@requiere_rol("admin")
def sala_espera():
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
        'admin/dashboards/sala_espera.html',
        pacientes_en_espera=pacientes_en_espera,
        especialidades=especialidades,
        total=total,
        error=error,
    )
