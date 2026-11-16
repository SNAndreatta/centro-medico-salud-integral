from flask import Blueprint, render_template, request, redirect, url_for
from datetime import date, timedelta
from routes.agenda_mensual import contexto_agenda_mensual
from src.permisos import requiere_rol



medico_admin_routes = Blueprint('rutas_admin_medico', __name__)

# =================================
# DATOS SIMULADOS DE MÉDICOS
# =================================

medicos = [
    {
        "id": 104,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "CARDIOLOGÍA",
        "color": "bg-pink-500/30 text-pink-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA",
        "fecha_registro": "DD/MM/AAAA"
    },
    {
        "id": 10,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "DERMATOLOGÍA",
        "color": "bg-emerald-500/30 text-emerald-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA",
        "fecha_registro": "DD/MM/AAAA"
    },
    {
        "id": 9,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "OFTALMOLOGÍA",
        "color": "bg-cyan-500/30 text-cyan-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA",
        "fecha_registro": "DD/MM/AAAA"
    },
    {
        "id": 8,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "CLÍNICA MÉDICA",
        "color": "bg-amber-500/30 text-amber-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA",
        "fecha_registro": "DD/MM/AAAA"
    },
    {
        "id": 7,
        "nombre_completo": "Dr. Nombre Completo",
        "iniciales": "NC",
        "especialidad": "PEDIATRÍA",
        "color": "bg-red-500/30 text-red-500",
        "matricula": "987654321",
        "email": "ejemplo.usuario@gmail.com",
        "documento": "44.444.444",
        "fecha_nacimiento": "DD/MM/AAAA",
        "fecha_registro": "DD/MM/AAAA"
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
        "fecha_nacimiento": "DD/MM/AAAA",
        "fecha_registro": "DD/MM/AAAA"
    }
]

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
# CONSULTORIOS Y AGENDAS SIMULADAS
# =================================

consultorios = [
    {"id": 1, "numero": 101},
    {"id": 2, "numero": 102},
    {"id": 3, "numero": 103},
]

agendas_medicos = []

# =================================
# PERFIL DE UN MÉDICO
# =================================


@medico_admin_routes.route("/medicos/<int:id_medico>")
@requiere_rol("admin")
def medico_perfil(id_medico):

    medico_encontrado = next(
        (m for m in medicos if m["id"] == id_medico),
        None
    )

    if medico_encontrado is None:
        return "Médico no encontrado", 404

    # Separar nombre y apellido para completar el formulario.
    partes_nombre = medico_encontrado["nombre_completo"].replace("Dr. ", "").split(" ", 1)

    medico_vista = medico_encontrado.copy()
    medico_vista["nombre"] = partes_nombre[0] if partes_nombre else ""
    medico_vista["apellido"] = partes_nombre[1] if len(partes_nombre) > 1 else ""

    return render_template(
        "admin/abm/usuarios/profile.html",
        medico=medico_vista,
        coberturas=coberturas,
        consultorios=consultorios
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
@requiere_rol("admin")
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
@requiere_rol("admin")
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
        consultorio=consultorio,
        **contexto_agenda_mensual(request.args),
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

    medico = next(
        (m for m in medicos if m["id"] == id_medico),
        None
    )

    if medico is None:
        return "Médico no encontrado", 404

    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    email = request.form.get("email", "").strip()
    documento = request.form.get("documento", "").strip()
    fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()

    if not all([nombre, apellido, email, documento, fecha_nacimiento]):
        return "Todos los campos son obligatorios", 400

    medico["nombre_completo"] = f"Dr. {nombre} {apellido}"
    medico["iniciales"] = (
        nombre[0].upper() + apellido[0].upper()
    )
    medico["email"] = email
    medico["documento"] = documento
    medico["fecha_nacimiento"] = fecha_nacimiento

    # Guardar IDs de las coberturas seleccionadas.
    ids_coberturas = request.form.getlist("coberturas")
    medico["coberturas_ids"] = [
        int(id_cobertura)
        for id_cobertura in ids_coberturas
        if id_cobertura.isdigit()
    ]

    return redirect(
        url_for(
            "rutas_admin_medico.medico_perfil",
            id_medico=id_medico
        )
    )


# =================================
# ELIMINAR MÉDICO
# =================================

@medico_admin_routes.route(
    "/medicos/<int:id_medico>/eliminar",
    methods=["POST"]
)
@requiere_rol("admin")
def eliminar_medico(id_medico):

    medico = next(
        (m for m in medicos if m["id"] == id_medico),
        None
    )

    if medico is None:
        return "Médico no encontrado", 404

    medicos.remove(medico)

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

    medico = next(
        (m for m in medicos if m["id"] == id_medico),
        None
    )

    if medico is None:
        return "Médico no encontrado", 404

    consultorio_id = request.form.get("consultorio", "").strip()
    duracion_turno = request.form.get("duracion_turno", "").strip()
    fecha_inicio = request.form.get("fecha_inicio", "").strip()
    fecha_hasta = request.form.get("fecha_hasta", "").strip()

    if not all([
        consultorio_id,
        duracion_turno,
        fecha_inicio,
        fecha_hasta
    ]):
        return "Todos los campos son obligatorios", 400

    consultorio_encontrado = next(
        (
            c for c in consultorios
            if c["id"] == int(consultorio_id)
        ),
        None
    )

    if consultorio_encontrado is None:
        return "Consultorio no encontrado", 404

    if int(duracion_turno) not in [15, 20, 30, 45, 60]:
        return "Duración de turno inválida", 400

    try:
        inicio = date.fromisoformat(fecha_inicio)
        fin = date.fromisoformat(fecha_hasta)
    except ValueError:
        return "Formato de fecha inválido", 400

    if fin < inicio:
        return "La fecha hasta no puede ser anterior a la fecha de inicio", 400

    agendas_medicos.append({
        "id": len(agendas_medicos) + 1,
        "id_medico": id_medico,
        "consultorio_id": int(consultorio_id),
        "consultorio_numero": consultorio_encontrado["numero"],
        "duracion_turno": int(duracion_turno),
        "fecha_inicio": fecha_inicio,
        "fecha_hasta": fecha_hasta
    })

    return redirect(
        url_for(
            "rutas_admin_medico.medico_perfil",
            id_medico=id_medico
        )
    )
