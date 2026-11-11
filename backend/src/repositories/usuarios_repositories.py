import mysql.connector

from src.db import obtener_cursor


def obtener_usuarios_staff(id_rol=None):
    conexion, cursor = obtener_cursor()
    try:
        consulta = """
            SELECT id_usuario, id_rol, nombre, apellido, dni, correo_electronico
            FROM usuario
            WHERE id_rol IN (1, 2)
        """
        parametros = []
        if id_rol is not None:
            consulta += ' AND id_rol = %s'
            parametros.append(id_rol)
        consulta += ' ORDER BY apellido, nombre, id_usuario'
        cursor.execute(consulta, parametros)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


def obtener_usuario_para_cambio_password(id_usuario):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_usuario, id_rol, contrasenia FROM usuario WHERE id_usuario = %s',
            (id_usuario,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def actualizar_hash_password(usuario, nuevo_hash):
    conexion, cursor = obtener_cursor()
    try:
        # El hash y el rol deben seguir siendo los que se verificaron antes del cambio.
        cursor.execute(
            """
            UPDATE usuario
            SET contrasenia = %s
            WHERE id_usuario = %s AND id_rol = %s
              AND CAST(contrasenia AS BINARY) = CAST(%s AS BINARY)
            """,
            (nuevo_hash, usuario['id_usuario'], usuario['id_rol'], usuario['contrasenia']),
        )
        conexion.commit()
        return cursor.rowcount == 1
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def guardar_usuario_staff(usuario):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_usuario
            FROM usuario
            WHERE correo_electronico = %s OR dni = %s
            LIMIT 1
            """,
            (usuario['correo_electronico'], usuario['dni']),
        )
        if cursor.fetchone() is not None:
            return None

        cursor.execute(
            """
            INSERT INTO usuario (
                id_rol, nombre, apellido, correo_electronico, dni, contrasenia
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                usuario['id_rol'],
                usuario['nombre'],
                usuario['apellido'],
                usuario['correo_electronico'],
                usuario['dni'],
                usuario['contrasenia'],
            ),
        )
        usuario_guardado = {
            'id_usuario': int(cursor.lastrowid),
            'id_rol': usuario['id_rol'],
            'nombre': usuario['nombre'],
            'apellido': usuario['apellido'],
            'correo_electronico': usuario['correo_electronico'],
            'dni': usuario['dni'],
        }
        conexion.commit()
        return usuario_guardado
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return None
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()
