import mysql.connector
from mysql.connector import errorcode

from src.db import obtener_cursor


def registrar_paciente(paciente):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_usuario FROM usuario WHERE correo_electronico = %s LIMIT 1',
            (paciente['correo_electronico'],),
        )
        if cursor.fetchone() is not None:
            return None, 'EMAIL_DUPLICADO'

        if paciente['id_plan'] is not None:
            cursor.execute(
                'SELECT id_plan FROM plan WHERE id_plan = %s',
                (paciente['id_plan'],),
            )
            if cursor.fetchone() is None:
                return None, 'PLAN_INEXISTENTE'

        cursor.execute(
            """
            INSERT INTO usuario (
                id_rol, nombre, apellido, correo_electronico, dni,
                fecha_nacimiento, contrasenia
            )
            VALUES (3, %s, %s, %s, %s, %s, %s)
            """,
            (
                paciente['nombre'],
                paciente['apellido'],
                paciente['correo_electronico'],
                paciente['dni'],
                paciente['fecha_nacimiento'],
                paciente['contrasenia'],
            ),
        )
        id_usuario = int(cursor.lastrowid)

        cursor.execute(
            """
            INSERT INTO paciente (id_plan, id_usuario, nro_afiliado)
            VALUES (%s, %s, %s)
            """,
            (paciente['id_plan'], id_usuario, paciente['nro_afiliado']),
        )
        id_paciente = int(cursor.lastrowid)
        conexion.commit()

        return {
            'id_paciente': id_paciente,
            'id_usuario': id_usuario,
            'nombre': paciente['nombre'],
            'apellido': paciente['apellido'],
            'dni': paciente['dni'],
            'correo_electronico': paciente['correo_electronico'],
            'fecha_nacimiento': paciente['fecha_nacimiento'].isoformat(),
            'id_plan': paciente['id_plan'],
            'nro_afiliado': paciente['nro_afiliado'],
        }, None
    except mysql.connector.IntegrityError as exc:
        conexion.rollback()
        if exc.errno == errorcode.ER_DUP_ENTRY:
            return None, 'EMAIL_DUPLICADO'
        raise
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def buscar_pacientes(dni=None, apellido=None):
    condiciones = []
    parametros = []

    if dni:
        condiciones.append('u.dni LIKE %s')
        parametros.append(f'%{dni}%')
    if apellido:
        condiciones.append('LOWER(u.apellido) LIKE LOWER(%s)')
        parametros.append(f'%{apellido}%')

    where = ' WHERE ' + ' AND '.join(condiciones) if condiciones else ''
    consulta = """
        SELECT p.id_paciente, u.id_usuario, u.nombre, u.apellido, u.dni,
               u.correo_electronico, p.id_plan, pl.nombre AS plan,
               c.nombre AS cobertura, p.nro_afiliado
        FROM paciente p
        JOIN usuario u ON u.id_usuario = p.id_usuario
        LEFT JOIN plan pl ON pl.id_plan = p.id_plan
        LEFT JOIN cobertura c ON c.id_cobertura = pl.id_cobertura
    """ + where + ' ORDER BY u.apellido, u.nombre, p.id_paciente'

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()