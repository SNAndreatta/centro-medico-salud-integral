import re
from datetime import date

from werkzeug.security import generate_password_hash

from src.errores import error_respuesta
from src.repositories.pacientes_repositories import registrar_paciente


CAMPOS_REQUERIDOS = {
    'nombre',
    'apellido',
    'dni',
    'correo_electronico',
    'fecha_nacimiento',
    'password',
}
CAMPOS_OPCIONALES = {'id_plan', 'nro_afiliado'}


def procesar_registro_paciente(datos):
    if not CAMPOS_REQUERIDOS.issubset(datos) or set(datos) - CAMPOS_REQUERIDOS - CAMPOS_OPCIONALES:
        return error_respuesta(
            'Faltan campos obligatorios o se recibieron campos desconocidos',
            'CUERPO_INVALIDO',
        ), 400

    for campo in ('nombre', 'apellido', 'dni', 'correo_electronico', 'password', 'fecha_nacimiento'):
        if not isinstance(datos[campo], str) or not datos[campo].strip():
            return error_respuesta(f'{campo} es obligatorio', 'CAMPO_INVALIDO'), 400

    nombre = datos['nombre'].strip()
    apellido = datos['apellido'].strip()
    dni = datos['dni'].strip()
    correo = datos['correo_electronico'].strip().lower()
    password = datos['password']

    if len(nombre) > 100 or len(apellido) > 100:
        return error_respuesta('Nombre y apellido no pueden superar 100 caracteres', 'CAMPO_INVALIDO'), 400
    if not re.fullmatch(r'\d{7,8}', dni):
        return error_respuesta('El DNI debe contener 7 u 8 dígitos', 'DNI_INVALIDO'), 400
    if len(correo) > 150 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', correo):
        return error_respuesta('El correo electrónico no es válido', 'EMAIL_INVALIDO'), 400
    if len(password) > 256:
        return error_respuesta('La contraseña excede la longitud permitida', 'PASSWORD_INVALIDO'), 400

    try:
        fecha_nacimiento = date.fromisoformat(datos['fecha_nacimiento'].strip())
    except ValueError:
        return error_respuesta('fecha_nacimiento debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA'), 400
    if fecha_nacimiento > date.today():
        return error_respuesta('fecha_nacimiento no puede ser futura', 'FECHA_INVALIDA'), 400

    id_plan = datos.get('id_plan')
    if id_plan is not None and (
        isinstance(id_plan, bool) or not isinstance(id_plan, int) or id_plan <= 0
    ):
        return error_respuesta('id_plan debe ser un entero positivo o nulo', 'PLAN_INVALIDO'), 400

    nro_afiliado = datos.get('nro_afiliado')
    if nro_afiliado is not None:
        if not isinstance(nro_afiliado, str) or not nro_afiliado.strip() or len(nro_afiliado.strip()) > 50:
            return error_respuesta('nro_afiliado debe ser texto de hasta 50 caracteres o nulo', 'AFILIADO_INVALIDO'), 400
        nro_afiliado = nro_afiliado.strip()

    paciente = {
        'nombre': nombre,
        'apellido': apellido,
        'dni': dni,
        'correo_electronico': correo,
        'fecha_nacimiento': fecha_nacimiento,
        'contrasenia': generate_password_hash(password),
        'id_plan': id_plan,
        'nro_afiliado': nro_afiliado,
    }
    paciente_guardado, error = registrar_paciente(paciente)
    if error == 'EMAIL_DUPLICADO':
        return error_respuesta('Ya existe una cuenta con ese correo electrónico', 'EMAIL_DUPLICADO'), 400
    if error == 'PLAN_INEXISTENTE':
        return error_respuesta('El plan indicado no existe', 'PLAN_INEXISTENTE'), 400

    return {'mensaje': 'Paciente registrado exitosamente', 'paciente': paciente_guardado}, 201