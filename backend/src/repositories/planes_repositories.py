import mysql.connector
from src.db import obtener_cursor

def obtener_planes_de_cobertura(id_cobertura):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT 1
            FROM cobertura
            WHERE id_cobertura = %s
            LIMIT 1
            """,
            (id_cobertura,),
        )
        if cursor.fetchone() is None:
            return None, 'COBERTURA_NO_EXISTE'

        consulta = """
            SELECT id_plan, id_cobertura, nombre
            FROM plan
            WHERE id_cobertura = %s
            ORDER BY nombre
            """
        cursor.execute(consulta,(id_cobertura,))
        return cursor.fetchall(), None
    except Exception:
        raise
    finally:
        cursor.close()
        conexion.close()


def guardar_plan(id_cobertura, nombre):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_cobertura
            FROM cobertura
            WHERE id_cobertura = %s
            LIMIT 1
            """,
            (id_cobertura,),
        )
        if cursor.fetchone() is None:
            return None, 'COBERTURA_NO_EXISTE'

        cursor.execute(
            """
            SELECT id_plan
            FROM plan
            WHERE id_cobertura = %s AND nombre = %s
            LIMIT 1
            """,
            (id_cobertura, nombre),
        )
        if cursor.fetchone() is not None:
            return None, 'PLAN_DUPLICADO'

        consulta = """
            INSERT INTO plan (id_cobertura, nombre)
            VALUES (%s, %s)
        """
        cursor.execute(consulta,(id_cobertura, nombre))
        plan_guardado = {
            'id_plan': int(cursor.lastrowid),
            'id_cobertura': id_cobertura,
            'nombre': nombre,
        }
        conexion.commit()
        return plan_guardado, None
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return None, 'PLAN_DUPLICADO'
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def actualizar_plan(id_plan, nombre):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_plan, id_cobertura 
            FROM plan 
            WHERE id_plan = %s
            """,
            (id_plan,),
        )
        existente = cursor.fetchone()
        if existente is None:
            return None, 'NO_EXISTE'
        
        cursor.execute(
            """
            SELECT id_plan FROM plan
            WHERE id_cobertura = %s AND nombre = %s AND id_plan <> %s
            LIMIT 1
            """,
            (existente['id_cobertura'], nombre, id_plan),
        )
        if cursor.fetchone() is not None:
            return None, 'PLAN_DUPLICADO'

        consulta = """
            UPDATE plan 
            SET nombre = %s 
            WHERE id_plan = %s
        """
        cursor.execute(consulta, (nombre, id_plan))
        plan_actualizado = {
            'id_plan': id_plan,
            'id_cobertura': existente['id_cobertura'],
            'nombre': nombre,
        }
        conexion.commit()
        return plan_actualizado, None
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return None, 'PLAN_DUPLICADO'
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def borrar_plan(id_plan):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_plan 
            FROM plan 
            WHERE id_plan = %s
            """,
            (id_plan,)
        )
        if cursor.fetchone() is None:
            return None, 'NO_EXISTE'
        
        cursor.execute(
            """
            SELECT 1 
            FROM paciente 
            WHERE id_plan = %s 
            LIMIT 1
            """,
            (id_plan,),
        )
        if cursor.fetchone() is not None:
            return None, 'EN_USO'

        consulta = """
            DELETE FROM plan
            WHERE id_plan = %s
        """
        cursor.execute(consulta,(id_plan,))
        conexion.commit()
        return 'OK', None
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()