import base64
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

from src.config import Config
from src.errores import error_respuesta
from src.repositories.agendas_repositories import buscar_agendas
from src.repositories.turnos_repositories import (
    buscar_datos_turno_comprobante,
    buscar_turno_para_cancelar,
    buscar_turno_por_codigo_qr,
    buscar_turno_por_id,
    buscar_turno_y_estado_destino,
    buscar_turnos,
    buscar_turnos_disponibles,
    confirmar_checkin,
    guardar_estado_turno,
    insertar_turnos_disponibles,
    reservar_turno as reservar_turno_repositorio,
    cancelar_turno as cancelar_turno_repositorio,
)
from src.services.pacientes_services import (
    obtener_id_paciente_por_usuario,
    obtener_id_usuario_por_paciente,
)
from src.services.smtp_service import enviar_comprobante_turno
from src.utils.qr_utils import decodificar_payload_qr, generar_qr_para_turno
from src.utils.roles import PACIENTE, MEDICO
from src.utils.tokens import validar_token_cancelacion_turno
from src.validators.turnos_validators import (
    validar_filtros_turnos,
    validar_filtros_turnos_disponibles,
    validar_reserva_turno,
)


def _ahora_local():
    return datetime.now(ZoneInfo(Config.TIMEZONE)).replace(tzinfo=None)


def _respuesta_llegada_registrada(turno):
    return {
        'mensaje': 'Llegada ya registrada',
        'id_turno': int(turno['id_turno']),
        'estado': 'confirmado',
        'fecha_horario_llegada': turno['fecha_horario_llegada'],
    }, 200


def actualizar_estado_turno(id_turno, id_estado):
    turno = buscar_turno_y_estado_destino(id_turno, id_estado)
    if turno is None:
        return error_respuesta('El turno no existe', 'TURNO_INEXISTENTE'), 404

    destino = turno['estado_destino']
    if destino not in ('atendido', 'ausente'):
        return error_respuesta(
            'El estado solicitado debe ser atendido o ausente',
            'ESTADO_TURNO_INVALIDO',
        ), 400

    estado_actualizado = {
        'id_turno': id_turno,
        'id_estado': id_estado,
        'estado': destino,
    }
    if turno['id_estado'] == id_estado:
        return {'mensaje': 'El turno ya tiene ese estado', **estado_actualizado}, 200

    estado_requerido = 'confirmado' if destino == 'atendido' else 'reservado'
    if turno['estado_actual'] != estado_requerido or turno['id_paciente'] is None:
        return error_respuesta(
            f'El turno debe estar {estado_requerido} y tener un paciente asignado',
            'TRANSICION_ESTADO_INVALIDA',
        ), 400

    if destino == 'ausente':
        fin_tolerancia = turno['fecha_horario_inicial'] + timedelta(minutes=15)
        if turno['fecha_horario_llegada'] is not None or _ahora_local() <= fin_tolerancia:
            return error_respuesta(
                'Solo se puede marcar ausente a un paciente sin llegada registrada y fuera de la tolerancia',
                'TRANSICION_ESTADO_INVALIDA',
            ), 400

    if not guardar_estado_turno(id_turno, id_estado, turno):
        return error_respuesta(
            'El turno cambió durante la operación. Volvé a consultar su estado',
            'TURNO_MODIFICADO',
        ), 409

    return {'mensaje': 'Estado del turno actualizado correctamente', **estado_actualizado}, 200


def reservar_turno_solicitado(id_turno, datos, usuario_actual):
    if datos is None:
        datos = {}

    es_paciente = usuario_actual['id_rol'] == PACIENTE
    id_paciente, error = validar_reserva_turno(
        datos,
        requiere_id_paciente=not es_paciente,
    )
    if error:
        return error

    if es_paciente:
        id_paciente = obtener_id_paciente_por_usuario(usuario_actual['id_usuario'])
        if id_paciente is None:
            return error_respuesta('El paciente autenticado no existe', 'PACIENTE_INEXISTENTE'), 404

    return reservar_turno(id_turno, id_paciente)


def reservar_turno(id_turno, id_paciente):
    turno = buscar_turno_por_id(id_turno)
    if turno is None:
        return error_respuesta('El turno no existe', 'TURNO_INEXISTENTE'), 404
    if turno['id_paciente'] is not None or turno['estado_turno'] != 'disponible':
        return error_respuesta('El turno ya no está disponible', 'TURNO_NO_DISPONIBLE'), 409

    qr = generar_qr_para_turno({
        'id_turno': turno['id_turno'],
        'id_agenda': turno['id_agenda'],
        'id_paciente': id_paciente,
        'fecha_horario_inicial': turno['fecha_horario_inicial'],
    }, estado='reservado', formato='png')

    resultado = reservar_turno_repositorio(id_turno, id_paciente, qr['codigo_qr'])
    if resultado is None:
        return error_respuesta('El turno no existe', 'TURNO_INEXISTENTE'), 404
    if resultado['resultado'] == 'NO_DISPONIBLE':
        return error_respuesta('El turno ya no está disponible', 'TURNO_NO_DISPONIBLE'), 409

    datos_turno = buscar_datos_turno_comprobante(id_turno)
    paciente = None
    if datos_turno is not None and datos_turno.get('correo_electronico'):
        paciente = {
            'id_paciente': int(id_paciente),
            'nombre': datos_turno.get('nombre_paciente'),
            'apellido': datos_turno.get('apellido_paciente'),
            'correo_electronico': datos_turno.get('correo_electronico'),
        }

    email_result = enviar_comprobante_turno(
        {
            'id_turno': id_turno,
            'fecha_horario_inicial': turno['fecha_horario_inicial'],
            'medico': {
                'nombre': datos_turno.get('nombre_medico') if datos_turno else None,
                'apellido': datos_turno.get('apellido_medico') if datos_turno else None,
                'especialidad': datos_turno.get('nombre_especialidad') if datos_turno else None,
            },
            'consultorio': {
                'numero': datos_turno.get('numero_consultorio') if datos_turno else None,
                'piso': datos_turno.get('piso_consultorio') if datos_turno else None,
            },
        },
        paciente,
        qr['imagen_bytes'],
        qr['mime_type'],
    )

    respuesta = {
        'mensaje': 'Turno reservado correctamente',
        'turno': {
            'id_turno': id_turno,
            'id_paciente': id_paciente,
            'estado': 'reservado',
            'codigo_qr': qr['codigo_qr'],
        },
        'qr': {
            'codigo_qr': qr['codigo_qr'],
            'mime_type': qr['mime_type'],
            'imagen_base64': base64.b64encode(qr['imagen_bytes']).decode('ascii'),
        },
    }

    if email_result.get('enviado') is False:
        respuesta['email'] = {
            'enviado': False,
            'motivo': email_result.get('motivo', 'ERROR_ENVIO'),
            'error': email_result.get('error'),
        }
    else:
        respuesta['email'] = {'enviado': True, 'destinatario': email_result.get('destinatario')}

    return respuesta, 200


def registrar_checkin_por_qr(token):
    try:
        payload = decodificar_payload_qr(token)
    except ValueError as exc:
        return error_respuesta(str(exc), 'QR_INVALIDO'), 400

    turno = buscar_turno_por_codigo_qr(token)
    if turno is None:
        return error_respuesta('El código QR no pertenece a un turno válido', 'QR_INEXISTENTE'), 404
    if turno['estado_turno'] == 'confirmado':
        return _respuesta_llegada_registrada(turno)
    if turno['estado_turno'] != 'reservado':
        return error_respuesta('El turno ya no está en estado reservado', 'TURNO_NO_RESERVADO'), 409

    id_turno = int(turno['id_turno'])
    if int(payload.get('id_turno', -1)) != id_turno:
        return error_respuesta('El QR no coincide con el turno asociado', 'QR_INVALIDO'), 400

    fecha_turno = datetime.fromisoformat(turno['fecha_horario_inicial'])
    ahora = _ahora_local()
    inicio_valido = fecha_turno - timedelta(minutes=30)
    fin_valido = fecha_turno + timedelta(minutes=15)

    if not (inicio_valido <= ahora <= fin_valido):
        return error_respuesta('El check-in está fuera del rango permitido', 'QR_EXPIRADO'), 409

    actualizado = confirmar_checkin(id_turno, ahora.strftime('%Y-%m-%d %H:%M:%S'))
    if not actualizado:
        turno_actual = buscar_turno_por_codigo_qr(token)
        if turno_actual is not None and turno_actual['estado_turno'] == 'confirmado':
            return _respuesta_llegada_registrada(turno_actual)
        return error_respuesta('No fue posible confirmar el check-in del turno', 'CHECKIN_NO_ACTUALIZADO'), 500

    return {
        'mensaje': 'Check-in registrado correctamente',
        'id_turno': id_turno,
        'estado': 'confirmado',
        'fecha_horario_llegada': ahora.strftime('%Y-%m-%d %H:%M:%S'),
    }, 200


def cancelar_turno(id_turno, usuario_actual):
    turno = buscar_turno_para_cancelar(id_turno)
    if turno is None:
        return error_respuesta('El turno no existe', 'TURNO_INEXISTENTE'), 404
    if turno['estado_turno'] != 'reservado':
        return error_respuesta(
            'El turno no se encuentra reservado',
            'TURNO_NO_CANCELABLE',
        ), 409

    if usuario_actual['id_rol'] == PACIENTE:
        if turno['id_usuario_paciente'] != usuario_actual['id_usuario']:
            return error_respuesta(
                'El turno no pertenece al paciente autenticado',
                'TURNO_NO_AUTORIZADO',
            ), 403

        fecha_turno = datetime.fromisoformat(turno['fecha_horario_inicial'])
        limite_cancelacion = fecha_turno - timedelta(hours=24)
        if _ahora_local() > limite_cancelacion:
            return error_respuesta(
                'La cancelación solo está disponible hasta 24 horas antes del turno; comuníquese con recepción',
                'CANCELACION_FUERA_DE_PLAZO',
            ), 409

    resultado = cancelar_turno_repositorio(id_turno)
    if resultado['resultado'] == 'NO_CANCELABLE':
        return error_respuesta(
            'El turno no se encuentra reservado',
            'TURNO_NO_CANCELABLE',
        ), 409
    return {
        'mensaje': 'Turno cancelado correctamente',
        'id_turno': resultado['id_turno'],
        'estado': 'cancelado',
        'disponible': True,
    }, 200


def cancelar_turno_por_token(id_turno, token):
    try:
        payload = validar_token_cancelacion_turno(token)
    except ValueError as exc:
        return error_respuesta(str(exc), 'TOKEN_INVALIDO'), 400

    if int(payload.get('id_turno')) != id_turno:
        return error_respuesta('El token no corresponde a este turno', 'TOKEN_INVALIDO'), 400

    id_paciente = int(payload.get('id_paciente'))
    id_usuario = obtener_id_usuario_por_paciente(id_paciente)
    if id_usuario is None:
        return error_respuesta('El paciente asociado a este enlace ya no existe', 'PACIENTE_INEXISTENTE'), 404

    return cancelar_turno(id_turno, {'id_usuario': id_usuario, 'id_rol': PACIENTE})


def filtrar_turnos_disponibles(parametros):
    filtros, error = validar_filtros_turnos_disponibles(parametros)
    if error:
        return error, 400
    return {'turnos': buscar_turnos_disponibles(**filtros)}, 200


def _filtros_visibilidad_turnos(usuario_actual):
    if usuario_actual['id_rol'] == PACIENTE:
        return {'id_usuario_paciente': usuario_actual['id_usuario']}
    if usuario_actual['id_rol'] == MEDICO:
        return {'id_usuario_medico': usuario_actual['id_usuario']}
    return {}


def filtrar_turnos(parametros, usuario_actual):
    filtros, error = validar_filtros_turnos(parametros)
    if error:
        return error, 400

    turnos = buscar_turnos(**filtros, **_filtros_visibilidad_turnos(usuario_actual))
    return {'turnos': turnos}, 200


def obtener_detalle_turno(id_turno, usuario_actual):
    turnos = buscar_turnos(id_turno=id_turno, **_filtros_visibilidad_turnos(usuario_actual))
    if not turnos:
        return error_respuesta('El turno no existe', 'TURNO_INEXISTENTE'), 404

    return {'turno': turnos[0]}, 200


def _obtener_periodo_proximo_mes(hoy=None):
    hoy = hoy or _ahora_local().date()

    fecha_desde = (hoy.replace(day=28) + timedelta(days=4)).replace(day=1)
    primer_dia_mes_siguiente = (fecha_desde.replace(day=28) + timedelta(days=4)).replace(day=1)

    fecha_hasta = primer_dia_mes_siguiente - timedelta(days=1)

    return fecha_desde, fecha_hasta


def generar_disponibilidad():
    hoy = _ahora_local().date()
    if hoy.day < 15:
        return error_respuesta(
            'La apertura de agendas se habilita a partir del día 15 de cada mes',
            'APERTURA_AGENDA_NO_HABILITADA',
        ), 409

    fecha_desde, fecha_hasta = _obtener_periodo_proximo_mes(hoy)

    agendas = buscar_agendas()
    turnos_a_generar = []
    agendas_procesadas = 0

    for agenda in agendas:
        inicio_agenda = date.fromisoformat(agenda['fecha_inicio'])
        fin_agenda = date.fromisoformat(agenda['fecha_hasta'])
        inicio_periodo = max(fecha_desde, inicio_agenda)
        fin_periodo = min(fecha_hasta, fin_agenda)

        if inicio_periodo > fin_periodo:
            continue

        agendas_procesadas += 1
        duracion_turno = agenda['duracion_turno']

        for dia in agenda['dias']:
            dia_semana = dia['dia_semana']

            hora_inicio = time.fromisoformat(dia['horario_inicio_jornada'])
            hora_fin = time.fromisoformat(dia['horario_final_jornada'])

            fecha_actual = inicio_periodo

            while fecha_actual <= fin_periodo:
                if fecha_actual.isoweekday() == dia_semana:
                    inicio_turno = datetime.combine(fecha_actual, hora_inicio)

                    fin_jornada = datetime.combine(fecha_actual, hora_fin)
                    while(inicio_turno + timedelta(minutes=duracion_turno) <= fin_jornada):
                        turnos_a_generar.append({
                            'id_agenda': agenda['id_agenda'],
                            'fecha_horario_inicial': inicio_turno,
                        })

                        inicio_turno += timedelta(minutes=duracion_turno)
                fecha_actual += timedelta(days=1)

    cantidad_generada = insertar_turnos_disponibles(turnos_a_generar)

    return{
        'mensaje': 'Disponibilidad generada correctamente',
        'periodo': {
            'fecha_desde': fecha_desde.isoformat(),
            'fecha_hasta': fecha_hasta.isoformat(),
        },
        'agendas_procesadas': agendas_procesadas,
        'turnos_generados': cantidad_generada,
        'turnos_omitidos': len(turnos_a_generar) - cantidad_generada,
    }, 200
