
from flask import Blueprint, render_template, request, session, redirect, url_for, flash

paciente_routes = Blueprint('rutas_paciente', __name__)

@paciente_routes.route('/turnos-paciente', methods=['GET'])
def mis_turnos():

    # Datos hardcodeados de prueba
    turnos = [
        {
            "id": 1,
            "iniciales": "NC",
            "especialidad": "Especialidad",
            "medico": "Nombre Completo",
            "fecha": "Día - Mes - Año",
            "hora": "15:00",
            "consultorio": "123"
        },
        {
            "id": 2,
            "iniciales": "NC",
            "especialidad": "Especialidad",
            "medico": "Nombre Completo",
            "fecha": "Día - Mes - Año",
            "hora": "15:00",
            "consultorio": "123"
        },
        {
            "id": 3,
            "iniciales": "NC",
            "especialidad": "Especialidad",
            "medico": "Nombre Completo",
            "fecha": "Día - Mes - Año",
            "hora": "15:00",
            "consultorio": "123"
        },
        {
            "id": 4,
            "iniciales": "NC",
            "especialidad": "Especialidad",
            "medico": "Nombre Completo",
            "fecha": "Día - Mes - Año",
            "hora": "15:00",
            "consultorio": "123"
        }
    ]

    return render_template(
        'pacientes/mis_turnos.html',
        turnos=turnos
    )


ESPECIALIDADES = [
    {"id": 1, "nombre": "Cardiología"},
    {"id": 2, "nombre": "Clínica Médica"},
    {"id": 3, "nombre": "Dermatología"},
    {"id": 4, "nombre": "Oftalmología"},
    {"id": 5, "nombre": "Pediatría"},
    {"id": 6, "nombre": "Traumatología"}
]

MEDICOS = [
    {
        "id": 1,
        "nombre": "Nombre Completo",
        "iniciales": "NC",
        "especialidad_id": 1
    },
    {
        "id": 2,
        "nombre": "Nombre Completo",
        "iniciales": "NC",
        "especialidad_id": 1
    },
    {
        "id": 3,
        "nombre": "Nombre Completo",
        "iniciales": "NC",
        "especialidad_id": 2
    },
    {
        "id": 4,
        "nombre": "Nombre Completo",
        "iniciales": "NC",
        "especialidad_id": 3
    },
    {
        "id": 5,
        "nombre": "Nombre Completo",
        "iniciales": "NC",
        "especialidad_id": 4
    },
    {
        "id": 6,
        "nombre": "Nombre Completo",
        "iniciales": "NC",
        "especialidad_id": 5
    },
    {
        "id": 7,
        "nombre": "Nombre Completo",
        "iniciales": "NC",
        "especialidad_id": 6
    }
]

FECHAS = [
    {
        "valor": "2026-11-09",
        "dia_semana": "LUN",
        "dia": 9,
        "mes": "NOVIEMBRE"
    },
    {
        "valor": "2026-11-10",
        "dia_semana": "MAR",
        "dia": 10,
        "mes": "NOVIEMBRE"
    },
    {
        "valor": "2026-11-11",
        "dia_semana": "MIÉ",
        "dia": 11,
        "mes": "NOVIEMBRE"
    },
    {
        "valor": "2026-11-12",
        "dia_semana": "JUE",
        "dia": 12,
        "mes": "NOVIEMBRE"
    }
]

HORARIOS = ["15:30", "16:30", "17:30", "18:30"]



@paciente_routes.route('/sacar-turno', methods=['GET', 'POST'])
def sacar_turno():

    # --------------------------------------
    # INICIAR UN NUEVO PROCESO
    # --------------------------------------

    if request.method == 'GET' and 'paso' not in request.args:
        session.pop('turno_especialidad_id', None)
        session.pop('turno_medico_id', None)
        session.pop('turno_fecha', None)
        session.pop('turno_hora', None)

    paso = request.args.get('paso', 1, type=int)

    # --------------------------------------
    # PROCESAR FORMULARIOS
    # --------------------------------------

    if request.method == 'POST':

        paso = request.form.get('paso', 1, type=int)
        accion = request.form.get('accion')

        # PASO 1: ESPECIALIDAD
        if paso == 1:

            especialidad_id = request.form.get('especialidad_id', type=int)

            especialidad = next(
                (e for e in ESPECIALIDADES if e['id'] == especialidad_id),
                None
            )

            if especialidad is None:
                flash('Seleccioná una especialidad válida.', 'error')
                return redirect(url_for('rutas_paciente.sacar_turno'))

            session['turno_especialidad_id'] = especialidad_id

            # Reiniciar las selecciones posteriores.
            session.pop('turno_medico_id', None)
            session.pop('turno_fecha', None)
            session.pop('turno_hora', None)

            return redirect(url_for('rutas_paciente.sacar_turno', paso=2))

        # PASO 2: MÉDICO
        elif paso == 2:

            # Volver al paso anterior.
            if accion == 'anterior':
                return redirect(url_for('rutas_paciente.sacar_turno', paso=1))

            especialidad_id = session.get('turno_especialidad_id')
            medico_id = request.form.get('medico_id', type=int)

            medico = next(
                (
                    m for m in MEDICOS
                    if m['id'] == medico_id
                    and m['especialidad_id'] == especialidad_id
                ),
                None
            )

            if medico is None:
                flash('Seleccioná un médico válido.', 'error')
                return redirect(url_for('rutas_paciente.sacar_turno', paso=2))

            session['turno_medico_id'] = medico_id

            session.pop('turno_fecha', None)
            session.pop('turno_hora', None)

            return redirect(url_for('rutas_paciente.sacar_turno', paso=3))

        # PASO 3: FECHA Y HORARIO
        elif paso == 3:

            # Volver al paso anterior.
            if accion == 'anterior':
                return redirect(url_for('rutas_paciente.sacar_turno', paso=2))

            if not session.get('turno_medico_id'):
                return redirect(url_for('rutas_paciente.sacar_turno'))

            fecha = request.form.get('fecha')
            hora = request.form.get('hora')

            fecha_valida = any(
                f['valor'] == fecha for f in FECHAS
            )

            horario_valido = hora in HORARIOS

            if not fecha_valida or not horario_valido:
                flash('Seleccioná una fecha y un horario válidos.', 'error')
                return redirect(url_for('rutas_paciente.sacar_turno', paso=3))

            session['turno_fecha'] = fecha
            session['turno_hora'] = hora

            return redirect(url_for('rutas_paciente.sacar_turno', paso=4))

        # PASO 4: CONFIRMAR TURNO
        elif paso == 4:

            # Verificar que estén completas todas las selecciones.
            if not all([
                session.get('turno_especialidad_id'),
                session.get('turno_medico_id'),
                session.get('turno_fecha'),
                session.get('turno_hora')
            ]):
                return redirect(url_for('rutas_paciente.sacar_turno'))

            # Volver al paso anterior.
            if accion == 'anterior':
                return redirect(url_for('rutas_paciente.sacar_turno', paso=3))

            # Confirmar turno.
            elif accion == 'confirmar':

                # Por ahora no se guarda en la base de datos.
                session['turno_reservado'] = True

                session.pop('turno_especialidad_id', None)
                session.pop('turno_medico_id', None)
                session.pop('turno_fecha', None)
                session.pop('turno_hora', None)

                return redirect(url_for('rutas_home.home'))

    # --------------------------------------
    # RECUPERAR DATOS DE LA SESIÓN
    # --------------------------------------

    especialidad_id = session.get('turno_especialidad_id')
    medico_id = session.get('turno_medico_id')
    fecha_seleccionada = session.get('turno_fecha')
    hora_seleccionada = session.get('turno_hora')

    especialidad = next(
        (e for e in ESPECIALIDADES if e['id'] == especialidad_id),
        None
    )

    medico = next(
        (m for m in MEDICOS if m['id'] == medico_id),
        None
    )

    fecha_objeto = next(
        (f for f in FECHAS if f['valor'] == fecha_seleccionada),
        None
    )

    # --------------------------------------
    # MOSTRAR LOS TEMPLATES
    # --------------------------------------

    # PASO 1: ESPECIALIDAD
    if paso == 1:

        return render_template(
            'pacientes/pasos_turno/especialidad.html',
            paso=1,
            especialidades=ESPECIALIDADES
        )

    # PASO 2: MÉDICO
    elif paso == 2:

        if especialidad is None:
            return redirect(url_for('rutas_paciente.sacar_turno'))

        medicos_disponibles = [
            m for m in MEDICOS
            if m['especialidad_id'] == especialidad_id
        ]

        return render_template(
            'pacientes/pasos_turno/medico.html',
            paso=2,
            especialidad=especialidad,
            medicos=medicos_disponibles,
            medico_seleccionado=medico_id
        )
    # PASO 3: FECHA Y HORARIO
    elif paso == 3:

        if especialidad is None or medico is None:
            return redirect(url_for('rutas_paciente.sacar_turno'))

        return render_template(
            'pacientes/pasos_turno/fecha.html',
            paso=3,
            especialidad=especialidad,
            medico=medico,
            fechas=FECHAS,
            horarios=HORARIOS,
            fecha_seleccionada=fecha_seleccionada,
            hora_seleccionada=hora_seleccionada
        )

    # PASO 4: CONFIRMACIÓN
    elif paso == 4:

        if not all([
            especialidad,
            medico,
            fecha_seleccionada,
            hora_seleccionada
        ]):
            return redirect(url_for('rutas_paciente.sacar_turno'))

        fecha_texto = None

        if fecha_objeto:
            fecha_texto = (
                f"{fecha_objeto['dia_semana']} "
                f"{fecha_objeto['dia']} DE "
                f"{fecha_objeto['mes']}"
            )

        return render_template(
            'pacientes/pasos_turno/confirmacion.html',
            paso=4,
            especialidad=especialidad,
            medico=medico,
            fecha=fecha_seleccionada,
            fecha_texto=fecha_texto,
            hora=hora_seleccionada
        )

    # Número de paso inválido.
    return redirect(url_for('rutas_home.sacar_turno'))

