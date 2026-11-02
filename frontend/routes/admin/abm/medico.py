from flask import Blueprint, render_template, request, redirect, url_for
from datetime import date, timedelta

medico_admin_routes = Blueprint('rutas_admin_medico', __name__)

# =================================
# DATOS SIMULADOS DE MÉDICOS
# =================================

medicos = [
    {
        "id": 1,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "CARDIOLOGÍA",
        "color": "bg-pink-500/30 text-pink-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA"
    },
    {
        "id": 2,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "DERMATOLOGÍA",
        "color": "bg-emerald-500/30 text-emerald-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA"
    },
    {
        "id": 3,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "OFTALMOLOGÍA",
        "color": "bg-cyan-500/30 text-cyan-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA"
    },
    {
        "id": 4,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "CLÍNICA MÉDICA",
        "color": "bg-amber-500/30 text-amber-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA"
    },
    {
        "id": 5,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "PEDIATRÍA",
        "color": "bg-red-500/30 text-red-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA"
    },
    {
        "id": 6,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "CARDIOLOGÍA",
        "color": "bg-lime-500/30 text-lime-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA"
    }
]

# =================================
# MOSTRAR MÉDICOS
# =================================

@medico_admin_routes.route("/medicos/")
def obtener_medicos():

    return render_template(
        "admin/abm/medicos/index.html",
        medicos=medicos
    )

# =================================
# COBERTURAS SIMULADAS
# =================================

coberturas = [
    {"id": 1, "nombre": "Galeno"},
    {"id": 2, "nombre": "IOMA"},
    {"id": 3, "nombre": "Swiss Medical"},
    {"id": 4, "nombre": "OSDE"},
]


# =================================
# PERFIL DE UN MÉDICO
# =================================

@medico_admin_routes.route("/medicos/<int:id_medico>")
def medico_perfil(id_medico):

    medico_encontrado = None

    for medico in medicos:
        if medico["id"] == id_medico:
            medico_encontrado = medico
            break

    if medico_encontrado is None:
        return "Médico no encontrado", 404

    return render_template(
        "admin/abm/medicos/profile.html",
        medico=medico_encontrado,
        coberturas=coberturas
    )

# =================================
# DATOS SIMULADOS DE TURNOS
# =================================

turnos_medicos = {
    1: [
        {
            "id": 1,
            "iniciales": "NE",
            "estado": "pendiente",
            "estado_nombre": "Especialidad",
            "hora": "15:00 pm.",
            "fecha": "Día - Mes - Año",
            "consultorio": 123,
            "color": "bg-pink-500/30 text-pink-500"
        },
        {
            "id": 2,
            "iniciales": "NE",
            "estado": "confirmado",
            "estado_nombre": "Especialidad",
            "hora": "15:00 pm.",
            "fecha": "Día - Mes - Año",
            "consultorio": 123,
            "color": "bg-lime-500/30 text-lime-500"
        },
        {
            "id": 3,
            "iniciales": "NE",
            "estado": "realizado",
            "estado_nombre": "Especialidad",
            "hora": "15:00 pm.",
            "fecha": "Día - Mes - Año",
            "consultorio": 123,
            "color": "bg-purple-500/30 text-purple-500"
        },
        {
            "id": 4,
            "iniciales": "NE",
            "estado": "cancelado",
            "estado_nombre": "Especialidad",
            "hora": "15:00 pm.",
            "fecha": "Día - Mes - Año",
            "consultorio": 123,
            "color": "bg-emerald-500/30 text-emerald-500"
        }
    ]
}


# =================================
# DATOS SIMULADOS DE AGENDA
# =================================

horarios_disponibles = [
    ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"],
    ["13:00", "13:30", "14:00", "14:30", "15:00", "15:30"],
    ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"],
    [],
    ["13:00", "13:30", "14:00", "14:30", "15:00", "15:30"],
    []
]


# =================================
# MOSTRAR TURNOS DE UN MÉDICO
# =================================

@medico_admin_routes.route("/turnos/<int:id_medico>")
def turnos(id_medico):

    medico_encontrado = next(
        (medico for medico in medicos if medico["id"] == id_medico),
        None
    )

    if medico_encontrado is None:
        return "Médico no encontrado", 404

    turnos = turnos_medicos.get(id_medico, [])

    return render_template(
        "admin/abm/medicos/turnos.html",
        medico=medico_encontrado,
        turnos=turnos
    )


# =================================
# MOSTRAR AGENDA DE UN MÉDICO
# =================================

@medico_admin_routes.route("/agenda/<int:id_medico>")
def agenda(id_medico):

    medico_encontrado = next(
        (medico for medico in medicos if medico["id"] == id_medico),
        None
    )

    if medico_encontrado is None:
        return "Médico no encontrado", 404

    # Fecha del lunes de la semana actual
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())

    nombres_dias = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB"]

    dias = []

    for i in range(6):
        fecha = lunes + timedelta(days=i)

        dias.append({
            "nombre": nombres_dias[i],
            "fecha": fecha.isoformat()
        })

    # Construir las columnas de horarios
    horarios = []

    for indice_dia, lista_horarios in enumerate(horarios_disponibles):

        columna = []

        for hora in lista_horarios:

            columna.append({
                "hora": hora,
                "disponible": True
            })

        horarios.append(columna)

    # Consultorio simulado
    consultorio = {
        "id": 1,
        "numero": 123
    }

    # Turno seleccionado de ejemplo
    turno_seleccionado = {
        "iniciales": "NC",
        "nombre": "Nombre Completo",
        "cobertura": "COBERTURA",
        "hora": "10:30 am.",
        "fecha": "11 - 10 - 2026"
    }

    rango_semana = (
        lunes.strftime("%d %b").upper()
        + " - "
        + (lunes + timedelta(days=5)).strftime("%d %b").upper()
    )

    # Datos para el calendario
    horarios_js = [
        [
            {
                "hora": horario["hora"],
                "disponible": horario["disponible"]
            }
            for horario in columna
        ]
        for columna in horarios
    ]

    return render_template(
        "admin/abm/medicos/agenda.html",
        medico=medico_encontrado,
        dias=dias,
        nombre_dias=nombres_dias,
        horarios=horarios,
        horarios_js=horarios_js,
        consultorio=consultorio,
        turno_seleccionado=turno_seleccionado,
        rango_semana=rango_semana,
        fecha_inicio=lunes.isoformat()
    )