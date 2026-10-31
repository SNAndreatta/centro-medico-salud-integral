from src.db import obtener_cursor

def buscar_agendas(id_medico=None, id_consultorio=None, vigente=None, id_usuario_medico=None, id_agenda=None):
    condiciones = []
    parametros = []

    if id_medico is not None:
        condiciones.append('a.id_medico = %s')
        parametros.append(id_medico)

    if id_consultorio is not None:
        condiciones.append('a.id_consultorio = %s')
        parametros.append(id_consultorio)

    if vigente is True:
        condiciones.append('CURDATE() BETWEEN a.fecha_inicio AND a.fecha_hasta')
    elif vigente is False:
        condiciones.append('(a.fecha_inicio > CURDATE() OR a.fecha_hasta < CURDATE())')

    if id_usuario_medico is not None:
        condiciones.append('m.id_usuario = %s')
        parametros.append(id_usuario_medico)

    if id_agenda is not None:
        condiciones.append('a.id_agenda = %s')
        parametros.append(id_agenda)

    where = ' WHERE ' + ' AND '.join(condiciones) if condiciones else ''

    consulta = """
        SELECT
            a.id_agenda,
            a.id_medico,
            um.id_usuario AS id_usuario_medico,
            um.nombre AS nombre_medico,
            um.apellido AS apellido_medico,
            a.id_consultorio,
            c.numero AS numero_consultorio,
            c.piso AS piso_consultorio,
            a.duracion_turno,
            DATE_FORMAT(a.fecha_inicio, '%Y-%m-%d') AS fecha_inicio,
            DATE_FORMAT(a.fecha_hasta, '%Y-%m-%d') AS fecha_hasta,
            ad.id_agenda_dias,
            ad.dia_semana,
            TIME_FORMAT(ad.horario_inicio_jornada, '%H:%i:%S') AS horario_inicio_jornada,
            TIME_FORMAT(ad.horario_final_jornada, '%H:%i:%S') AS horario_final_jornada
        FROM agenda a
        JOIN medico m ON m.id_medico = a.id_medico
        JOIN usuario um ON um.id_usuario = m.id_usuario
        JOIN consultorio c ON c.id_consultorio = a.id_consultorio
        LEFT JOIN agenda_dias ad ON ad.id_agenda = a.id_agenda
    """ + where + " ORDER BY a.id_agenda, ad.dia_semana, ad.horario_inicio_jornada"

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()

        agendas = {}
        for fila in filas:
            id_agenda = int(fila['id_agenda'])
            if id_agenda not in agendas:
                agendas[id_agenda] = {
                    'id_agenda': id_agenda,
                    'id_medico': int(fila['id_medico']),
                    'medico': {
                        'id_usuario': int(fila['id_usuario_medico']),
                        'nombre': fila['nombre_medico'],
                        'apellido': fila['apellido_medico'],
                    },
                    'id_consultorio': int(fila['id_consultorio']),
                    'consultorio': {
                        'numero': int(fila['numero_consultorio']),
                        'piso': fila['piso_consultorio'],
                    },
                    'duracion_turno': int(fila['duracion_turno']),
                    'fecha_inicio': fila['fecha_inicio'],
                    'fecha_hasta': fila['fecha_hasta'],
                    'dias': [],
                }

            if fila['id_agenda_dias'] is not None:
                agendas[id_agenda]['dias'].append({
                    'id_agenda_dias': int(fila['id_agenda_dias']),
                    'dia_semana': int(fila['dia_semana']),
                    'horario_inicio_jornada': fila['horario_inicio_jornada'],
                    'horario_final_jornada': fila['horario_final_jornada']
                })

        return list(agendas.values())
    finally:
        cursor.close()
        conexion.close()

def verificar_referencias_agenda(id_medico, id_consultorio):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1 FROM medico WHERE id_medico = %s
            ) AS medico_existe,
            EXISTS(
                SELECT 1 FROM consultorio WHERE id_consultorio = %s
            ) AS consultorio_existe
            """, (id_medico, id_consultorio),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()

def buscar_conflicto_agenda(agenda):
    conexion, cursor = obtener_cursor()

    try:
        for dia in agenda['dias']:
            cursor.execute(
                """
                SELECT  a.id_agenda, a.id_medico, a.id_consultorio
                FROM agenda a JOIN agenda_dias ad ON ad.id_agenda = a.id_agenda
                WHERE a.fecha_inicio <= %s AND a.fecha_hasta >= %s
                AND ad.dia_semana = %s AND(a.id_medico = %s OR a.id_consultorio = %s)
                AND %s < ad.horario_final_jornada AND %s > ad.horario_inicio_jornada
                LIMIT 1
                """,
                (
                    agenda['fecha_hasta'],
                    agenda['fecha_inicio'],
                    dia['dia_semana'],
                    agenda['id_medico'],
                    agenda['id_consultorio'],
                    dia['horario_inicio_jornada'],
                    dia['horario_final_jornada'],
                ),
            )

            conflicto = cursor.fetchone()

            if conflicto is not None:
                if int(conflicto['id_medico']) == agenda['id_medico']:
                    return {
                        'tipo': 'MEDICO',
                        'id_agenda': int(conflicto['id_agenda']),
                    }

                return {
                    'tipo': 'CONSULTORIO',
                    'id_agenda': int(conflicto['id_agenda']),
                }
        return None
    finally:
        cursor.close()
        conexion.close()

def guardar_agenda(agenda):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            INSERT INTO agenda(id_medico, id_consultorio, 
            duracion_turno, fecha_inicio, fecha_hasta)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                agenda['id_medico'],
                agenda['id_consultorio'],
                agenda['duracion_turno'],
                agenda['fecha_inicio'],
                agenda['fecha_hasta'],
            ),
        )

        id_agenda = int(cursor.lastrowid)
        jornadas = []
        for dia in agenda['dias']:
            jornadas.append((
                id_agenda,
                dia['dia_semana'],
                dia['horario_inicio_jornada'],
                dia['horario_final_jornada'],
            ))

        cursor.executemany(
            """
            INSERT INTO agenda_dias(id_agenda, dia_semana,
            horario_inicio_jornada, horario_final_jornada)
            VALUES (%s, %s, %s, %s)
            """,
            jornadas,
        )

        conexion.commit()
        return id_agenda

    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()

def actualizar_fecha_hasta_agenda(id_agenda, fecha_hasta):
    consulta = """
            UPDATE agenda SET fecha_hasta = %s WHERE id_agenda = %s
    """

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, (fecha_hasta, id_agenda))
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()

def agenda_tiene_turnos(id_agenda):
    consulta = """
        SELECT 1 FROM turno WHERE id_agenda = %s LIMIT 1
    """        
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, (id_agenda,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conexion.close()

def borrar_agenda(id_agenda):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute("DELETE FROM agenda_dias WHERE id_agenda = %s", (id_agenda,))
        
        cursor.execute("DELETE FROM agenda WHERE id_agenda = %s", (id_agenda,))
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()