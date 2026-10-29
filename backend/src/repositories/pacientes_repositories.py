from src.db import obtener_cursor


def buscar_pacientes(dni=None, apellido=None):
    condiciones = []
    parametros = []

    if dni:
        condiciones.append('u.dni LIKE %s')
        parametros.append(f'%{dni}%')
    if apellido:
        condiciones.append('LOWER(u.apellido) LIKE LOWER(%s)')
        parametros.append(f'%{apellido}%')

    where = ' WHERE ' + ' AND '.join(condiciones) if condiciones else ''
    consulta = """
        SELECT p.id_paciente, u.id_usuario, u.nombre, u.apellido, u.dni,
               u.correo_electronico, p.id_plan, pl.nombre AS plan,
               c.nombre AS cobertura, p.nro_afiliado
        FROM paciente p
        JOIN usuario u ON u.id_usuario = p.id_usuario
        LEFT JOIN plan pl ON pl.id_plan = p.id_plan
        LEFT JOIN cobertura c ON c.id_cobertura = pl.id_cobertura
    """ + where + ' ORDER BY u.apellido, u.nombre, p.id_paciente'

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()