from src.repositories.usuarios_repositories import obtener_usuario_por_id
from src.repositories.medicos_repositories import obtener_medico_por_usuario
from src.repositories.pacientes_repositories import (
    obtener_paciente_por_id,
    obtener_paciente_por_usuario,
)
from src.repositories.usuarios_repositories import (
    actualizar_hash_password,
    actualizar_usuario as actualizar_usuario_repositorio,
    eliminar_usuario_por_id,
    guardar_usuario_staff,
    obtener_usuario_para_cambio_password,
    obtener_usuarios,
)
from src.services.medicos_services import eliminar_medico
from src.errores import error_respuesta
from src.utils.roles import ADMINISTRADOR, MEDICO, PACIENTE, RECEPCIONISTA
from src.utils.security import hash_password, verify_password
from src.validators.usuarios_validators import (
    ROLES_FILTRO,
    validar_cambio_password,
    validar_datos_actualizacion_usuario,
    validar_datos_usuario_staff,
)

ROLES_STAFF = {'admin': ADMINISTRADOR, 'recepcionista': RECEPCIONISTA}


def obtener_perfil_usuario(id_usuario):
    usuario = obtener_usuario_por_id(id_usuario)
    if usuario is None:
        return None

    perfil = {
        'id_usuario': int(usuario['id_usuario']),
        'nombre': usuario['nombre'],
        'apellido': usuario['apellido'],
        'id_rol': int(usuario['id_rol']),
        'correo_electronico': usuario['correo_electronico'],
        'dni': usuario['dni'],
        'fecha_nacimiento': usuario['fecha_nacimiento'],
        'fecha_creacion': usuario['fecha_creacion'],
    }

    if perfil['id_rol'] == PACIENTE:
        id_paciente = obtener_paciente_por_usuario(id_usuario)
        if id_paciente is not None:
            paciente = obtener_paciente_por_id(id_paciente)
            if paciente is not None:
                perfil['paciente'] = {
                    'id_paciente': int(paciente['id_paciente']),
                    'id_cobertura': paciente['id_cobertura'],
                    'nombre_cobertura': paciente['nombre_cobertura'],
                    'nro_afiliado': paciente['nro_afiliado'],
                }
    elif perfil['id_rol'] == MEDICO:
        medico = obtener_medico_por_usuario(id_usuario)
        if medico is not None:
            perfil['medico'] = {
                'id_medico': int(medico['id_medico']),
                'id_especialidad': int(medico['id_especialidad']),
                'nombre_especialidad': medico['nombre_especialidad'],
                'matricula': medico['matricula'],
            }

    return perfil


def listar_usuarios(rol=None):
    id_rol = ROLES_FILTRO.get(rol) if rol is not None else None
    return obtener_usuarios(id_rol)


def crear_usuario_staff(datos):
    usuario, error = validar_datos_usuario_staff(datos)
    if error:
        return error, 400

    usuario['contrasenia'] = hash_password(usuario.pop('password'))
    usuario_guardado = guardar_usuario_staff(usuario)
    if usuario_guardado is None:
        return error_respuesta(
            'Ya existe un usuario con ese correo electrónico o DNI',
            'USUARIO_DUPLICADO',
        ), 400

    return {'usuario': usuario_guardado}, 201


def actualizar_usuario(id_usuario, datos):
    datos_validados, error = validar_datos_actualizacion_usuario(datos)
    if error:
        return error, 400

    error = actualizar_usuario_repositorio(id_usuario, datos_validados)
    if error == 'USUARIO_NO_EXISTE':
        return error_respuesta('El usuario no existe', 'USUARIO_INEXISTENTE'), 404
    if error == 'USUARIO_DUPLICADO':
        return error_respuesta(
            'Ya existe un usuario con ese correo electrónico o DNI',
            'USUARIO_DUPLICADO',
        ), 400

    return {'mensaje': 'Datos actualizados correctamente'}, 200


def eliminar_usuario(id_usuario, usuario_actual):
    if id_usuario == usuario_actual['id_usuario']:
        return error_respuesta(
            'No podés eliminar tu propia cuenta',
            'OPERACION_NO_PERMITIDA',
        ), 400

    usuario = obtener_usuario_por_id(id_usuario)
    if usuario is None:
        return error_respuesta('El usuario no existe', 'USUARIO_INEXISTENTE'), 404

    # Los médicos tienen datos asociados (agendas, coberturas) y su baja
    # ya está resuelta en su propio servicio.
    if usuario['id_rol'] == MEDICO:
        medico = obtener_medico_por_usuario(id_usuario)
        if medico is None:
            return error_respuesta(
                'El usuario no tiene un perfil de médico asociado',
                'MEDICO_INEXISTENTE',
            ), 404
        return eliminar_medico(int(medico['id_medico']))

    error = eliminar_usuario_por_id(id_usuario)
    if error == 'USUARIO_NO_EXISTE':
        return error_respuesta('El usuario no existe', 'USUARIO_INEXISTENTE'), 404
    if error == 'USUARIO_EN_USO':
        return error_respuesta(
            'No se puede eliminar el usuario porque tiene datos asociados',
            'USUARIO_EN_USO',
        ), 409

    return {'mensaje': 'Usuario eliminado correctamente'}, 200


def actualizar_password_usuario(id_usuario, datos, usuario_actual):
    es_cambio_propio = id_usuario == usuario_actual['id_usuario']
    sin_permiso = error_respuesta(
        'No tenés permiso para cambiar esta contraseña',
        'PERMISOS_INSUFICIENTES',
    ), 403
    if not es_cambio_propio:
        if usuario_actual['id_rol'] != ADMINISTRADOR:
            return sin_permiso
        administrador = obtener_usuario_por_id(usuario_actual['id_usuario'])
        if administrador is None or administrador['id_rol'] != ADMINISTRADOR:
            return sin_permiso

    error = validar_cambio_password(datos, es_cambio_propio)
    if error:
        return error

    usuario = obtener_usuario_para_cambio_password(id_usuario)
    if usuario is None:
        return error_respuesta('El usuario no existe', 'USUARIO_INEXISTENTE'), 404

    if es_cambio_propio:
        if not verify_password(usuario['contrasenia'], datos['password_actual']):
            return error_respuesta('La contraseña actual es incorrecta', 'PASSWORD_ACTUAL_INVALIDA'), 403
    elif usuario['id_rol'] not in ROLES_STAFF.values():
        return error_respuesta(
            'El administrador solo puede restablecer contraseñas del personal administrativo y de recepción',
            'PERMISOS_INSUFICIENTES',
        ), 403

    nuevo_hash = hash_password(datos['nueva_password'])
    if not actualizar_hash_password(usuario, nuevo_hash):
        return error_respuesta(
            'La cuenta cambió durante la operación. Volvé a intentar el cambio',
            'USUARIO_MODIFICADO',
        ), 409

    return {'mensaje': 'Contraseña actualizada correctamente'}, 200
