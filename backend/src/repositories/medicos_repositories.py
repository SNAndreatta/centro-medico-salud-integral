import mysql.connector
from mysql.connector import errorcode

from src.db import obtener_cursor
from src.utils.roles import MEDICO


def guardar_medico(medico):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_especialidad
            FROM especialidad
            WHERE id_especialidad = %s""",
            (medico['id_especialidad'],),
        )
        if cursor.fetchone() is None:
            return None, 'ESPECIALIDAD_INEXISTENTE'

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuario
            WHERE correo_electronico = %s
            LIMIT 1
            """,
            (medico['correo_electronico'],),
        )
        if cursor.fetchone() is not None:
            return None, 'USUARIO_DUPLICADO'

        cursor.execute(
            """
            SELECT id_medico
            FROM medico
            WHERE matricula = %s LIMIT 1
            """,
            (medico['matricula'],),
        )
        if cursor.fetchone() is not None:
            return None, 'MATRICULA_DUPLICADA'

        cursor.execute(
            """
            INSERT INTO usuario (
                id_rol,
                nombre,
                apellido,
                correo_electronico,
                dni,
                fecha_nacimiento,
                contrasenia
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                MEDICO,
                medico['nombre'],
                medico['apellido'],
                medico['correo_electronico'],
                medico['dni'],
                medico.get('fecha_nacimiento'),
                medico['contrasenia'],
            ),
        )
        id_usuario = int(cursor.lastrowid)

        cursor.execute(
            """
            INSERT INTO medico (
                id_especialidad, id_usuario, matricula
            )
            VALUES (%s, %s, %s)
            """,
            (
                medico['id_especialidad'],
                id_usuario,
                medico['matricula']
            ),
        )
        medico_guardado = {
            'id_medico': int(cursor.lastrowid),
            'id_usuario': id_usuario,
            'id_especialidad': medico['id_especialidad'],
            'nombre': medico['nombre'],
            'apellido': medico['apellido'],
            'correo_electronico': medico['correo_electronico'],
            'dni': medico['dni'],
            'matricula': medico['matricula'],
        }
        conexion.commit()
        return medico_guardado, None
    except mysql.connector.IntegrityError as exc:
        conexion.rollback()
        if exc.errno == errorcode.ER_DUP_ENTRY:
            return None, 'MEDICO_DUPLICADO'
        raise
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()

def obtener_medico_por_usuario(id_usuario):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT m.id_medico, u.id_usuario, u.nombre, u.apellido,
                   u.correo_electronico, u.dni, m.matricula,
                   e.id_especialidad, e.nombre_especialidad
            FROM medico m
            JOIN usuario u ON u.id_usuario = m.id_usuario
            JOIN especialidad e ON e.id_especialidad = m.id_especialidad
            WHERE m.id_usuario = %s
            LIMIT 1
            """,
            (id_usuario,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def obtener_medico_por_id(id_medico):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT m.id_medico, u.id_usuario, u.nombre, u.apellido,
                   u.correo_electronico, u.dni, m.matricula,
                   e.id_especialidad, e.nombre_especialidad
            FROM medico m
            JOIN usuario u ON u.id_usuario = m.id_usuario
            JOIN especialidad e ON e.id_especialidad = m.id_especialidad
            WHERE m.id_medico = %s
            """,
            (id_medico,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def actualizar_especialidad_medico(id_medico, id_especialidad, matricula=None):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_medico FROM medico WHERE id_medico = %s LIMIT 1',
            (id_medico,),
        )
        if cursor.fetchone() is None:
            return 'MEDICO_NO_EXISTE'

        cursor.execute(
            'SELECT id_especialidad FROM especialidad WHERE id_especialidad = %s LIMIT 1',
            (id_especialidad,),
        )
        if cursor.fetchone() is None:
            return 'ESPECIALIDAD_NO_EXISTE'

        if matricula is None:
            cursor.execute(
                'UPDATE medico SET id_especialidad = %s WHERE id_medico = %s',
                (id_especialidad, id_medico),
            )
        else:
            cursor.execute(
                """
                SELECT id_medico
                FROM medico
                WHERE matricula = %s AND id_medico != %s
                LIMIT 1
                """,
                (matricula, id_medico),
            )
            if cursor.fetchone() is not None:
                return 'MATRICULA_DUPLICADA'

            cursor.execute(
                """
                UPDATE medico
                SET id_especialidad = %s, matricula = %s
                WHERE id_medico = %s
                """,
                (id_especialidad, matricula, id_medico),
            )

        conexion.commit()
        return None
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return 'MATRICULA_DUPLICADA'
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def eliminar_medico(id_medico):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_usuario FROM medico WHERE id_medico = %s LIMIT 1',
            (id_medico,),
        )
        medico = cursor.fetchone()
        if medico is None:
            return 'MEDICO_NO_EXISTE'

        cursor.execute(
            """
            SELECT 1
            FROM turno t
            JOIN agenda a ON a.id_agenda = t.id_agenda
            WHERE a.id_medico = %s
            LIMIT 1
            """,
            (id_medico,),
        )
        if cursor.fetchone() is not None:
            return 'MEDICO_CON_TURNOS'

        cursor.execute('DELETE FROM cobertura_medico WHERE id_medico = %s', (id_medico,))
        cursor.execute(
            """
            DELETE FROM agenda_dias
            WHERE id_agenda IN (
                SELECT id_agenda FROM agenda WHERE id_medico = %s
            )
            """,
            (id_medico,),
        )
        cursor.execute('DELETE FROM agenda WHERE id_medico = %s', (id_medico,))
        cursor.execute('DELETE FROM medico WHERE id_medico = %s', (id_medico,))
        cursor.execute('DELETE FROM usuario WHERE id_usuario = %s', (medico['id_usuario'],))
        conexion.commit()
        return None
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return 'MEDICO_EN_USO'
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def obtener_coberturas_de_medico(id_medico):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_medico
            FROM medico
            WHERE id_medico = %s
            LIMIT 1
            """,
            (id_medico,),
        )
        if cursor.fetchone() is None:
            return None, 'MEDICO_NO_EXISTE'

        cursor.execute(
            """
            SELECT c.id_cobertura, c.nombre
            FROM cobertura_medico cm
            JOIN cobertura c ON c.id_cobertura = cm.id_cobertura
            WHERE cm.id_medico = %s
            ORDER BY c.nombre
            """,
            (id_medico,),
        )
        return cursor.fetchall(), None
    finally:
        cursor.close()
        conexion.close()


def vincular_cobertura_medico(id_medico, id_cobertura):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_medico
            FROM medico
            WHERE id_medico = %s
            LIMIT 1
            """,
            (id_medico,),
        )
        if cursor.fetchone() is None:
            return None, 'MEDICO_NO_EXISTE'

        cursor.execute(
            """
            SELECT id_cobertura, nombre
            FROM cobertura
            WHERE id_cobertura = %s
            LIMIT 1
            """,
            (id_cobertura,),
        )
        cobertura = cursor.fetchone()
        if cobertura is None:
            return None, 'COBERTURA_NO_EXISTE'

        cursor.execute(
            """
            SELECT id_cobertura_medico
            FROM cobertura_medico
            WHERE id_medico = %s AND id_cobertura = %s
            LIMIT 1
            """,
            (id_medico, id_cobertura),
        )
        if cursor.fetchone() is not None:
            return None, 'VINCULO_EXISTENTE'

        cursor.execute(
            """
            INSERT INTO cobertura_medico (id_medico, id_cobertura)
            VALUES (%s, %s)
            """,
            (id_medico, id_cobertura),
        )
        conexion.commit()
        return {
            'id_medico': id_medico,
            'id_cobertura': id_cobertura,
            'nombre': cobertura['nombre'],
        }, None
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def desvincular_cobertura_medico(id_medico, id_cobertura):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_medico
            FROM medico
            WHERE id_medico = %s
            LIMIT 1
            """,
            (id_medico,),
        )
        if cursor.fetchone() is None:
            return 'MEDICO_NO_EXISTE'

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
            return 'COBERTURA_NO_EXISTE'

        cursor.execute(
            """
            DELETE FROM cobertura_medico
            WHERE id_medico = %s AND id_cobertura = %s
            """,
            (id_medico, id_cobertura),
        )
        if cursor.rowcount == 0:
            return 'VINCULO_NO_EXISTE'

        conexion.commit()
        return None
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


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