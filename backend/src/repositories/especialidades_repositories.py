from src.db import obtener_cursor

def obtener_especialidades():
    conexion, cursor = obtener_cursor()
    try:
        consulta = """
            SELECT id_especialidad, nombre_especialidad
            FROM especialidad
            ORDER BY nombre_especialidad
        """
        cursor.execute(consulta)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()
