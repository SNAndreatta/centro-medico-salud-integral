import mysql.connector

from src.db import obtener_cursor
from src.utils.roles import PACIENTE


def obtener_usuarios(id_rol=None):
    conexion, cursor = obtener_cursor()
    try:
        # Se listan todos los roles y se agregan los datos del médico o
        # del paciente cuando correspondan, para poder mostrar el rol real
        # y enlazar al perfil correcto desde el ABM.
        consulta = """
            SELECT u.id_usuario, u.id_rol, r.nombre AS rol,
                   u.nombre, u.apellido, u.correo_electronico, u.dni,
                   DATE_FORMAT(u.fecha_nacimiento, '%Y-%m-%d') AS fecha_nacimiento,
                   DATE_FORMAT(u.fecha_creacion, '%Y-%m-%d') AS fecha_creacion,
                   m.id_medico, m.matricula,
                   e.nombre_especialidad,
                   p.id_paciente, c.nombre AS nombre_cobertura
            FROM usuario u
            JOIN rol r ON r.id_rol = u.id_rol
            LEFT JOIN medico m ON m.id_usuario = u.id_usuario
            LEFT JOIN especialidad e ON e.id_especialidad = m.id_especialidad
            LEFT JOIN paciente p ON p.id_usuario = u.id_usuario
            LEFT JOIN cobertura c ON c.id_cobertura = p.id_cobertura
        """
        parametros = []
        if id_rol is not None:
            consulta += ' WHERE u.id_rol = %s'
            parametros.append(id_rol)
        consulta += ' ORDER BY u.apellido, u.nombre, u.id_usuario'
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
                id_rol, nombre, apellido, correo_electronico, dni,
                fecha_nacimiento, contrasenia
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                usuario['id_rol'],
                usuario['nombre'],
                usuario['apellido'],
                usuario['correo_electronico'],
                usuario['dni'],
                usuario.get('fecha_nacimiento'),
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
            'fecha_nacimiento': usuario.get('fecha_nacimiento'),
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


def obtener_usuario_por_id(id_usuario):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_usuario, id_rol, nombre, apellido, correo_electronico,
                   dni, fecha_nacimiento, fecha_creacion
            FROM usuario
            WHERE id_usuario = %s
            """,
            (id_usuario,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def actualizar_usuario(id_usuario, datos):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_usuario FROM usuario WHERE id_usuario = %s LIMIT 1',
            (id_usuario,),
        )
        if cursor.fetchone() is None:
            return 'USUARIO_NO_EXISTE'

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuario
            WHERE (correo_electronico = %s OR dni = %s)
              AND id_usuario != %s
            LIMIT 1
            """,
            (datos['correo_electronico'], datos['dni'], id_usuario),
        )
        if cursor.fetchone() is not None:
            return 'USUARIO_DUPLICADO'

        cursor.execute(
            """
            UPDATE usuario
            SET nombre = %s, apellido = %s, dni = %s,
                correo_electronico = %s, fecha_nacimiento = %s
            WHERE id_usuario = %s
            """,
            (
                datos['nombre'],
                datos['apellido'],
                datos['dni'],
                datos['correo_electronico'],
                datos.get('fecha_nacimiento'),
                id_usuario,
            ),
        )
        conexion.commit()
        return None
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return 'USUARIO_DUPLICADO'
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def eliminar_usuario_por_id(id_usuario):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_rol FROM usuario WHERE id_usuario = %s LIMIT 1',
            (id_usuario,),
        )
        usuario = cursor.fetchone()
        if usuario is None:
            return 'USUARIO_NO_EXISTE'

        # Los pacientes tienen una fila propia que debe eliminarse antes
        # que el usuario para respetar la clave foránea.
        if int(usuario['id_rol']) == PACIENTE:
            cursor.execute(
                'DELETE FROM paciente WHERE id_usuario = %s',
                (id_usuario,),
            )

        cursor.execute('DELETE FROM usuario WHERE id_usuario = %s', (id_usuario,))
        conexion.commit()
        return None
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return 'USUARIO_EN_USO'
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()