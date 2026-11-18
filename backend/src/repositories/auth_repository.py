from src.db import obtener_cursor


def obtener_usuario_por_email(correo_electronico):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute(
            """
            SELECT id_usuario, id_rol, nombre, apellido, correo_electronico, contrasenia
            FROM usuario
            WHERE LOWER(correo_electronico) = LOWER(%s)
            """,
            (correo_electronico,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()

