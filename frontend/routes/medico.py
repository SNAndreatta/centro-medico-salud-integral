from flask import Blueprint, render_template, request, redirect, url_for

medico_routes = Blueprint('rutas_medico', __name__)


# ==========================================================
# DATOS DE PRUEBA
# ==========================================================

todos_los_turnos = [
    {
        'id': 1,
        'iniciales': 'NC',
        'nombre_paciente': 'Nombre Completo',
        'cobertura': 'Nombre Completo',
        'hora': '10:30 am.',
        'fecha': '11 - 10 - 2026',
        'consultorio': '123',
        'especialidad': 'Dr. Nombre Completo',
        'color': 'bg-pink-500/30 text-pink-500',
        'fecha_filtro': '2026-10-11',
        'cobertura_filtro': 'OSDE',
        'especialidad_filtro': 'Cardiología',
        'atendido': False
    },
    {
        'id': 2,
        'iniciales': 'NC',
        'nombre_paciente': 'Nombre Completo',
        'cobertura': 'Nombre Completo',
        'hora': '11:00 am.',
        'fecha': '11 - 10 - 2026',
        'consultorio': '123',
        'especialidad': 'Dr. Nombre Completo',
        'color': 'bg-purple-500/30 text-purple-500',
        'fecha_filtro': '2026-10-11',
        'cobertura_filtro': 'Swiss Medical',
        'especialidad_filtro': 'Dermatología',
        'atendido': False
    },
    {
        'id': 3,
        'iniciales': 'NC',
        'nombre_paciente': 'Nombre Completo',
        'cobertura': 'Nombre Completo',
        'hora': '11:30 am.',
        'fecha': '11 - 10 - 2026',
        'consultorio': '123',
        'especialidad': 'Dr. Nombre Completo',
        'color': 'bg-green-500/30 text-green-500',
        'fecha_filtro': '2026-10-11',
        'cobertura_filtro': 'PAMI',
        'especialidad_filtro': 'Clínica Médica',
        'atendido': False
    },
    {
        'id': 4,
        'iniciales': 'NC',
        'nombre_paciente': 'Nombre Completo',
        'cobertura': 'Nombre Completo',
        'hora': '10:30 am.',
        'fecha': '12 - 10 - 2026',
        'consultorio': '123',
        'especialidad': 'Dr. Nombre Completo',
        'color': 'bg-red-500/30 text-red-500',
        'fecha_filtro': '2026-10-12',
        'cobertura_filtro': 'OSDE',
        'especialidad_filtro': 'Cardiología',
        'atendido': False
    },
    {
        'id': 5,
        'iniciales': 'NC',
        'nombre_paciente': 'Nombre Completo',
        'cobertura': 'Nombre Completo',
        'hora': '11:00 am.',
        'fecha': '12 - 10 - 2026',
        'consultorio': '123',
        'especialidad': 'Dr. Nombre Completo',
        'color': 'bg-cyan-500/30 text-cyan-500',
        'fecha_filtro': '2026-10-12',
        'cobertura_filtro': 'Swiss Medical',
        'especialidad_filtro': 'Dermatología',
        'atendido': False
    }
]


# ==========================================================
# MARCAR TURNO COMO ATENDIDO
# ==========================================================

@medico_routes.route('/turno/<int:id_turno>/atendido', methods=['POST'])
def marcar_turno_atendido(id_turno):

    for turno in todos_los_turnos:

        if turno['id'] == id_turno:
            turno['atendido'] = True
            break

    return redirect(
        request.referrer or url_for('rutas_medico.ver_turnos')
    )


# ==========================================================
# VER TURNOS
# ==========================================================

@medico_routes.route('/turnos', methods=['GET'])
def ver_turnos():

    fecha = request.args.get('fecha', '')
    especialidad = request.args.get('especialidad', '')
    cobertura = request.args.get('cobertura', '')

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

    especialidades = sorted(set(
        turno['especialidad_filtro']
        for turno in todos_los_turnos
    ))

    coberturas = sorted(set(
        turno['cobertura_filtro']
        for turno in todos_los_turnos
    ))

    return render_template(
        'medico/mis_turnos.html',
        turnos=turnos,
        especialidades=especialidades,
        coberturas=coberturas
    )


# ==========================================================
# AGENDA
# ==========================================================

@medico_routes.route('/agenda', methods=['GET'])
def agenda():

    # ------------------------------------------------------
    # DATOS DEL MÉDICO
    # ------------------------------------------------------

    medico = {
        "id": 1,
        "nombre_completo": "Dr. Nombre Completo"
    }

    consultorio = {
        "numero": 123
    }

    fecha_inicio = "2026-10-12"


    # ------------------------------------------------------
    # DÍAS Y HORARIOS DE LA AGENDA
    # ------------------------------------------------------

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


    # ------------------------------------------------------
    # TURNO SELECCIONADO
    # ------------------------------------------------------

    turno_seleccionado = {
        "iniciales": "NC",
        "nombre_completo": "Nombre Completo",
        "nombre": "Nombre Completo",
        "cobertura": "COBERTURA",
        "hora": "10:30 am.",
        "fecha": "12 - 10 - 2026",
        "consultorio": 123,
        "color": "bg-pink-100 text-pink-400",
    }


    # ------------------------------------------------------
    # ENVIAR DATOS AL TEMPLATE
    # ------------------------------------------------------

    return render_template(
        'medico/agenda.html',
        medico=medico,
        dias_semana=dias_semana,
        turno_seleccionado=turno_seleccionado,
        consultorio=consultorio,
        fecha_inicio=fecha_inicio,
        rango_fechas="12 OCT - 17 OCT"
    )