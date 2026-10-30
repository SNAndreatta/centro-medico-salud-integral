from flask import Blueprint
from flask import render_template, request

medico_routes = Blueprint('rutas_medico_prefijo_api', __name__)

@medico_routes.route('/turnos', methods=['GET'])
def ver_turnos():

    # Datos harcodeados de prueba
    todos_los_turnos = [
        {
            'iniciales': 'NC',
            'cobertura': 'Nombre Completo',
            'hora': '10:30 am.',
            'fecha': '11 - 10 - 2026',
            'consultorio': '123',
            'especialidad': 'Dr. Nombre Completo',
            'color': "bg-pink-500/30 text-pink-500",
            'fecha_filtro': '2026-10-11',
            'cobertura_filtro': 'OSDE',
            'especialidad_filtro': 'Cardiología'
        },
        {
            'iniciales': 'NC',
            'cobertura': 'Nombre Completo',
            'hora': '10:30 am.',
            'fecha': '11 - 10 - 2026',
            'consultorio': '123',
            'especialidad': 'Dr. Nombre Completo',
            'color': "bg-purple-500/30 text-purple-500",
            'fecha_filtro': '2026-10-11',
            'cobertura_filtro': 'Swiss Medical',
            'especialidad_filtro': 'Dermatología'
        },
        {
            'iniciales': 'NC',
            'cobertura': 'Nombre Completo',
            'hora': '10:30 am.',
            'fecha': '11 - 10 - 2026',
            'consultorio': '123',
            'especialidad': 'Dr. Nombre Completo',
            'color': "bg-green-500/30 text-green-500",
            'fecha_filtro': '2026-10-11',
            'cobertura_filtro': 'PAMI',
            'especialidad_filtro': 'Clínica Médica'
        },
        {
            'iniciales': 'NC',
            'cobertura': 'Nombre Completo',
            'hora': '10:30 am.',
            'fecha': '11 - 10 - 2026',
            'consultorio': '123',
            'especialidad': 'Dr. Nombre Completo',
            'color': "bg-red-500/30 text-red-500",
            'fecha_filtro': '2026-10-12',
            'cobertura_filtro': 'OSDE',
            'especialidad_filtro': 'Cardiología'
        },
        {
            'iniciales': 'NC',
            'cobertura': 'Nombre Completo',
            'hora': '10:30 am.',
            'fecha': '11 - 10 - 2026',
            'consultorio': '123',
            'especialidad': 'Dr. Nombre Completo',
            'color': "bg-blue-500/30 text-blue-500",
            'fecha_filtro': '2026-10-12',
            'cobertura_filtro': 'Swiss Medical',
            'especialidad_filtro': 'Dermatología'
        }
    ]

    # Obtener filtros del formulario
    fecha = request.args.get('fecha', '')
    especialidad = request.args.get('especialidad', '')
    cobertura = request.args.get('cobertura', '')

    # Aplicar filtros
    turnos = todos_los_turnos

    if fecha:
        turnos = [
            turno for turno in turnos
            if turno['fecha_filtro'] == fecha
        ]

    if especialidad:
        turnos = [
            turno for turno in turnos
            if turno['especialidad_filtro'] == especialidad
        ]

    if cobertura:
        turnos = [
            turno for turno in turnos
            if turno['cobertura_filtro'] == cobertura
        ]

    # Opciones disponibles para los filtros
    especialidades = sorted(set(
        turno['especialidad_filtro']
        for turno in todos_los_turnos
    ))

    coberturas = sorted(set(
        turno['cobertura_filtro']
        for turno in todos_los_turnos
    ))

    return render_template(
        '/medico/mis_turnos.html',
        turnos=turnos,
        especialidades=especialidades,
        coberturas=coberturas
    )

@medico_routes.route('/agenda', methods=['GET'])
def agenda():

    dias_semana = [
        {
            "nombre": "LUN",
            "turnos": [
                {"hora": "09:00", "disponible": False, "seleccionado": False},
                {"hora": "09:30", "disponible": True, "seleccionado": False},
                {"hora": "10:00", "disponible": False, "seleccionado": False},
                {"hora": "10:30", "disponible": True, "seleccionado": False},
                {"hora": "11:00", "disponible": False, "seleccionado": False},
                {"hora": "11:30", "disponible": True, "seleccionado": False},
            ],
        },
        {
            "nombre": "MAR",
            "turnos": [
                {"hora": "13:00", "disponible": True, "seleccionado": False},
                {"hora": "13:30", "disponible": True, "seleccionado": False},
                {"hora": "14:00", "disponible": False, "seleccionado": False},
                {"hora": "14:30", "disponible": True, "seleccionado": False},
                {"hora": "15:00", "disponible": True, "seleccionado": False},
                {"hora": "15:30", "disponible": True, "seleccionado": False},
            ],
        },
        {
            "nombre": "MIÉ",
            "turnos": [
                {"hora": "09:00", "disponible": True, "seleccionado": False},
                {"hora": "09:30", "disponible": True, "seleccionado": False},
                {"hora": "10:00", "disponible": True, "seleccionado": False},
                {"hora": "10:30", "disponible": True, "seleccionado": True},
                {"hora": "11:00", "disponible": False, "seleccionado": False},
                {"hora": "11:30", "disponible": True, "seleccionado": False},
            ],
        },
        {
            "nombre": "JUE",
            "turnos": [
                {"hora": "", "disponible": False, "seleccionado": False},
                {"hora": "", "disponible": False, "seleccionado": False},
                {"hora": "", "disponible": False, "seleccionado": False},
                {"hora": "", "disponible": False, "seleccionado": False},
                {"hora": "", "disponible": False, "seleccionado": False},
                {"hora": "", "disponible": False, "seleccionado": False},
            ],
        },
        {
            "nombre": "VIE",
            "turnos": [
                {"hora": "13:00", "disponible": False, "seleccionado": False},
                {"hora": "13:30", "disponible": False, "seleccionado": False},
                {"hora": "14:00", "disponible": False, "seleccionado": False},
                {"hora": "14:30", "disponible": True, "seleccionado": False},
                {"hora": "15:00", "disponible": False, "seleccionado": False},
                {"hora": "15:30", "disponible": True, "seleccionado": False},
            ],
        },
        {
            "nombre": "SÁB",
            "turnos": [
                {"hora": "", "disponible": False, "seleccionado": False},
                {"hora": "", "disponible": False, "seleccionado": False},
                {"hora": "", "disponible": False, "seleccionado": False},
                {"hora": "", "disponible": False, "seleccionado": False},
                {"hora": "", "disponible": False, "seleccionado": False},
                {"hora": "", "disponible": False, "seleccionado": False},
            ],
        },
    ]

    # Datos del turno seleccionado
    turno_seleccionado = {
        "iniciales": "NC",
        "nombre_completo": "Nombre Completo",
        "cobertura": "COBERTURA",
        "hora": "10:30 am.",
        "fecha": "11 - 10 - 2026",
        "consultorio": 123,
        "color": "bg-pink-100 text-pink-400",
    }

    return render_template(
        'medico/agenda.html',
        dias_semana=dias_semana,
        turno_seleccionado=turno_seleccionado,
        consultorio=123,
        rango_fechas="09 OCT - 14 OCT",
    )