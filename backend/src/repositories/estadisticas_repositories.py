from src.db import obtener_cursor
from src.utils.fechas import hoy_local


def _condiciones_periodo(fecha_desde, fecha_hasta):
    condiciones = []
    parametros = []

    if fecha_desde is not None:
        condiciones.append('DATE(t.fecha_horario_inicial) >= %s')
        parametros.append(fecha_desde)
    if fecha_hasta is not None:
        condiciones.append('DATE(t.fecha_horario_inicial) <= %s')
        parametros.append(fecha_hasta)

    where = ' AND ' + ' AND '.join(condiciones) if condiciones else ''
    return where, parametros


def listar_sala_espera(id_usuario_medico=None):
    condiciones = [
        'DATE(t.fecha_horario_inicial) = %s',
        't.fecha_horario_llegada IS NOT NULL',
        "LOWER(et.estado_turno) = 'confirmado'",
    ]
    # La fecha se calcula en hora local: no depende de la zona horaria del
    # contenedor de MySQL.
    parametros = [hoy_local()]

    if id_usuario_medico is not None:
        condiciones.append('m.id_usuario = %s')
        parametros.append(id_usuario_medico)

    consulta = """
        SELECT
            t.id_turno,
            DATE_FORMAT(t.fecha_horario_inicial, '%Y-%m-%d %H:%i:%S') AS fecha_horario_inicial,
            DATE_FORMAT(t.fecha_horario_llegada, '%Y-%m-%d %H:%i:%S') AS fecha_horario_llegada,
            p.id_paciente,
            up.nombre AS nombre_paciente,
            up.apellido AS apellido_paciente,
            up.dni AS dni_paciente,
            m.id_medico,
            m.id_especialidad,
            e.nombre_especialidad AS especialidad_medico,
            um.nombre AS nombre_medico,
            um.apellido AS apellido_medico,
            c.numero AS numero_consultorio
        FROM turno t
        JOIN agenda a ON a.id_agenda = t.id_agenda
        JOIN medico m ON m.id_medico = a.id_medico
        JOIN especialidad e ON e.id_especialidad = m.id_especialidad
        JOIN usuario um ON um.id_usuario = m.id_usuario
        JOIN paciente p ON p.id_paciente = t.id_paciente
        JOIN usuario up ON up.id_usuario = p.id_usuario
        JOIN consultorio c ON c.id_consultorio = a.id_consultorio
        JOIN estado_turno et ON et.id_estado_turno = t.id_estado
        WHERE """ + ' AND '.join(condiciones) + ' ORDER BY t.fecha_horario_llegada, t.fecha_horario_inicial'

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        resultado = []
        for fila in filas:
            resultado.append({
                'id_turno': int(fila['id_turno']),
                'fecha_horario_inicial': fila['fecha_horario_inicial'],
                'fecha_horario_llegada': fila['fecha_horario_llegada'],
                'paciente': {
                    'id_paciente': int(fila['id_paciente']),
                    'nombre': fila['nombre_paciente'],
                    'apellido': fila['apellido_paciente'],
                    'dni': fila['dni_paciente'],
                },
                'medico': {
                    'id_medico': int(fila['id_medico']),
                    'id_especialidad': int(fila['id_especialidad']),
                    'especialidad': fila['especialidad_medico'],
                    'nombre': fila['nombre_medico'],
                    'apellido': fila['apellido_medico'],
                },
                'numero_consultorio': int(fila['numero_consultorio']),
            })
        return resultado
    finally:
        cursor.close()
        conexion.close()

def obtener_turnos_por_estado(fecha_desde=None, fecha_hasta=None):
    condiciones_join = []
    parametros = []

    if fecha_desde is not None:
        condiciones_join.append('DATE(t.fecha_horario_inicial) >= %s')
        parametros.append(fecha_desde)
    if fecha_hasta is not None:
        condiciones_join.append('DATE(t.fecha_horario_inicial) <= %s')
        parametros.append(fecha_hasta)

    join_extra = ''
    if condiciones_join:
        join_extra = ' AND ' + ' AND '.join(condiciones_join)

    consulta = """
        SELECT
            et.id_estado_turno,
            et.estado_turno,
            COUNT(t.id_turno) AS cantidad
        FROM estado_turno et
        LEFT JOIN turno t
            ON t.id_estado = et.id_estado_turno
    """ + join_extra + """
        GROUP BY et.id_estado_turno, et.estado_turno
        ORDER BY et.id_estado_turno
    """

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        resultado = []
        for fila in filas:
            resultado.append({
                'id_estado': int(fila['id_estado_turno']),
                'estado': fila['estado_turno'],
                'cantidad': int(fila['cantidad']),
            })
        return resultado
    finally:
        cursor.close()
        conexion.close()

def obtener_ocupacion_consultorios(fecha_desde=None, fecha_hasta=None):
    condiciones_join = []
    parametros = []

    if fecha_desde is not None:
        condiciones_join.append('DATE(t.fecha_horario_inicial) >= %s')
        parametros.append(fecha_desde)
    if fecha_hasta is not None:
        condiciones_join.append('DATE(t.fecha_horario_inicial) <= %s')
        parametros.append(fecha_hasta)

    join_extra = ''
    if condiciones_join:
        join_extra = ' AND ' + ' AND '.join(condiciones_join)

    consulta = """
        SELECT
            c.id_consultorio,
            c.numero,
            c.piso,
            COUNT(t.id_turno) AS total_turnos,
            SUM(CASE
                WHEN LOWER(et.estado_turno) IN ('reservado', 'confirmado', 'atendido', 'ausente')
                THEN 1 ELSE 0
            END) AS turnos_ocupados,
            SUM(CASE
                WHEN LOWER(et.estado_turno) = 'disponible'
                THEN 1 ELSE 0
            END) AS turnos_disponibles,
            SUM(CASE
                WHEN LOWER(et.estado_turno) = 'cancelado'
                THEN 1 ELSE 0
            END) AS turnos_cancelados,
            SUM(CASE
                WHEN t.id_turno IS NOT NULL AND LOWER(et.estado_turno) <> 'cancelado'
                THEN 1 ELSE 0
            END) AS turnos_considerados
        FROM consultorio c
        LEFT JOIN agenda a ON a.id_consultorio = c.id_consultorio
        LEFT JOIN turno t ON t.id_agenda = a.id_agenda
    """ + join_extra + """
        LEFT JOIN estado_turno et ON et.id_estado_turno = t.id_estado
        GROUP BY c.id_consultorio, c.numero, c.piso
        ORDER BY c.numero, c.id_consultorio
    """

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        resultado = []
        for fila in filas:
            total_turnos = int(fila['total_turnos'] or 0)
            ocupados = int(fila['turnos_ocupados'] or 0)
            disponibles = int(fila['turnos_disponibles'] or 0)
            cancelados = int(fila['turnos_cancelados'] or 0)
            considerados = int(fila['turnos_considerados'] or 0)
            porcentaje = round((ocupados * 100 / considerados), 2) if considerados else 0.0

            resultado.append({
                'id_consultorio': int(fila['id_consultorio']),
                'numero': int(fila['numero']),
                'piso': fila['piso'],
                'total_turnos': total_turnos,
                'turnos_ocupados': ocupados,
                'turnos_disponibles': disponibles,
                'turnos_cancelados': cancelados,
                'turnos_considerados': considerados,
                'porcentaje_ocupacion': porcentaje,
            })
        return resultado
    finally:
        cursor.close()
        conexion.close()


def obtener_ausentismo_medicos(fecha_desde=None, fecha_hasta=None):
    where, parametros = _condiciones_periodo(fecha_desde, fecha_hasta)
    consulta = """
        SELECT
            m.id_medico,
            um.nombre AS nombre_medico,
            um.apellido AS apellido_medico,
            SUM(CASE WHEN LOWER(et.estado_turno) = 'ausente' THEN 1 ELSE 0 END) AS ausentes,
            COUNT(*) AS considerados
        FROM turno t
        JOIN agenda a ON a.id_agenda = t.id_agenda
        JOIN medico m ON m.id_medico = a.id_medico
        JOIN usuario um ON um.id_usuario = m.id_usuario
        JOIN estado_turno et ON et.id_estado_turno = t.id_estado
        WHERE LOWER(et.estado_turno) IN ('atendido', 'ausente')
    """ + where + """
        GROUP BY m.id_medico, um.nombre, um.apellido
    """

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        return [
            {
                'id_medico': int(fila['id_medico']),
                'nombre': fila['nombre_medico'],
                'apellido': fila['apellido_medico'],
                'ausentes': int(fila['ausentes']),
                'considerados': int(fila['considerados']),
            }
            for fila in cursor.fetchall()
        ]
    finally:
        cursor.close()
        conexion.close()


def obtener_ausentismo_especialidades(fecha_desde=None, fecha_hasta=None):
    where, parametros = _condiciones_periodo(fecha_desde, fecha_hasta)
    consulta = """
        SELECT
            e.id_especialidad,
            e.nombre_especialidad AS nombre,
            SUM(CASE WHEN LOWER(et.estado_turno) = 'ausente' THEN 1 ELSE 0 END) AS ausentes,
            COUNT(*) AS considerados
        FROM turno t
        JOIN agenda a ON a.id_agenda = t.id_agenda
        JOIN medico m ON m.id_medico = a.id_medico
        JOIN especialidad e ON e.id_especialidad = m.id_especialidad
        JOIN estado_turno et ON et.id_estado_turno = t.id_estado
        WHERE LOWER(et.estado_turno) IN ('atendido', 'ausente')
    """ + where + """
        GROUP BY e.id_especialidad, e.nombre_especialidad
    """

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        return [
            {
                'id_especialidad': int(fila['id_especialidad']),
                'nombre': fila['nombre'],
                'ausentes': int(fila['ausentes']),
                'considerados': int(fila['considerados']),
            }
            for fila in cursor.fetchall()
        ]
    finally:
        cursor.close()
        conexion.close()


def _tiempos_espera(campos, columnas, agrupacion, fecha_desde, fecha_hasta):
    where, parametros = _condiciones_periodo(fecha_desde, fecha_hasta)
    consulta = """
        SELECT
    """ + campos + """,
            SUM(ROUND(GREATEST(
                0,
                TIMESTAMPDIFF(SECOND, t.fecha_horario_llegada, t.fecha_horario_inicial) / 60
            ))) AS minutos_totales,
            COUNT(*) AS turnos
        FROM turno t
        JOIN agenda a ON a.id_agenda = t.id_agenda
        JOIN medico m ON m.id_medico = a.id_medico
        JOIN usuario um ON um.id_usuario = m.id_usuario
        JOIN especialidad e ON e.id_especialidad = m.id_especialidad
        JOIN estado_turno et ON et.id_estado_turno = t.id_estado
        WHERE t.fecha_horario_llegada IS NOT NULL
    """ + where + """
        GROUP BY """ + agrupacion

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        resultado = []
        for fila in cursor.fetchall():
            item = {}
            for clave, alias in columnas.items():
                item[clave] = int(fila[alias]) if clave in ('id_medico', 'id_especialidad') else fila[alias]
            item['minutos_totales'] = int(fila['minutos_totales'] or 0)
            item['turnos'] = int(fila['turnos'])
            resultado.append(item)
        return resultado
    finally:
        cursor.close()
        conexion.close()


def obtener_tiempos_espera_medicos(fecha_desde=None, fecha_hasta=None):
    return _tiempos_espera(
        'm.id_medico, um.nombre AS nombre_medico, um.apellido AS apellido_medico',
        {'id_medico': 'id_medico', 'nombre': 'nombre_medico', 'apellido': 'apellido_medico'},
        'm.id_medico, um.nombre, um.apellido',
        fecha_desde,
        fecha_hasta,
    )


def obtener_tiempos_espera_especialidades(fecha_desde=None, fecha_hasta=None):
    return _tiempos_espera(
        'e.id_especialidad, e.nombre_especialidad AS nombre_especialidad',
        {'id_especialidad': 'id_especialidad', 'nombre': 'nombre_especialidad'},
        'e.id_especialidad, e.nombre_especialidad',
        fecha_desde,
        fecha_hasta,
    )