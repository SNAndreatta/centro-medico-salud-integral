from datetime import datetime, timedelta

from src.db import obtener_cursor
from src.utils.fechas import ahora_local as _ahora_local


def intentar_adquirir_ejecucion_tarea(nombre, ahora, intervalo_segundos):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            INSERT IGNORE INTO control_tarea_programada (nombre, ultima_ejecucion)
            VALUES (%s, %s)
            """,
            (nombre, datetime(1970, 1, 1)),
        )
        cursor.execute(
            """
            SELECT ultima_ejecucion
            FROM control_tarea_programada
            WHERE nombre = %s
            FOR UPDATE
            """,
            (nombre,),
        )
        fila = cursor.fetchone()
        ultima_ejecucion = fila['ultima_ejecucion']

        if ahora - ultima_ejecucion < timedelta(seconds=intervalo_segundos):
            conexion.commit()
            return False

        cursor.execute(
            """
            UPDATE control_tarea_programada
            SET ultima_ejecucion = %s
            WHERE nombre = %s
            """,
            (ahora, nombre),
        )
        conexion.commit()
        return True
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def buscar_turno_por_id(id_turno):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
                SELECT
                    t.id_turno,
                    t.id_agenda,
                    t.id_paciente,
                    t.id_estado,
                    LOWER(et.estado_turno) AS estado_turno,
                    DATE_FORMAT(t.fecha_horario_inicial, '%Y-%m-%d %H:%i:%S') AS fecha_horario_inicial,
                    t.codigo_qr
                FROM turno t
                JOIN estado_turno et ON et.id_estado_turno = t.id_estado
                WHERE t.id_turno = %s
            """,
            (id_turno,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def buscar_turno_y_estado_destino(id_turno, id_estado):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT t.id_estado, t.id_paciente, t.fecha_horario_inicial,
                   t.fecha_horario_llegada, LOWER(actual.estado_turno) AS estado_actual,
                   LOWER(destino.estado_turno) AS estado_destino,
                   m.id_usuario AS id_usuario_medico
            FROM turno t
            JOIN agenda a ON a.id_agenda = t.id_agenda
            JOIN medico m ON m.id_medico = a.id_medico
            JOIN estado_turno actual ON actual.id_estado_turno = t.id_estado
            LEFT JOIN estado_turno destino ON destino.id_estado_turno = %s
            WHERE t.id_turno = %s
            """,
            (id_estado, id_turno),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def buscar_id_estado_turno(nombre):
    """Devuelve el id del estado de turno a partir de su nombre."""
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_estado_turno
            FROM estado_turno
            WHERE LOWER(estado_turno) = LOWER(%s)
            LIMIT 1
            """,
            (nombre,),
        )
        fila = cursor.fetchone()
        return int(fila['id_estado_turno']) if fila else None
    finally:
        cursor.close()
        conexion.close()


def guardar_estado_turno(id_turno, id_estado, turno_actual):
    conexion, cursor = obtener_cursor()
    try:
        # Se confirma el cambio solo si la reserva y su llegada siguen siendo las verificadas.
        cursor.execute(
            """
            UPDATE turno
            SET id_estado = %s
            WHERE id_turno = %s
              AND id_estado = %s
              AND id_paciente = %s
              AND fecha_horario_inicial = %s
              AND fecha_horario_llegada <=> %s
            """,
            (
                id_estado, id_turno, turno_actual['id_estado'], turno_actual['id_paciente'],
                turno_actual['fecha_horario_inicial'], turno_actual['fecha_horario_llegada'],
            ),
        )
        conexion.commit()
        return cursor.rowcount == 1
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def reservar_turno(id_turno, id_paciente, codigo_qr):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
                SELECT id_turno, id_paciente, id_estado
                FROM turno
                WHERE id_turno = %s
                FOR UPDATE
            """,
            (id_turno,),
        )
        turno = cursor.fetchone()
        if turno is None:
            return None
        if turno['id_paciente'] is not None or turno['id_estado'] != 1:
            return {'resultado': 'NO_DISPONIBLE'}

        cursor.execute(
            """
                UPDATE turno
                SET id_paciente = %s,
                    id_estado = (SELECT id_estado_turno FROM estado_turno WHERE LOWER(estado_turno) = 'reservado'),
                    codigo_qr = %s
                WHERE id_turno = %s
            """,
            (id_paciente, codigo_qr, id_turno),
        )
        conexion.commit()
        return {'resultado': 'RESERVADO', 'id_turno': id_turno, 'codigo_qr': codigo_qr}
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def buscar_turno_por_codigo_qr(codigo_qr):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
                SELECT
                    t.id_turno,
                    t.id_agenda,
                    t.id_paciente,
                    t.id_estado,
                    LOWER(et.estado_turno) AS estado_turno,
                    DATE_FORMAT(t.fecha_horario_inicial, '%Y-%m-%d %H:%i:%S') AS fecha_horario_inicial,
                    DATE_FORMAT(t.fecha_horario_llegada, '%Y-%m-%d %H:%i:%S') AS fecha_horario_llegada,
                    t.codigo_qr
                FROM turno t
                JOIN estado_turno et ON et.id_estado_turno = t.id_estado
                WHERE t.codigo_qr = %s
            """,
            (codigo_qr,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def buscar_datos_turno_comprobante(id_turno):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
                SELECT
                    t.id_turno,
                    t.id_agenda,
                    t.id_paciente,
                    DATE_FORMAT(t.fecha_horario_inicial, '%Y-%m-%d %H:%i:%S') AS fecha_horario_inicial,
                    a.duracion_turno,
                    m.id_medico,
                    um.nombre AS nombre_medico,
                    um.apellido AS apellido_medico,
                    e.nombre_especialidad,
                    c.numero AS numero_consultorio,
                    c.piso AS piso_consultorio,
                    p.id_usuario AS id_usuario_paciente,
                    up.nombre AS nombre_paciente,
                    up.apellido AS apellido_paciente,
                    up.correo_electronico
                FROM turno t
                JOIN agenda a ON a.id_agenda = t.id_agenda
                JOIN medico m ON m.id_medico = a.id_medico
                JOIN usuario um ON um.id_usuario = m.id_usuario
                JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                JOIN consultorio c ON c.id_consultorio = a.id_consultorio
                LEFT JOIN paciente p ON p.id_paciente = t.id_paciente
                LEFT JOIN usuario up ON up.id_usuario = p.id_usuario
                WHERE t.id_turno = %s
            """,
            (id_turno,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def confirmar_checkin(id_turno, fecha_horario_llegada):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
                UPDATE turno
                SET id_estado = (SELECT id_estado_turno FROM estado_turno WHERE LOWER(estado_turno) = 'confirmado'),
                    fecha_horario_llegada = %s
                WHERE id_turno = %s
                  AND id_estado = (
                      SELECT id_estado_turno
                      FROM estado_turno
                      WHERE LOWER(estado_turno) = 'reservado'
                  )
            """,
            (fecha_horario_llegada, id_turno),
        )
        conexion.commit()
        return cursor.rowcount > 0
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def buscar_turnos_disponibles(
    id_especialidad=None,
    id_medico=None,
    id_cobertura=None,
    fecha_desde=None,
    fecha_hasta=None,
    hora_desde=None,
    hora_hasta=None,
):
    condiciones = [
        "LOWER(et.estado_turno) IN ('disponible', 'cancelado')",
        't.id_paciente IS NULL',
    ]
    parametros = []

    if id_especialidad is not None:
        condiciones.append('m.id_especialidad = %s')
        parametros.append(id_especialidad)
    if id_medico is not None:
        condiciones.append('m.id_medico = %s')
        parametros.append(id_medico)
    if id_cobertura is not None:
        condiciones.append(
            'EXISTS (SELECT 1 FROM cobertura_medico cm '
            'WHERE cm.id_medico = m.id_medico AND cm.id_cobertura = %s)'
        )
        parametros.append(id_cobertura)
    if fecha_desde is not None:
        condiciones.append('DATE(t.fecha_horario_inicial) >= %s')
        parametros.append(fecha_desde)
    if fecha_hasta is not None:
        condiciones.append('DATE(t.fecha_horario_inicial) <= %s')
        parametros.append(fecha_hasta)
    if hora_desde is not None:
        condiciones.append('TIME(t.fecha_horario_inicial) >= %s')
        parametros.append(hora_desde)
    if hora_hasta is not None:
        condiciones.append('TIME(t.fecha_horario_inicial) <= %s')
        parametros.append(hora_hasta)

    consulta = """
        SELECT
            t.id_turno,
            t.id_agenda,
            DATE_FORMAT(t.fecha_horario_inicial, '%Y-%m-%d %H:%i:%S') AS fecha_horario_inicial,
            a.duracion_turno,
            m.id_medico,
            um.nombre AS nombre_medico,
            um.apellido AS apellido_medico,
            e.id_especialidad,
            e.nombre_especialidad,
            c.id_consultorio,
            c.numero AS numero_consultorio,
            c.piso AS piso_consultorio,
            et.id_estado_turno,
            et.estado_turno
        FROM turno t
        JOIN agenda a ON a.id_agenda = t.id_agenda
        JOIN medico m ON m.id_medico = a.id_medico
        JOIN usuario um ON um.id_usuario = m.id_usuario
        JOIN especialidad e ON e.id_especialidad = m.id_especialidad
        JOIN consultorio c ON c.id_consultorio = a.id_consultorio
        JOIN estado_turno et ON et.id_estado_turno = t.id_estado
        WHERE """ + ' AND '.join(condiciones) + ' ORDER BY t.fecha_horario_inicial, t.id_turno'

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        turnos = []
        for fila in filas:
            turnos.append({
                'id_turno': int(fila['id_turno']),
                'id_agenda': int(fila['id_agenda']),
                'fecha_horario_inicial': fila['fecha_horario_inicial'],
                'duracion_turno': int(fila['duracion_turno']),
                'paciente': None,
                'medico': {
                    'id_medico': int(fila['id_medico']),
                    'nombre': fila['nombre_medico'],
                    'apellido': fila['apellido_medico'],
                    'id_especialidad': int(fila['id_especialidad']),
                    'especialidad': fila['nombre_especialidad'],
                },
                'consultorio': {
                    'id_consultorio': int(fila['id_consultorio']),
                    'numero': int(fila['numero_consultorio']),
                    'piso': fila['piso_consultorio'],
                },
                'estado': {
                    'id_estado': int(fila['id_estado_turno']),
                    'nombre': fila['estado_turno'],
                },
            })
        return turnos
    finally:
        cursor.close()
        conexion.close()


def buscar_turnos(
    fecha_desde=None,
    fecha_hasta=None,
    id_medico=None,
    id_estado=None,
    id_usuario_paciente=None,
    id_usuario_medico=None,
    id_turno=None,
):
    condiciones = []
    parametros = []

    if id_turno is not None:
        condiciones.append('t.id_turno = %s')
        parametros.append(id_turno)

    if fecha_desde is not None:
        condiciones.append('DATE(t.fecha_horario_inicial) >= %s')
        parametros.append(fecha_desde)

    if fecha_hasta is not None:
        condiciones.append('DATE(t.fecha_horario_inicial) <= %s')
        parametros.append(fecha_hasta)

    if id_medico is not None:
        condiciones.append('m.id_medico = %s')
        parametros.append(id_medico)

    if id_estado is not None:
        condiciones.append('t.id_estado = %s')
        parametros.append(id_estado)

    if id_usuario_paciente is not None:
        condiciones.append('p.id_usuario = %s')
        parametros.append(id_usuario_paciente)

    if id_usuario_medico is not None:
        condiciones.append('m.id_usuario = %s')
        parametros.append(id_usuario_medico)

    where = ' WHERE ' + ' AND '.join(condiciones) if condiciones else ''
    campos_detalle = ''
    if id_turno is not None:
        campos_detalle = ', t.codigo_qr'

    # La cobertura del paciente se devuelve siempre: se usa en el listado
    # de turnos del médico y del administrador.
    join_cobertura = ' LEFT JOIN cobertura co ON co.id_cobertura = p.id_cobertura '

    consulta = """
        SELECT
            t.id_turno,
            t.id_agenda,
            DATE_FORMAT(t.fecha_creacion_turno, '%Y-%m-%d %H:%i:%S') AS fecha_creacion_turno,
            DATE_FORMAT(t.fecha_horario_inicial, '%Y-%m-%d %H:%i:%S') AS fecha_horario_inicial,
            DATE_FORMAT(t.fecha_horario_llegada, '%Y-%m-%d %H:%i:%S') AS fecha_horario_llegada,
            t.id_paciente,
            p.id_usuario AS id_usuario_paciente,
            up.nombre AS nombre_paciente,
            up.apellido AS apellido_paciente,
            up.dni AS dni_paciente,
            a.duracion_turno,
            m.id_medico,
            um.nombre AS nombre_medico,
            um.apellido AS apellido_medico,
            e.id_especialidad,
            e.nombre_especialidad,
            c.id_consultorio,
            c.numero AS numero_consultorio,
            c.piso AS piso_consultorio,
            et.id_estado_turno,
            et.estado_turno,
            co.id_cobertura,
            co.nombre AS nombre_cobertura
    """ + campos_detalle + """
        FROM turno t
        JOIN agenda a ON a.id_agenda = t.id_agenda
        JOIN medico m ON m.id_medico = a.id_medico
        JOIN usuario um ON um.id_usuario = m.id_usuario
        JOIN especialidad e ON e.id_especialidad = m.id_especialidad
        JOIN consultorio c ON c.id_consultorio = a.id_consultorio
        JOIN estado_turno et ON et.id_estado_turno = t.id_estado
        LEFT JOIN paciente p ON p.id_paciente = t.id_paciente
        LEFT JOIN usuario up ON up.id_usuario = p.id_usuario         
    """ + join_cobertura + where + ' ORDER BY t.fecha_horario_inicial, t.id_turno '

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        turnos = []

        for fila in filas:
            paciente = None
            if fila['id_paciente'] is not None:
                paciente = {
                    'id_paciente': int(fila['id_paciente']),
                    'id_usuario': int(fila['id_usuario_paciente']),
                    'nombre': fila['nombre_paciente'],
                    'apellido': fila['apellido_paciente'],
                    'dni': fila['dni_paciente'],
                }

            turno = {
                'id_turno': int(fila['id_turno']),
                'id_agenda': int(fila['id_agenda']),
                'fecha_creacion_turno': fila['fecha_creacion_turno'],
                'fecha_horario_inicial': fila['fecha_horario_inicial'],
                'fecha_horario_llegada': fila['fecha_horario_llegada'],
                'duracion_turno': int(fila['duracion_turno']),
                'paciente': paciente,
                'medico': {
                    'id_medico': int(fila['id_medico']),
                    'nombre': fila['nombre_medico'],
                    'apellido': fila['apellido_medico'],
                    'id_especialidad': int(fila['id_especialidad']),
                    'especialidad': fila['nombre_especialidad'],
                },
                'consultorio': {
                    'id_consultorio': int(fila['id_consultorio']),
                    'numero': int(fila['numero_consultorio']),
                    'piso': fila['piso_consultorio'],
                },
                'estado': {
                    'id_estado': int(fila['id_estado_turno']),
                    'nombre': fila['estado_turno'],
                },
                'cobertura': None,
            }

            if fila['id_cobertura'] is not None:
                turno['cobertura'] = {
                    'id_cobertura': int(fila['id_cobertura']),
                    'nombre': fila['nombre_cobertura'],
                }

            if id_turno is not None:
                turno['codigo_qr'] = fila['codigo_qr']

            turnos.append(turno)

        return turnos
    finally:
        cursor.close()
        conexion.close()

def insertar_turnos_disponibles(turnos):
    if not turnos:
        return 0

    turnos_por_agenda = {}

    for turno in turnos:
        id_agenda = turno['id_agenda']
        turnos_por_agenda.setdefault(id_agenda, []).append(turno['fecha_horario_inicial'])
    conexion, cursor = obtener_cursor()
    cantidad_insertada = 0

    try:
        for id_agenda in sorted(turnos_por_agenda):
            cursor.execute(
                """
                    SELECT id_agenda FROM agenda WHERE id_agenda = %s FOR UPDATE
                """, (id_agenda,)
            )
            if cursor.fetchone() is None:
                continue

            cursor.execute(
                """
                    SELECT fecha_horario_inicial FROM turno
                    WHERE id_agenda = %s FOR UPDATE
                """, (id_agenda,)
            )

            existentes = {
                fila['fecha_horario_inicial']
                for fila in cursor.fetchall()
            }

            nuevos = []

            for fecha_horario in turnos_por_agenda[id_agenda]:
                if fecha_horario not in existentes:
                    nuevos.append((id_agenda, fecha_horario))
                    existentes.add(fecha_horario)

            if nuevos:
                cursor.executemany(
                    """
                        INSERT INTO turno(id_agenda, id_paciente, id_estado, fecha_horario_inicial)
                        VALUES (%s, NULL, 1, %s)
                    """, (nuevos)
                )
                cantidad_insertada += cursor.rowcount

        conexion.commit()
        return cantidad_insertada
    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def buscar_ids_turnos_ausentes_pendientes():
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT t.id_turno
            FROM turno t
            JOIN estado_turno et ON et.id_estado_turno = t.id_estado
            WHERE LOWER(et.estado_turno) = 'reservado'
              AND t.id_paciente IS NOT NULL
              AND t.fecha_horario_llegada IS NULL
              AND t.fecha_horario_inicial + INTERVAL 15 MINUTE < %s
            """,
            (_ahora_local(),),
        )
        return [int(fila['id_turno']) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()


def buscar_turno_para_cancelar(id_turno):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT
                t.id_turno,
                t.id_paciente,
                p.id_usuario AS id_usuario_paciente,
                t.id_estado,
                LOWER(et.estado_turno) AS estado_turno,
                DATE_FORMAT(t.fecha_horario_inicial, '%Y-%m-%d %H:%i:%S') AS fecha_horario_inicial
            FROM turno t
            JOIN estado_turno et ON et.id_estado_turno = t.id_estado
            LEFT JOIN paciente p ON p.id_paciente = t.id_paciente
            WHERE t.id_turno = %s
            """,
            (id_turno,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def cancelar_turno(id_turno):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            UPDATE turno
            SET id_estado = (
                SELECT id_estado_turno
                FROM estado_turno
                WHERE LOWER(estado_turno) = 'cancelado'
            )
            WHERE id_turno = %s
              AND id_estado = (
                  SELECT id_estado_turno
                  FROM estado_turno
                  WHERE LOWER(estado_turno) = 'reservado'
              )
            """,
            (id_turno,),
        )
        if cursor.rowcount == 0:
            conexion.rollback()
            return {'resultado': 'NO_CANCELABLE'}

        cursor.execute(
            """
            SELECT id_agenda, fecha_horario_inicial
            FROM turno
            WHERE id_turno = %s
            """,
            (id_turno,),
        )
        turno_cancelado = cursor.fetchone()

        cursor.execute(
            """
            SELECT 1
            FROM turno t
            JOIN estado_turno et ON et.id_estado_turno = t.id_estado
            WHERE t.id_agenda = %s
              AND t.fecha_horario_inicial = %s
              AND LOWER(et.estado_turno) = 'disponible'
            LIMIT 1
            """,
            (
                turno_cancelado['id_agenda'],
                turno_cancelado['fecha_horario_inicial'],
            ),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO turno (id_agenda, id_paciente, id_estado, fecha_horario_inicial)
                VALUES (
                    %s,
                    NULL,
                    (SELECT id_estado_turno FROM estado_turno WHERE LOWER(estado_turno) = 'disponible'),
                    %s
                )
                """,
                (
                    turno_cancelado['id_agenda'],
                    turno_cancelado['fecha_horario_inicial'],
                ),
            )

        conexion.commit()
        return {'resultado': 'CANCELADO', 'id_turno': id_turno}
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()
