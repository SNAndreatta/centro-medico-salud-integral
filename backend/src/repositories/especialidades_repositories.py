import mysql.connector

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

def guardar_especialidad(nombre_especialidad):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_especialidad
            FROM especialidad
            WHERE nombre_especialidad = %s
            LIMIT 1
            """,
            (nombre_especialidad,),
        )
        if cursor.fetchone() is not None:
            return None, 'ESPECIALIDAD_DUPLICADA'

        consulta = """
            INSERT INTO especialidad (nombre_especialidad)
            VALUES (%s)
        """
        cursor.execute(consulta, (nombre_especialidad,))
        especialidad_guardada = {
            'id_especialidad': int(cursor.lastrowid),
            'nombre_especialidad': nombre_especialidad,
        }
        conexion.commit()
        return especialidad_guardada
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return None
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()
