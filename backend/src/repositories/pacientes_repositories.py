import mysql.connector
from mysql.connector import errorcode

from src.db import obtener_cursor
from src.utils.roles import PACIENTE


def generar_nro_afiliado(id_paciente):
    """Genera automáticamente el número de afiliado de un paciente."""
    return f"AFI-{int(id_paciente):06d}"


def obtener_paciente_por_id(id_paciente):
    conexion, cursor = obtener_cursor()
    try:
        query = """
        SELECT p.id_paciente, p.nro_afiliado, u.id_usuario, u.nombre, u.apellido, 
               u.correo_electronico, u.dni, u.fecha_nacimiento, u.fecha_creacion, 
               r.id_rol, r.nombre AS nombre_rol, c.id_cobertura, c.nombre AS nombre_cobertura
        FROM paciente p
        INNER JOIN usuario u ON p.id_usuario = u.id_usuario
        LEFT JOIN rol r ON u.id_rol = r.id_rol
        LEFT JOIN cobertura c ON p.id_cobertura = c.id_cobertura
        WHERE p.id_paciente = %s 
        LIMIT 1
        """
        cursor.execute(query, (id_paciente,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()

def actualizar_datos_paciente(id_paciente, datos):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_usuario, id_cobertura FROM paciente WHERE id_paciente = %s LIMIT 1',
            (id_paciente,),
        )
        paciente = cursor.fetchone()
        if paciente is None:
            return 'PACIENTE_INEXISTENTE'

        id_usuario = paciente['id_usuario']

        if 'correo_electronico' in datos:
            cursor.execute(
                """
                SELECT id_usuario
                FROM usuario
                WHERE correo_electronico = %s AND id_usuario <> %s
                LIMIT 1
                """,
                (datos['correo_electronico'], id_usuario),
            )
            if cursor.fetchone() is not None:
                return 'EMAIL_DUPLICADO'

        if datos.get('id_cobertura') is not None:
            cursor.execute(
                'SELECT id_cobertura FROM cobertura WHERE id_cobertura = %s LIMIT 1',
                (datos['id_cobertura'],),
            )
            if cursor.fetchone() is None:
                return 'COBERTURA_INEXISTENTE'

        # El nro. de afiliado es automático: si el paciente cambia de cobertura
        # se genera uno nuevo para la nueva cobertura (sin intervención manual).
        if 'id_cobertura' in datos:
            nueva_cobertura = datos['id_cobertura']
            if nueva_cobertura != paciente['id_cobertura']:
                datos = dict(datos)
                datos['nro_afiliado'] = (
                    generar_nro_afiliado(id_paciente)
                    if nueva_cobertura is not None
                    else None
                )

        campos_usuario = ('nombre', 'apellido', 'correo_electronico', 'dni', 'fecha_nacimiento')
        set_usuario = [f'{campo} = %s' for campo in campos_usuario if campo in datos]
        if set_usuario:
            valores_usuario = [datos[campo] for campo in campos_usuario if campo in datos]
            valores_usuario.append(id_usuario)
            cursor.execute(
                f"UPDATE usuario SET {', '.join(set_usuario)} WHERE id_usuario = %s",
                valores_usuario,
            )

        campos_paciente = ('id_cobertura', 'nro_afiliado')
        set_paciente = [f'{campo} = %s' for campo in campos_paciente if campo in datos]
        if set_paciente:
            valores_paciente = [datos[campo] for campo in campos_paciente if campo in datos]
            valores_paciente.append(id_paciente)
            cursor.execute(
                f"UPDATE paciente SET {', '.join(set_paciente)} WHERE id_paciente = %s",
                valores_paciente,
            )

        conexion.commit()
        return {'paciente': obtener_paciente_por_id(id_paciente)} ,None
    except mysql.connector.IntegrityError as exc:
        conexion.rollback()
        if exc.errno == errorcode.ER_DUP_ENTRY:
            return 'EMAIL_DUPLICADO'
        raise
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()

def obtener_paciente_por_usuario(id_usuario):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_paciente FROM paciente WHERE id_usuario = %s LIMIT 1',
            (id_usuario,),
        )
        fila = cursor.fetchone()
        if fila is None:
            return None
        return int(fila['id_paciente'])
    finally:
        cursor.close()
        conexion.close()


def obtener_usuario_por_paciente(id_paciente):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_usuario FROM paciente WHERE id_paciente = %s LIMIT 1',
            (id_paciente,),
        )
        fila = cursor.fetchone()
        if fila is None:
            return None
        return int(fila['id_usuario'])
    finally:
        cursor.close()
        conexion.close()


def registrar_paciente(paciente):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_usuario FROM usuario WHERE correo_electronico = %s LIMIT 1',
            (paciente['correo_electronico'],),
        )
        if cursor.fetchone() is not None:
            return None, 'EMAIL_DUPLICADO'

        if paciente['id_cobertura'] is not None:
            cursor.execute(
                'SELECT id_cobertura FROM cobertura WHERE id_cobertura = %s',
                (paciente['id_cobertura'],),
            )
            if cursor.fetchone() is None:
                return None, 'COBERTURA_INEXISTENTE'

        cursor.execute(
            """
            INSERT INTO usuario (
                id_rol, nombre, apellido, correo_electronico, dni,
                fecha_nacimiento, contrasenia
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                PACIENTE,
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
            INSERT INTO paciente (id_cobertura, id_usuario, nro_afiliado)
            VALUES (%s, %s, NULL)
            """,
            (paciente['id_cobertura'], id_usuario),
        )
        id_paciente = int(cursor.lastrowid)

        # El nro. de afiliado se genera automáticamente.
        # Los pacientes particulares (sin cobertura) se guardan sin nro. de afiliado.
        nro_afiliado = None
        if paciente['id_cobertura'] is not None:
            nro_afiliado = generar_nro_afiliado(id_paciente)
            cursor.execute(
                'UPDATE paciente SET nro_afiliado = %s WHERE id_paciente = %s',
                (nro_afiliado, id_paciente),
            )

        conexion.commit()

        return {
            'id_paciente': id_paciente,
            'id_usuario': id_usuario,
            'nombre': paciente['nombre'],
            'apellido': paciente['apellido'],
            'dni': paciente['dni'],
            'correo_electronico': paciente['correo_electronico'],
            'fecha_nacimiento': paciente['fecha_nacimiento'].isoformat(),
            'id_cobertura': paciente['id_cobertura'],
            'nro_afiliado': nro_afiliado,
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

def obtener_turnos_de_paciente(id_paciente):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            'SELECT id_paciente FROM paciente WHERE id_paciente = %s LIMIT 1',
            (id_paciente,),
        )
        if cursor.fetchone() is None:
            return None, 'PACIENTE_NO_EXISTE'

        cursor.execute(
            """
            SELECT t.id_turno,
                   t.fecha,
                   t.hora,
                   t.estado,
                   m.id_medico,
                   u.nombre AS nombre_medico,
                   u.apellido AS apellido_medico,
                   e.id_especialidad,
                   e.nombre_especialidad,
                   c.id_cobertura,
                   c.nombre AS nombre_cobertura
            FROM turno t
            JOIN agenda a ON a.id_agenda = t.id_agenda
            JOIN medico m ON m.id_medico = a.id_medico
            JOIN usuario u ON u.id_usuario = m.id_usuario
            JOIN especialidad e ON e.id_especialidad = m.id_especialidad
            LEFT JOIN cobertura c ON c.id_cobertura = t.id_cobertura
            WHERE t.id_paciente = %s
            ORDER BY t.fecha DESC, t.hora DESC
            """,
            (id_paciente,),
        )
        return cursor.fetchall(), None
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
               u.correo_electronico, p.id_cobertura,
               c.nombre AS cobertura, p.nro_afiliado
        FROM paciente p
        JOIN usuario u ON u.id_usuario = p.id_usuario
        LEFT JOIN cobertura c ON c.id_cobertura = p.id_cobertura
    """ + where + ' ORDER BY u.apellido, u.nombre, p.id_paciente'

    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()