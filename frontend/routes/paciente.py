from flask import Blueprint
from flask import render_template, request
from datetime import date, timedelta

paciente_routes = Blueprint('rutas_paciente_prefijo_api', __name__)

@paciente_routes.route('/turnos-paciente', methods=['GET'])
def mis_turnos():

    # Datos harcodeados de prueba
    turnos = [
        {
            "id": 1,
            "iniciales": "NC",
            "especialidad": "Especialidad",
            "medico": "Nombre Completo",
            "fecha": "Día - Mes - Año",
            "hora": "15:00 pm.",
            "consultorio": "123"
        },
        {
            "id": 2,
            "iniciales": "NC",
            "especialidad": "Especialidad",
            "medico": "Nombre Completo",
            "fecha": "Día - Mes - Año",
            "hora": "15:00 pm.",
            "consultorio": "123"
        },
        {
            "id": 3,
            "iniciales": "NC",
            "especialidad": "Especialidad",
            "medico": "Nombre Completo",
            "fecha": "Día - Mes - Año",
            "hora": "15:00 pm.",
            "consultorio": "123"
        },
        {
            "id": 4,
            "iniciales": "NC",
            "especialidad": "Especialidad",
            "medico": "Nombre Completo",
            "fecha": "Día - Mes - Año",
            "hora": "15:00 pm.",
            "consultorio": "123"
        }
    ]

    return render_template(
        '/pacientes/mis_turnos.html',
        turnos=turnos
    )

@paciente_routes.route('/sacar-turno', methods=['GET'])
def sacar_turno():

    especialidades = [
        {"id": 1, "nombre": "Cardiología"},
        {"id": 2, "nombre": "Clínica Médica"},
        {"id": 3, "nombre": "Dermatología"},
        {"id": 4, "nombre": "Oftalmología"},
        {"id": 5, "nombre": "Pediatría"},
        {"id": 6, "nombre": "Traumatología"}
    ]

    medicos = [
        {"id": 1, "nombre": "Dr. Nombre Completo", "iniciales": "NC"},
        {"id": 2, "nombre": "Dr. Nombre Completo", "iniciales": "NC"},
        {"id": 3, "nombre": "Dr. Nombre Completo", "iniciales": "NC"}
    ]

    fechas = [
        {"dia_semana": "LUN", "dia": 19, "mes": "OCTUBRE"},
        {"dia_semana": "MAR", "dia": 20, "mes": "OCTUBRE"},
        {"dia_semana": "MIÉ", "dia": 21, "mes": "OCTUBRE"},
        {"dia_semana": "JUE", "dia": 22, "mes": "OCTUBRE"}
    ]

    horarios = ["15:30", "16:30", "17:30", "18:30"]

    return render_template(
        'pacientes/pasos_turno/especialidad.html',
        paso=1,
        especialidades=especialidades,
        medicos=medicos,
        fechas=fechas,
        horarios=horarios
    )