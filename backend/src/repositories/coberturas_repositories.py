import mysql.connector

from src.db import obtener_cursor

def obtener_coberturas():
    conexion, cursor = obtener_cursor()
    try:
        consulta = """
            SELECT id_cobertura, nombre
            FROM cobertura
            ORDER BY nombre
        """
        cursor.execute(consulta)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()

def guardar_cobertura(nombre):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_cobertura
            FROM cobertura
            WHERE nombre = %s
            LIMIT 1
            """, 
            (nombre,)
            )
        if cursor.fetchone() is not None:
            return None, 'COBERTURA_DUPLICADA'

        consulta = """
            INSERT INTO cobertura (nombre)
            VALUES (%s)
        """
        cursor.execute(consulta, (nombre,))
        cobertura_guardada = {
            'id_cobertura': int(cursor.lastrowid),
            'nombre': nombre,
        }
        conexion.commit()
        return cobertura_guardada, None
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return None, 'COBERTURA_DUPLICADA'
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()

def actualizar_cobertura(id_cobertura, nombre):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_cobertura
            FROM cobertura
            WHERE id_cobertura = %s
            """, 
            (id_cobertura,)
            )
        if cursor.fetchone() is None:
            return None, 'NO_EXISTE'

        cursor.execute(
            """
            SELECT id_cobertura
            FROM cobertura
            WHERE nombre = %s AND id_cobertura <> %s
            LIMIT 1
            """, 
            (nombre, id_cobertura)
            )
        if cursor.fetchone() is not None:
            return None, 'COBERTURA_DUPLICADA'

        consulta = """
            UPDATE cobertura
            SET nombre = %s
            WHERE id_cobertura = %s
        """
        cursor.execute(consulta,(nombre, id_cobertura))
        cobertura_actualizada = {
            'id_cobertura': id_cobertura,
            'nombre': nombre,
        }
        conexion.commit()
        return cobertura_actualizada, None
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def borrar_cobertura(id_cobertura):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_cobertura
            FROM cobertura
            WHERE id_cobertura = %s
            """,
            (id_cobertura,)
        )
        if cursor.fetchone() is None:
            return None, 'NO_EXISTE'

        cursor.execute(
            """
            SELECT 1
            FROM paciente
            WHERE id_cobertura = %s
            LIMIT 1
            """,
            (id_cobertura,),
        )
        if cursor.fetchone() is not None:
            return None, 'EN_USO'

        cursor.execute(
            """
            SELECT 1
            FROM cobertura_medico
            WHERE id_cobertura = %s
            LIMIT 1
            """,
            (id_cobertura,),
        )
        if cursor.fetchone() is not None:
            return None, 'EN_USO'

        consulta_cobertura_medico = """
            DELETE FROM cobertura_medico
            WHERE id_cobertura = %s
        """
        cursor.execute(consulta_cobertura_medico, (id_cobertura,))

        consulta_cobertura = """
            DELETE FROM cobertura
            WHERE id_cobertura = %s
        """
        cursor.execute(consulta_cobertura, (id_cobertura,))
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
