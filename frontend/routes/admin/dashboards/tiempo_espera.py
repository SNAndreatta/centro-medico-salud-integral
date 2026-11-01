from flask import Blueprint, render_template

tiempo_espera_admin_routes = Blueprint('tiempo_espera_admin_routes', __name__)


@tiempo_espera_admin_routes.route('/admin/tiempo-espera')
def tiempo_espera():

    medicos = [
        {
            'nombre': 'Nombre Completo',
            'iniciales': 'NC',
            'espera': 10,
            'color_fondo': 'bg-[#FAD8E0]',
            'color_texto': 'text-[#E47789]'
        },
        {
            'nombre': 'Nombre Completo',
            'iniciales': 'NC',
            'espera': 15,
            'color_fondo': 'bg-[#DDF3F3]',
            'color_texto': 'text-[#72BDBD]'
        },
        {
            'nombre': 'Nombre Completo',
            'iniciales': 'NC',
            'espera': 7,
            'color_fondo': 'bg-[#E5D5E9]',
            'color_texto': 'text-[#A16AA9]'
        },
        {
            'nombre': 'Nombre Completo',
            'iniciales': 'NC',
            'espera': 20,
            'color_fondo': 'bg-[#EAB8B8]',
            'color_texto': 'text-[#B91C1C]'
        },
        {
            'nombre': 'Nombre Completo',
            'iniciales': 'NC',
            'espera': 5,
            'color_fondo': 'bg-[#B5C5D1]',
            'color_texto': 'text-acento'
        },
        {
            'nombre': 'Nombre Completo',
            'iniciales': 'NC',
            'espera': 13,
            'color_fondo': 'bg-[#FAD8E0]',
            'color_texto': 'text-[#E47789]'
        }
    ]

    especialidades = [
        {'nombre': 'Cardiología', 'espera': 40},
        {'nombre': 'Clínica Médica', 'espera': 15},
        {'nombre': 'Dermatología', 'espera': 7},
        {'nombre': 'Oftalmología', 'espera': 12},
        {'nombre': 'Pediatría', 'espera': 6},
        {'nombre': 'Traumatología', 'espera': 7}
    ]

    return render_template(
        'admin/dashboards/tiempo_espera.html',
        medicos=medicos,
        especialidades=especialidades
    )