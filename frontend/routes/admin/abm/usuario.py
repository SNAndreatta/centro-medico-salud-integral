from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from src.api import ErrorAPI
from src.api_catalogos import (
    agregar_coberturas_medico,
    coberturas_medico,
    obtener_coberturas,
    obtener_especialidades,
)
from src.api_usuario import (
    buscar_usuario,
    crear_medico as api_crear_medico,
    crear_usuario as api_crear_usuario,
    editar_usuario as api_editar_usuario,
    editar_medico as api_editar_medico,
    eliminar_usuario as api_eliminar_usuario,
    listar_usuarios,
)
from src.errores import es_sesion_vencida, sesion_vencida
from src.permisos import requiere_rol

usuario_admin_routes = Blueprint('rutas_admin_usuario', __name__)

# id_rol -> (clave usada por los filtros, etiqueta visible)
ROLES = {
    1: ('admin', 'ADMIN'),
    2: ('recepcionista', 'RECEPCIÓN'),
    3: ('paciente', 'PACIENTE'),
    4: ('medico', 'MÉDICO'),
}

ROLES_FILTRO = [
    {'clave': clave, 'nombre': etiqueta}
    for clave, etiqueta in ROLES.values()
]

# Roles que se pueden crear desde este ABM. Los pacientes se registran
# desde el formulario público de alta.
ROLES_CREAR = [
    {'id': id_rol, 'nombre': ROLES[id_rol][1]}
    for id_rol in (1, 2, 4)
]
ROLES_CREAR_IDS = {rol['id'] for rol in ROLES_CREAR}


def _con_rol(usuario):
    clave, etiqueta = ROLES.get(usuario['id_rol'], ('desconocido', 'SIN ROL'))

    return {**usuario, 'rol_clave': clave, 'rol': etiqueta}


def _catalogos():
    especialidades = []
    coberturas = []

    try:
        especialidades = obtener_especialidades()
    except ErrorAPI:
        pass

    try:
        coberturas = obtener_coberturas()
    except ErrorAPI:
        pass

    return especialidades, coberturas


# =================================
# MOSTRAR USUARIOS
# =================================

@usuario_admin_routes.route('/usuarios')
@requiere_rol("admin")
def obtener_usuarios():
    usuarios = []
    error = None

    try:
        usuarios = [_con_rol(usuario) for usuario in listar_usuarios()]
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        error = e.mensaje

    especialidades, coberturas = _catalogos()

    return render_template(
        'admin/abm/usuarios/index.html',
        usuarios=usuarios,
        roles=ROLES_FILTRO,
        roles_crear=ROLES_CREAR,
        especialidades=especialidades,
        coberturas=coberturas,
        error=error,
    )


# =================================
# CREAR USUARIO
# =================================

@usuario_admin_routes.route('/usuarios/crear', methods=['POST'])
@requiere_rol("admin")
def crear_usuario():
    nombre = request.form.get('nombre', '').strip()
    apellido = request.form.get('apellido', '').strip()
    mail = request.form.get('mail', '').strip().lower()
    dni = request.form.get('dni', '').strip()
    fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
    password = request.form.get('password', '')
    id_rol = request.form.get('id_rol', type=int)

    if not all([nombre, apellido, mail, dni, password]) or id_rol not in ROLES_CREAR_IDS:
        flash('Completá todos los campos obligatorios.', 'error')
        return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

    datos = {
        'nombre': nombre,
        'apellido': apellido,
        'dni': dni,
        'correo_electronico': mail,
        'password': password,
    }
    if fecha_nacimiento:
        datos['fecha_nacimiento'] = fecha_nacimiento

    try:
        if id_rol in (1, 2):
            api_crear_usuario({**datos, 'id_rol': id_rol})
            flash('Usuario creado correctamente.', 'success')

        elif id_rol == 4:
            id_especialidad = request.form.get('id_especialidad', type=int)
            matricula = request.form.get('matricula', '').strip()

            if not id_especialidad or not matricula:
                flash('Para crear un médico tenés que indicar especialidad y matrícula.', 'error')
                return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

            id_medico = api_crear_medico({
                **datos,
                'id_especialidad': id_especialidad,
                'matricula': matricula,
            })
            coberturas_error = False

            for id_cobertura in request.form.getlist('coberturas'):
                try:
                    agregar_coberturas_medico(id_medico, [id_cobertura])
                except (ErrorAPI, ValueError):
                    coberturas_error = True

            if coberturas_error:
                flash(
                    'El médico se creó, pero no se pudieron asociar todas las coberturas.',
                    'error',
                )
            else:
                flash('Médico creado correctamente.', 'success')

    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')

    return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))


# =================================
# PERFIL DE USUARIO
# =================================

@usuario_admin_routes.route('/usuario/<int:id_usuario>')
@requiere_rol("admin")
def usuario_perfil(id_usuario):
    try:
        usuario = buscar_usuario(id_usuario)
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

    if usuario is None:
        return 'Usuario no encontrado', 404

    usuario = _con_rol(usuario)
    especialidades = []
    coberturas_medico_actuales = []
    coberturas_disponibles = []

    # Los datos extra solo se necesitan para los médicos.
    if usuario['id_rol'] == 4:
        especialidades, catalogo_coberturas = _catalogos()
        coberturas_medico_actuales = coberturas_medico(usuario['id_medico'])

        ids_asociadas = {c['id'] for c in coberturas_medico_actuales}
        coberturas_disponibles = [
            c for c in catalogo_coberturas if c['id'] not in ids_asociadas
        ]

    return render_template(
        'admin/abm/usuarios/profile.html',
        usuario=usuario,
        especialidades=especialidades,
        coberturas_medico=coberturas_medico_actuales,
        coberturas_disponibles=coberturas_disponibles,
    )


# =================================
# EDITAR USUARIO
# =================================

@usuario_admin_routes.route('/usuario/<int:id_usuario>/editar', methods=['POST'])
@requiere_rol("admin")
def editar_usuario(id_usuario):
    perfil = redirect(
        url_for('rutas_admin_usuario.usuario_perfil', id_usuario=id_usuario)
    )

    try:
        usuario = buscar_usuario(id_usuario)
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')
        return perfil

    if usuario is None:
        return 'Usuario no encontrado', 404

    nombre = request.form.get('nombre', '').strip()
    apellido = request.form.get('apellido', '').strip()
    dni = request.form.get('dni', '').strip()
    mail = request.form.get('mail', '').strip().lower()
    fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()

    if not all([nombre, apellido, dni, mail]):
        flash('Completá todos los campos obligatorios.', 'error')
        return perfil

    datos = {
        'nombre': nombre,
        'apellido': apellido,
        'dni': dni,
        'correo_electronico': mail,
    }
    if fecha_nacimiento:
        datos['fecha_nacimiento'] = fecha_nacimiento

    try:
        api_editar_usuario(id_usuario, datos)

        if usuario['id_rol'] == 4 and usuario['id_medico']:
            id_especialidad = request.form.get('id_especialidad', type=int)
            matricula = request.form.get('matricula', '').strip()

            if not id_especialidad or not matricula:
                flash('Para un médico tenés que indicar especialidad y matrícula.', 'error')
                return perfil

            api_editar_medico(usuario['id_medico'], {
                'id_especialidad': id_especialidad,
                'matricula': matricula,
            })

            # Solo se agregan coberturas nuevas (las que ya tenía no se tocan).
            coberturas_error = False

            for id_cobertura in request.form.getlist('coberturas'):
                try:
                    agregar_coberturas_medico(usuario['id_medico'], [id_cobertura])
                except (ErrorAPI, ValueError):
                    coberturas_error = True

            if coberturas_error:
                flash(
                    'Los datos se guardaron, pero no se pudieron agregar todas las coberturas.',
                    'error',
                )
                return perfil

        flash('Datos actualizados correctamente.', 'success')

    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')

    return perfil


# =================================
# ELIMINAR USUARIO
# =================================

@usuario_admin_routes.route('/usuario/<int:id_usuario>/eliminar', methods=['POST'])
@requiere_rol("admin")
def eliminar_usuario(id_usuario):
    try:
        api_eliminar_usuario(id_usuario)
    except ErrorAPI as e:
        if es_sesion_vencida(e):
            return sesion_vencida()
        flash(e.mensaje, 'error')
        return redirect(
            url_for('rutas_admin_usuario.usuario_perfil', id_usuario=id_usuario)
        )

    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))
