import mysql.connector
from src.db import obtener_cursor

def obtener_consultorios():
    conexion, cursor = obtener_cursor()
    try:
        consulta = """
            SELECT id_consultorio, numero, piso FROM consultorio
            ORDER BY numero, piso, id_consultorio
        """
        cursor.execute(consulta)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


def guardar_consultorio(numero, piso):
    conexion, cursor = obtener_cursor()
    try:
        consulta = """
            INSERT INTO consultorio (numero, piso) VALUES (%s, %s)    
        """
        cursor.execute(consulta, (numero, piso))

        consultorio_guardado = {
            'id_consultorio': int(cursor.lastrowid),
            'numero': numero,
            'piso': piso,
        }

        conexion.commit()
        return consultorio_guardado, None

    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()

def actualizar_consultorio(id_consultorio, numero, piso):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_consultorio FROM consultorio WHERE id_consultorio = %s
            """, (id_consultorio,),
        )

        if cursor.fetchone() is None:
            return None, 'NO_EXISTE'

        consulta = """
            UPDATE consultorio SET numero = %s, piso = %s
            WHERE id_consultorio = %s
        """
        cursor.execute(consulta, (numero, piso, id_consultorio))

        consultorio_actualizado = {
            'id_consultorio': id_consultorio,
            'numero': numero,
            'piso': piso,
        }
        conexion.commit()
        return consultorio_actualizado, None

    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()

def borrar_consultorio(id_consultorio):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_consultorio FROM consultorio 
            WHERE id_consultorio = %s
            """, (id_consultorio,),
        )
        if cursor.fetchone() is None:
            return None, 'NO_EXISTE'

        cursor.execute(
            """
            SELECT 1 FROM agenda WHERE id_consultorio = %s
            LIMIT 1
            """, (id_consultorio,),
        )
        if cursor.fetchone() is not None:
            return None, 'EN_USO'

        cursor.execute(
            """
            DELETE FROM consultorio WHERE id_consultorio = %s
            """, (id_consultorio,),
        )

        conexion.commit()
        return 'OK', None

    except mysql.connector.IntegrityError:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()

