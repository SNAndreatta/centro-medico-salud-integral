import calendar
from datetime import date, datetime

from flask import (
    Blueprint, render_template, request, session, redirect, url_for, flash
)

from src.api import ErrorAPI
from src.api_catalogos import medicos_por_especialidad, obtener_especialidades
from src.api_paciente import cobertura_paciente, id_paciente_actual
from src.api_turnos import (
    cancelar_turno as api_cancelar_turno,
    mis_turnos_paciente,
    obtener_agendas,
    reservar_turno,
)
from src.api_turnos import disponibles as turnos_disponibles
from src.errores import atender_error
from src.normalizar import ESTADOS_TURNO
from src.permisos import requiere_rol
from src.tiempo import ahora_local, hoy_local

paciente_routes = Blueprint('rutas_paciente', __name__)

CLAVES_TURNO = ('turno_especialidad_id', 'turno_medico', 'turno_fecha', 'turno_hora')

MESES_CALENDARIO = [
    (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
    (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
    (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'),
]
DIAS_SEMANA_CALENDARIO = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']


def _limpiar(*claves):
    for c in claves:
        session.pop(c, None)


def _contexto_calendario(medico, anio, mes, fecha_sel=None, hora_sel=None):
    """Datos para la agenda mensual del paso 3."""
    hoy = hoy_local()
    ahora = ahora_local()

    agendas = obtener_agendas(id_medico=medico['id'])

    rangos = []
    consultorio = None
    duracion = None
    for agenda in agendas:
        try:
            inicio = date.fromisoformat(agenda['fecha_inicio'])
            fin = date.fromisoformat(agenda['fecha_hasta'])
        except (KeyError, TypeError, ValueError):
            continue

        dias = {
            d['dia_semana'] for d in agenda.get('dias', [])
            if d.get('dia_semana')
        }
        rangos.append((inicio, fin, dias))

        if consultorio is None:
            c = agenda.get('consultorio') or {}
            consultorio = c.get('numero') if isinstance(c, dict) else None
        if duracion is None:
            duracion = agenda.get('duracion_turno')

    # Turnos libres futuros del médico.
    libres = []
    for t in turnos_disponibles(id_medico=medico['id']):
        try:
            momento = datetime.fromisoformat(f"{t['fecha_iso']}T{t['hora']}")
        except (TypeError, ValueError):
            continue
        if momento > ahora:
            libres.append(t)

    por_fecha = {}
    for t in libres:
        por_fecha.setdefault(t['fecha_iso'], set()).add(t['hora'])

    # Mes por defecto: el del primer turno libre; si no hay, el mes actual.
    if anio is None or mes is None or not 1 <= mes <= 12:
        referencia = (
            date.fromisoformat(min(por_fecha)) if por_fecha else hoy
        )
        anio, mes = referencia.year, referencia.month

    primer_dia = date(anio, mes, 1)
    cantidad_dias = calendar.monthrange(anio, mes)[1]

    dias_mes = []
    for numero in range(1, cantidad_dias + 1):
        fecha = date(anio, mes, numero)
        iso = fecha.isoformat()
        horas = sorted(por_fecha.get(iso, set()))

        atiende = any(
            inicio <= fecha <= fin and fecha.isoweekday() in dias_semana
            for inicio, fin, dias_semana in rangos
        )

        if fecha < hoy:
            estado = 'pasado'
        elif horas:
            estado = 'disponible'
        elif atiende:
            estado = 'sin_turnos'
        else:
            estado = 'cerrado'

        dias_mes.append({
            'fecha': iso,
            'numero': numero,
            'dia_semana': fecha.weekday(),
            'libres': len(horas),
            'estado': estado,
        })

    hay_disponibles = any(d['estado'] == 'disponible' for d in dias_mes)

    # Sólo los horarios del mes visible viajan al navegador.
    prefijo = f"{anio:04d}-{mes:02d}-"
    horarios_mes = {
        f: sorted(horas) for f, horas in por_fecha.items()
        if f.startswith(prefijo)
    }

    if mes == 1:
        anio_anterior, mes_anterior = anio - 1, 12
    else:
        anio_anterior, mes_anterior = anio, mes - 1

    if mes == 12:
        anio_siguiente, mes_siguiente = anio + 1, 1
    else:
        anio_siguiente, mes_siguiente = anio, mes + 1

    anios = sorted({
        hoy.year, anio,
        *(inicio.year for inicio, _, _ in rangos),
        *(fin.year for _, fin, _ in rangos),
    })

    return {
        'dias': dias_mes,
        'dias_semana': DIAS_SEMANA_CALENDARIO,
        'offset_inicio': primer_dia.weekday(),
        'mes': mes,
        'anio': anio,
        'nombre_mes': dict(MESES_CALENDARIO)[mes],
        'meses': MESES_CALENDARIO,
        'anios': anios,
        'mes_anterior': mes_anterior,
        'anio_anterior': anio_anterior,
        'mes_siguiente': mes_siguiente,
        'anio_siguiente': anio_siguiente,
        'horarios_por_fecha': horarios_mes,
        'hay_disponibles': hay_disponibles,
        'duracion': duracion,
        'consultorio': consultorio,
        'fecha_seleccionada': fecha_sel,
        'hora_seleccionada': hora_sel,
    }


# ---------------- MIS TURNOS ----------------

@paciente_routes.route('/turnos-paciente', methods=['GET'])
@requiere_rol("paciente")
def mis_turnos():
    if 'access_token' not in session:
        return redirect(url_for('rutas_auth.login'))
    try:
        turnos = mis_turnos_paciente()
        especialidades = obtener_especialidades()
    except ErrorAPI as e:
        return atender_error(e) or redirect(url_for('rutas_home.home'))

    return render_template(
        'pacientes/mis_turnos.html',
        turnos=turnos,
        especialidades=especialidades,
        estados=ESTADOS_TURNO,
    )


@paciente_routes.route('/turnos-paciente/<int:id_turno>/cancelar', methods=['POST'])
@requiere_rol("paciente")
def cancelar_turno(id_turno):
    if 'access_token' not in session:
        return redirect(url_for('rutas_auth.login'))

    try:
        api_cancelar_turno(id_turno)
        flash('Turno cancelado correctamente.', 'success')
    except ErrorAPI as e:
        resp = atender_error(e)   # 409 = fuera del plazo de 24 hs o ya no reservado
        if resp:
            return resp

    return redirect(request.referrer or url_for('rutas_paciente.mis_turnos'))


# ---------------- SACAR TURNO ----------------

@paciente_routes.route('/sacar-turno', methods=['GET', 'POST'])
@requiere_rol("paciente")
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
                cobertura = cobertura_paciente()
                elegido = next(
                    (m for m in medicos_por_especialidad(
                        especialidad_id, cobertura['id'])
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
                fecha = (request.form.get('fecha') or '').strip()
                hora = (request.form.get('hora') or '').strip()

                try:
                    date.fromisoformat(fecha)
                except ValueError:
                    fecha = None

                existe = bool(fecha and hora) and any(
                    t['hora'] == hora
                    for t in turnos_disponibles(
                        id_medico=medico['id'],
                        fecha_desde=fecha,
                        fecha_hasta=fecha,
                    )
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
                        t for t in turnos_disponibles(
                            id_medico=medico['id'],
                            fecha_desde=fecha_sel,
                            fecha_hasta=fecha_sel,
                        )
                        if t['hora'] == hora_sel
                    ), None)
                    if turno is None:
                        flash('Ese turno ya no está disponible. Elegí otro horario.', 'error')
                        return redirect(url_for('rutas_paciente.sacar_turno', paso=3))
                    try:
                        respuesta = reservar_turno(
                            turno['id'],
                            {'id_paciente': id_paciente_actual()},
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

            cobertura = cobertura_paciente()
            return render_template(
                'pacientes/pasos_turno/medico.html',
                paso=2, especialidad=especialidad,
                medicos=medicos_por_especialidad(
                    especialidad_id, cobertura['id']),
                cobertura=cobertura,
                medico_seleccionado=medico['id'] if medico else None)

        if paso == 3:
            if especialidad is None or medico is None:
                return redirect(url_for('rutas_paciente.sacar_turno'))

            contexto = _contexto_calendario(
                medico,
                request.args.get('anio', type=int),
                request.args.get('mes', type=int),
                fecha_sel,
                hora_sel,
            )
            return render_template(
                'pacientes/pasos_turno/fecha.html',
                paso=3, especialidad=especialidad, medico=medico,
                **contexto)

        if paso == 4:
            if not all([especialidad, medico, fecha_sel, hora_sel]):
                return redirect(url_for('rutas_paciente.sacar_turno'))
            f = next((
                t for t in turnos_disponibles(
                    id_medico=medico['id'],
                    fecha_desde=fecha_sel,
                    fecha_hasta=fecha_sel,
                )
                if t['hora'] == hora_sel
            ), None)
            fecha_texto = f"{f['dia_semana']} {f['dia']} DE {f['mes']}" if f else fecha_sel
            return render_template(
                'pacientes/pasos_turno/confirmacion.html',
                paso=4, especialidad=especialidad, medico=medico,
                fecha=fecha_sel, fecha_texto=fecha_texto, hora=hora_sel)

        return redirect(url_for('rutas_paciente.sacar_turno'))  # paso inválido (corregido el BuildError)

    except ErrorAPI as e:
        return atender_error(e) or redirect(url_for('rutas_paciente.sacar_turno'))