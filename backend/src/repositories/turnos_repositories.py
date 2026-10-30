from src.db import obtener_cursor

def buscar_turnos(
    fecha_desde=None,
    fecha_hasta=None,
    id_medico=None,
    id_estado=None,
    id_usuario_paciente=None,
    id_usuario_medico=None,
):
    condiciones = []
    parametros = []

    if fecha_desde is not None:
        condiciones.append('DATE(t.fecha_horario_inicial) >= %s')
        parametros.append(fecha_desde)

    if fecha_hasta is not None:
        condiciones.append('DATE(t.fecha_horario_hasta) <= %s')
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
            et.estado_turno
        FROM turno t
        JOIN agenda a ON a.id_agenda = t.id_agenda
        JOIN medico m ON m.id_medico = a.id_medico
        JOIN usuario um ON um.id_usuario = m.id_usuario
        JOIN especialidad e ON e.id_especialidad = m.id_especialidad
        JOIN consultorio c ON c.id_consultorio = a.id_consultorio
        JOIN estado_turno et ON et.id_estado_turno = t.id_estado
        LEFT JOIN paciente p ON p.id_paciente = t.id_paciente
        LEFT JOIN usuario up ON up.id_usuario = p.id_usuario         
    """ + where + ' ORDER BY t.fecha_horario_inicial, t.id_turno '

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

            turnos.append({
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
            })

        return turnos
    finally:
        cursor.close()
        conexion.close()