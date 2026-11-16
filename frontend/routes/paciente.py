from flask import (
    Blueprint, render_template, request, session, redirect, url_for, flash
)

from src.api import ErrorAPI, api
from src.api_paciente import (
    ESTADOS_TURNO, id_paciente_actual, medicos_por_especialidad,
    mis_turnos_paciente, obtener_especialidades, turnos_disponibles,
)

paciente_routes = Blueprint('rutas_paciente', __name__)

CLAVES_TURNO = ('turno_especialidad_id', 'turno_medico', 'turno_fecha', 'turno_hora')


def _limpiar(*claves):
    for c in claves:
        session.pop(c, None)


def _error_api(e):
    """401 -> sesión vencida; el resto se muestra como mensaje."""
    if e.status == 401:
        session.clear()
        flash('Tu sesión expiró. Iniciá sesión de nuevo.', 'error')
        return redirect(url_for('rutas_auth.login'))
    flash(e.mensaje, 'error')
    return None


# ---------------- MIS TURNOS ----------------

@paciente_routes.route('/turnos-paciente', methods=['GET'])
def mis_turnos():
    if 'access_token' not in session:
        return redirect(url_for('rutas_auth.login'))
    try:
        turnos = mis_turnos_paciente()
        especialidades = obtener_especialidades()
    except ErrorAPI as e:
        return _error_api(e) or redirect(url_for('rutas_home.home'))

    return render_template(
        'pacientes/mis_turnos.html',
        turnos=turnos,
        especialidades=especialidades,
        estados=ESTADOS_TURNO,
    )


@paciente_routes.route('/turnos-paciente/<int:id_turno>/cancelar', methods=['POST'])
def cancelar_turno(id_turno):
    if 'access_token' not in session:
        return redirect(url_for('rutas_auth.login'))

    try:
        api('POST', '/turnos/cancelar', json={'id_turno': id_turno})
        flash('Turno cancelado correctamente.', 'success')
    except ErrorAPI as e:
        resp = _error_api(e)   # 409 = fuera del plazo de 24 hs o ya no reservado
        if resp:
            return resp

    return redirect(request.referrer or url_for('rutas_paciente.mis_turnos'))


# ---------------- SACAR TURNO ----------------

@paciente_routes.route('/sacar-turno', methods=['GET', 'POST'])
def sacar_turno():
    if 'access_token' not in session:
        return redirect(url_for('rutas_auth.login'))

    if request.method == 'GET' and 'paso' not in request.args:
        _limpiar(*CLAVES_TURNO)

    paso = request.args.get('paso', 1, type=int)
    especialidad_id = session.get('turno_especialidad_id')
    medico = session.get('turno_medico')
    fecha_sel = session.get('turno_fecha')
    hora_sel = session.get('turno_hora')

    try:
        # La especialidad elegida se resuelve una sola vez para todos los pasos.
        especialidad = next(
            (e for e in obtener_especialidades() if e['id'] == especialidad_id), None)

        # ---------- POST ----------
        if request.method == 'POST':
            paso = request.form.get('paso', 1, type=int)
            accion = request.form.get('accion')

            if paso == 1:
                esp_id = request.form.get('especialidad_id', type=int)
                if esp_id not in [e['id'] for e in obtener_especialidades()]:
                    flash('Seleccioná una especialidad válida.', 'error')
                    return redirect(url_for('rutas_paciente.sacar_turno'))
                session['turno_especialidad_id'] = esp_id
                _limpiar('turno_medico', 'turno_fecha', 'turno_hora')
                return redirect(url_for('rutas_paciente.sacar_turno', paso=2))

            if paso == 2:
                if accion == 'anterior':
                    return redirect(url_for('rutas_paciente.sacar_turno', paso=1))
                medico_id = request.form.get('medico_id', type=int)
                elegido = next(
                    (m for m in medicos_por_especialidad(especialidad_id)
                     if m['id'] == medico_id), None)
                if elegido is None:
                    flash('Seleccioná un médico válido.', 'error')
                    return redirect(url_for('rutas_paciente.sacar_turno', paso=2))
                session['turno_medico'] = elegido
                _limpiar('turno_fecha', 'turno_hora')
                return redirect(url_for('rutas_paciente.sacar_turno', paso=3))

            if paso == 3:
                if accion == 'anterior':
                    return redirect(url_for('rutas_paciente.sacar_turno', paso=2))
                if not medico:
                    return redirect(url_for('rutas_paciente.sacar_turno'))
                fecha = request.form.get('fecha')
                hora = request.form.get('hora')
                existe = any(
                    t['fecha_iso'] == fecha and t['hora'] == hora
                    for t in turnos_disponibles(id_medico=medico['id'])
                )
                if not existe:
                    flash('Ese horario no está disponible para esa fecha.', 'error')
                    return redirect(url_for('rutas_paciente.sacar_turno', paso=3))
                session['turno_fecha'] = fecha
                session['turno_hora'] = hora
                return redirect(url_for('rutas_paciente.sacar_turno', paso=4))

            if paso == 4:
                if not all([especialidad_id, medico, fecha_sel, hora_sel]):
                    return redirect(url_for('rutas_paciente.sacar_turno'))
                if accion == 'anterior':
                    return redirect(url_for('rutas_paciente.sacar_turno', paso=3))
                if accion == 'confirmar':
                    # Se vuelve a buscar el turno: el id_turno no se guarda
                    # en sesión porque pudo ocuparse mientras el paciente elegía.
                    turno = next((
                        t for t in turnos_disponibles(id_medico=medico['id'])
                        if t['fecha_iso'] == fecha_sel and t['hora'] == hora_sel
                    ), None)
                    if turno is None:
                        flash('Ese turno ya no está disponible. Elegí otro horario.', 'error')
                        return redirect(url_for('rutas_paciente.sacar_turno', paso=3))
                    try:
                        respuesta = api(
                            'POST',
                            f"/turnos/{turno['id']}/reservar",
                            json={'id_paciente': id_paciente_actual()},
                        )
                    except ErrorAPI as e:
                        if e.status == 409:
                            flash('Alguien reservó ese turno antes. Elegí otro.', 'error')
                            return redirect(url_for('rutas_paciente.sacar_turno', paso=3))
                        raise

                    _limpiar(*CLAVES_TURNO)
                    session['turno_reservado'] = True

                    qr = respuesta.get('qr') or {}
                    email = respuesta.get('email') or {}

                    return render_template(
                        'pacientes/pasos_turno/reservado.html',
                        especialidad=especialidad,
                        medico=medico,
                        fecha=fecha_sel,
                        fecha_texto=turno.get('fecha', fecha_sel),
                        hora=hora_sel,
                        consultorio=turno.get('consultorio'),
                        turno=respuesta.get('turno') or {},
                        qr_imagen=qr.get('imagen_base64'),
                        qr_mime=qr.get('mime_type') or 'image/png',
                        email_enviado=bool(email.get('enviado')),
                        email_destinatario=email.get('destinatario'),
                        email_error=email.get('error') or email.get('motivo'),
                    )

        # ---------- GET ----------
        if paso == 1:
            return render_template(
                'pacientes/pasos_turno/especialidad.html',
                paso=1, especialidades=obtener_especialidades())

        if paso == 2:
            if especialidad is None:
                return redirect(url_for('rutas_paciente.sacar_turno'))
            return render_template(
                'pacientes/pasos_turno/medico.html',
                paso=2, especialidad=especialidad,
                medicos=medicos_por_especialidad(especialidad_id),
                medico_seleccionado=medico['id'] if medico else None)

        if paso == 3:
            if especialidad is None or medico is None:
                return redirect(url_for('rutas_paciente.sacar_turno'))
            libres = turnos_disponibles(id_medico=medico['id'])
            fechas, por_fecha = [], {}
            for t in libres:
                if t['fecha_iso'] not in por_fecha:
                    por_fecha[t['fecha_iso']] = []
                    fechas.append({'valor': t['fecha_iso'], 'dia_semana': t['dia_semana'],
                                   'dia': t['dia'], 'mes': t['mes']})
                por_fecha[t['fecha_iso']].append(t['hora'])
            horarios = sorted({h for hs in por_fecha.values() for h in hs})
            duracion = next((t['duracion'] for t in libres if t.get('duracion')), None)
            return render_template(
                'pacientes/pasos_turno/fecha.html',
                paso=3, especialidad=especialidad, medico=medico,
                fechas=fechas, horarios=horarios,
                horarios_por_fecha=por_fecha,
                duracion=duracion,
                fecha_seleccionada=fecha_sel, hora_seleccionada=hora_sel)

        if paso == 4:
            if not all([especialidad, medico, fecha_sel, hora_sel]):
                return redirect(url_for('rutas_paciente.sacar_turno'))
            f = next((t for t in turnos_disponibles(id_medico=medico['id'])
                      if t['fecha_iso'] == fecha_sel), None)
            fecha_texto = f"{f['dia_semana']} {f['dia']} DE {f['mes']}" if f else fecha_sel
            return render_template(
                'pacientes/pasos_turno/confirmacion.html',
                paso=4, especialidad=especialidad, medico=medico,
                fecha=fecha_sel, fecha_texto=fecha_texto, hora=hora_sel)

        return redirect(url_for('rutas_paciente.sacar_turno'))  # paso inválido (corregido el BuildError)

    except ErrorAPI as e:
        return _error_api(e) or redirect(url_for('rutas_paciente.sacar_turno'))