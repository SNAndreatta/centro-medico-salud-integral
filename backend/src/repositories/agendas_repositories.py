from src.db import obtener_cursor

def buscar_agendas(id_medico=None, id_consultorio=None, vigente=None, id_usuario_medico=None):
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
