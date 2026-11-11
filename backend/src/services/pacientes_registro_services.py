from src.errores import error_respuesta
from src.repositories.pacientes_repositories import registrar_paciente
from src.utils.security import hash_password
from src.validators.pacientes_validators import validar_datos_registro_paciente


def procesar_registro_paciente(datos):
    paciente, error, status_code = validar_datos_registro_paciente(datos)
    if error:
        return error, status_code

    paciente['contrasenia'] = hash_password(paciente.pop('password'))
    paciente_guardado, error = registrar_paciente(paciente)
    if error == 'EMAIL_DUPLICADO':
        return error_respuesta('Ya existe una cuenta con ese correo electrónico', 'EMAIL_DUPLICADO'), 400
    if error == 'COBERTURA_INEXISTENTE':
        return error_respuesta('La cobertura indicada no existe', 'COBERTURA_INEXISTENTE'), 400

    return {'mensaje': 'Paciente registrado exitosamente', 'paciente': paciente_guardado}, 201