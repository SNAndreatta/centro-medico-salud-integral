from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

from src.api import ErrorAPI
from src.api_auth import coberturas as coberturas_registro
from src.api_auth import login as login_api
from src.api_auth import registrar as registrar_api

auth_routes = Blueprint('rutas_auth', __name__)


ROLES = {
    1: 'administrador',
    2: 'recepcionista',
    3: 'paciente',
    4: 'medico',
}


def _listar_coberturas():
    """Devuelve [] si el backend no está disponible (alta como Particular)."""
    try:
        return coberturas_registro()
    except ErrorAPI:
        return []


# LOGIN
@auth_routes.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        correo_electronico = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not correo_electronico or not password:
            return render_template(
                'auth/login.html',
                mensaje='Completá todos los campos.'
            )

        try:
            datos = login_api(correo_electronico, password)
        except ErrorAPI as error:
            return render_template('auth/login.html', mensaje=error.mensaje)

        usuario = datos.get('usuario')
        print("LOGIN USUARIO:", usuario, flush=True)
        access_token = datos.get('access_token')

        if not usuario or not access_token:
            return render_template(
                'auth/login.html',
                mensaje='El servidor devolvió una respuesta incompleta.'
            )

        id_rol = usuario.get('id_rol')

        session.clear()
        session['access_token'] = access_token
        session['usuario'] = usuario
        session['id_usuario'] = usuario.get('id_usuario')
        session['id_rol'] = id_rol
        session['rol'] = ROLES.get(id_rol, 'paciente')
        session['nombre'] = usuario.get('nombre', '')
        session['apellido'] = usuario.get('apellido', '')

        return redirect(url_for('rutas_home.home'))

    return render_template('auth/login.html')


# REGISTRO
@auth_routes.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        nombre = request.form.get('first_name', '').strip()
        apellido = request.form.get('last_name', '').strip()
        dni = request.form.get('dni', '').strip()
        correo_electronico = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirmar_password = request.form.get('confirm_password', '')
        fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
        id_cobertura = request.form.get('id_cobertura', '').strip()

        if not all([
            nombre,
            apellido,
            dni,
            correo_electronico,
            password,
            confirmar_password,
            fecha_nacimiento
        ]):
            return render_template(
                'auth/register.html',
                mensaje='Completá todos los campos.',
                coberturas=_listar_coberturas(),
                id_cobertura=id_cobertura
            )

        if password != confirmar_password:
            return render_template(
                'auth/register.html',
                mensaje='Las contraseñas no coinciden.',
                coberturas=_listar_coberturas(),
                id_cobertura=id_cobertura
            )

        # El nro. de afiliado NO se pide: el backend lo genera automáticamente
        # cuando el paciente elige una cobertura.
        cobertura_id = None
        if id_cobertura:
            try:
                cobertura_id = int(id_cobertura)
            except ValueError:
                return render_template(
                    'auth/register.html',
                    mensaje='La cobertura seleccionada no es válida.',
                    coberturas=_listar_coberturas(),
                    id_cobertura=''
                )

        datos = {
            'nombre': nombre,
            'apellido': apellido,
            'dni': dni,
            'correo_electronico': correo_electronico,
            'fecha_nacimiento': fecha_nacimiento,
            'password': password,
            'id_cobertura': cobertura_id,
        }

        try:
            registrar_api(datos)
        except ErrorAPI as error:
            return render_template(
                'auth/register.html',
                mensaje=error.mensaje,
                coberturas=_listar_coberturas(),
                id_cobertura=id_cobertura
            )

        return redirect(url_for('rutas_auth.login'))

    return render_template(
        'auth/register.html',
        coberturas=_listar_coberturas(),
        id_cobertura=''
    )


# LOGOUT
@auth_routes.route('/logout', methods=['GET', 'POST'])
def logout():

    session.clear()

    return redirect(url_for('rutas_auth.login'))
