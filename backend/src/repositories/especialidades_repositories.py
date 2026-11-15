import mysql.connector

from src.db import obtener_cursor

def obtener_especialidades():
    conexion, cursor = obtener_cursor()
    try:
        consulta = """
            SELECT e.id_especialidad, e.nombre_especialidad,
                   COUNT(DISTINCT m.id_medico) AS cantidad_medicos
            FROM especialidad e
            LEFT JOIN medico m
                ON m.id_especialidad = e.id_especialidad
            GROUP BY e.id_especialidad, e.nombre_especialidad
            ORDER BY e.nombre_especialidad
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
        return especialidad_guardada, None
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return None, 'ESPECIALIDAD_DUPLICADA'
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()

def actualizar_especialidad(id_especialidad, nombre):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_especialidad 
            FROM especialidad 
            WHERE id_especialidad = %s
            """,
            (id_especialidad,),
        )
        if cursor.fetchone() is None:
            return None, 'NO_EXISTE'
 
        cursor.execute(
            """
            SELECT id_especialidad
            FROM especialidad
            WHERE nombre_especialidad = %s AND id_especialidad <> %s
            LIMIT 1
            """,
            (nombre, id_especialidad),
        )
        if cursor.fetchone() is not None:
            return None, 'YA_EXISTE'

        consulta = """
            UPDATE especialidad
            SET nombre_especialidad = %s
            WHERE id_especialidad = %s
        """
        cursor.execute(consulta, (nombre, id_especialidad))
        especialidad_actualizada = {
            'id_especialidad': id_especialidad,
            'nombre_especialidad': nombre,
        }
        conexion.commit()
        return especialidad_actualizada, None
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()
 
 
def borrar_especialidad(id_especialidad):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_especialidad 
            FROM especialidad 
            WHERE id_especialidad = %s
            """,
            (id_especialidad,)
        )
        if cursor.fetchone() is None:
            return None, 'NO_EXISTE'
 
        cursor.execute(
            """
            SELECT 1 
            FROM medico 
            WHERE id_especialidad = %s 
            LIMIT 1
            """,
            (id_especialidad,)
        )
        if cursor.fetchone() is not None:
            return None, 'EN_USO'

        consulta = """
            DELETE FROM especialidad
            WHERE id_especialidad = %s
        """
        cursor.execute(consulta,(id_especialidad,))
        conexion.commit()
        return 'OK', None
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return None, 'EN_USO'
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()