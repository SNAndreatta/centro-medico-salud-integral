from datetime import date

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from src.api import ErrorAPI, api

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


def _iniciales(nombre, apellido):
    return f"{(nombre or ' ')[0]}{(apellido or ' ')[0]}".upper().strip() or 'NC'


def _fecha(valor):
    if not valor:
        return '-'
    try:
        return date.fromisoformat(str(valor)[:10]).strftime('%d/%m/%Y')
    except ValueError:
        return '-'


def _normalizar_usuario(usuario):
    id_rol = int(usuario['id_rol'])
    clave, etiqueta = ROLES.get(id_rol, ('desconocido', 'SIN ROL'))

    return {
        'id': int(usuario['id_usuario']),
        'nombre': usuario['nombre'],
        'apellido': usuario['apellido'],
        'iniciales': _iniciales(usuario['nombre'], usuario['apellido']),
        'id_rol': id_rol,
        'rol_clave': clave,
        'rol': etiqueta,
        'mail': usuario['correo_electronico'],
        'dni': usuario['dni'],
        'fecha_nacimiento': _fecha(usuario.get('fecha_nacimiento')),
        'fecha_registro': _fecha(usuario.get('fecha_creacion')),
        'id_medico': usuario.get('id_medico'),
        'matricula': usuario.get('matricula'),
        'especialidad': usuario.get('nombre_especialidad'),
        'id_paciente': usuario.get('id_paciente'),
        'cobertura': usuario.get('nombre_cobertura'),
    }


def _catalogos():
    especialidades = []
    coberturas = []

    try:
        especialidades = [
            {
                'id': e['id_especialidad'],
                'nombre': e['nombre_especialidad'],
            }
            for e in api('GET', '/especialidades').get('especialidades', [])
        ]
    except ErrorAPI:
        pass

    try:
        coberturas = [
            {'id': c['id_cobertura'], 'nombre': c['nombre']}
            for c in api('GET', '/coberturas').get('coberturas', [])
        ]
    except ErrorAPI:
        pass

    return especialidades, coberturas


# =================================
# MOSTRAR USUARIOS
# =================================

@usuario_admin_routes.route('/usuarios')
def obtener_usuarios():
    usuarios = []
    error = None

    try:
        datos = api('GET', '/usuarios')
        usuarios = [
            _normalizar_usuario(usuario)
            for usuario in datos.get('usuarios', [])
        ]
    except ErrorAPI as e:
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
            api('POST', '/usuarios', json={**datos, 'id_rol': id_rol})
            flash('Usuario creado correctamente.', 'success')

        elif id_rol == 4:
            id_especialidad = request.form.get('id_especialidad', type=int)
            matricula = request.form.get('matricula', '').strip()

            if not id_especialidad or not matricula:
                flash('Para crear un médico tenés que indicar especialidad y matrícula.', 'error')
                return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

            respuesta = api('POST', '/medicos', json={
                **datos,
                'id_especialidad': id_especialidad,
                'matricula': matricula,
            })

            id_medico = respuesta['medico']['id_medico']
            coberturas_error = False

            for id_cobertura in request.form.getlist('coberturas'):
                try:
                    api(
                        'POST',
                        f'/medicos/{id_medico}/coberturas',
                        json={'id_cobertura': int(id_cobertura)},
                    )
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
        flash(e.mensaje, 'error')

    return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))


# =================================
# PERFIL DE USUARIO
# =================================

@usuario_admin_routes.route('/usuario/<int:id_usuario>')
def usuario_perfil(id_usuario):
    try:
        datos = api('GET', '/usuarios')
    except ErrorAPI as e:
        flash(e.mensaje, 'error')
        return redirect(url_for('rutas_admin_usuario.obtener_usuarios'))

    usuario = next(
        (
            _normalizar_usuario(u)
            for u in datos.get('usuarios', [])
            if int(u['id_usuario']) == id_usuario
        ),
        None,
    )

    if usuario is None:
        return 'Usuario no encontrado', 404

    return render_template(
        'admin/abm/usuarios/profile.html',
        usuario=usuario,
    )
