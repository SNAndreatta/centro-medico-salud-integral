from src.db import obtener_cursor


def buscar_medicos(id_especialidad=None, id_cobertura=None, nombre=None):
    condiciones = []
    parametros = []

    if id_especialidad is not None:
        condiciones.append('m.id_especialidad = %s')
        parametros.append(id_especialidad)
    if id_cobertura is not None:
        condiciones.append(
            "EXISTS (SELECT 1 FROM cobertura_medico cm "
            "WHERE cm.id_medico = m.id_medico AND cm.id_cobertura = %s)"
        )
        parametros.append(id_cobertura)
    if nombre:
        condiciones.append('(LOWER(u.nombre) LIKE LOWER(%s) OR LOWER(u.apellido) LIKE LOWER(%s))')
        patron = f'%{nombre}%'
        parametros.extend((patron, patron))

    where = ' WHERE ' + ' AND '.join(condiciones) if condiciones else ''
    consulta = """
        SELECT m.id_medico, u.id_usuario, u.nombre, u.apellido,
               u.correo_electronico, u.dni, m.matricula,
               e.id_especialidad, e.nombre_especialidad
        FROM medico m
        JOIN usuario u ON u.id_usuario = m.id_usuario
        JOIN especialidad e ON e.id_especialidad = m.id_especialidad
    """ + where + ' ORDER BY u.apellido, u.nombre, m.id_medico'

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()